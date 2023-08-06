import types
import os
import sys
import base64

from jsonserver import SimpleJSONRPCServer

from git import Repo, Blob, Tree, Head
from time import time as _time, sleep as _sleep, strftime

class Service:

    def __init__(self, repobase):
        self.repobase = repobase
        self.repos = {}

    def repo(self, d):
        if not self.repos.has_key(d):
            self.repos[d] = Repo(os.path.join(self.repobase, d))
        return self.repos[d]

    def treej(self, tree, include_contents=False):
        return {'__jsonclass__': ['gitjson.Tree'],
                'repo': str(tree.repo),
                'id': str(tree.id),
                'mode': str(tree.mode),
                'name': str(tree.name),
                'contents': tree.keys()
            }

    def commitj(self, commit):
        return {'__jsonclass__': ['gitjson.Commit'],
                'id': str(commit.id),
                'parents': repr(commit.parents),
                'tree': self.treej(commit.tree),
                'author': str(commit.author),
                'authored_date': strftime("%c", commit.authored_date),
                'committer': str(commit.committer),
                'committed_date': strftime("%c", commit.committed_date),
                'message': str(commit.message),
                }

    def headj(self, head):
        return {'__jsonclass__': ['gitjson.Head'],
                'name': head.name,
                'commit': self.commitj(head.commit)
                }

    def blobj(self, blob, include_data=False):
        b = {'__jsonclass__': ['gitjson.Blob'],
                'name': blob.name,
                'mode': blob.mode,
                'id': str(blob.id),
                'mimetype': blob.mime_type,
                'size': blob.size,
                }
        if include_data:
            b['data'] = base64.b64encode(blob.data)
        return b

    def heads(self, base):
        return map(self.headj, self.repo(base).heads)

    def commits(self, base, start='master', path='', max_ct=10, skip=0):
        return map(self.commitj, self.repo(base).commits(start, path, max_ct, skip))

    def commits_since(self, base, start='master', path='', since='1970-01-01'):
        return map(self.commitj, self.repo(base).commits_since(start, path, since))

    def items_in_by_commit_id(self, base, id, include_data=False):
        commit = self.repo(base).commit(id)
        res = []
        for item in commit.tree.values():
            if isinstance(item, Blob):
                res.append(self.blobj(item, include_data))
            elif isinstance(item, Tree):
                res.append(self.treej(item))
        return res

    def items_in(self, base, idx, name, include_data=False):
        tree = self.repo(base).commits(start=idx)[0].tree
        for n in name.split('/'): # entirely defeats the purpose of ids...
            tree = tree/n
        res = []
        for item in tree.values():
            if isinstance(item, Blob):
                res.append(self.blobj(item, include_data))
            elif isinstance(item, Tree):
                res.append(self.treej(item))
        return res

    def item(self, base, idx, name, include_data=False):
        item = self.repo(base).commits(start=idx)[0].tree/name
        if isinstance(item, Blob):
            return self.blobj(item, include_data)
        elif isinstance(item, Tree):
            return self.treej(item)
        return item

    def items(self, base, idx, names, include_data=False):
        res = []
        for name in names:
            res.append(self.item(base, idx, name, include_data))
        return res

    def item(self, base, idx, name, include_data=False):
        #item = self.repo(base).heads[idx].commit.tree
        item = self.repo(base).commits(start=idx)[0].tree
        for n in name.split('/'): # entirely defeats the purpose of ids...
            item = item/n
        if isinstance(item, Blob):
            return self.blobj(item, include_data)
        elif isinstance(item, Tree):
            return self.treej(item)
        return item

if __name__ == '__main__':

    svc = Service(sys.argv[1])

    server = SimpleJSONRPCServer(("localhost", 8000))
    for fname in dir(svc):
        fn = getattr(svc, fname)
        print fn, type(fn)
        if not isinstance(fn, types.FunctionType) and \
           not isinstance(fn, types.MethodType):
            continue
        server.register_function(fn, fname)
    server.serve_forever()

