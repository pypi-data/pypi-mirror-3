from StringIO import StringIO
from logging import getLogger
from DateTime.DateTime import DateTime

def gen_sitemap(self, min, max):
    """ this fixes schema of old documents """
    pc = self.portal_catalog
    types = ('Document', 'Event', 'FeedFeederItem', 'FeedfeederFolder', 'File', 'FileAttachment', 'Folder', 'Image', 'ImageAttachment', 'Large Plone Folder', 'News Item', 'Ploneboard', 'PloneboardComment', 'PloneboardConversation', 'PloneboardForum', 'Topic', 'ATFolder', 'Discussion Item')
    hdr = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.google.com/schemas/sitemap/0.84"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.google.com/schemas/sitemap/0.84
                            http://www.google.com/schemas/sitemap/0.84/sitemap.xsd">"""
    log = getLogger('Plone')
    file_cnt = 0
    mx_cnt = 50000
    count = 0
    query = {'query': [DateTime(min), DateTime(max)], 'range': 'min:max'}
    log.warning('gen_sitemap: using query %s', query)
    res = pc(created=query)
    for o1 in res:
        try:
            o2 = o1.getObject()
        except AttributeError:
            log.warning('AttributeError from %s', o1.getURL())
            continue
        if not o2:
            log.warning('no object from %s', o1.getURL())
            continue 
        if o2.portal_type not in types:
            log.warning('Discarding %s of type %s', o1.getURL(), o2.portal_type)
            continue 
        if count == 0:
            out = open('%s/Extensions/sitemap%d.xml' % (INSTANCE_HOME, file_cnt), 'w')
            print >> out, hdr
            file_cnt += 1
        mod_time = str(o2.modified()).split()[0].replace('/', '-')
        print >> out, """<url>
   <loc>%s</loc>
   <lastmod>%s</lastmod>
</url>""" % (o2.absolute_url(), mod_time)
        count += 1
        if count >= mx_cnt:
            count = 0
            print >> out, "</urlset>"
            out.close()
    if count:
        print >> out, "</urlset>"
        out.close()
    return str(file_cnt)
