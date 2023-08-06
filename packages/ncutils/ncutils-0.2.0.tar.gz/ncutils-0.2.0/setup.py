"""
ncutils
----------

ncutils is a python module for niconico douga. You can install ncutils by
pip/easy_install. Have fun!

Documents and other resources are available at
`github <https://github.com/sakamotomsh/ncutils>`_ . 

Releases
~~~~~~~~~~
- 0.2.0 (2012-09-09)
    - Windows support 
    - Added some scripts

- 0.1.0 (2012-08-25)
    - Initial Release
"""

from distutils.core import setup
setup(
    name='ncutils',
    version='0.2.0',
    url='https://github.com/sakamotomsh/ncutils',
    license='BSD',
    author='sakamotomsh',
    author_email='sakamotomsh@lolloo.net',
    description='niconico douga module',
    long_description=__doc__,
    packages=['ncutils', ],
    scripts=[
        'scripts/nc_download',
        'scripts/nc_download_mylist',
        'scripts/nc_queue_consume',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Utilities'
    ],
)
