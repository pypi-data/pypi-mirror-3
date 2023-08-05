from setuptools import setup, find_packages

import os
execfile(os.path.join("pwc", "release.py"))

setup(
    name=name,
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [
        "pyparsing >= 1.5.1",
#        "filelike >= 0.3.2"
    ],
    scripts = ["ipwc.py","ipwc"],
    #zip_safe=False,
    packages=find_packages(),
    #package_data = find_package_data(where='pwc', package='pwc'),
    include_package_data=True,
    namespace_packages = ['pwc'],
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved',
        
    ],
#    test_suite = 'nose.collector',
    )
    
