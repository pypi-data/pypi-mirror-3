from StringIO import StringIO
import urllib2
from DateTime.interfaces import SyntaxError

def dump_mod_time(self):
    out = StringIO()
    ptool = self
    fp = open('%s/Extensions/get_mod_time.txt' % INSTANCE_HOME)
    for line in fp:
        line = line.strip()
        obj = self.restrictedTraverse(line)
        print >> out, '/'.join(obj.getPhysicalPath()), obj.ModificationDate()
    return out.getvalue()
    
def load_mod_time(self):
    out = StringIO()
    ptool = self
    fp = open('%s/Extensions/set_mod_time.txt' % INSTANCE_HOME)
    for line in fp:
        path, mod_date = line.strip().split(' ', 1)
        obj = self.restrictedTraverse(path)
        obj.setModificationDate(mod_date)
        obj.reindexObject(idxs=['modified'])
        print >> out, '/'.join(obj.getPhysicalPath()), obj.ModificationDate()
    return out.getvalue()

def copy_mod_time(self, url_replace, count, meta, obj=None, out=None):
    out = StringIO()
    #url = 'http://localhost8080'
    #mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    #mgr.add_password('Zope', url, 'admin', 'admin')
    #opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(mgr))
    #s1 = opener.open(url + '/manage_main').read()
    pc = self.portal_catalog
    res = pc(portal_type=meta)
    res = [o.getObject() for o in res if o.getObject()]
    count = int(count)
    url_replace = url_replace.split('__')
    for o1 in res:
        if not count: break
        url = o1.absolute_url()
        new_url = url
        for j in range(len(url_replace)/2):
            new_url = new_url.replace(url_replace[2*j], url_replace[2*j+1])
        new_url += '/ModificationDate'
        try:
            mod_date = urllib2.urlopen(new_url).read().strip()[:19]
        except urllib2.HTTPError:
            print >> out, 'NOT FOUND ', new_url
            continue
        old_mod = o1.ModificationDate()
        old_mdate = old_mod.replace('T', ' ')
        old_mdate = old_mdate.split()
        new_mdate = mod_date.split()
        if old_mdate[0] == new_mdate[0]:
            print >> out, 'SAME', '/'.join(o1.getPhysicalPath()), old_mod, mod_date
            continue
        try:
            o1.setModificationDate(mod_date)
        except SyntaxError:
            print >> out, 'SYNTAX ERROR ', '/'.join(o1.getPhysicalPath()), old_mod, mod_date
        else:
            count -= 1
            print >> out, 'Changed ', '/'.join(o1.getPhysicalPath()), old_mod, mod_date
    return out.getvalue()
