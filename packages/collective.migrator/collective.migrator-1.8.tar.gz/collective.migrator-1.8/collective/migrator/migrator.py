"""Do the migration
"""
import logging, os, sys, shutil, urllib2

BOOTSTRAP_URL = 'http://python-distribute.org/bootstrap.py'


logger = logging.getLogger('migrator')


def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if len(sys.argv) > 1:
        if '-v' in sys.argv:
            return logging.DEBUG
    return logging.INFO


def main():
    logging.basicConfig(level=loglevel(),
                        format="%(levelname)s: %(message)s")
    logger.info('Starting migraton.')
    cur_dir = os.getcwd()
    mig_dir = os.path.join(cur_dir, 'migrator')
    if os.path.exists(mig_dir):
        logger.info('directory migrator already present. please delete/rename and try again!')
        return
    os.mkdir(mig_dir)
    src_dir = os.path.dirname(__file__)
    buildout_cfg = os.path.join(src_dir, 'buildout.cfg')
    shutil.copy(buildout_cfg, mig_dir)
    scripts_dir = os.path.join(src_dir, 'scripts')
    mig_scripts_dir = os.path.join(mig_dir, 'scripts')
    shutil.copytree(scripts_dir, mig_scripts_dir)
    templates_dir = os.path.join(src_dir, 'templates')
    mig_templates_dir = os.path.join(mig_dir, 'templates')
    shutil.copytree(templates_dir, mig_templates_dir)
    os.chdir(mig_dir)
    ez = {}
    exec urllib2.urlopen(BOOTSTRAP_URL).read() in ez
    os.system('bin/buildout')
