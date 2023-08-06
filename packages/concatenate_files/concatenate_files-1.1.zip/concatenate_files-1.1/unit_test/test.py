import unittest
import os.path
import sys


    # the path where this script is executed
TEST_PATH = os.path.dirname( os.path.abspath(__file__) )

    # where we have the concatenate module
CONCATENATE_PATH = os.path.abspath( os.path.join(TEST_PATH, '..') )

sys.path.append( CONCATENATE_PATH )


from concatenate_files import concatenate
from concatenate_files import CouldntConvertFromJsonError, NotADictError


UNIT_TEST_PATH = os.path.dirname( os.path.abspath(__file__) )
 
TEST_DATA_PATH = os.path.abspath( os.path.join(UNIT_TEST_PATH, 'test_data') )


class ConcatenateTest( unittest.TestCase ):

    def test_invalidBasePath( self ):
        
        self.assertRaises( ValueError, concatenate, "", "result.txt", "aaa" )

        # failed to found the configuration file
    def test_fileNotFound( self ):
    
        self.assertRaises( IOError, concatenate, os.path.join( TEST_DATA_PATH, "no_config.txt" ), "result.txt" )
    
        # found the configuration file, but is invalid JSON
    def test_wrongJson( self ):
    
        self.assertRaises( CouldntConvertFromJsonError, concatenate, os.path.join( TEST_DATA_PATH, "invalid_json_config.txt" ), "result.txt" )
        
        # the JSON is valid, but not on the format required
    def test_notADict( self ):
    
        self.assertRaises( NotADictError, concatenate, os.path.join( TEST_DATA_PATH, "not_dict_config.txt" ), "result.txt" )
    
    def test_config( self ):
        
            # manually concatenate the files, for comparison later
        concatenatedText = ""
        
        with open( os.path.join( TEST_DATA_PATH, "aa.txt" ), 'r' ) as f:
            concatenatedText += f.read()
            
        with open( os.path.join( TEST_DATA_PATH, "test", "bb.txt" ), 'r' ) as f:
            concatenatedText += f.read()
            
        with open( os.path.join( TEST_DATA_PATH, "test", "cc.txt" ), 'r' ) as f:
            concatenatedText += f.read()

        with open( os.path.join( TEST_DATA_PATH, "test", "test2", "dd.txt" ), 'r' ) as f:
            concatenatedText += f.read()
    
    
        concatenate( os.path.join( TEST_DATA_PATH, "config.txt" ), "result.txt", TEST_DATA_PATH )
        
        with open( "result.txt", 'r' ) as f:
            result = f.read() 
            
        self.assertEqual( concatenatedText, result )
    
    
    
    def test_config2( self ):
        
            # manually concatenate the files, for comparison later
        concatenatedText = ""
        
        with open( os.path.join( TEST_DATA_PATH, "test", "bb.txt" ), 'r' ) as f:
            concatenatedText += f.read()
            
        with open( os.path.join( TEST_DATA_PATH, "test", "cc.txt" ), 'r' ) as f:
            concatenatedText += f.read()
            
        concatenate( os.path.join( TEST_DATA_PATH, "config2.txt" ), "result.txt", TEST_DATA_PATH )
        
        with open( "result.txt", 'r' ) as f:
            result = f.read() 
            
            
        self.assertEqual( concatenatedText, result )
    
    
    
    
if __name__ == '__main__':

    unittest.main()