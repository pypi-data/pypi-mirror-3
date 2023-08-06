Concatenates the content of files
=================================


Requires:
	
* **python3**


Configuration file format
=========================

	{
		"folder1":
			[
			"file1.txt",
			"file2.txt"
			],
		
		"folder2":
			[
			],
				
		"":
			[
			"file3.txt",
			"file4.txt"
			]
	}


Its an object in json (or a dictionary, in python), where the key is the folder (or relative path to it), and the value a list with the files to be concatenated (in that order).
Only the files in that list are concatenated, if the folder has other files, they won't be added.

When you have an empty list (as in folder2), it means to concatenate all the files in that folder (but the order is arbitrary, so only use it when it doesn't matter).

The third folder (the empty string ""), points to the current path where the program is executed.



Arguments
=========


	configFile        : path to the configuration file.
	resultingFileName : the name of the file (or a relative path to it) which will have the concatenated text.
	
	
	
Run the program
===============


	python concatenate_files.py config.txt
	
		or	
	
	python concatenate_files.py config.txt result.txt

	
	
---------------------------------------
	
	

A little history
================


	I've written this program mainly to join separate javascript files into a single one (to run it in a optimizer). I used to do this manually, which was a bit annoying, so I decided to write a program to do this for me. 
	First I thought about writing it in c++, but got stomped right from the start. How would I deal with the filesystem in a portable way? Ok, there are libraries that deal with that, but just the thought of trying to link a library... (yea, I've had bad experiences :p)

	So I had been reading stuff about python, and how simple and portable it is, and decided to give it a try, and thus this program (yes, my very first python program).
	
	It was a nice experience, python is a pretty cool language... it would have been nice if I had come across it sooner but hey, better late than never :)