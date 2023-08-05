from setuptools import setup, find_packages

import os
execfile("release.py")

setup(
    name=name,
    version=version,
    
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [
        "pyparsing >= 1.5.1",
        "PowerConsole",
        "fdb>=0.7.0"
    ],
    #zip_safe=False,
    py_modules = ['fbcore'],
    packages=find_packages(),
    #package_data = find_package_data(where='pwc', package='pwc'),
    namespace_packages = ['pwc'],
    entry_points = {
        'powerconsole.package': [   
            'firebird = pwc.fbcmd:packageFirebird',
        ],
    },
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        
    ],
#    test_suite = 'nose.collector',
    )
    
