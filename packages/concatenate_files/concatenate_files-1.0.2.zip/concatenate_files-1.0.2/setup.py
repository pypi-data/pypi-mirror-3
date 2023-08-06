from distutils.core import setup

setup(

    name = 'concatenate_files',
    version = '1.0.2',
    author = "Pedro Ferreira",
    author_email = "darkiiiiii@gmail.com",
    url = "http://www.bitbucket.org/drk4/concatenate_files/",
    description = 'Concatenates the content of files',
    long_description = "You need to write a configuration file, which tells which files to concatenate. Go to the url for more information.",
    classifiers = [ 
                    "Programming Language :: Python :: 3",
                    "Development Status :: 5 - Production/Stable",
                    "Environment :: Console", 
                    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                    "Operating System :: OS Independent",
                    "Topic :: Utilities",
                    "Intended Audience :: Developers", 
                    "Natural Language :: English"
                    ],
    py_modules = ["concatenate_files"] 
     )