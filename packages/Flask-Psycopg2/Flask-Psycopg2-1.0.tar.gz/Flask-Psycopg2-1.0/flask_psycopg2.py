import psycopg2
import urlparse

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Psycopg2(object):

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.config.setdefault('PSYCOPG2_DATABASE_URI', 'postgresql://postgres@localhost:5432/test')
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def connect(self):
        r = urlparse.urlparse(self.app.config['PSYCOPG2_DATABASE_URI'])
        if not r.scheme == 'postgres':
            raise ValueError('scheme must be postgres')
        return psycopg2.connect(user=r.username, password=r.password, host=r.hostname, port=r.port, dbname=r.path[1:])

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'postgresql_db'):
            if not ctx.postgresql_db.closed:
                ctx.postgresql_db.close()

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'postgresql_db'):
                ctx.postgresql_db = self.connect()
            return ctx.postgresql_db
