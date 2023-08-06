# -*- coding: utf-8 -*-
# Django authentication backend, based on openid2rp
# Copyright Peter Tröger, 2010
# Licensed under the Academic Free License, version 3

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from openid2rp.django.models import UserOpenID, OpenIDSession, OpenIDNonce, DiscoveryCache
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import openid2rp
import datetime

# we need to accept some difference between provider time and our time, for nonce and session checking
# Martin says: Use the Kerberos default
shiftVal = int(getattr(settings, 'OPENID2RP_MAXTIMESHIFT', '5'))
maxTimeShift=datetime.timedelta(minutes=shiftVal)
delayVal = int(getattr(settings, 'OPENID2RP_MAXLOGINDELAY', '5'))
maxLoginDelay=datetime.timedelta(minutes=delayVal)

# mirror the AX key name dict, so that the app does not need openid2rp at all
AX = openid2rp.AX

class IncorrectURIError(Exception):
	pass

class IncorrectClaimError(Exception):
	pass
	
class MissingSessionError(Exception):
	pass

class AuthenticationError(Exception):
	pass

class ReplayAttackError(Exception):
	pass

class IncompleteAnswerError(Exception):
	pass
	
class MultipleClaimUsageError(Exception):
	pass
	
class TookTooLongError(Exception):
	pass

def cleanup():
	try:
		# delete all expired nonces 
		entries=OpenIDNonce.objects.filter(Q(expiration_date__lt = datetime.datetime.utcnow()))
		for e in entries:
			e.delete()
	except:
		pass
	try:
		# delete all expired sessions
		entries=OpenIDSession.objects.filter(Q(expiration_date__lt = datetime.datetime.utcnow()))
		for e in entries:
			e.delete()
	except:
		pass
	
def storeNonce(nonce):
	global maxTimeShift, maxLoginDelay
	db = OpenIDNonce()
	db.nonce=nonce
	db.expiration_date = datetime.datetime.utcnow() + maxTimeShift + maxLoginDelay
	db.save()
	
def knownNonce(n):
	try:
		OpenIDNonce.objects.get(nonce=n)
	except:
		return False
	return True
	
def storeSession(session, claim):
	global maxTimeShift

	db = OpenIDSession()
	db.assoc_handle=session['assoc_handle']
	db.mac_key=session['mac_key']
	db.claimedId=claim
	# Expire session in provider-given amount of seconds, consider possible shift
	db.expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=long(session['expires_in'])) - maxTimeShift
	if 'assoc_type' in session:
		db.assoc_type=session['assoc_type']
	if 'ns' in session:
		db.ns=session['ns']
	if 'session_type' in session:
		db.session_type=session['session_type']
	db.save()

def getSessionByHandle(handle):
	try:
		result = OpenIDSession.objects.filter(Q(assoc_handle=handle)).values()[0]
	except:
		return None
	# we can live with the fact that the original expires_in field is missing, since openid2rp is not checking it anyway
	return result

def getSessionByClaim(claim):
	try:
		result = OpenIDSession.objects.filter(Q(claimedId=claim)).values()[0]
	except:
		return None
	# we can live with the fact that the original expires_in field is missing, since openid2rp is not checking it anyway
	return result

	
def linkOpenID(user, openid):
	claim=UserOpenID(user=user, uri=openid)
	claim.save()

def getOpenIDs(user):
	return UserOpenID.objects.filter(user=user).values_list('uri', flat=True)

def unlinkOpenID(user, openid):
	res = UserOpenID.objects.filter(Q(user=user, uri=openid))
	for r in res:
		r.delete()

def preAuthenticate(uri, answer_url, 
					sreg = (('nickname', 'email'), ()),
					ax = ((openid2rp.AX.email, openid2rp.AX.first, openid2rp.AX.last), ()),
					reuse_session = True):

	cleanup()
	try:
		kind, claimedId = openid2rp.normalize_uri(uri)			
	except Exception, e:
		raise IncorrectURIError(str(e))
	res = openid2rp.discover(claimedId)
	if res is not None:
		services, op_endpoint, op_local = res
		try:
			dcache=DiscoveryCache.objects.get(uri=claimedId)
		except:
			dcache=DiscoveryCache()
			dcache.uri=claimedId
		dcache.services=" ".join(services)
		dcache.op_local=op_local
		dcache.op_endpoint=op_endpoint
		dcache.save()
		# re-use session in order to avoid provider roundtrip here
		# some providers (Wordpress) do not like that, and send 'invalidate_handle' then,
		# which would need another user roundtrip - therefore, the app can switch it off
		if reuse_session:
			session = getSessionByClaim(claimedId)
		else:
			session = None
		if not session:
			session = openid2rp.associate(services, op_endpoint)
			storeSession(session, claimedId)
		redirect_url=openid2rp.request_authentication( services, op_endpoint, session['assoc_handle'], answer_url, claimedId, op_local, sreg=sreg, ax=ax )
		response=HttpResponse()
		response['Location']=redirect_url
		response.status_code=303
		return response
	else:
		raise IncorrectClaimError()

class Backend(ModelBackend):	
	supports_object_permissions = False
	supports_anonymous_user = True
	supports_inactive_user = True
	
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None

	def discovered_get(self, uri):
		try:
			dcache=DiscoveryCache.objects.get(uri=uri)
			return dcache.services.split(" "), dcache.op_endpoint, dcache.op_local		
		except DiscoveryCache.DoesNotExist:
			return None


	def authenticate(self, **credentials):
		global maxTimeShift, maxLoginDelay

		# the default way for telling Django that this auth backend does not fit
		if not ("openidrequest" in credentials):
			raise TypeError

		request=credentials['openidrequest']
		query=request.META['QUERY_STRING']

		try:
			signed, claimedId = openid2rp.verify(query, self.discovered_get, getSessionByHandle, knownNonce)
		except Exception, e:
			raise AuthenticationError(str(e))

		if 'openid.response_nonce' in request.GET:
			storeNonce(request.GET['openid.response_nonce'])

		# look up OpenID claim string in local database
		idrecord=UserOpenID.objects.filter(Q(uri=claimedId))
		if len(idrecord)>1:
			# more than one user has this claimID, which is definitly wrong
			raise MultipleClaimUsageError()
		elif len(idrecord)<1:
			# No user has this OpenID claim string assigned
			user = AnonymousUser()
		else:
			user=idrecord[0].user

		# inactive users are handled by the later login() method, so we can return them here too
		user.openid_claim = claimedId
		user.openid_ax = openid2rp.get_ax(query, openid2rp.get_namespaces(query), signed)
		user.openid_sreg = openid2rp.get_sreg(query, signed)
		user.openid_email = openid2rp.get_email(query)
		return user
		
