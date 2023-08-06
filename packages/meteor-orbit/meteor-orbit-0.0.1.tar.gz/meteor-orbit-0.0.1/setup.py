"""
orbit

Meteor.js Virtual Environment builder.
"""
from setuptools import setup

setup(
    name='meteor-orbit',
    version="0.0.1",
    url='https://github.com/boundsj/orbit',
    license='MIT',
    author='Jesse Bounds',
    author_email='jesse@rebounds.net',
    description="Virtual environment management for Meteor.js",
    py_modules=['orbit'],
    install_requires=[
        'docopt'
    ],
    entry_points={
        'console_scripts': ['orbit = orbit:main']
    },
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
