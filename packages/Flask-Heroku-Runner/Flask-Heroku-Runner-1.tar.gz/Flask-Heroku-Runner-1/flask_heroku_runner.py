import os
import flask


class HerokuApp(flask.Flask):
    def run(self, *positional, **keywords):
        if 'PORT' in os.environ:
            keywords.setdefault('port', int(os.environ['PORT']))
        if 'HOST' in os.environ:
            keywords.setdefault('host', os.environ['HOST'])
        super(HerokuApp, self).run(*positional, **keywords)
