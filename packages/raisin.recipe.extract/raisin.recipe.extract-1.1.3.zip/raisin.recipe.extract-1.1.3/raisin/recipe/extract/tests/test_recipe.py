"""
Test for raisin.recipe.extract
"""

import os
import unittest
from pkg_resources import get_provider
import StringIO

from raisin.recipe.extract import accessions
from raisin.recipe.extract import annotations
from raisin.recipe.extract import files
from raisin.recipe.extract import genomes
from raisin.recipe.extract import profiles
from raisin.recipe.extract import replicates
from raisin.recipe.extract import runs

PROVIDER = get_provider('raisin.recipe.extract')
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
        Test the accessions main method
        """
        workspace = SANDBOX
        accession_files = {}
        self.failUnless(accessions.main(workspace, accession_files) == None)

    def test_annotations(self):
        """
        Test the annotations main method
        """
        workspace = SANDBOX
        annotations_file = StringIO.StringIO()
        self.failUnless(annotations.main(workspace, annotations_file) == None)

    def test_files(self):
        """
        Test the files method
        """
        workspace = SANDBOX
        accessions_files = StringIO.StringIO()
        self.failUnless(files.main(workspace, accessions_files) == None)

    def test_genomes(self):
        """
        Test the files method
        """
        workspace = SANDBOX
        genomes_file = StringIO.StringIO()
        self.failUnless(genomes.main(workspace, genomes_file) == None)

    def test_profiles(self):
        """
        Test the profiles method
        """
        workspace = SANDBOX
        profile_files = StringIO.StringIO()
        self.failUnless(profiles.main(workspace, profile_files) == None)

    def test_replicates(self):
        """
        Test the replicates method
        """
        workspace = SANDBOX
        profile_files = StringIO.StringIO()
        self.failUnless(replicates.main(workspace, profile_files) == None)

    def test_runs(self):
        """
        Test the runs method
        """
        workspace = SANDBOX
        dumps_folder = StringIO.StringIO()
        self.failUnless(runs.main(workspace, dumps_folder) == None)


def test_suite():
    """
    Run the test suite
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
