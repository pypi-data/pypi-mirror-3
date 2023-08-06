"""

For a more detailed description, visit https://bitbucket.org/drk4/concatenate_files/overview

"""


'''

    Copyright - 2012 - Pedro Ferreira

    This file is part of concatenate_files.

    concatenate_files is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    concatenate_files is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with concatenate_files.  If not, see <http://www.gnu.org/licenses/>.

'''

import os
import argparse
import json
import textwrap


# exceptions used in the program

class CouldntConvertFromJsonError( ValueError ):
    pass

class NotADictError( ValueError ):
    pass




def concatenateFiles( directoryPath, fileNames ):

    '''

    Opens the files, and appends its content
    Returns a string with the result

    Arguments:

        directoryPath (string) : absolute path to the directory
        fileNames       (list) : a list of dictionaries with two keys: 
                                    "file"     (the file name/path, a string)
                                    "encoding" (the encoding to open the file)

    '''
  
    text = ""

    for files in fileNames:
        
        fileValue = files["file"]
        path = os.path.join( directoryPath, fileValue )

        if os.path.isdir( path ):
            continue

        try:
            currentFile = open( path, "r", encoding=files["encoding"] )

        except IOError:

            print( "    Didn't find:", path )

        else:
            content = currentFile.read()

            currentFile.close()

            text += content
            
            print( "    {}".format( fileValue ) )

    return text





def concatenate( config, resultingFileName="result.txt", basePath="" ):

    '''

    For a more detailed description, visit https://bitbucket.org/drk4/concatenate_files/overview

    Arguments:

        config (string or dictionary) : 
            when is a string     -> path to the configuration file
            when is a dictionary -> its the actual configuration, following the same pattern as the content of the file
        
        resultingFileName (string) : name of the file which will have the result (can be a relative path too)
        basePath          (string) : the paths in the configuration file are relative to this

    If basePath is not provided, the paths are relative to the current path where the script is executed.

    '''

        # see if valid path was given
        # by default, the base path is where the script is executed, but can be changed
        # changes in the base path only applies to the files in the configuration file
    if basePath:

        if not os.path.exists( basePath ):

            raise ValueError( "Invalid base path:", basePath )

    else:

        basePath = os.path.dirname( os.path.abspath(__file__) )


        # means the configuration is in a file, we have to open it, and parse it
    if isinstance( config, str ):
        
        
            # read the configuration file
        try:
            configFile = open( config, "r", encoding="utf-8" )
    
        except IOError:
    
            raise IOError( "Couldn't open the configuration file: " + config )
    
    
            # convert to an object from the json representation
        try:
            configContent = json.loads( configFile.read() )
    
        except ValueError:
            raise CouldntConvertFromJsonError( "Invalid configuration (couldn't convert from the json representation): " + config )
    
    
        configFile.close()

        # the configuration was sent as a dictionary
    else:
        configContent = config


        # check if we have a dictionary in the configuration
    if not isinstance( configContent, dict ):

        raise NotADictError( textwrap.dedent("""

            Invalid configuration (has to be an object/dictionary)
            Content: {0}
            Type: {1}

                """.format( configContent, type(configContent) )) )



    concatenatedText = ""

        # travel through all the folders
    for folder in configContent:

            # check if we got a string for the folder (the key)
        if not isinstance( folder, str ):

            print( "Invalid folder (the key has to be a string)" )
            print( "Content:", folder )
            print( "Type:", type( folder ) )
            continue


            # check if we have a list as the value
        if not isinstance( configContent[ folder ], list ):

            print( "Invalid configuration (the value has to be an array/list)" )
            print( "Content:", configContent[ folder ] )
            print( "Type:", type( configContent[ folder ] ) )
            continue


        path = os.path.join( basePath, folder )

            # normalize the path
        path = os.path.abspath( path )

        print( "\nDealing with folder:", path, "\n" )

            # if there's an empty list, it means to open all the files in that folder (its in random order)		
        if len( configContent[ folder ] ) == 0:

            print( "  Concatenating all the files in this folder." )

                # get a list of the file names in the directory
            fileNames = os.listdir( path )

            # the list will specify the files to open
        else:
            fileNames = configContent[ folder ]
        
        
            # add the encoding (for the ones that don't have already)
        for number, value in enumerate( fileNames ):
            
                # value is a string for the elements that don't have encoding set, so we change it to a dictionary
                # with the default encoding (utf-8)  
            if isinstance(value, str):
                fileNames[ number ] = { "file": value, "encoding": "utf-8" }
                


        concatenatedText += concatenateFiles( path, fileNames )



    resultingFileName = os.path.normpath( resultingFileName )

        # create the new file
    try:
        newFile = open( resultingFileName, "w", encoding="utf-8" )

    except IOError:
        raise IOError( "Couldn't create the file:", resultingFileName )


    newFile.write( concatenatedText )

    newFile.close()

    print( "\nCreated file:", resultingFileName )
    print( "Have a nice day!\n" )

    return





    # set up the parser, where the first argument is the path to the configuration file
    # and the second the name of the resulting file (default: result.txt)
    # basically: python concatenate_files.py config.txt (if the configuration file is in the same folder)

if __name__ == '__main__':

    parser = argparse.ArgumentParser( description = 'Concatenate files' )

    parser.add_argument( 'configFile', help = "path to the configuration file." )
    parser.add_argument( 'resultingFileName', help = "the name of the file (or a relative path to it) which will have the concatenated text.", nargs="?", default="result.txt" )
    parser.add_argument( 'basePath', help = "The paths in the configuration file are relatives, and are relative to the path where this script is executed. You can change this by proving an absolute path here.", nargs="?", default="" )

    args = parser.parse_args()


    concatenate( args.configFile, args.resultingFileName, args.basePath )

