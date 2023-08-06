from StringIO import StringIO
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base as BTreeFolder
import transaction
from Acquisition import aq_base, aq_inner
from pickle import PicklingError
from logging import getLogger
from Products.CMFCore.WorkflowCore import WorkflowException
import urllib2
from zope.component.interfaces import ComponentLookupError
from contentratings.interfaces import IEditorRatable, IUserRatable, IUserRating, IEditorialRating
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable


def fix_forums(self):
    out = StringIO()
    pc = self.portal_catalog
    res = [ r.getObject() for r in pc(portal_type='PloneboardConversation') if r.getObject() ]
    for r in res:
        orig_mod = r.getLastCommentDate()
        r.setModificationDate(orig_mod)
        r.reindexObject(idxs=['modified'])
    print >> out, len(res), ' conversations modified'
    return out.getvalue()
    
def update_catalog(self, obj):
    out = StringIO()
    def indexObject(obj, path):
        try:
            obj.reindexObject(idxs=[])
            print >> out, 'Reindexed ', '/'.join(obj.getPhysicalPath())
        except KeyError:
            print >> out, '(POS)KeyError ', '/'.join(obj.getPhysicalPath())
            pass
        except AttributeError:
            print >> out, 'AttributeError ', '/'.join(obj.getPhysicalPath())
            pass
        except TypeError:
            pass
    pc = self.portal_catalog
    obj = self.restrictedTraverse(obj)
    pc.ZopeFindAndApply(obj, search_sub=True, apply_func=indexObject)
    return out.getvalue()

def chg_catalog_icon(self):
    out = StringIO()
    pc = self.portal_catalog
    res = pc(portal_type='FeedFeederItem')
    res = ( o.getObject() for o in res if o.getIcon == 'folder_icon.gif' and o.getObject() )
    cnt = 0
    for obj in res:
        obj.reindexObject(idxs=[])
        cnt += 1
    print >> out, cnt, 'objects updated'
    return out.getvalue()

def enable_syndication(self, obj):
    """ enable syndication """
    tool = self.portal_syndication
    obj = self.restrictedTraverse(obj)
    #tool.enableSyndication(obj)
    #ob1 = getattr(obj, 'syndication_information')
    #return ob1.absolute_url()
    return tool.isSyndicationAllowed(obj)

def show_fieldsets(self):
    """ this fixes schema of old documents """
    out = StringIO()
    pc = self.portal_catalog
    res = pc(portal_type='Document')
    res = ( o.getObject() for o in res if o.getObject() )
    total = count = 0
    for o1 in res:
        schematas = o1.Schemata()
        all_keys = list(schematas.keys())
        total += 1
        if 'categorization' not in all_keys:
            finalizeATCTSchema(o1.schema)
            count += 1
            o1.schema._p_changed = True
    print >> out, 'Fixed', count, 'of', total
    return out.getvalue()

def fix_portal_setup(self, key):
    """ this fixes junk in portal_setup that interferes with installing a new product """
    out = StringIO()
    registry = self.portal_setup.getToolsetRegistry()
    del registry._required[key]
    print >> out, 'Deleted', key
    return out.getvalue()

def find_bad_types(self):
    out = StringIO()
    res = self.portal_catalog(portal_type='ATFolder')
    for r in res:
        print >> out, r.getPath()
    return out.getvalue()

def chk_portal_types(self):
    out = StringIO()
    types = self.portal_catalog.uniqueValuesFor('portal_type')
    for t1 in types:
        t2 = self.portal_types.getTypeInfo(t1)
        if t2:
            print >> out, 'TYPEINFO SAYS', t1, t2.Title()
        else:
            print >> out, 'NO TYPEINFO', t1
    return out.getvalue()

def chk_edit_rating(self):
    out = StringIO()
    object = self.Members.Marshall.index_html
    try:
        rated = IEditorialRating(object)
        print >> out, rated.rating, str(rated.rating)
    except (ComponentLookupError, TypeError, ValueError):
        print >> out, 'NO RATING'
    return out.getvalue()

def check_edit_rating(self):
    out = StringIO()
    pc = self.portal_catalog
    print >> out, pc.uniqueValuesFor('editorial_rating')
    return out.getvalue()

def fix_mod_time(self, obj, out=None):
    if self:
        out = StringIO()
        obj = self.restrictedTraverse(obj.replace('__', '/'))
    orig_mod = obj.ModificationDate()
    try:
        obj.reindexObject()
    except AttributeError:
        pass
    obj.setModificationDate(orig_mod)
    obj.reindexObject(idxs=['modified'])
    print >> out, '/'.join(obj.getPhysicalPath()), orig_mod, obj.ModificationDate()
    if hasattr(aq_base(obj), 'objectItems'):
        for o1 in obj.objectValues():
            fix_mod_time(None, o1, out)
    print >> out, 'Done'
    return out.getvalue()

def check_perm(self):
    from zope.annotation.interfaces import IAnnotations, IAnnotatable
    out = StringIO()
    obj = self.Members.Marshall.index_html
    annotations = IAnnotations(obj)
    print >> out, annotations.items()
    return out.getvalue()

def fix_portal_type(self, obj, ptype):
    out = StringIO()
    obj = self.restrictedTraverse(obj.replace('__', '/'))
    obj1 = aq_base(obj)
    old_type = obj1.portal_type
    if old_type != ptype:
        obj1.portal_type = ptype
        obj1.reindexObject(idxs=['portal_type'])
        print >> out, 'Changed ptype from', old_type, 'to', ptype, 'for', '/'.join(obj.getPhysicalPath())
    else:
        print >> out, 'No change in type', old_type, 'for', '/'.join(obj.getPhysicalPath())
    return out.getvalue()


def make_visible(self, obj, wf_tool=None, out=None, recursive=0, publish=None):
    if self:
        out = StringIO()
        wf_tool = self.portal_workflow
        obj = self.restrictedTraverse(obj)
    recursive = int(recursive)
    orig_mod = obj.ModificationDate()
    if publish:
        try:
            cur_state =  wf_tool.getInfoFor(obj, 'review_state')
        except WorkflowException:
            cur_state = 'published'
            print >> out, 'No workflow for',
        if cur_state != 'published':
            try:
                wf_tool.doActionFor(obj, 'publish')
                obj.reindexObject()
            except WorkflowException:
                print >> out, 'No way to ',
            except AttributeError:
                pass
            print >> out, 'Publish',
    obj.setModificationDate(orig_mod)
    obj.reindexObject(idxs=['modified'])
    print >> out, '/'.join(obj.getPhysicalPath()), orig_mod, obj.ModificationDate()
    transaction.commit()
    if recursive and hasattr(aq_base(obj), 'objectItems'):
        for o1 in obj.objectValues():
            make_visible(None, o1, wf_tool, out, recursive-1, publish)
    return out.getvalue()

def activate_pas_plugins(self):
    out = StringIO()
    activatePluginInterfaces(self, 'source_users')
    activatePluginInterfaces(self, 'source_groups')
    activatePluginInterfaces(self, 'portal_role_manager')
    print >> out, 'Done'
    return out.getvalue()

def migrate_btrees(self, obj=None):
    out = StringIO()
    ptool = self
    if obj:
        ptool = ptool.restrictedTraverse(obj)
    for o1 in ptool.objectIds():
        if isinstance(o1, BTreeFolder):
            view = getMultiAdapter((o1, self.REQUEST), name='migrate-btrees')
            view()
            print >> out, 'Done', o1.getId()
    # Another way to skin the cat is:
    view = getMultiAdapter((ptool, self.REQUEST), name='migrate-btrees')
    view()
    print >> out, 'Done'
    return out.getvalue()

def publish_all(self, obj):
    out = StringIO()
    ptool = getToolByName(self, 'plone_utils')
    for o1 in obj.split('__'):
        failures = ptool.transitionObjectsByPaths('publish', o1,
                             include_children=True, handle_errors=True)
        print >> out, failures
        transaction.commit()
    print >> out, 'Done'
    return out.getvalue()

def fix_feedfeeder_items(self, obj_path):
    out = StringIO()
    wf_tool = self.portal_workflow
    for path in obj_path.split('__'):
        obj = self.restrictedTraverse(path)
        for i1 in obj.objectValues('FeedFeederItem'):
            old_mod_time = i1.getFeedItemUpdated()
            old_mod = str(old_mod_time)[:19]
            old_mod = old_mod.replace('/', '-')
            old_mod = old_mod.replace(' ', 'T')
            cur_state =  wf_tool.getInfoFor(i1, 'review_state')
            if cur_state != 'published':
                wf_tool.doActionFor(i1, 'publish')
                i1.reindexObject()
                print >> out, 'published', '/'.join(i1.getPhysicalPath())
            new_mod_time = i1.ModificationDate()
            new_mod = str(new_mod_time)[:19]
            if new_mod != old_mod:
                i1.setModificationDate(old_mod_time)
                i1.reindexObject(idxs=['modified'])
                print >> out, 'Updated mod time for', '/'.join(i1.getPhysicalPath()), old_mod_time, new_mod_time
        transaction.commit()
    print >> out, 'Done'
    return out.getvalue()

def find_broken_items(self, path, out=None):
    """ Allow workflows to update the role-permission mappings.  """
    if not out:
        out = StringIO()
    real_path = path.replace('___', '/')
    obj = self.restrictedTraverse(real_path)
    print >> out, obj.meta_type, '/'.join(obj.getPhysicalPath())
    for o1 in obj.objectIds():
        new_path = '%s___%s' % (path, o1)
        try:
            find_broken_items(self, new_path, out)
        except AttributeError:
            print >> out, 'AttributeError', new_path
        except PicklingError:
            print >> out, 'PicklingError', new_path
    return out.getvalue()


def recursive_ob(self, ob, wfs):
    """ Update roles-permission mappings recursively, and
        reindex special index.  """
    # Returns a count of updated objects.
    log = getLogger('Plone')
    log.info('recursive_ob: %s\n', ob.getPhysicalPath())
    count = 0
    wf_ids = self.getChainFor(ob)
    if wf_ids:
        changed = 0
        for wf_id in wf_ids:
            wf = wfs.get(wf_id, None)
            if wf is not None:
                did = wf.updateRoleMappingsFor(ob)
                if did:
                    changed = 1
        if changed:
            count = count + 1
            if hasattr(aq_base(ob), 'reindexObject'):
                # Reindex security-related indexes
                try:
                    ob.reindexObject(idxs=['allowedRolesAndUsers'])
                except TypeError:
                    # Catch attempts to reindex portal_catalog.
                    pass
    if hasattr(aq_base(ob), 'objectItems'):
        obs = ob.objectItems()
        if obs:
            for k, v in obs:
                changed = getattr(v, '_p_changed', 0)
                count = count + recursive_ob(self, v, wfs)
                if changed is None:
                    # Re-ghostify.
                    v._p_deactivate()
    try:
        transaction.commit()
    except PicklingError:
        log.info('recursive_ob: PicklingError %s\n', ob.getPhysicalPath())
    return count

def updateRoleMappings(self, path):
    """ Allow workflows to update the role-permission mappings.  """
    out = StringIO()
    log = self.plone_log
    wfs = {}
    wf_tool = self.portal_workflow
    for id in wf_tool.objectIds():
        wf = wf_tool.getWorkflowById(id)
        if hasattr(aq_base(wf), 'updateRoleMappingsFor'):
            wfs[id] = wf
    path = path.replace('__', '/')
    obj = self.restrictedTraverse(path)
    count = recursive_ob(wf_tool, obj, wfs)
    print >> out, '%d object(s) updated.' % count
    return out.getvalue()

def get_obj_list(self, obj=None, parms=None):
    """ Get list of objects in root folder """
    out = StringIO()
    ptool = self
    if obj:
        ptool = ptool.restrictedTraverse(obj)
    parms = parms and parms.split('__') or ['getId']
    for o1 in ptool.objectValues():
        out_p1 = []
        for p1 in parms:
            if p1 == 'getPhysicalPath':
                out_p1.append('/'.join(o1.getPhysicalPath()))
            elif p1 == 'getId':
                out_p1.append(o1.getId())
            else:
                rc = getattr(o1, p1, None)
                if not rc:
                    out_p1.append('+++NO_%s+++' % p1)
                elif callable(rc):
                    out_p1.append(rc())
                else:
                    out_p1.append(rc)
        print >> out, ' '.join(out_p1)
    print >> out, 'Done'
    return out.getvalue()
