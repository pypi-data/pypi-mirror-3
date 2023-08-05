==============================================
Tacot (Generate easily your statics web sites)
==============================================

Installation
============

::

    $ pip install tacot


Quick start
===========

Download `demo1.tar.gz <http://packages.python.org/tacot/en/_static/demo1.tar.gz>`_ archive to ``demos`` folder.

::

    $ mkdir demos; cd demos
    $ curl -o demo1.tar.gz http://packages.python.org/tacot/en/_static/demo1.tar.gz
    $ tar xfz demo1.tar.gz
    $ cd demo1


Web site generation :

::

    $ tacot
    Please wait, tacot process 11 files :

    jupiter.html
    pluto.html
    neptune.html
    styles.css
    index.html
    saturn.html
    uranus.html
    earth.html
    mars.html
    venus.html
    mercury.html


The site is generated in ``_build`` folder :

::

    $ ls _build/ -1
    earth.html
    index.html
    jupiter.html
    mars.html
    mercury.html
    neptune.html
    pluto.html
    saturn.html
    styles.css
    uranus.html
    venus.html

You can see the web site with your browser :

::

    $ firefox _build

See `documentation <http://packages.python.org/tacot/>`_ for more informations...
