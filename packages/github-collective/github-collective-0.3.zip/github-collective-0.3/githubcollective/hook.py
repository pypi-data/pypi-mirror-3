import json

HOOK_BOOL_OPTIONS = ('active',)

class Hook(object):

    config = ''

    def __init__(self, **kw):
        self.__dict__.update(kw)
        #Handle case of unicode coming from GitHub
        self.name = unicode(self.name)
        if isinstance(self.config, str):
            try:
                self.config = json.loads(self.config)
            except ValueError:
                raise ValueError("Error parsing JSON config for %r" % self)

    def __repr__(self):
        return '<Hook "%s">' % self.name

    def __str__(self):
        return self.__repr__()

    def dumps(self):
        return self.__dict__
