""" content traverser """
import ptah
from ptah import config
from sqlalchemy import sql
from zope import interface
from pyramid.interfaces import ITraverser
from pyramid.traversal import traversal_path, ResourceTreeTraverser

from node import Session
from content import Content
from interfaces import IApplicationRoot


class ContentTraverser(object):
    interface.implements(ITraverser)
    config.adapter(IApplicationRoot)

    _path_queries = {}

    def __init__(self, root):
        self.root = root

    def __call__(self, request, queries=_path_queries):
        environ = request.environ
        context = root = self.root

        if root.__default_root__ and 'bfg.routes.route' in environ:
            return ResourceTreeTraverser(root)(request)

        path = '/%s/'%'/'.join(traversal_path(environ.get('PATH_INFO','/')))

        vroot_tuple = ()

        l_path = len(root.__root_path__)

        # build paths for all parents in content hierarchy
        idx = 0
        paths = {}
        current = root.__path__
        for sec in path[l_path:].split('/'):
            if sec:
                current = '%s%s/'%(current, sec)
                paths[str(idx)] = current
                idx += 1

        if idx:
            if idx not in queries:
                bindparams = [sql.bindparam(str(p)) for p in range(idx)]

                queries[idx] = ptah.QueryFreezer(
                    lambda: Session.query(Content)\
                        .filter(Content.__path__.in_(bindparams))
                        .order_by(sql.desc(Content.__path__)))

            parents = queries[idx].all(**paths)
        else:
            parents = []

        if parents:
            # set __parent__
            parents[-1].__parent__ = root
            for idx in range(len(parents)-1):
                parents[idx].__parent__ = parents[idx+1]

            context = parents[0]
            node = context.__path__[len(root.__path__):]
            leaf = path[l_path+len(node):].split('/')
            leaf, subpath = leaf[0], leaf[1:]

            return {'context': context,
                    'view_name': leaf,
                    'subpath': subpath,
                    'traversed': traversal_path(node),
                    'virtual_root': root,
                    'virtual_root_path': vroot_tuple,
                    'root': root}
        else:
            vpath_tuple = ()

            leaf = path[l_path:].split('/')
            leaf, subpath = leaf[0], leaf[1:]

            return {'context': context,
                    'view_name': leaf,
                    'subpath': subpath,
                    'traversed': vpath_tuple,
                    'virtual_root': root,
                    'virtual_root_path': (),
                    'root': root}
