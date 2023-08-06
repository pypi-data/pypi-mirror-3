================================
Kanbanize.com Python API Wrapper
================================

Installation
============

To install just::

    $ easy_istall python-kanbanize

or::

    $ pip install python-kanbanize

Usage
=====
Getting started::

    from python_kanbanize.wrapper import Kanbanize

    k = Kanbanize(<your api key here>)
    k.get_all_tasks(<boardid>)

Note
====

The wrapper will reproduce all the methods available at:

http://kanbanize.com/ctrl_integration

Changelog
=========

0.2.0
-----
Switched from restkit to requests library
Made create_new_task work passing parameters into POST BODY
Renamed main module from "kanbanize" to "python-kanbanize"
Added logging messages