######################################################
# bg.solr
# Written by ZOPYX Limited for BG Phoenics
######################################################

import urllib
from sunburnt.schema import SolrError
from sunburnt.sunburnt import SolrConnection

def select(self, params):
    qs = urllib.urlencode(params)
    # ajung - fixes improper escaping of quoted strings (phrase searches)
    qs = qs.replace('%5c', '').replace('%5C', '')
    url = "%s?%s" % (self.select_url, qs)
    r, c = self.request(url)
    if r.status != 200:
        raise SolrError(r, c)
    return c

SolrConnection.select = select
