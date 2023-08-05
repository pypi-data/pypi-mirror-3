# -*- coding: utf-8 -*-
from pkg_resources import parse_requirements

from zc.buildout import UserError
from zc.recipe.egg.egg import Eggs


class Extension(object):
    """Adds extras_require to the targeted sections if the extra is available
    """

    def __init__(self, buildout):
        self.buildout = buildout
        buildout_section = buildout['buildout']
        parse = lambda v, k: [i.strip()
                              for i in v.get(k, '').split('\n')
                              if i.strip()]
        self.keys = parse(buildout_section, 'autoextra-keys')
        self.targets = parse(buildout_section, 'autoextra-targets')
        self._verify_targets()

    def _verify_targets(self):
        """Verify the targets are formatted correctly and/or exist."""
        pass

    def _has_wanted_extra(self, extra):
        if extra in self.keys:
            return True
        return False

    def _build_recipe(self, section, option):
        name = "%s-%s" % (section, option)
        section_opts = self.buildout[section]
        index = section_opts.get('index', None)
        find_links = section_opts.get('find-links', None)
        options = {'eggs': section_opts.get(option, ''),
                   'index': index,
                   'find-links': find_links,
                   }
        recipe = Eggs(self.buildout, name, options)
        return recipe

    def __call__(self):
        for target in self.targets:
            section, option = target.split(':')
            # Parse distribution names to Requirements
            pkg_reqs = [parse_requirements(value).next() for value in self.buildout[section].get(option, '').split()]
            # Grab the distributions from a Setuptools' working_set.
            # This can't be perfect because there is no standard interface for recipes.
            eggs_recipe = self._build_recipe(section, option)
            names, working_set = eggs_recipe.working_set()
            for pkg_req in pkg_reqs:
                dist = working_set.find(pkg_req)
                # Determine if the package has extra_requires
                extras = [e for e in dist.extras if self._has_wanted_extra(e)]
                req_line = dist.project_name

                # Tack on the extras if we find any
                if extras:
                    req_line += "[%s]" % ', '.join(extras)
                # Append the new requirement line to target
                value = self.buildout[section][option].split()
                value.append(req_line)
                self.buildout[section][option] = '\n'.join(value)


def extension(buildout):
    return Extension(buildout)()
