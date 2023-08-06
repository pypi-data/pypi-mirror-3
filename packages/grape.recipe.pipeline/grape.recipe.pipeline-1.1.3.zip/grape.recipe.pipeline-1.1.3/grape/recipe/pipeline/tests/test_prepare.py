"""
Test for prepare.py
"""

import os
import unittest
import shutil
from pkg_resources import get_provider

from grape.recipe.pipeline.prepare import main

PROVIDER = get_provider('grape.recipe.pipeline')
SANDBOX = PROVIDER.get_resource_filename("", 'tests/sandbox/')
BUILDOUT = os.path.join(SANDBOX, 'buildout')


class MainTests(unittest.TestCase):
    """
    Test the main method in prepare.py
    """

    def setUp(self):
        shutil.rmtree(BUILDOUT, ignore_errors=True)
        os.mkdir(BUILDOUT)
        os.mkdir(os.path.join(BUILDOUT, 'bin'))
        os.mkdir(os.path.join(BUILDOUT, 'parts'))
        os.mkdir(os.path.join(BUILDOUT, 'parts/TestRun'))
        os.mkdir(os.path.join(BUILDOUT, 'src'))
        os.mkdir(os.path.join(BUILDOUT, 'src/flux'))
        os.mkdir(os.path.join(BUILDOUT, 'src/flux/bin'))
        path = open(os.path.join(BUILDOUT, 'src/flux/bin/flux.sh'), 'w')
        path.close()
        os.mkdir(os.path.join(BUILDOUT, 'src/gem'))
        os.mkdir(os.path.join(BUILDOUT, 'src/overlap'))
        path = open(os.path.join(BUILDOUT, 'src/overlap/overlap'), 'w')
        path.close()
        os.mkdir(os.path.join(BUILDOUT, 'src/pipeline'))
        os.mkdir(os.path.join(BUILDOUT, 'src/pipeline/bin'))
        os.mkdir(os.path.join(BUILDOUT, 'src/pipeline/lib'))
        os.mkdir(os.path.join(BUILDOUT, 'src/testdata'))
        path = open(os.path.join(BUILDOUT,
                                 'src/testdata/testA.r1.fastq.gz'), 'w')
        path.close()
        path = open(os.path.join(BUILDOUT,
                                 'src/testdata/testA.r2.fastq.gz'), 'w')
        path.close()
        path = open(os.path.join(BUILDOUT,
                                 'src/testdata/testB.r1.fastq.gz'), 'w')
        path.close()
        path = open(os.path.join(BUILDOUT,
                                 'src/testdata/testB.r2.fastq.gz'), 'w')
        path.close()
        os.mkdir(os.path.join(BUILDOUT, 'var'))

    def test_main(self):
        """
        Test the main method
        """
        os.chdir(BUILDOUT)
        options = {'accession': 'TestRun',
                   'location': os.path.join(BUILDOUT, 'parts/TestRun'),
                   }

        file_location = '\n'.join([
            os.path.join(BUILDOUT, "src/testdata/testA.r2.fastq.gz"),
            os.path.join(BUILDOUT, "src/testdata/testA.r1.fastq.gz"),
            os.path.join(BUILDOUT, "src/testdata/testB.r2.fastq.gz"),
            os.path.join(BUILDOUT, "src/testdata/testB.r1.fastq.gz")])

        buildout = {
            'TestRun': {
                'file_location': file_location,
                'species': 'Homo sapiens',
                'readType': '2x76',
                'cell': 'NHEK',
                'rnaExtract': 'LONGPOLYA',
                'localization': 'CELL',
                'qualities': 'solexa',
                'pair_id': 'testA\ntestA\ntestB\ntestB',
                'mate_id': 'testA.2\ntestA.1\ntestB.2\ntestB.1',
                'label': 'Test\nTest\nTest\nTest',
               },
            'pipeline': {
                 'TEMPLATE': os.path.join(
                     BUILDOUT,
                     "/src/pipeline/template3.0.txt"),
                 'PROJECTID': 'Test',
                 'THREADS': '2',
                 'DB': 'TestRNAseqPipeline',
                 'COMMONDB': 'TestRNAseqPipelineCommon',
                 'MAPPER': 'GEM',
                 'MISMATCHES': '2',
                 'GENOMESEQ': os.path.join(
                     BUILDOUT,
                     "/src/testdata/H.sapiens.genome.hg19.test.fa"),
                 'ANNOTATION': os.path.join(
                     BUILDOUT,
                     "/src/testdata/H.sapiens.EnsEMBL.55.test.gtf"),
                },
            'buildout': {'directory': BUILDOUT},
            'settings': {
                 'java': '',
                 'flux_jar': '',
                 'overlap': os.path.join(BUILDOUT, 'src/overlap/overlap'),
                 'gem_folder': os.path.join(BUILDOUT, 'src/gem'),
                 }
            }
        result = main(options, buildout)
        self.failUnless(result == None)


def test_suite():
    """
    Run the test suite
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
