import logging, os, zc.buildout
import utils

class Mkdir:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        options['path'] = os.path.join(
                              buildout['buildout']['directory'],
                              options['path'],
                              )
        if not os.path.isdir(os.path.dirname(options['path'])):
            logging.getLogger(self.name).error(
                'Cannot create %s. %s is not a directory.',
                options['path'], os.path.dirname(options['path']))
            raise zc.buildout.UserError('Invalid Path')


    def install(self):
        path = self.options['path']
        logging.getLogger(self.name).info(
            'Creating directory %s', os.path.basename(path))
        os.mkdir(path)
        return path

    def update(self):
        pass


class ExportObject:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        instance = options['instance']
        self.obj_path = options['obj'].split()
        self.instance = buildout[instance]
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)

    def install(self):
        br = utils.get_browser(self.instance)
        for obj1 in self.obj_path:
            if not utils.export_one(self.instance, obj1, br):
                raise zc.buildout.UserError('%s Export failed' % obj1)
        if not os.path.exists(self.path): os.mkdir(self.path)
        return self.path

    def update(self):
        pass

class CopyFile:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)
        self.files = options['files'].split()
        self.source = buildout[options['source']]
        self.target = buildout[options['target']]
        self.source_dir = options['source_dir']
        self.target_dir = options['target_dir']
        self.keep = options.get('keep', False)

    def install(self):
        """ copy file, create external method and run it """
        for f1 in self.files:
            if utils.copy_file(self.source, self.source_dir, f1, self.target, self.target_dir, self.keep):
                logging.getLogger(self.name).error('Cannot verify file %s.', f1)
                break
        if not os.path.exists(self.path): os.mkdir(self.path)
        return self.path

    def update(self):
        pass

class ExternalMethod:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        file_path = os.path.join(buildout['buildout']['directory'], options['source'])
        self.source_dir, self.source_file = os.path.split(file_path)
        instance = options['instance']
        self.instance = buildout[instance]
        self.function = options['func']
        self.out_file = options['output']
        self.no_copy = options.get('no_copy', False)
        self.loop = options.get('loop', False)
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)
        self.args = {}
        if 'args' in options:
            for arg in options['args'].split():
                self.args[arg] = options[arg]

    def install(self):
        """ copy file, create external method and run it """
        local_instance = {}
        local_instance['host'] = 'localhost'
        if not self.no_copy:
            if not utils.create_dir(self.instance, self.instance['extensions']):
                raise zc.buildout.UserError('Cannot mkdir')
            if utils.copy_file(local_instance, self.source_dir, self.source_file,
                        self.instance, self.instance['extensions'], keep=True) < 0:
                raise zc.buildout.UserError('Could not copy script')
        br = utils.get_browser(self.instance)
        rc = utils.create_ext_method(self.instance, self.source_file, self.function, br)
        if rc:
            logging.getLogger(self.name).error('Error running %s: %s.', self.function, rc)
            raise zc.buildout.UserError('Create Ext Method')
        if self.loop:
            loop = self.args[self.loop]
            for arg in loop.split():
                self.args[self.loop] = arg
                rc = utils.run_ext_method(self.instance, self.args, self.out_file, br)
                if rc:
                    logging.getLogger(self.name).error('Error running %s: %s.', self.function, rc)
                    break
        else:
            rc = utils.run_ext_method(self.instance, self.args, self.out_file, br)
            if rc: logging.getLogger(self.name).error('Error running %s: %s.', self.function, rc)
        utils.del_object(self.instance, utils.METH_ID, br)
        if rc:
            raise zc.buildout.UserError('Run Ext Method')
        if not os.path.exists(self.path): os.mkdir(self.path)
        return self.path
 

    def update(self):
        pass


class DelObject:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        instance = options['instance']
        self.obj = options['obj']
        self.host_name = buildout[instance]['host']
        self.port = buildout[instance]['port']
        self.zmi_user = buildout[instance]['zmi_user']
        self.zmi_pwd = buildout[instance]['zmi_pwd']
        self.plone_root = buildout[instance]['root']

    def install(self):
        """ copy file, create external method and run it """
        br = utils.get_browser(self.host_name, self.port, self.zmi_user, self.zmi_pwd)
        utils.del_object(self.host_name, self.port, self.plone_root, self.obj, br)
        path = os.path.join(buildout['buildout']['directory'], self.name)
        if not os.path.exists(path): os.mkdir(path)
        return path

    def update(self):
        pass



class PackDb:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        instance = options['instance']
        self.instance = buildout[instance]
        self.db_name = options.get('db_name', 'main')
        self.old_db = options.get('old_db', None)
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)

    def install(self):
        """ pack database and remove old Data.fs if needed """
        br = utils.get_browser(self.instance)
        out = utils.pack_db(self.instance, self.db_name, br)
        if self.old_db:
            utils.remove_file(self.instance, self.old_db)
        if not os.path.exists(self.path): os.mkdir(self.path)
        fp = open('%s/out.txt' % self.path, "w")
        print >> fp, out
        fp.close()
        return self.path

    def update(self):
        pass


class ImportObject:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        instance = options['instance']
        self.obj = options['obj'].split()
        self.replace = options.get('replace', 0)
        self.instance = buildout[instance]
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)

    def install(self):
        """ copy file, create external method and run it """
        br = utils.get_browser(self.instance)
        for obj1 in self.obj:
            if self.replace:
                utils.del_object(self.instance, obj1, br)
            rc = utils.import_one(self.instance, obj1, br)
            if rc:
                logging.getLogger(self.name).error('Cannot import %s: %s', obj1, rc)

        if not os.path.exists(self.path): os.mkdir(self.path)
        return self.path

    def update(self):
        pass


class SubmitUrl:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        instance = options['instance']
        self.url = options['url']
        self.out_file = options['output']
        self.instance = buildout[instance]
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)
        self.args = {}
        if 'args' in options:
            for arg in options['args'].split():
                self.args[arg] = options[arg]

    def install(self):
        """ copy file, create external method and run it """
        br = utils.get_browser(self.instance)
        utils.submit_url(self.instance, self.url, self.args, self.out_file, br)
        if not os.path.exists(self.path): os.mkdir(self.path)
        return self.path

    def update(self):
        pass



class PrepareContent:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        self.top_folder = options['top_folder']
        self.path = os.path.join(buildout['buildout']['directory'], 'parts', self.name)

    def install(self):
        """ copy file, create external method and run it """
        rc = utils.prepare_content(self.top_folder)
        if not os.path.exists(self.path): os.mkdir(self.path)
        logging.getLogger(self.name).info(rc)
        return self.path

    def update(self):
        pass


