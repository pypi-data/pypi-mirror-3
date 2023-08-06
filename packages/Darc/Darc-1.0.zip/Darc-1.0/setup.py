__author__="Nekroze"
__date__ ="$21/02/2012 7:43:11 AM$"

from setuptools import setup

setup (
  name = 'Darc',
  version = '1.0',
  
  py_modules = ["darc"],

  author = 'Taylor "Nekroze" Lawson',
  author_email = 'nekroze@eturnilnetwork.com',
  url = 'https://github.com/Nekroze/Darc.git',
  download_url = 'http://pypi.python.org/pypi/Darc/',
  license = '',
  platforms = ['win32', 'unix'],
  classifiers = [
	  'Development Status :: 4 - Beta',
	  'Intended Audience :: Developers',
	  'Operating System :: Microsoft',
	  'Operating System :: POSIX',
	  'Programming Language :: Python :: 2 :: Only',
	  'Topic :: Games/Entertainment',
	  'Topic :: Multimedia',
	  'Topic :: Security :: Cryptography',
	  'Topic :: Software Development :: Libraries :: Python Modules',
	  'Topic :: System :: Archiving'
	  ],

  description = 'Darc is a python based archiving system for use in media projects that allows developers to contain and use their data files from .darc files that store data in a bz2 compressed and AES encrypted (optional) format.',
  long_description= """Darc allows data files for media projects (images, sounds, videos etc.) to be stored in special container files called a .darc which compresses, encrypts, hashes and then stores each file for verification and use at a later date.

There are several benefits to using Darc for your projects data files:
1: All files are hashed so the integrity of data files can be checked on the end-users machine.

2: All files are compressed with bz2, allowing a reasonable size-speed trade off bz2 can save a good deal of space which can make all the difference on limited space environments.

3: All files can be encrypted using AES methods from the pycrypto library to ensure your data is not modified by the user.

4: All files are stored in large single file archives, projects that use many small files can save space wasted by the filesystems cluster size.

5: All files can be loaded using a relative path and filename as if it were really in that path rather then in a .darc archive. This allows Darc to even check if there is a file matching that path and name outside of a .darc file and will load that instead of the one archived solong as override is enabled, allowing your project to be capable of modification by the end-user.


Using Darc is meant to be as pain free as possible and be able to be implemented with as little effort or change to your code as possible. To this end, using Darc in your project is as simple as calling the darc.get_file() method and telling it the relative path and name of the file you want to load.

The override functionality allows the end-user of your project to customize their experience by placing a file in your data directory that mirrors the path and name of the archived file so that it will be loaded instead.

For more information check out https://github.com/Nekroze/Darc.git and check out the wiki.""",
  
)