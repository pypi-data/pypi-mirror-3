import os
import sys
import json
import shutil
import logging.config
from . import runtime, application, commands





def run(**settings):

    if os.path.exists('logging.conf'):
        logging.config.fileConfig('logging.conf')
    else:
        logconf = os.path.join(os.path.dirname(__file__), 'logging.json')
        with open(logconf, 'r') as f:
            conf = json.load(f)
            conf['handlers']['file']['filename'] = sys.argv[0]+'.log'
            logging.config.dictConfig(conf)

    runtime.init(settings)
    app = application.Application(**settings)
    commands.run(app)


def create_project(name, dir):
    tmpl_pkg = os.path.join(os.path.dirname(__file__), 'resources/appsample')
    tmpl_run = os.path.join(os.path.dirname(__file__), 'resources/appsample.py')
    tmpl_hgignore = os.path.join(os.path.dirname(__file__), 'resources/.hgignore')
    tmpl_setup = os.path.join(os.path.dirname(__file__), 'resources/setup.py')

    pkg_path = os.path.join(dir, name)
    run_path = os.path.join(dir, name+'.py')
    hgignore_path = os.path.join(dir, '.hgignore')
    setup_path = os.path.join(dir, 'setup.py')

    shutil.copytree(tmpl_pkg, pkg_path, ignore=shutil.ignore_patterns('*.pyc'))
    shutil.copy2(tmpl_run, run_path)
    shutil.copy2(tmpl_hgignore, hgignore_path)
    shutil.copy2(tmpl_setup, setup_path)

    def rewrite_file(fpath):
        with open(fpath, 'rb') as f:
            content = f.read()
            content = content.replace('appsample', name)
        with open(fpath, 'wb') as f:
            f.write(content)

    rewrite_file(run_path)
    rewrite_file(setup_path)

