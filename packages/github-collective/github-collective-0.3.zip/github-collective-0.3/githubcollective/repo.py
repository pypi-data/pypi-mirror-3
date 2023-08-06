REPO_RESERVED_OPTIONS = ('fork', 'owners', 'teams', 'hooks')
REPO_BOOL_OPTIONS = ('private', 'has_issues', 'has_wiki', 'has_downloads')

class Repo(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return '<Repo "%s">' % self.name

    def __str__(self):
        return self.__repr__()

    def dumps(self):
        dump = self.__dict__.copy()
        dump['hooks'] = [hook.dumps() for hook in dump['hooks']]
        return dump

    def getGroupedHooks(self):
        """GitHub repos can only have 1 of each hook, except `web`."""
        hooks = {}
        for hook in self.hooks:
            if hook.name != 'web':
                hooks[hook.name] = [hook]
            else:
                if 'web' not in hooks:
                    hooks['web'] = []
                hooks['web'].append(hook)
        return hooks
