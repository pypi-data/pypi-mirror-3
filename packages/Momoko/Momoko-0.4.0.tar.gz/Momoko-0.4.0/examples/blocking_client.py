#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import momoko

import settings


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        # Create a database connection when a request handler is called
        # and store the connection in the application object.
        if not hasattr(self.application, 'db'):
            self.application.db = momoko.BlockingClient({
                'host': settings.host,
                'port': settings.port,
                'database': settings.database,
                'user': settings.user,
                'password': settings.password,
                'min_conn': settings.min_conn,
                'max_conn': settings.max_conn,
                'cleanup_timeout': settings.cleanup_timeout
            })
        return self.application.db


class OverviewHandler(BaseHandler):
    def get(self):
        self.write('''
<ul>
    <li><a href="/query">A single query</a></li>
</ul>
        ''')
        self.finish()


class SingleQueryHandler(BaseHandler):
    def get(self):
        # Besides using a with statement everyting is the same as the normal
        # Psycopg2 module
        with self.db.connection as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 42, 12, 40, 11;')

        self.write('Query results: %s' % cursor.fetchall())
        self.finish()


def main():
    try:
        tornado.options.parse_command_line()
        application = tornado.web.Application([
            (r'/', OverviewHandler),
            (r'/query', SingleQueryHandler)
        ], debug=True)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('Exit')


if __name__ == '__main__':
    main()
