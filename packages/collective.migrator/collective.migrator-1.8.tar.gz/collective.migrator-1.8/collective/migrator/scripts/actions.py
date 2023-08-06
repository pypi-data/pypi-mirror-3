from StringIO import StringIO
from Products.CMFCore.ActionInformation import Action

def dump_actions(self):
    out = StringIO()
    atool = self.portal_actions
    actions = atool.listFilteredActionsFor(self)
    for k1,v1 in actions.items():
        print >> out, '===========', k1, '=========='
        for v in v1:
            for k2, v2 in v.items():
                if k2 == 'url':
                    if callable(v2):
                        v2 = v2()
                    else:
                        print >> out, 'Uncallable ', type(v2)
                print >> out, k2, '=', v2
    print >> out, 'Done'
    return out.getvalue()

def add_action(self, mode, id, title, action, permission, category):
    out = StringIO()
    atool = self.portal_actions[category]
    if mode == 'update':
        old_action = atool[id]
        if title:
            old_action._setPropValue('title', title)
            print >> out, 'Updated title:', old_action.getProperty('title')
        if action:
            old_action._setPropValue('url_expr', action)
            print >> out, 'Updated action:', old_action.getProperty('url_expr')
        if permission:
            old_action._setPropValue('permissions', permission)
            print >> out, 'Updated permission:', old_action.getProperty('permissions')
    elif mode == 'create':
        new_action = Action(id)
        new_action._setPropValue('title', title)
        new_action._setPropValue('url_expr', action)
        new_action._setPropValue('permissions', permission)
        atool._setObject(id, new_action)
        print >> out, 'Created: ', atool[id].title_or_id()
    elif mode == 'delete':
        atool.manage_delObjects(ids=[id])
        print >> out, 'Deleted: ', atool.objectIds()
    return out.getvalue()
