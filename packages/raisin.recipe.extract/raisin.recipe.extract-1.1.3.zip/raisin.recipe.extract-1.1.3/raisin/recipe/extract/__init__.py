# -*- coding: utf-8 -*-
"""Recipe raisin.recipe.extract"""

import os
import glob

from raisin.recipe.extract import accessions
from raisin.recipe.extract import annotations
from raisin.recipe.extract import files
from raisin.recipe.extract import genomes
from raisin.recipe.extract import profiles
from raisin.recipe.extract import replicates
from raisin.recipe.extract import runs


class Recipe(object):
    """
    Recipe to extract diverse configurations from the buildout configuration.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.buildout_directory = self.buildout['buildout']['directory']
        self.name = name
        self.options = options

    def get_workspace(self):
        """
        Get the workspace where the extracted files will be stored.
        If it doesn't exist, it is created.
        """
        if not os.path.exists(self.options['workspace']):
            os.makedirs(self.options['workspace'])
        return self.options['workspace']

    def get_profile_files(self):
        """
        Get the profiles configured in the

            pipelines_configurations

        section of the buildout.

        Alternatively looks in the configured

            profiles_folder

        And takes all profile configurations from there.
        """
        result = []
        if 'pipelines_configurations' in self.buildout:
            configuration = self.buildout['pipelines_configurations']['profiles']
            for path in configuration.split('\n'):
                result.append(os.path.join(self.buildout_directory, path))
        elif 'profiles_folder' in self.options:
            path = os.path.join(self.options['profiles_folder'], '*/db.cfg')
            result = [f for f in glob.glob(path)]
        return result

    def get_accession_files(self):
        """
        Get the accessions configured in the

            pipelines_configurations

        section of the buildout
        """
        result = []
        if 'pipelines_configurations' in self.buildout:
            configuration = self.buildout['pipelines_configurations']['accessions']
            for path in configuration.split('\n'):
                result.append(os.path.join(self.buildout_directory, path))
        elif 'accessions_folder' in self.options:
            path = os.path.join(self.options['accessions_folder'], '*/db.cfg')
            result = [f for f in glob.glob(path)]
        return result

    def get_dumps_folder(self):
        """
        Get the location of the dumps folder.
        If it doesn't exist, raise an error.
        """
        if not os.path.exists(self.options['pipeline_dumps']):
            message = "dumps_folder not found: %s"
            raise AttributeError(message % self.options['pipeline_dumps'])
        return self.options['pipeline_dumps']

    def get_annotations_file(self):
        """
        Get the location of the annotations file.
        If it doesn't exist, raise an error.
        """
        if not os.path.exists(self.options['annotations_file']):
            message = "annotations_file not found: %s"
            raise AttributeError(message % self.options['annotations_file'])
        return self.options['annotations_file']

    def get_genomes_file(self):
        """
        Get the location of the genomes file.
        If it doesn't exist, raise an error.
        """
        if not os.path.exists(self.options['genomes_file']):
            message = "genomes_file not found: %s"
            raise AttributeError(message % self.options['genomes_file'])
        return self.options['genomes_file']

    def install(self):
        """
        Run the recipe.
        """
        workspace = self.get_workspace()
        profile_files = self.get_profile_files()
        accession_files = self.get_accession_files()
        dumps_folder = self.get_dumps_folder()
        annotations_file = self.get_annotations_file()
        genomes_file = self.get_genomes_file()

        accessions.main(workspace, accession_files)
        annotations.main(workspace, open(annotations_file, 'r'))
        files.main(workspace, accession_files)
        genomes.main(workspace, open(genomes_file, 'r'))
        profiles.main(workspace, profile_files)
        replicates.main(workspace, profile_files)
        runs.main(workspace, dumps_folder)

    def update(self):
        """
        Update the recipe.
        """
        return self.install()
