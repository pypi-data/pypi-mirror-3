
Introduction
============

Have you ever had problems deploying and configuring ``django`` project? This project
removes headaches that you used to have when quick-starting ``django`` project, configuring
environments, downloading packages and etc.

It creates ``django`` project by using one simple command, ready for running.

Solution is based on ``pip`` and ``virtualenv``, it has minimal external requirements.

Installation
============

To install this package:

::

    pip install django-pip-starter

If you already have django-pip-starter install you can use the following command to upgrade installation:

::

    pip install --upgrade django-pip-starter


Quick start
===========

The following commands creates empty, configured ``django`` project in virtual environment. Additionally it will
install ``south`` package. For development environment it additionally installs ``django-debug-toolbar``, ``ipython``, ``ipdb``

::

    django-pip-starter.py project-name
    cd project-name
    make
    make run

Where ``project-name`` is destination folder where starter should create files.

``make`` command will download and setup development virtualenv, download latest stable ``django`` version and create
sqlite3 database, load initial data.

``make run`` will run development server. It's the same as running ``project/manage.py runserver`` which would also work.

Default logins for django administration are user: ``admin`` pass: ``admin``

Documentation
=============

You can read documentation at http://readthedocs.org/docs/django-pip-starter/

History
=======

Idea for this project came from Mantas Zimickas (sirex, https://bitbucket.org/sirex/django-starter/overview).
This was based on ``zc.buildout`` solution. After some time using ``django-starter`` we had problems deploying it
and Petras Zdanavicius (petraszd) made a fork of ``django-starter`` that used only ``pip``. This was simple and elegant solution
that Marius Grigaitis (marltu) expanded and packaged it into this project.
