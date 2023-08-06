
from StringIO import StringIO

def dump_props(self, obj=None):
    out = StringIO()
    ptool = self
    if obj:
        obj = obj.split('__')
        for o1 in obj:
            ptool = getattr(ptool, o1)
    props = ptool.propertyIds()
    for p in props:
        typ, val = ptool.getPropertyType(p), ptool.getProperty(p)
        if typ == 'text':
            val = val.replace('\n', '\\n')
        print >> out, "%s, %s, %s" % (p, typ, val)
    return out.getvalue()

def load_props(self, obj=None):
    out = StringIO()
    ptool = self
    if obj:
        obj = obj.split('__')
        for o1 in obj:
            ptool = getattr(ptool, o1)
    fp = open('%s/Extensions/props.txt' % INSTANCE_HOME)
    prop_vals = {}
    for line in fp:
        prop, prop_type, val = line.split(', ', 2)
        val = val.strip()
        if not ptool.hasProperty(prop):
            print >> out, 'No such property: %s' % prop
            continue
        old_val = ptool.getProperty(prop)
        if prop_type in ('int', 'lines', 'boolean'):
            val = eval(val)
        elif prop_type == 'text':
            val = val.replace('\\n', '\n')
        elif prop_type != 'string':
            print >> out, 'Unknown type %s' % prop_type
            continue
        if val != old_val:
            prop_vals[prop] = val
            print >> out, 'Changed %s from %s to %s' % (prop, old_val, val)
    if prop_vals:
        ptool.manage_changeProperties(prop_vals)
    print >> out, 'Done'
    return out.getvalue()
