Why?!
=====

Daily programming tasks, such as code compilation and running automated tests, often consumes a lot of time even on rather small projects.

While alt-tabbing away from the command you just started, this simple tool will help you to get back on your development track as soon as possible.

Saving you minutes every day :)


Installation
============

On Linux with pip::

    sudo pip install naf

On Mac OS X with pip (with Growl installed)::

    sudo pip install growl-py
    sudo pip install naf

On Windows:
In theory, ``naf`` should work on Windows wth Growl for Windows (http://www.growlforwindows.com/) and growl-py installed.
I would highly appreciate any feedback on this.

From source::

    git clone git://github.com/knutz3n/naf.git
    cd naf
    sudo python setup.py install


Usage
=====

::

    naf mvn clean install

This will run ``mvn clean install`` and notify you when the command has exited with the exit code it returned.


Customization
=============

Customizations can be made by creating a file ``~/.naf.conf``.

Default configuration::

    [Success]
    description = finished successfully
     in %s
    timeout     = -1
    show        = true

    [Failed]
    description = failed with return code %s
     in %s
    timeout     = -1
    show        = true

    [Aborted]
    description = was aborted after
     %s
    timeout     = -1
    show        = true
