import unittest
import os.path
import sys


    # the path where this script is executed
TEST_PATH = os.path.dirname( os.path.abspath(__file__) )

    # where we have the concatenate module
CONCATENATE_PATH = os.path.abspath( os.path.join(TEST_PATH, '..') )

    # so we can refer to the concatenate_files.py module
sys.path.append( CONCATENATE_PATH )


from concatenate_files import concatenate
from concatenate_files import CouldntConvertFromJsonError, NotADictError


UNIT_TEST_PATH = os.path.dirname( os.path.abspath(__file__) )

TEST_DATA_PATH = os.path.abspath( os.path.join(UNIT_TEST_PATH, 'test_data') )




def manuallyConcatenateFiles( listOfPaths ):

    '''
        Arguments:

            listOfPaths (list) : list of strings with the path to the files
    '''

    concatenatedText = ""

    for path in listOfPaths:

        with open( path, 'r', encoding = 'utf-8' ) as f:
            concatenatedText += f.read()

    return concatenatedText




class ConcatenateTest( unittest.TestCase ):

    def test_invalidBasePath( self ):

        '''
            We're passing an invalid path to the basePath argument.
        '''
        
        print( "\nStarting: {}\n".format( self.id() ) )

        self.assertRaises( ValueError, concatenate, "config.txt", "result.txt", "aaa" )


    def test_fileNotFound( self ):

        '''
            Failed to found the configuration file.
        '''
        
        print( "\nStarting: {}\n".format( self.id() ) )

        self.assertRaises( IOError, concatenate, os.path.join( TEST_DATA_PATH, "no_config.txt" ), "result.txt" )


    def test_wrongJson( self ):

        '''
            Found the configuration file, but is invalid JSON.
        '''

        print( "\nStarting: {}\n".format( self.id() ) )

        self.assertRaises( CouldntConvertFromJsonError, concatenate, os.path.join( TEST_DATA_PATH, "invalid_json_config.txt" ), "result.txt" )


    def test_notADict( self ):

        '''
            The JSON is valid, but not on the format required.
        '''

        print( "\nStarting: {}\n".format( self.id() ) )

        self.assertRaises( NotADictError, concatenate, os.path.join( TEST_DATA_PATH, "not_dict_config.txt" ), "result.txt" )


    def test_config( self ):

        '''
            Tests a well-written configuration file (see "config.txt").
        '''

        print( "\nStarting: {}\n".format( self.id() ) )

            # manually concatenate the files, for comparison later
        files = [ os.path.join( TEST_DATA_PATH, "aa.txt" ),
                    os.path.join( TEST_DATA_PATH, "test", "bb.txt" ),
                    os.path.join( TEST_DATA_PATH, "test", "cc.txt" ),
                    os.path.join( TEST_DATA_PATH, "test", "test2", "dd.txt" ) ]


        compareText = manuallyConcatenateFiles( files )


        concatenate( os.path.join( TEST_DATA_PATH, "config.txt" ), "result.txt", TEST_DATA_PATH )

        with open( "result.txt", 'r', encoding="utf-8" ) as f:
            result = f.read()

        self.assertEqual( compareText, result )



    def test_config2( self ):

        '''
            Tests another well-written configuration file ("config2.txt").
        '''
        
        print( "\nStarting: {}\n".format( self.id() ) )

            # manually concatenate the files, for comparison later
        files = [ os.path.join( TEST_DATA_PATH, "test", "bb.txt" ),
                    os.path.join( TEST_DATA_PATH, "test", "cc.txt" ) ]

        compareText = manuallyConcatenateFiles( files )

        concatenate( os.path.join( TEST_DATA_PATH, "config2.txt" ), "result.txt", TEST_DATA_PATH )

        with open( "result.txt", 'r', encoding="utf-8" ) as f:
            result = f.read()


        self.assertEqual( compareText, result )


    def test_defaultBasePath( self ):

        '''
            Calls concatenate() without providing the basePath argument (defaults to the current path where the concatenate_files.py  script is executed)

            Calls without the resultingFileName argument too (should be "result.txt")

            ( configuration file: config3_defaultBasePath.txt )
        '''

        print( "\nStarting: {}\n".format( self.id() ) )

        files = [ os.path.join( TEST_DATA_PATH, "aa.txt" ),
                   os.path.join( TEST_DATA_PATH, "test", "test2", "dd.txt" ) ]

        compareText = manuallyConcatenateFiles( files )

        
        concatenate( os.path.join( TEST_DATA_PATH, "config3_defaultBasePath.txt" ) )


        with open( "result.txt", 'r', encoding="utf-8" ) as f:
            result = f.read()

        self.assertEqual( compareText, result )


    def test_differentEncoding( self ):
        
        '''
            Tests the possibility to specify the encoding for each file
            
            ( uses config4_encoding.txt )
        '''
        
        print( "\nStarting: {}\n".format( self.id() ) )
        
            # japanese encoding
        with open( os.path.join( TEST_DATA_PATH, "different_encoding", "ee.txt"), "r", encoding="shift-jisx0213" ) as f:
            text1 = f.read()

            
            # utf-8 encoding (the default)
        with open( os.path.join( TEST_DATA_PATH, "different_encoding", "asd.txt"), "r", encoding="utf-8" ) as f:
            text2 = f.read()
            
            # greek encoding
        with open( os.path.join( TEST_DATA_PATH, "different_encoding", "ff.txt" ), "r", encoding="iso8859-7") as f:
            text3 = f.read()

        


        concatenate( os.path.join( TEST_DATA_PATH, "config4_encoding.txt" ), "result.txt", TEST_DATA_PATH )


        with open( "result.txt", 'r', encoding="utf-8" ) as f:
            result = f.read()

        self.assertEqual( text1 + text2 + text3, result )



    def test_dictionaryArgument( self ):
        
        '''
            Tests calling concatenate() directly with a dictionary (in the right format), and compare with the same configuration, but
                reading it from a file ( "config.txt" )
        '''

        print( "\nStarting: {}\n".format( self.id() ) )

        concatenate( os.path.join( TEST_DATA_PATH, "config.txt" ), "result.txt", TEST_DATA_PATH )

        with open( "result.txt", 'r', encoding="utf-8" ) as f:
            result1 = f.read()
        
        
        config = {
                "":
                    [
                    "aa.txt"
                    ],
            
                "test":
                    [
                    "bb.txt",
                    "doesntExist.txt",
                    "cc.txt"
                    ],
            
                "test/test2":
                    [
                    ]
                  }

        concatenate( config, "result.txt", TEST_DATA_PATH )
        
        with open( "result.txt", 'r', encoding="utf-8" ) as f:
            result2 = f.read()
            
            
        self.assertEqual( result1, result2 )
    


if __name__ == '__main__':

    unittest.main()
