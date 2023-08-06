# -*- coding: utf-8 -*-
"""
Buildout recipe raisin.recipe.dashboard
"""

import os
from raisin.recipe.dashboard import main


class Recipe(object):
    """
    Buildout recipe for creating dashboards.
    """

    def __init__(self, buildout, name, options):
        """
        Store the parameters for the buildout recipe.
        """
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        """
        Install the dashboard.
        """
        buildout_directory = self.buildout['buildout']['directory']
        dashboards_path = os.path.join(buildout_directory, 'dashboards')
        if not os.path.exists(dashboards_path):
            os.makedirs(dashboards_path)
        return main.main(self.options, self.buildout)

    def update(self):
        """
        Install the updated dashboard.
        """
        return self.install()
