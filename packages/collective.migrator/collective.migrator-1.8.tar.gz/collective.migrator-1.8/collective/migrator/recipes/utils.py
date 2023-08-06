import os
import time
import base64
from zope.testbrowser.browser import Browser
from urllib2 import HTTPError
import subprocess
import urllib
import os.path
from StringIO import StringIO

RETRIES = 1
METH_ID = 'meth_collective_migrator'

Browsers = {}


def get_zmi(instance):
    zmi = instance.get('zmi', None)
    if zmi:
        return 'http://%s' % zmi
    else:
        return 'http://%(host)s:%(port)s/%(root)s' % instance

def import_one(instance, obj, br):
    zmi = get_zmi(instance)
    pos = obj.rfind('/')
    if pos == -1:
        url = '%s/manage_importObject?file=%s.zexp&set_owner:int=0'% (zmi, obj)
    else:
        top_obj = obj[:pos]
        obj = obj[pos+1:]
        url = '%s/%s/manage_importObject?file=%s.zexp&set_owner:int=0'% (zmi, top_obj, obj)

    try:
        br.open(url)
    except HTTPError:
        return dump_error_log(instance)
    s1 = br.contents
    success = s1.find('successfully imported') != -1
    if success:
        import_file = "'%s/%s.zexp'" % (instance['import'], obj)
        remove_file(instance, import_file)
    return None

def export_one(instance, obj, br):
    zmi = get_zmi(instance)
    export_folder = instance['export']
    pos = obj.rfind('/')
    if pos == -1:
        url = '%s/manage_exportObject?id=%s&download:int=0&submit=Export'% (zmi, obj)
    else:
        top_obj = obj[:pos]
        obj = obj[pos+1:]
        url = '%s/%s/manage_exportObject?id=%s&download:int=0&submit=Export'% (zmi, top_obj, obj)

    export_file = "'%s/%s.zexp'" % (export_folder, obj)
    remove_file(instance, export_file)

    try:
        f1 = br.open(url)
    except HTTPError:
        return -1
    else:
        s1 = br.contents
        str1 = "successfully exported"
        return s1.find(str1) >= 0

def create_dir(source, source_dir):
    cmd = ['mkdir', source_dir]
    if source['host'] != 'localhost':
        cmd = ['ssh', '%s@%s' % (source['user'], source['host'])] + cmd 
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
    cmd = ['ls', '-d', source_dir]
    if source['host'] != 'localhost':
        cmd = ['ssh', '%s@%s' % (source['user'], source['host'])] + cmd 
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].strip()
    return output == source_dir

def copy_file(source, source_dir, file_name, target, target_dir, keep=False):
    file_name = urllib.unquote(file_name)
    if source['host'] == 'localhost' or source['host'] == target['host']:
        source_file = '%s/%s' % (source_dir, file_name)
    else:
        source_file = '%s@%s:%s/%s' % (source['user'], source['host'], source_dir, file_name)
    if target['host'] == 'localhost' or source['host'] == target['host']:
        target_file = target_dir
    else:
        target_file = '%s@%s:%s' % (target['user'], target['host'], target_dir)
    pos1 = source_file.find(':')
    pos2 = target_file.find(':')
    if pos1 == -1 and pos2 == -1:
        cmd = "cp '%s' '%s'" % (source_file, target_file)
        if target['host'] != 'localhost':
            cmd = 'ssh %s@%s %s' % (target['user'], target['host'], cmd)
    else:
        cmd = "scp '%s' '%s'" % (source_file, target_file)
    os.system(cmd)
    target_file = '%s/%s' % (target_dir, file_name)
    cmd = ['ls "%s"' % target_file]
    if target['host'] != 'localhost':
        cmd = ['ssh %s@%s %s' % (target['user'], target['host'], cmd[0])]
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
    if output != target_file:
        return -1
    if not keep:
        file_name = '"%s/%s"' % (source_dir, file_name)
        remove_file(source, file_name)
    return 0

def remove_file(instance, file_name):
    cmd = 'rm -f %s' % file_name
    host_name = instance['host']
    if host_name != 'localhost':
        cmd = 'ssh %s@%s %s' % (instance['user'], host_name, cmd)
    os.system(cmd)

def get_browser(instance):
    host_name, host_port = (instance['host'], instance['port'])
    key = '%s:%s' % (host_name, host_port)
    if key not in Browsers:
        br = Browser()
        pwd_file = instance.get('pwd_file', None)
        if pwd_file:
            zmi_user, zmi_pwd = get_login_details(pwd_file)
            br.addHeader('Authorization', 'Basic %s' % base64.encodestring('%s:%s' % (zmi_user, zmi_pwd)))
        elif instance.get('zmi_user', None):
            zmi_user, zmi_pwd = (instance['zmi_user'], instance['zmi_pwd'])
            br.addHeader('Authorization', 'Basic %s' % base64.encodestring('%s:%s' % (zmi_user, zmi_pwd)))
        Browsers[key] = br
    return Browsers[key]
    

def get_login_details(filename):
    fp = open(filename)
    for line in fp.readlines():
        line = line.strip()
        if line.startswith('Username: '):
            username = line.replace('Username: ', '')
        elif line.startswith('Password: '):
            password = line.replace('Username: ', '')
    return (username, password)

def create_ext_method(instance, module, function, br):
    zmi = get_zmi(instance)
    rc = del_object(instance, METH_ID, br)
    if rc:
        return rc
    rc = None
    url = '%s/manage_addProduct/ExternalMethod/manage_addExternalMethod' % zmi
    try:
        br.post(url, 'id=%s&module=%s&function=%s&title=collective_migrator' % (METH_ID, module, function))
    except HTTPError as err1:
        rc = dump_error_log(instance)
    return rc

def run_ext_method(instance, args, out_file, br):
    zmi = get_zmi(instance)
    url = '%s/%s' % (zmi, METH_ID)
    if args:
        url_add = []
        for k,v in args.items():
            url_add.append('%s=%s' % (k, v))
        url_add = '&'.join(url_add)
        url = url + '?' + url_add
    try:
        br.open(url)
    except HTTPError:
        return dump_error_log(instance)
    fp = open(out_file, "a")
    fp.write('--- %s\n' % time.asctime())
    fp.write(br.contents)
    fp.close()
    return ''

def dump_error_log(instance):
    cmd = 'sed -n -e "/^---*/{h;d;}" -e H -e "\${g;p;}" %s' % instance['log']
    if instance['host'] != 'localhost':
        cmd = "ssh %s@%s '%s'" % (instance['user'], instance['host'], cmd)
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
    return output

def chk_object(instance, obj, br):
    zmi = get_zmi(instance)
    url = '%s/%s/getId' % (zmi, obj)
    try:
        br.open(url)
    except HTTPError:
        return False
    else:
        return True

def del_object(instance, obj, br):
    if not chk_object(instance, obj, br):
        return None
    zmi = get_zmi(instance)
    pos = obj.rfind('/')
    if pos == -1:
        url = '%s/manage_delObjects?ids=%s' % (zmi, obj)
    else:
        top_obj = obj[:pos]
        obj = obj[pos+1:]
        url = '%s/%s' % (zmi, obj)
        url = '%s/%s/manage_delObjects?ids=%s' % (zmi, top_obj, obj)
    try:
        br.open(url)
    except HTTPError:
        return dump_error_log(instance)
    return None

def submit_url(instance, url, args, out_file, br):
    zmi = get_zmi(instance)
    url = '%s/%s' % (zmi, url)
    br.open(url)
    if 'form_index' in args:
        br = br.getForm(index=int(args['form_index']))
    for k in args:
        if k in ('submit', 'form_index') :
            continue
        br.getControl(name=k).value = args[k]
    if 'submit' in args:
        br.getControl(name=args['submit']).click()
    elif 'form_index' in args:
        br.submit()
    else:
        br.getForm().submit()
    fp = open(out_file, "a")
    fp.write(br.contents)
    fp.close()

def get_db_size(lines):
    """ gets the size of the db """
    lines = [ x.strip() for x in lines.split('\n') ]
    start = lines.index('Database Size')
    return lines[start + 5]

def pack_db(instance, db_name, br):
    url = 'http://%s:%s/Control_Panel/Database/%s/manage_main' % (instance['host'],
              instance['port'], db_name)
    br.open(url)
    old_sz = get_db_size(br.contents)
    br.getForm().submit()
    new_sz = get_db_size(br.contents)
    return old_sz, new_sz

def fix_name(d1):
    bad_chars = "&+,"
    for b in bad_chars:
        new_d1 = d1.replace(b, '')
    while new_d1.find('  ') != -1:
        new_d1 = new_d1.replace('  ', ' ')
    return new_d1

def prepare_content(top_folder):
    """ prepares content for import """
    out = StringIO()
    rc = rename_files(top_folder)
    if rc: print >> out, rc
    for root, dirs, files in os.walk(top_folder):
        if '.objects' not in files:
            outfile = open(os.path.join(root, '.objects'), "w")
            for d1 in dirs:
                if d1 == '.svn':
                    continue
                print >> outfile, "%s,Folder" % d1
            for d1 in files:
                print >> outfile, "%s,File" % d1
            outfile.close()
            print >> out, 'Created .objects in', root
        if '.preserve' not in files:
            outfile = open(os.path.join(root, '.preserve'), "w")
            for d1 in dirs:
                if d1 == '.svn':
                    continue
                print >> outfile, d1
            for d1 in files:
                print >> outfile, d1
            outfile.close()
            print >> out, 'Created .preserve in', root
        if '.properties' not in files:
            outfile = open(os.path.join(root, '.properties'), "w")
            print >> outfile, "[DEFAULT]"
            print >> outfile, "description = "
            print >> outfile, "title =", os.path.basename(root)
            outfile.close()
            print >> out, 'Created .properties in', root
        for d1 in dirs:
            if d1 == '.svn':
                continue
            rc = prepare_content(os.path.join(top_folder, d1))
            if rc: print >> out, rc
        return out.getvalue()

def rename_files(top_folder):
    """ prepares content for import """
    out = StringIO()
    for root, dirs, files in os.walk(top_folder):
        for d1 in files:
            new_d1 = fix_name(d1)
            if d1 != new_d1:
                os.rename(os.path.join(root, d1), os.path.join(root, new_d1))
                print >> out, 'Renamed file %s to %s' % (d1, new_d1)
        for d1 in dirs:
            if d1 == '.svn':
                continue
            new_d1 = fix_name(d1)
            if d1 != new_d1:
                os.rename(os.path.join(root, d1), os.path.join(root, new_d1))
                print >> out, 'Renamed dir %s to %s' % (d1, new_d1)
                d1 = new_d1
            rc = rename_files(os.path.join(top_folder, d1))
            if rc: print >> out, rc
    return out.getvalue()

def get_uname_pwd(pwd_file):
    username = password = ''
    infile = open(pwd_file)
    for line in infile.readlines():
        line = line.strip()
        if line.startswith('Username:'):
            username = line.replace('Username: ', '')
        elif line.startswith('Password:'):
            password = line.replace('Password: ', '')
            break
    return (username, password)
