# -*- coding: utf-8 -*-
"""
    sphinxcontrib.scaladomain
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    The Sphinx domain for documenting Scala APIs.

    :copyright: (c) 2012 by Georges Discry.
    :license: BSD, see LICENSE for more details.
"""

__version__ = '0.1'
__release__ = '0.1a1'

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType, Index
from sphinx.roles import XRefRole
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.compat import Directive
from sphinx.util.nodes import make_refnode

class ScalaPackage(Directive):
    """Directive to mark description of a new package."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        pkgname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['scl:package'] = pkgname
        if noindex:
            return []
        env.domaindata['scl']['packages'][pkgname] = \
            (env.docname, self.options.get('synopsis', ''),
             self.options.get('platform', ''), 'deprecated' in
             self.options)
        # Make a duplicate entry in 'objects' to facilitate searching for the
        # package in ScalaDomain.find_obj()
        env.domaindata['scl']['objects'][pkgname] = \
            (env.docname, 'package')
        targetnode = nodes.target(ids=['package-' + pkgname])
        self.state.document.note_explicit_target(targetnode)
        indextext = '%s (package)' % pkgname
        inode = addnodes.index(entries=[('single', indextext,
                                         'package-' + pkgname, '')])
        return [targetnode, inode]


class ScalaCurrentPackage(Directive):
    """Directive to mark the description of the content of a package, but
    the links to the package won't lead here.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        pkgname = self.arguments[0].strip()
        if pkgname == 'None':
            env.temp_data['scl:package'] = None
        else:
            env.temp_data['scl:package'] = pkgname
        return []


class ScalaXRefRole(XRefRole):
    """Scala cross-referencing role."""

    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['scl:package'] = env.temp_data.get('scl:package')
        if not has_explicit_title:
            title = title.lstrip('.') # Only has a meaning for the target
            target = target.lstrip('~') # Only has a meaning for the title
            # If the first character is a tilde, don't display the package part
            # of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        # If the first character is a dot, search more specific namespaces
        # first, else search builtins first
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target


class ScalaPackageIndex(Index):
    """Index subclass to provide the Scala package index."""

    name = 'pkgindex'
    localname = 'Scala Package Index'
    shortname = 'packages'

    def generate(self, docnames=None):
        content = {}
        # List of prefixes to ignore
        ignores = self.domain.env.config['scaladomain_pkgindex_common_prefix']
        ignores = sorted(ignores, key=len, reverse=True)
        # List of all packages, sorted by name
        packages = sorted(self.domain.data['packages'].iteritems(),
                          key=lambda x: x[0].lower())
        # Sort out collapsable packages
        prev_pkgname = ''
        num_toplevels = 0
        for pkgname, (docname, synopsis, platforms, deprecated) in packages:
            if docnames and docname not in docnames:
                continue

            for ignore in ignores:
                if pkgname.startswith(ignore):
                    pkgname = pkgname[len(ignore):]
                    stripped = ignore
                    break
            else:
                stripped = ''
            # The whole package name was stripped
            if not pkgname:
                pkgname, stripped = stripped, ''

            entries = content.setdefault(pkgname[0].lower(), [])

            parent = pkgname.split('.')[0]
            if parent != pkgname:
                # It's a child package
                if prev_pkgname == parent:
                    # First children package -- make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_pkgname.startswith(parent):
                    # Orphan package, add dummy entry
                    entries.append([stripped + parent, 1, '', '', '', '', ''])
                subtype = 2
            else:
                num_toplevels += 1
                subtype = 0

            qualifier = 'Deprecated' if deprecated else ''
            entries.append([stripped + pkgname, subtype, docname,
                        'package-' + stripped + pkgname, platforms, qualifier,
                        synopsis])
            prev_pkgname = pkgname
        # Collapse only if the number of top-level packages is larger than the
        # number of sub-packages
        collapse = len(packages) - num_toplevels < num_toplevels
        # Sort by first letter
        content = sorted(content.iteritems())

        return content, collapse


class ScalaDomain(Domain):
    """Scala language domain."""

    name = 'scl'
    label = 'Scala'
    object_types = {
        'package': ObjType('package', 'pkg'),
    }
    directives = {
        'package': ScalaPackage,
        'currentpackage': ScalaCurrentPackage,
    }
    roles = {
        'pkg': ScalaXRefRole(),
    }
    initial_data = {
        'objects': {},
        'packages': {},
    }
    indices = [
        ScalaPackageIndex,
    ]

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]
        for pkgname, (fn, _, _, _) in self.data['packages'].items():
            if fn == docname:
                del self.data['packages'][pkgname]

    def find_obj(self, env, pkgname, name, type, searchmode=0):
        """Find a Scala object for "name", perhaps using the given package.
        Returns a list of (name, object entry) tuples.
        """

        if not name:
            return []

        objects = self.data['objects']
        matches = []

        newname = None
        if searchmode == 1:
            objtypes = self.objtypes_for_role(type)
            if objtypes is not None:
                if pkgname and pkgname + '.' + name in objects and \
                   objects[pkgname + '.' + name][1] in objtypes:
                    newname = pkgname + '.' + name
                elif name in objects and objects[name][1] in objtypes:
                    newname = name
                else:
                    searchname = '.' + name
                    matches = [(oname, objects[oname]) for oname in objects
                               if oname.endswith(searchname)
                               and objects[oname][1] in objtypes]
        else:
            # NOTE: Searching for exact match, object type not considered
            if name in objects:
                newname = name
            elif type == 'pkg':
                return []
            elif pkgname and pkgname + '.' + name in objects:
                newname = pkgname + '.' + name
        if newname is not None:
            matches.append((newname, objects[newname]))
        return matches

    def resolve_xref(self, env, fromdocname, builder, type, target, node,
                     contnode):
        pkgname = node.get('scl:package')
        searchmode = 1 if node.hasattr('refspecific') else 0
        matches = self.find_obj(env, pkgname, target, type, searchmode)
        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, obj = matches[0]

        if obj[1] == 'package':
            docname, synopsis, platform, deprecated = self.data['packages'][name]
            assert docname == obj[0]
            title = name
            if synopsis:
                title += ': ' + synopsis
            if deprecated:
                title += ' (deprecated)'
            if platform:
                title += ' (' + platform + ')'
            return make_refnode(builder, fromdocname, docname,
                                'package-' + name, contnode, title)
        else:
            return make_refnode(builder, fromdocname, obj[0], name,
                                contnode, name)

    def get_objects(self):
        for pkgname, info in self.data['packages'].iteritems():
            yield (pkgname, pkgname, 'package', info[0], 'package-' + pkgname, 0)
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield (refname, refname, type, docname, refname, 1)



def setup(app):
    app.add_config_value('scaladomain_pkgindex_common_prefix', [], 'html')
    app.add_domain(ScalaDomain)
