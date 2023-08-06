'''
Tests for the console commands provided by __main__.py

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
#===============================================================================
# Copyright (c) 2012, Chris Fournier
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#       
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================
import os
import unittest
from .__main__ import main


class TestMain(unittest.TestCase):
    '''
    Test command line functions.
    '''
    # pylint: disable=R0904,C0301
    
    test_data_dir = os.path.join(os.path.split(__file__)[0], 'data')
    
    print_output = True
    test_help    = False
    
    EXPECTED_FILE_STRINGS = [
'Pi*_s = 0.7165532879818594104308390023',
'K*_s = 0.7170345217883418222976796831',
'B_s = 0.0014285714285714285714285714',
'F_1 \n \tmean\t= 0.5488257630783062008183635783\n\tstd\t= 0.1541776268839723153329934675\n\tvar\t= 0.02377074063157338283693571885\n\tstderr\t= 0.02379012431740241024748814014',
'P \n \tmean\t= 0.5705026455026455026455026457\n\tstd\t= 0.1913327668048554567150062580\n\tvar\t= 0.03660822765320119817474314830\n\tstderr\t= 0.04175223270517067477184376667',
'R \n \tmean\t= 0.5708994708994708994708994710\n\tstd\t= 0.2009486961610950520518783548\n\tvar\t= 0.0403803784888440973097057753\n\tstderr\t= 0.04385060052194762366757538877',
'Pr \n \tmean\t= 0.3933140933140933140933140934\n\tstd\t= 0.1432599301657948205815072907\n\tvar\t= 0.02052340759110840880922651004\n\tstderr\t= 0.03126187971613534798006584564',
'S \n \tmean\t= 0.7619047619047619047619047619\n\tstd\t= 0.07055015423823358837798727192\n\tvar\t= 0.004977324263038548752834467119\n\tstderr\t= 0.01539530581369118988034410932',
'Pk \n \tmean\t= 0.3258145363408521303258145360\n\tstd\t= 0.08839695282480399887931269980\n\tvar\t= 0.007814021268710623676986953602\n\tstderr\t= 0.01363994594730826050014572596',
'WindowDiff \n \tmean\t= 0.3047619047619047619047619048\n\tstd\t= 0.08438116736509214477138630998\n\tvar\t= 0.007120181405895691609977324262\n\tstderr\t= 0.01302029679814566213216037145']

    EXPECTED_FOLDER_STRINGS = [
'Mean Pi*_s \n \tmean\t= 0.7165532879818594104308390023\n\tstd\t= 0\n\tvar\t= 0\n\tstderr\t= 0',
'Mean K*_s \n \tmean\t= 0.7170345217883418222976796831\n\tstd\t= 0\n\tvar\t= 0\n\tstderr\t= 0',
'Mean B_s \n \tmean\t= 0.0014285714285714285714285714\n\tstd\t= 0\n\tvar\t= 0\n\tstderr\t= 0',
'F_1 \n \tmean\t= 0.5488257630783062008183635783\n\tstd\t= 0.1541776268839723153329934675\n\tvar\t= 0.02377074063157338283693571885\n\tstderr\t= 0.02379012431740241024748814014',
'P \n \tmean\t= 0.5705026455026455026455026457\n\tstd\t= 0.1913327668048554567150062580\n\tvar\t= 0.03660822765320119817474314830\n\tstderr\t= 0.04175223270517067477184376667',
'R \n \tmean\t= 0.5708994708994708994708994710\n\tstd\t= 0.2009486961610950520518783548\n\tvar\t= 0.04038037848884409730970577530\n\tstderr\t= 0.04385060052194762366757538877',
'Pr \n \tmean\t= 0.3933140933140933140933140934\n\tstd\t= 0.1432599301657948205815072907\n\tvar\t= 0.02052340759110840880922651004\n\tstderr\t= 0.03126187971613534798006584564',
'S \n \tmean\t= 0.7619047619047619047619047619\n\tstd\t= 0.07055015423823358837798727192\n\tvar\t= 0.004977324263038548752834467119\n\tstderr\t= 0.01539530581369118988034410932',
'Pk \n \tmean\t= 0.3258145363408521303258145360\n\tstd\t= 0.08839695282480399887931269982\n\tvar\t= 0.007814021268710623676986953605\n\tstderr\t= 0.01363994594730826050014572597',
'WindowDiff \n \tmean\t= 0.3047619047619047619047619048\n\tstd\t= 0.08438116736509214477138630999\n\tvar\t= 0.007120181405895691609977324264\n\tstderr\t= 0.01302029679814566213216037145']

    EXPECTED_OM_STRINGS = [
'1 - Pk \n \tmean\t= 0.6741854636591478696741854645\n\tstd\t= 0.08839695282480399887931269980\n\tvar\t= 0.007814021268710623676986953602\n\tstderr\t= 0.01363994594730826050014572596',
'1 - WindowDiff \n \tmean\t= 0.6952380952380952380952380952\n\tstd\t= 0.08438116736509214477138630998\n\tvar\t= 0.007120181405895691609977324262\n\tstderr\t= 0.01302029679814566213216037145']
    
    EXPECTED_WPR_STRINGS = [
'WinPR-f_1 \n \tmean\t= 0.6537078835417392808312562948\n\tstd\t= 0.1104334172259618258006709431\n\tvar\t= 0.01219553964020336212051245300\n\tstderr\t= 0.02409854731860048794927717470',
'WinPR-p \n \tmean\t= 0.6700319521748093176664605238\n\tstd\t= 0.1469987063321598074606894023\n\tvar\t= 0.0216086196633285598741911137\n\tstderr\t= 0.03207774756322412707724005526',
'WinPR-r \n \tmean\t= 0.6683725005153576582148010719\n\tstd\t= 0.1570297604076544084333187669\n\tvar\t= 0.02465834565368534800463416065\n\tstderr\t= 0.03426670302042171194576414586']

    def test_load_files(self):
        '''
        Test the different ways to load files.
        '''
        metric = 'pi'
        argv = [metric, os.path.join(self.test_data_dir,
                                     'hearst1997.json')]
        self.assertEqual('Pi*_s = 0.7165532879818594104308390023', main(argv))
        
        argv = [metric, '-f', 'json', os.path.join(self.test_data_dir,
                                                   'hearst1997.json')]
        self.assertEqual('Pi*_s = 0.7165532879818594104308390023', main(argv))
        
        argv = [metric, '-f', 'tsv', os.path.join(self.test_data_dir,
                                                  'hearst1997.tsv')]
        self.assertEqual('Pi*_s = 0.7165532879818594104308390023', main(argv))


    def test_all_but_winpr_folder(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pi', 'k', 'b', 'f', 'p', 'r', 'pr', 's', 'pk', 'wd']
        for metric, expected in zip(metrics, self.EXPECTED_FOLDER_STRINGS):
            argv = [metric, os.path.join(self.test_data_dir,
                                         '..')]
            actual = main(argv)
            self.assertEqual(expected, actual)


    def test_all_but_winpr_metrics(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pi', 'k', 'b', 'f', 'p', 'r', 'pr', 's', 'pk', 'wd']
        for metric, expected in zip(metrics, self.EXPECTED_FILE_STRINGS):
            argv = [metric, os.path.join(self.test_data_dir,
                                         'hearst1997.json')]
            actual = main(argv)
            self.assertEqual(expected, actual)


    def test_winpr_metrics(self):
        '''
        Run through each metric and load from a file.
        '''
        submetrics = ['f', 'p', 'r']
        for submetric, expected in zip(submetrics, self.EXPECTED_WPR_STRINGS):
            argv = ['wpr', submetric, os.path.join(self.test_data_dir,
                                                   'hearst1997.json')]
            actual = main(argv)
            self.assertEqual(expected, actual)


    def test_om_metrics(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pk', 'wd']
        for metric, expected in zip(metrics, self.EXPECTED_OM_STRINGS):
            argv = [metric, '-om', os.path.join(self.test_data_dir,
                                         'hearst1997.json')]
            actual = main(argv)
            self.assertEqual(expected, actual)


    def test_file(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pi', 'k', 'b', 'f', 'p', 'r', 'pr', 's', 'pk', 'wd']
        filesizes = [51, 50, 49, 1524, 1524, 1524, 702, 584, 1747, 645]
        for metric, expected_filesize in zip(metrics, filesizes):
            filename = 'testfile.tsv'
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))
            argv = [metric, '-o', filename, os.path.join(self.test_data_dir,
                                                         'hearst1997.json')]
            try:
                main(argv)
                self.assertTrue(os.path.exists(filename))
                actual_filesize = len(open(filename).read())
                self.assertEqual(expected_filesize, actual_filesize, 
                                 '%(metric)s %(expected)i != %(actual)i' % \
                                 {'metric'   : metric,
                                  'expected' : expected_filesize,
                                  'actual'   : actual_filesize})
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            
            self.assertFalse(os.path.exists(filename))


    def test_file_om(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pk', 'wd']
        filesizes = [1751, 649]
        for metric, expected_filesize in zip(metrics, filesizes):
            filename = 'testfile.tsv'
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))
            argv = [metric, '-om', '-o', filename,
                    os.path.join(self.test_data_dir, 'hearst1997.json')]
            try:
                main(argv)
                self.assertTrue(os.path.exists(filename))
                actual_filesize = len(open(filename).read())
                self.assertEqual(expected_filesize, actual_filesize, 
                                 '%(metric)s %(expected)i != %(actual)i' % \
                                 {'metric'   : metric,
                                  'expected' : expected_filesize,
                                  'actual'   : actual_filesize})
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            
            self.assertFalse(os.path.exists(filename))


    def test_file_winpr(self):
        '''
        Run through each metric and load from a file.
        '''
        submetrics = ['f', 'p', 'r']
        filesizes = [1741, 1741, 1741]
        for submetric, expected_filesize in zip(submetrics, filesizes):
            
            filename = 'testfile.tsv'
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))
            argv = ['wpr', submetric, '-o', filename,
                    os.path.join(self.test_data_dir, 'hearst1997.json')]
            try:
                main(argv)
                self.assertTrue(os.path.exists(filename))
                actual_filesize = len(open(filename).read())
                self.assertEqual(expected_filesize, actual_filesize, 
                                 '%(metric)s %(expected)i != %(actual)i' % \
                                 {'metric'   : submetric,
                                  'expected' : expected_filesize,
                                  'actual'   : actual_filesize})
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            
            self.assertFalse(os.path.exists(filename))


    def test_file_s_detailed(self):
        '''
        Test detailed S output.
        '''
        expected_filesize = 2131
        filename = 'testfile.tsv'
        if os.path.exists(filename):
            os.remove(filename)
        self.assertFalse(os.path.exists(filename))
        argv = ['s', '-de', '-o', filename, os.path.join(self.test_data_dir,
                                                         'hearst1997.json')]
        try:
            main(argv)
            self.assertTrue(os.path.exists(filename))
            actual_filesize = len(open(filename).read())
            self.assertEqual(expected_filesize, actual_filesize, 
                             '%(metric)s %(expected)i != %(actual)i' % \
                             {'metric'   : 's',
                              'expected' : expected_filesize,
                              'actual'   : actual_filesize})
        finally:
            if os.path.exists(filename):
                os.remove(filename)
        
        self.assertFalse(os.path.exists(filename))

    def test_help_output(self):
        '''
        Test the help output.
        '''
        argv = ['wd', '-h']
        if self.print_output and self.test_help:
            main(argv)

