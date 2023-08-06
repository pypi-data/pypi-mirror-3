# -*- coding: utf-8 -*-
"""Recipe apache"""

import os
from raisin.recipe.load import database


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        staging_path = self.buildout['transform']['staging']
        database_path = self.buildout['load']['database']
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        database.main(self.buildout, staging_path, database_path)

    def update(self):
        return self.install()
