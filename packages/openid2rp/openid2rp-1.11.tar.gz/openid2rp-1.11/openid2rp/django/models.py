from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

class UserOpenID(models.Model):
	user = models.ForeignKey(User, related_name='openids')
	uri = models.CharField(max_length=255, blank=False, null=False)
	insert_date = models.DateTimeField(null=False, blank=False, auto_now_add=True, editable=False)
	last_modified = models.DateTimeField(null=False, blank=False, auto_now=True, editable=False)
	def __unicode__(self):
		return smart_unicode("OpenID claim for user '"+str(self.user)+"': "+str(self.uri))
		
class OpenIDSession(models.Model):
	claimedId = models.CharField(max_length=255, blank=False, null=False)
	assoc_handle = models.CharField(max_length=255, blank=False, null=False)
	mac_key = models.CharField(max_length=255, blank=False, null=False)
	expiration_date = models.DateTimeField(null=False, blank=False, editable=False)
	session_type = models.CharField(max_length=255, blank=True, null=True)
	assoc_type = models.CharField(max_length=255, blank=True, null=True)
	ns = models.CharField(max_length=255, blank=True, null=True)
	def __unicode__(self):
		return smart_unicode("OpenID session for '"+str(self.claimedId)+"', expires at "+str(self.expiration_date))
	
class OpenIDNonce(models.Model):
	nonce = models.CharField(max_length=255, blank=False, null=False)
	expiration_date = models.DateTimeField(null=False, blank=False, editable=False)
	def __unicode__(self):
		return smart_unicode("OpenID nonce '"+str(self.nonce)+"', expires at "+str(self.expiration_date))

class DiscoveryCache(models.Model):
	uri = models.CharField(max_length=255, blank=False, null=False)
	services = models.TextField(blank=True, null=True)
	op_endpoint = models.TextField(blank=True, null=True)
	op_local = models.TextField(blank=True, null=True)
