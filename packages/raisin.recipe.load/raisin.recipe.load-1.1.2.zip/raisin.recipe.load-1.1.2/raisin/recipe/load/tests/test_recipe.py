"""
Test for raisin.recipe.transformation
"""

import os
import unittest
import shutil
from pkg_resources import get_provider
from raisin.recipe.load.database import produce_files
from raisin.recipe.load.database import produce_accessions
from raisin.recipe.load.database import produce_experiments
from raisin.recipe.load.database import produce_runs
from raisin.recipe.load.database import produce_sqlite3_database

PROVIDER = get_provider('raisin.recipe.load')
SANDBOX = PROVIDER.get_resource_filename("", 'tests/sandbox/')
PATH = os.path.join(SANDBOX, 'buildout')


class RecipeTests(unittest.TestCase):
    """
    Test the main method in database.py
    """

    def setUp(self):  # pylint: disable=C0103
        pass
        
    def test_produce_files(self):
        """
        Test producing files
        """
        data = {'experiments':[],'accessions':[], 
                'view':[{'project_id':'',
                        'accession_id':'',
                        'file_location':''},
                        ],
                'files':[],
                'read_length':[],
               }
        database = SANDBOX
        self.failUnless(produce_files(data, database) == None)

    def test_produce_accessions(self):
        """
        Test producing accessions
        """
        data = {'experiments':[],'accessions':[],'read_length':[]}
        database = SANDBOX
        self.failUnless(produce_accessions(data, database) == None)

    def test_produce_experiments_empty(self):
        """
        Test producing experiments
        """
        data = {'experiments':[],'accessions':[], 'annotations':[],'read_length':[],
                'replicates':[]}
        database = SANDBOX
        project_parameters = None
        self.failUnless(produce_experiments(data, database, project_parameters) == None)

    def test_produce_experiments_missing_project(self):
        """
        Test producing experiments with missing project
        """
        data = {'experiments':[{'project_id': 'ProjectABC',
                                'accession_id': '123'
                               }
                              ],
                'accessions':[{'project_id': 'ProjectABC',
                               'accession_id': '123',
                               'partition': 'partition',
                               'lab':'lab',
                               'species':'species',
                               'cell':'cell',
                               'localization':'localization',
                               'rnaExtract':'rnaExtract',
                               'readType':'readType'
                               }
                              ], 
                'annotations':[{'file_location': '/tmp/anno',
                                'version':'v2'
                               }],
                'read_length':[{'project_id': 'ProjectABC',
                                'accession_id': '123',
                                'read_length':'76'
                               }
                              ],
                'replicates':[{'replicate_id': '123',
                               'project_id': 'ProjectABC',
                               'accession_id': '123',
                               'ANNOTATION': '/tmp/anno'
                              }]
               }
        database = SANDBOX
        project_parameters = {}
        self.failUnless(produce_experiments(data, database, project_parameters) == None)
        
    def test_produce_experiments_without_anotation(self):
        """
        Test producing experiments with missing annotation
        """    
        data = {'experiments':[{'project_id': 'ProjectABC',
                                'accession_id': '123'
                               }
                              ],
                'accessions':[{'project_id': 'ProjectABC',
                               'accession_id': '123',
                               'partition': 'partition',
                               'lab':'lab',
                               'species':'species',
                               'cell':'cell',
                               'localization':'localization',
                               'rnaExtract':'rnaExtract',
                               'readType':'readType'
                               }
                              ], 
                'annotations':[],
                'read_length':[{'project_id': 'ProjectABC',
                                'accession_id': '123',
                                'read_length':'76'
                               }
                              ],
                'replicates':[{'replicate_id': '123',
                               'project_id': 'ProjectABC',
                               'accession_id': '123',
                               'ANNOTATION': '/tmp/anno'
                              }]
               }
        database = SANDBOX
        project_parameters = {}
        self.failUnless(produce_experiments(data, database, project_parameters) == None)
        #annotations[annotation_file_location]['version'] 
 
    def test_produce_runs(self):
        """
        Test producing runs
        """
        data = {'experiments':[],
                'accessions':[],
                'read_length':[],
                'replicates':[],
                'runs':[],
               }
        database = SANDBOX
        project_parameters = None
        self.failUnless(produce_runs(data, database, project_parameters) == None)

    def test_produce_sqlite3_database(self):
        """
        Test producing the sqlite3 database
        """
        data = None
        database = SANDBOX
        self.failUnless(produce_sqlite3_database(data, database) == None)


def test_suite():
    """
    Run the test suite
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
