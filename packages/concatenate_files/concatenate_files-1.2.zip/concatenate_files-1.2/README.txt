Concatenates the content of files
=================================


Requires:

* python3


Configuration file format
=========================

    {
    "folder1":
        [
            "file1.txt",
            "file2.txt"
        ],
    
    "folder2":
        [],
            
    "":
        [
            "file3.txt",
            "file4.txt"
        ],

    "folder3":
        [
            {
            "file": "file5.txt",
            "encoding": "iso8859-7"
            },
            
            "something/file6.txt"
        ]
    }


Its an object in json (or a dictionary, in python), where the key is the folder (or relative path to it), and the value a list with the files to be concatenated (in that order).
Only the files in that list are concatenated, if the folder has other files, they won't be added.

When you have an empty list (as in folder2), it means to concatenate all the files in that folder (but the order is arbitrary, so only use it when it doesn't matter). It isn't recursive.

The third folder (the empty string ""), points to the current path where the program is executed.

By default, the encoding used is "utf-8", but you can specify the encoding for each individual file, as in "file5.txt" in the example above.

You can also write a path (instead of just the file basename), like in "file6.txt" (works in the folder too).



The paths are relative to the path where the script is being executed. You can change that by providing an additional argument (see below).


The configuration file can sometimes be generated, I've added an example (generate_config.py), but this is obviously very specific, your case will probably be different.


You can alternatively call the concatenate() function directly with a dictionary to work as the configuration (in the same form). Just pass it to the 'config' argument (the first one).


Arguments
=========


    configFile        : path to the configuration file.
    resultingFileName : the name of the file (or a relative path to it) which will have the concatenated text.
    basePath          : The paths in the configuration file are relatives, and are relative to the path where this script is executed. You can change this by proving an absolute path here.
    
    
    
Run the program
===============


    python concatenate_files.py config.txt
    
        or	
    
    python concatenate_files.py config.txt result.txt

        or
        
    python concatenate_files.py config.txt result.txt /other/base/path/here/

    
Without a configuration file
    
    
    import concatenate_files
    
        # in the same format as the file
    config = { "folder1": [ "file1.txt", "file2.txt" ] }
    
    concatenate_files.concatenate( config, "result.txt" )
        
    
    
---------------------------------------


Version 1.2:

- be able to specify the encoding for each individual file
- open the files with "utf-8" as default (and the resulting file, is written with "utf-8" as well)
- be able to call concatenate() directly with a dictionary argument
- improve print() formatting

Version 1.1:

- be able to change the base path from where the files in the configuration file will be relative to


---------------------------------------    
    

A little history
================


    I've written this program mainly to join separate javascript files into a single one (to run it in a optimizer). I used to do this manually, which was a bit annoying, so I decided to write a program to do this for me. 
    First I thought about writing it in c++, but got stomped right from the start. How would I deal with the filesystem in a portable way? Ok, there are libraries that deal with that, but just the thought of trying to link a library... (yea, I've had bad experiences :p)

    So I had been reading stuff about python, and how simple and portable it is, and decided to give it a try, and thus this program (yes, my very first python program).
    
    It was a nice experience, python is a pretty cool language... it would have been nice if I had come across it sooner but hey, better late than never :)