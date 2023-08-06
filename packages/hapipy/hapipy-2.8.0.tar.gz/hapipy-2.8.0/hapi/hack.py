# Hack

import time
from keywords import KeywordsClient

client = KeywordsClient("demo")

num = 100

ts = time.time()

for i in xrange(num):
	kw = client.get_keywords()
	print len(kw)

te = time.time()

tt = (te - ts)
print ' %2.2f sec - %2.2f' % (tt, tt/num)



# No gzip 69.61 sec - 0.70

#bc = BroadcastClient('559f704f-263d-4cac-87ba-9f0c89169aa8', portal_id=167695, api_base='https://api.hubapi.com')

#Headers: {'Content-Type': 'application/json'}
#Result body: 76221
#592


