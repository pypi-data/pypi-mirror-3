import time
import logging
import multiprocessing
import tornado.web
import tornado.httpserver

from .runtime import db





class Application(object):

    def __init__(self, **settings):
        self.settings = settings
        self.debug = settings.get('debug', False)

    def start_webapp(self, webapp):
        route = webapp['route']
        handlers = route.routes
        cookie_secret = webapp.get('cookie_secret', None)
        xsrf_cookies = bool(cookie_secret)
        template_path = route.template_path
        ui_modules = route.ui_modules
        ui_methods = route.ui_methods

        app = tornado.web.Application(handlers,
                debug=self.debug,
                xsrf_cookies=xsrf_cookies,
                cookie_secret=cookie_secret,
                template_path=template_path,
                ui_modules=ui_modules,
                ui_methods=ui_methods,
                )

        port = webapp['port']
        app.listen(port)
        logging.info('start http server: [web:%s]', port)


    def http_serve_forever(self):
        for webapp in self.settings['webapps']:
            self.start_webapp(webapp)
        if not self.debug:
            num_processes = self.settings.get('num_processes', None)
            if num_processes != 1:
                tornado.process.fork_processes(num_processes)
        tornado.ioloop.IOLoop.instance().start()


    def start_services(self):
        for service in self.settings.get('services', []):
            p = multiprocessing.Process(target=service)
            p.daemon = True
            p.start()
            logging.info('start service: %s', service)

    def join_services(self):
        while multiprocessing.active_children():
            time.sleep(1)

    def db_drop(self):
        metadata = self.settings['metadata']
        metadata.drop_all(db.engine)

    def db_init(self):
        metadata = self.settings['metadata']
        metadata.create_all(db.engine)

    def db_upgrade(self):
        import subprocess
        import ConfigParser
        database = self.settings['database']

        alembic_ini = ConfigParser.RawConfigParser()
        alembic_ini.read('etc/alembic/alembic.ini.sample')
        alembic_ini.set('alembic', 'sqlalchemy.url', database)
        with open('etc/alembic/alembic.ini', 'wb') as inifile:
            alembic_ini.write(inifile)

        subprocess.check_call(['env/bin/alembic', '--config', 'etc/alembic/alembic.ini', 'current'])
        subprocess.check_call(['env/bin/alembic', '--config', 'etc/alembic/alembic.ini', 'history'])
        subprocess.check_call(['env/bin/alembic', '--config', 'etc/alembic/alembic.ini', 'revision', '--autogenerate'])
        subprocess.check_call(['env/bin/alembic', '--config', 'etc/alembic/alembic.ini', 'upgrade', 'head'])

    def genconf():
        pwd = os.path.abspath('.')
        uploadroot = os.path.abspath(settings.upload_dir + '/..')

        nginx_conf = os.path.join(pwd, 'etc/nginx.conf')
        if not os.path.exists(nginx_conf):
            with open(nginx_conf, 'wb') as f, open(nginx_conf+'.sample', 'rb') as sf:
                data = sf.read()
                data = data.replace('${pwd}', pwd)
                data = data.replace('${uploadroot}', uploadroot)
                f.write(data)

        supervisor_conf = os.path.join(pwd, 'etc/supervisor.conf')
        if not os.path.exists(supervisor_conf):
            with open(supervisor_conf, 'wb') as f, open(supervisor_conf+'.sample', 'rb') as sf:
                data = sf.read()
                data = data.replace('${pwd}', pwd)
                f.write(data)






