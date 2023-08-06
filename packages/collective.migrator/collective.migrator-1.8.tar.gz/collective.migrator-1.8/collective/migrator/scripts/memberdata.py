from StringIO import StringIO

def chk_editor(self):
    out = StringIO()
    mtool = self.portal_membership
    dtool = self.portal_memberdata
    props = dtool.propertyIds()
    for mem_id in mtool.listMemberIds():
        mem = mtool.getMemberById(mem_id)
        if mem.getProperty('wysiwyg_editor') != 'TinyMCE':
            print >> out, 'Bad editor', mem.getProperty('wysiwyg_editor'), ' for member', mem_id
    print >> out, 'Done'
    return out.getvalue()

def chg_editor(self):
    out = StringIO()
    mtool = self.portal_membership
    dtool = self.portal_memberdata
    props = dtool.propertyIds()
    last_props = {}
    last_props['wysiwyg_editor'] = 'TinyMCE'
    for mem_id in mtool.listMemberIds():
        mem = mtool.getMemberById(mem_id)
        mem.setMemberProperties(last_props)
    print >> out, 'Done'
    return out.getvalue()

def load_memberdata(self):
    out = StringIO()
    mtool = self.portal_membership
    dtool = self.portal_memberdata
    props = dtool.propertyIds()
    fp = open('%s/Extensions/memberdata.txt' % INSTANCE_HOME)
    last_id = ''
    last_props = {}
    for line in fp:
        mem_id, prop, val = line.strip().split(',', 2)
        if mem_id != last_id:
            if last_id:
                mem = mtool.getMemberById(last_id)
                if not mem:
                    print >> out, 'mem %s does not exist' % last_id
                    continue
                if last_props:
                    mem.setMemberProperties(last_props)
                    last_props = {}
            last_id = mem_id
        val = val.replace('\\n', '\n')
        if val.startswith('(') and val.endswith(')'):
            val = eval(val)
        last_props[prop] = val
    print >> out, 'Done'
    return out.getvalue()

def dump_memberdata(self):
    out = StringIO()
    mtool = self.portal_membership
    dtool = self.portal_memberdata
    props = dtool.propertyIds()
    defaults = {}
    defaults['listed'] = ('1', 'True', 'on')
    defaults['login_time'] = ('2000/01/01',)
    defaults['last_login_time'] = ('2000/01/01',)
    defaults['wysiwyg_editor'] = ('Kupu',)
    defaults['error_log_update'] = ('0.0',)
    defaults['must_change_password'] = ('0', 'False')
    defaults['visible_ids'] = ('0', 'False')
    defaults['ext_editor'] = ('0', 'False')
    defaults['news_subscribed'] = ('0', 'False')
    defaults['user_categories'] = ('()', "('',)")

    for mem_id in mtool.listMemberIds():
        mem = mtool.getMemberById(mem_id)
        for prop in props:
            val = str(mem.getProperty(prop))
            if val == '':
                continue
            if prop in defaults.keys() and val in defaults[prop]:
                continue
            val = val.replace('\n', '\\n')
            print >> out, "%s,%s,%s" % (mem_id, prop, val)
    return out.getvalue()
