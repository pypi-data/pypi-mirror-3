.. contents::

Introduction
============


from fabric.buildout_recipe import BuildoutRecipe

import fabric.api


class Recipe(BuildoutRecipe):
    """zc.buildout recipe"""

    def execute(self):
        """override this."""
        fabric.api.run("uname -a")
