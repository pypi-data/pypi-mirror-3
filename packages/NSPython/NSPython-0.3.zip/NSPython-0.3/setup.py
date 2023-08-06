from distutils.core import setup

setup(
    name = 'NSPython',
    description = 'Cocoa for Python',
    version = '0.3',
    packages = ['nspython'],
    requires = ['cffi'],
    author = 'Juraj Sukop',
    author_email = 'juraj.sukop@gmail.com',
    url = 'http://bitbucket.org/sukop/nspython',
    license = 'MIT',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X :: Cocoa',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces'])