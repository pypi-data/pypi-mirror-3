from distutils.core import setup
setup(name = 'Pastebin',
      version = '1.0.2',
      py_modules = ['pastebin'],
      author = 'Morrolan',
      author_email = 'morrolan@me.com',
      url = 'http://www.morrolan.com',
      license = 'GNU General Public License (GPL)',
      description = 'Python Pastebin API interaction object.',
      long_description = """Paste to pastebin.com either with login credentials, or anonymously from code.
      
      Currently available as source only, but once unzipped, at a commandline go to the appropriate directory where you unzipped, and simply type:
      
      python setup.py install
      
      """,
      platforms = ['Windows','Unix','OS X'],
      download_url = "http://www.morrolan.com/python/Pastebin-1.0.2.tar.gz",
      keywords = ["pastebin", "paste", "xml", "pastebin API"],
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
         ],
      
      )