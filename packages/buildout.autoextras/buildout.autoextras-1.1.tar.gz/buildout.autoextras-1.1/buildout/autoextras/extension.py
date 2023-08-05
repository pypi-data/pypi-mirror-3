# -*- coding: utf-8 -*-
import pkg_resources
from zc.buildout.easy_install import logger as installer_logger, \
    _log_requirement, Installer


class Extension(object):
    """Adds extras_require to the targeted sections if the extra is available
    """

    keys = None
    targets = None

    def __init__(self, buildout):
        self.buildout = buildout
        buildout_section = buildout['buildout']
        parse = lambda v, k: [i.strip()
                              for i in v.get(k, '').split('\n')
                              if i.strip()]
        self.keys = parse(buildout_section, 'autoextra-keys')
        self.targets = parse(buildout_section, 'autoextra-targets')
        self._verify_targets()
        self._requirements = []

    def _verify_targets(self):
        """Verify the targets are formatted correctly and/or exist."""
        pass

    def get_wanted_extras(self, dist):
        extras = []
        if not dist.extras:
            return None
        for key in self.keys:
            if key in dist.extras:
                extras.append(key)
        return extras and extras or None

    def installer_install(self, autoextras_requirements):
        def install(installer, specs, working_set=None):
            """
            A monkeypatch on zc.buildout.easy_install.Installer's install method.

            I'd tell you to look at the original method's docstring for more
            information about what this method does, but it doesn't have one. >.<
            """
            # Yanked from zc.buildout==1.5.2, but attempts to be
            # backwards compatible.
            ##installer_logger.debug('Installing %s.', repr(specs)[1:-1])

            path = installer._path
            destination = installer._dest
            if destination is not None and destination not in path:
                path.insert(0, destination)

            requirements = [installer._constrain(pkg_resources.Requirement.parse(spec))
                            for spec in specs]
            if working_set is None:
                ws = pkg_resources.WorkingSet([])
            else:
                ws = working_set

            for requirement in requirements:
                for dist in installer._get_dist(requirement, ws, installer._always_unzip):
                    ws.add(dist)
                    installer._maybe_add_setuptools(ws, dist)

            # OK, we have the requested distributions and they're in the working
            # set, but they may have unmet requirements.  We'll resolve these
            # requirements. This is code modified from
            # pkg_resources.WorkingSet.resolve.  We can't reuse that code directly
            # because we have to constrain our requirements (see
            # versions_section_ignored_for_dependency_in_favor_of_site_packages in
            # zc.buildout.tests).
            requirements.reverse() # Set up the stack.
            processed = {}  # This is a set of processed requirements.
            best = {}  # This is a mapping of key -> dist.
            # Note that we don't use the existing environment, because we want
            # to look for new eggs unless what we have is the best that
            # matches the requirement.
            env = pkg_resources.Environment(ws.entries)
            while requirements:
                # Process dependencies breadth-first.
                req = installer._constrain(requirements.pop(0))
                if req in processed:
                    # Ignore cyclic or redundant dependencies.
                    continue
                dist = best.get(req.key)
                if dist is None:
                    # Find the best distribution and add it to the map.
                    dist = ws.by_key.get(req.key)
                    if dist is None:
                        try:
                            dist = best[req.key] = env.best_match(req, ws)
                        except pkg_resources.VersionConflict, err:
                            raise VersionConflict(err, ws)
                        if dist is None or (
                            dist.location in installer._site_packages and not
                            installer.allow_site_package_egg(dist.project_name)):
                            # If we didn't find a distribution in the
                            # environment, or what we found is from site
                            # packages and not allowed to be there, try
                            # again.
                            if destination:
                                installer_logger.debug('Getting required %r', str(req))
                            else:
                                installer_logger.debug('Adding required %r', str(req))
                            _log_requirement(ws, req)
                            for dist in installer._get_dist(req,
                                                            ws, installer._always_unzip):
                                ws.add(dist)
                                installer._maybe_add_setuptools(ws, dist)

                if req in autoextras_requirements:
                    extras = self.get_wanted_extras(dist)
                    if extras is None:
                        extras = []
                    extras.extend(req.extras)
                else:
                    extras = req.extras

                if dist not in req:
                    # Oops, the "best" so far conflicts with a dependency.
                    raise VersionConflict(
                        pkg_resources.VersionConflict(dist, req), ws)
                requirements.extend(dist.requires(extras)[::-1])
                processed[req] = True
                # BBB zc.buildout<1.5 doesn't have a _site_packages attr.
                if hasattr(installer, '_site_packages') and dist.location in installer._site_packages:
                    installer_logger.debug('Egg from site-packages: %s', dist)
            return ws
        return install

    def __call__(self):
        requirements = []
        for target in self.targets:
            section, option = target.split(':')
            # Parse distribution names to Requirements
            pkg_reqs = [pkg_resources.parse_requirements(value).next()
                        for value in self.buildout[section].get(option, '').split()
                        if pkg_resources.parse_requirements(value).next() not in requirements]
            requirements.extend(pkg_reqs)

        Installer._install = Installer.install
        # OH YEAH! Hack on a hack of a hack. Buildout is da shit!
        Installer.install = self.installer_install(requirements)


def extension(buildout):
    return Extension(buildout)()
