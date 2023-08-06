from StringIO import StringIO
from ZODB.POSException import POSKeyError
from datetime import datetime

def get_favorites(self):
    out = StringIO()
    pc = self.portal_catalog
    res = pc(meta_type='ATFavorite')
    for r in res:
        print >> out, r.getPath()
        o = r.getObject()
        if o:
            o.getParentNode().manage_delObjects(ids=[o.getId()])
    return out.getvalue()

def get_blogs(self, delete=False):
    out = StringIO()
    pc = self.portal_catalog
    res = pc(meta_type='Blog')
    for r in res:
        path = r.getPath()
        if delete:
            o = r.getObject()
            if o:
                o.getParentNode().manage_delObjects(ids=[o.getId()])
                print >> out, 'Deleted',
        print >> out, path
    return out.getvalue()

    
def move_blogs(self):
    out = StringIO()
    fp = open('%s/Extensions/blogs.txt' % INSTANCE_HOME)
    blogs_dir = self.restrictedTraverse('SimpleBlogs')
    for line in fp:
        line = line.strip()
        paths = line.split('/')
        if len(paths) != 3 or paths[0] != 'Members':
            print >> out, 'Bad blog', line
            continue
        if getattr(blogs_dir, paths[1], None) == None:
            new_id = blogs_dir.invokeFactory('Folder', paths[1])
        else:
            new_id = paths[1]
        obj = self.restrictedTraverse(line)
        parent = obj.getParentNode()
        new_parent = blogs_dir[new_id]
        cp = parent.manage_cutObjects(ids=obj.getId())
        new_parent.manage_pasteObjects(cp)
    print >> out, 'Done moving blogs'

def get_images(self):
    out = StringIO()
    pc = self.portal_catalog
    new_parent = self.Members.sureshvv.ZEROIMAGES
    res = pc(portal_type='Image')
    for r in res:
        try:
            o = r.getObject()
        except AttributeError:
            continue
        if o:
            try:
                sz = o.getSize()
            except AttributeError:
		sz = -100
            except POSKeyError:
                print >> out, 'Deleting', o.getId()
                o.getParentNode().manage_delObjects(ids=[o.getId()])
                continue
            if not sz:
                parent = o.getParentNode()
                print >> out, 'Moving', '/'.join(o.getPhysicalPath()), sz
                cp = parent.manage_cutObjects(ids=o.getId())
                new_parent.manage_pasteObjects(cp)
                continue
            elif sz == -100:
                print >> out, '/'.join(o.getPhysicalPath()), sz
            else:
                print >> out, '/'.join(o.getPhysicalPath())
    print >> out, 'Done'
    return out.getvalue()

def get_toprated(self):
    out = StringIO()
    cat=self.portal_catalog
    crit = dict(portal_type='FeedFeederItem', sort_on='Date', sort_order='descending')
    results = cat(crit)
    for o in results:
        try:
            o = o.getObject()
        except AttributeError:
            continue
        rating = o.editorial_rating()
        print >> out, '/'.join(o.getPhysicalPath()), rating
        
    return out.getvalue()

def create_fileitem(self, cnt="1"):
    out = StringIO()
    news_dir_name = 'LotsOfNews'
    news_dir = getattr(self, news_dir_name, None)
    the_text = """In the physiological disorder known as crud latex is exuded around the bracts in small droplets which harden and can prevent the normal development of the bracts and cyathia. It is associated with vigorous growth. Plants of the cv. Annette Hegg were grown for 8 weeks, from the start of short-day treatment to flowering, with different durations and combinations of 60 deg and 70 deg F, and watered by drip tubes or sub-irrigation. The only plants exhibiting crud were those maintained at 60 deg throughout and irrigated by tubes. It was observed that about 1 h after tube watering began these plants produced a bubble of latex in the bract and cyathium area which later hardened."""
    if not news_dir:
        self.invokeFactory(id=news_dir_name, type_name='Folder')
        news_dir = getattr(self, news_dir_name)
    for i in range(int(cnt)):
        new_id = 'News:' + datetime.now().isoformat('T')
        new_id = new_id.replace(':', '_')
        news_dir.invokeFactory(id=new_id, type_name='File')
        news_item = news_dir[new_id]
        news_item.setFile(StringIO(the_text))
        news_item.setTitle(new_id)
    print >> out, '%s news items created' % cnt
    return out.getvalue()

def create_newsitem(self, infile, n_skip=1, move=0):
    """ category, subcategory, title, description, tag1-tag20 """
    out = StringIO()
    main_dir_name = "AllContent"
    fp = open(infile)
    cnt = 0
    for l1 in fp:
        flds = l1.strip().split('\t')
        cnt += 1
        if cnt <= n_skip:
            continue
        len_flds = len(flds)
        main_dir = getattr(self, main_dir_name, None)
        if not main_dir:
            self.invokeFactory(id=main_dir_name, type_name='Folder')
            main_dir = getattr(self, main_dir_name)
        top_dir_name = flds[0].capitalize()
        top_dir = getattr(main_dir, top_dir_name, None)
        if not top_dir:
            main_dir.invokeFactory(id=top_dir_name, type_name='Folder')
            top_dir = getattr(main_dir, top_dir_name)
        sub_dir_name = flds[1].capitalize()
        if sub_dir_name:
            sub_dir = getattr(top_dir, sub_dir_name, None)
            if not sub_dir:
                top_dir.invokeFactory(id=sub_dir_name, type_name='Folder')
                sub_dir = getattr(top_dir, sub_dir_name)
        else:
            sub_dir = top_dir
        new_id = 'Doculite:' + datetime.now().isoformat('T')
        new_id = new_id.replace(':', '_')
        sub_dir.invokeFactory(id=new_id, type_name='Doculite')
        sub_item = sub_dir[new_id]
        sub_item.title = flds[2]
        sub_item.description = flds[3]
        tags = [ fld.strip() for fld in flds[4:] if fld.strip() ]
        sub_item.add_tags(tags)
        sub_item.indexObject()
    fp.close()
    if move:
        todir = os.path.join(os.path.dirname(infile), 'DONE')
        shutil.move(infile, todir)
    print >> out, '%s news items created' % cnt
    return out.getvalue()
