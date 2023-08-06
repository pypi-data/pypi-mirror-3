# This is a simple store of OpenID data
import heapq, time, calendar, openid2rp

class InMemoryStore:
    nonce_lifetime = 300 #s

    def __init__(self):
        # ongoing logins
        self.logins = {}
        # received reply nonces
        self.reply_nonces = {}
        # established provider associations
        self.associations = {}
        # heap of (time, dictionary, key) triples
        self.expirations = []

    def expire(self):
        now = time.time()
        while True:
            t, d, k = self.expirations[0]
            if t > now:
                break
            del d[k]
            heapq.heappop(heap)

    def start_login(self, key, value):
        now = time.time()
        self.logins[key] = value
        heapq.heappush(self.expirations, (now+3600, self.logins, key))

    def get_login(self, key):
        return self.logins.get(key)

    def end_login(self, key):
        del self.logins[key]
        for i, k in enumerate(self.expirations):
            if k[1] is self.logins and k[2] == key:
                del self.expirations[i]
                # deletion in the middle is not supported by heapq,
                # so re-heapify instead
                heapq.heapify(self.expirations)
                break

    def add_nonce(self, nonce):
        utc = calendar.timegm(openid2rp.parse_nonce(nonce).utctimetuple())
        self.reply_nonces[nonce] = None
        heapq.heappush(self.expirations, (utc+self.nonce_lifetime, self.reply_nonces, nonce))

    def has_nonce(self, nonce):
        return nonce in self.reply_nonces

    def add_association(self, key, expires, value):
        self.associations[key] = value
        heapq.heappush(self.expirations, (expires, self.associations, key))

    def get_association(self, key):
        return self.associations.get(key)
