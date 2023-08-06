# -*- coding: utf-8 -*-
from fabric.tasks import execute as fab


class BuildoutRecipe(object):
    """fabric recipe base"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        # fabric.state.env values
        options_key = buildout[self.name].get("__options__", "fabric:options")
        self.fabric_options = buildout.get(options_key, {})

        # make fabric.tasks.execute kwargs
        # step1: make hosts/roles
        names = ("hosts", "exclude_hosts", "roles", "host", "role")
        plurals = ("hosts", "exclude_hosts", "roles")
        hosts_key = buildout[name].get("__hosts__", "fabric:hosts")
        hosts = buildout.get(hosts_key, {})
        hosts = {k: v for k, v in hosts.items() if k in names}
        for x in plurals:
            if x in hosts:
                hosts[x] = hosts[x].strip().split("\n")
        self.hosts = hosts
        # step2: function params
        self.params = {k: v for k, v in buildout[name].items()
                       if k != "recipe" and not k.startswith("__")}
        # step3: merge
        self.params.update(hosts)

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.

        import fabric.state as state
        for name, value in self.fabric_options.items():
            state.env[name] = value
        fab(self.execute, **self.params)
        return tuple()

    def execute(self, **kwargs):
        raise NotImplementedError

    def update(self):
        """Updater"""
        pass
