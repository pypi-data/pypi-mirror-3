# coding: latin-1

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


'''
	Opens the files, and appends its content 
	Returns a string with the result

	Arguments:
	
		path    (string) : relative path to the files (points at a folder)
		fileNames (list) : has the file names
'''

def concatenateFiles( path, fileNames ):

	text = ""
	
	for files in fileNames:
		
		try:	
			currentFile = open( path + files, "r" )
		
		except IOError:
				
			print( "Didn't find:", path + files )
			
		else:
			content = currentFile.read()
	
			currentFile.close()
	
			text += content

	return text



'''
	Start here
	
	Arguments:
	
		pathToConfig      : path to the configuration file
		resultingFileName : name of the file which will have the result (can be a relative path too)
'''

def concatenate( pathToConfig, resultingFileName ):
	
		# read the configuration file	
	try:
		configFile = open( pathToConfig, "r" )
	
	except IOError:
		
		print( "Couldn't open the configuration file: " + pathToConfig )
		return
		
		# convert to an object from the json representation
	try:
		configContent = json.loads( configFile.read() )
	
	except ValueError:
		print( "Invalid configuration (couldn't convert from the json representation): " + pathToConfig )
		return
		
	configFile.close()
	
	
		# check if we have a dictionary in the configuration 
	if not isinstance( configContent, dict ):
		
		print( "Invalid configuration (has to be an object/dictionary)" )
		print( "Content:", configContent )
		print( "Type:", type( configContent ) )
		return
		
	
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
		
			# add a separator to the path
		path = os.path.normpath( folder ) + os.sep
		
		print ( "Dealing with folder: " + path )
		
			# if there's an empty list, it means to open all the files in that folder (its in random order)		
		if len( configContent[ folder ] ) == 0:
			
			print( "    Concatenating all the files in this folder." )
			
				# get a list of the file names in the directory
			fileNames = os.listdir( path )
			
			# the list will specify the files to open
		else:
			fileNames = configContent[ folder ]
		
		
		concatenatedText += concatenateFiles( path, fileNames )
		
		

		# create the new file 
	try:
		newFile = open( resultingFileName, "w" )

	except IOError:
		print( "Couldn't create the file:", resultingFileName )
		return
		
	newFile.write( concatenatedText )

	newFile.close()

	print( "Created file: " + resultingFileName )
	print( "Have a nice day!" )
		
	return



	# set up the parser, where the first argument is the path to the configuration file
	# and the second the name of the resulting file (default: result.txt)
	# basically: python concatenate_files.py config.txt (if the configuration file is in the same folder) 
	
if __name__ == '__main__':

	parser = argparse.ArgumentParser( description = 'Concatenate files' )

	parser.add_argument( 'configFile', help = "path to the configuration file." )
	parser.add_argument( 'resultingFileName', help = "the name of the file (or a relative path to it) which will have the concatenated text.", nargs="?", default="result.txt" )

	args = parser.parse_args()

	concatenate( args.configFile, args.resultingFileName )
	
