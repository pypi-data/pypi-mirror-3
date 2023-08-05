from distutils.core import setup

setup(
	name = "pyfileseq",
	py_modules = ["fileseq"],
	version = "1.0.1",
	description = "File sequence management",
	author = "Niklas Aldergren",
	author_email = "niklas@aldergren.com",
	url = "http://github.com/aldergren/pyfileseq",
	keywords = ["sequence", "file", "list", "find", "fileseq"],
	license = "Simplified BSD License",
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"Intended Audience :: System Administrators",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	long_description = """\
This library will find file sequences in a directory (or another source) and 
return them as a list of FileSequence instances. The FileSequence class provides
useful functionality for further manipulating a sequence; slicing, generation of
filenames, string representations, etc. 
""" 
)
