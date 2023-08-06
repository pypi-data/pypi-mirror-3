from distutils.core import setup

setup(
    name='naf',
    version='0.3.2',
    author='Johannes Knutsen',
    author_email='johannes@knutseninfo.no',
    url='http://github.com/knutz3n/naf',
    packages=['naf',],
    package_data={'': ['defaults.conf',]},
    scripts=['bin/naf',],
    license='Apache License, Version 2.0',
    description='Notify At Finish allows you to pass an arbitrary shell command as an argument and get a nice notification when the command finishes.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
)
