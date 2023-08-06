# -*- coding: utf-8 -*-
"""Recipe raisin.recipe.transformation"""

import csv
import glob
import os
import shutil

from raisin.recipe.transformation import accessions
from raisin.recipe.transformation import annotations
from raisin.recipe.transformation import files
from raisin.recipe.transformation import genomes
from raisin.recipe.transformation import profiles
from raisin.recipe.transformation import experiments
from raisin.recipe.transformation import read_length
from raisin.recipe.transformation import view


def read_csv(file_name):
    return [line for line in csv.DictReader(open(file_name, 'r'),
                                            delimiter='\t',
                                            skipinitialspace=True)]


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        workspace = self.buildout['extract']['workspace']
        staging = self.options['staging']
        if not os.path.exists(staging):
            os.makedirs(staging)

        data = {}
        for source in [f for f in glob.glob(os.path.join(workspace, '*.csv'))]:
            file_name = os.path.split(source)[-1]
            target = os.path.join(staging, file_name)
            shutil.copyfile(source, target)
            data[file_name] = read_csv(target)

        accessions.main(data, staging)
        annotations.main(data, staging)
        files.main(data, staging)
        genomes.main(data, staging)
        profiles.main(data)
        experiments.main(data, staging)
        read_length.main(data, staging)
        view.main(data, staging)

    def update(self):
        return self.install()
