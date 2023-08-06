"""
Test for raisin.recipe.transformation
"""

import os
import unittest
from pkg_resources import get_provider

from raisin.recipe.transformation import accessions
from raisin.recipe.transformation import annotations
from raisin.recipe.transformation import experiments
from raisin.recipe.transformation import files
from raisin.recipe.transformation import genomes
from raisin.recipe.transformation import profiles
from raisin.recipe.transformation import read_length
from raisin.recipe.transformation import view


PROVIDER = get_provider('raisin.recipe.transformation')
SANDBOX = PROVIDER.get_resource_filename("", 'tests/sandbox/')
PATH = os.path.join(SANDBOX, 'buildout')


class RecipeTests(unittest.TestCase):
    """
    Test the main method in prepare.py
    """

    def setUp(self):  # pylint: disable=C0103
        pass

    def test_accessions(self):
        """
        Test the accessions method
        """
        self.failUnless(accessions.main(data=None, workspace=None) == None)

    def test_annotations(self):
        """
        Test the annotations method
        """
        self.failUnless(annotations.main(data=None, workspace=None) == None)

    def test_experiments(self):
        """
        Test the experiments method
        """
        data = {'accessions.csv': [{'project_id': 'ENCODE',
                                    'accession_id': 'ABCD',
                                    'species': 'Homo sapiens',
                                    'cell': 'cell',
                                    'readType': 'readType',
                                    'type': 'type',
                                    'qualities': 'qualities',
                                    'dataType': 'dataType',
                                    'rnaExtract': 'rnaExtract',
                                    'localization': 'localization',
                                    'lab': 'lab'}]}
        experiments.main(data, SANDBOX)
        file_path = os.path.join(SANDBOX, 'experiments.csv')
        file_content = open(file_path, 'r').read()
        header = "\t".join(['project_id', 'accession_id', 'replicate_id'])
        line = "\t".join(['ENCODE', 'ABCD', '1'])
        expected = "%s\n%s\n" % (header, line)
        self.failUnless(file_content == expected, file_content)

    def test_files(self):
        """
        Test the files method
        """
        self.failUnless(files.main(data=None, workspace=None) == None)

    def test_genomes(self):
        """
        Test the files method
        """
        self.failUnless(genomes.main(data=None, workspace=None) == None)

    def test_profiles(self):
        """
        Test the profiles method
        """
        data = {'profiles.csv': [{'PROJECTID': 'ENCODE',
                                  'project_id': 'ENCODE',
                                  'ANNOTATION': '',
                                  'GENOMESEQ': ''}],
                'annotations.csv': [{'file_location': ''}],
                'genomes.csv': [],
                'accessions.csv': [{'project_id': 'ENCODE',
                                    'accession_id': 'ABCD',
                                    'species': 'Homo sapiens',
                                    'cell': 'cell',
                                    'readType': 'readType',
                                    'type': 'type',
                                    'qualities': 'qualities',
                                    'dataType': 'dataType',
                                    'rnaExtract': 'rnaExtract',
                                    'localization': 'localization',
                                    'lab': 'lab'}]}
        profiles.main(data)

    def test_read_length(self):
        """
        Test the read_length method
        """
        data = {'profiles.csv': [{'PROJECTID': 'ENCODE',
                                  'project_id': 'ENCODE',
                                  'ANNOTATION': ''}],
                'annotations.csv': [{}],
                'genomes.csv': [],
                'accessions.csv': [{'project_id': 'ENCODE',
                                    'accession_id': 'ABCD',
                                    'species': 'Homo sapiens',
                                    'cell': 'cell',
                                    'readType': '1x70D',
                                    'type': 'type',
                                    'qualities': 'qualities',
                                    'dataType': 'dataType',
                                    'rnaExtract': 'rnaExtract',
                                    'localization': 'localization',
                                    'lab': 'lab'}],
                'runs.csv': [{'project_id': 'ENCODE',
                              'run_id': 'run_id',
                              'read_length': 70}],
                'files.csv': [{}],
                             }
        read_length.main(data, SANDBOX)

    def test_view(self):
        """
        Test the view method
        """
        data = {'profiles.csv': [{'PROJECTID': 'ENCODE',
                                  'project_id': 'ENCODE',
                                  'ANNOTATION': ''}],
                'annotations.csv': [{}],
                'genomes.csv': [],
                'accessions.csv': [{'project_id': 'ENCODE',
                                    'accession_id': 'ABCD',
                                    'species': 'Homo sapiens',
                                    'cell': 'cell',
                                    'readType': '1x70D',
                                    'type': 'type',
                                    'qualities': 'qualities',
                                    'dataType': 'dataType',
                                    'rnaExtract': 'rnaExtract',
                                    'localization': 'localization',
                                    'lab': 'lab'}],
                'runs.csv': [{'project_id': 'ENCODE',
                              'run_id': 'run_id',
                              'read_length': 70}],
                'files.csv': [{'project_id': 'ENCODE',
                               'accession_id': 'ABCD',
                               'type': 'fastq',
                               'file_location': 'myfile.fastq.gz'
                               }],
                }
        view.main(data, SANDBOX)


def test_suite():
    """
    Run the test suite
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
