######################################################
# bg.solr
# Written by ZOPYX Limited for BG Phoenics
######################################################

import base64
import sunburnt
from Products.Five.browser import BrowserView

const = {'kB':1024,
         'MB':1024*1024,
         'GB':1024*1024*1024}
order = ('GB', 'MB', 'kB')
smaller = order[-1]

class Solr(BrowserView):

    @property
    def solr(self):
        return sunburnt.SolrInterface(self.context.portal_properties.bgsolr.solr_url)

    def search(self):

        query = self.request.get('query')
        rows = self.request.get('rows')
        if query is None:
            return ()

        # Query through the sunburnt API
        query = self.solr.query(query)
        query = query.highlight('text', snippets=10, usePhraseHighlighter=True)
        query = query.field_limit(['id', 'mimetype', 'created', 'filesize', 'tag', 'relpath', 'renderurl'])
        query = query.facet_by('mimetype')
        if rows:
            query = query.paginate(rows=rows)
        resultset = query.execute()

        # Queries through the native Solr query API
        # query = {'q':query, 'rows':rows, 'hl':'on', 'hl.snippets' : 10}
        # resultset = self.solr.search(**query)

        rows = list()
        for row in resultset:
            row['relpath'] = base64.decodestring(row['relpath'])
            rows.append(row)
        return dict(rows=rows, highlighting=resultset.highlighting)

    def filesize(self, size):
        if isinstance(size, (int, long)):
            if size < const[smaller]:
                return '1 %s' % smaller
            for c in order:
                if size/const[c] > 0:
                    break
            return '%.1f %s' % (float(size/float(const[c])), c)
        return ''

    def view_hit(self, id):
        query = self.solr.query('id:%s' %id)
        result = query.execute()
        if not result:
            raise RuntimeError('No document found with ID=%s' % id)
        fullpath = base64.decodestring(result[0]['fullpath'])
        relpath = base64.decodestring(result[0]['relpath'])
#        dest_url = 'file://%s' % fullpath
        return file(fullpath).read()

