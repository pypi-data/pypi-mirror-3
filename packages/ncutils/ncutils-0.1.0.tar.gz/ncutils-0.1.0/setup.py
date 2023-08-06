"""
ncutils
----------

ncutils is a python module for niconico douga. You can install ncutils by
pip/easy_install. Have fun!

Documents and other resources are available at
`github <https://github.com/sakamotomsh/ncutils>`_ . 
"""

from distutils.core import setup
setup(
    name='ncutils',
    version='0.1.0',
    url='https://github.com/sakamotomsh/ncutils',
    license='BSD',
    author='sakamotomsh',
    author_email='sakamotomsh@lolloo.net',
    description='niconico douga module',
    long_description=__doc__,
    packages=['ncutils', ],

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
