Introduction
============

Have you ever had problems deploying and configuring django project? This project
removes headaches that you used to have when quick-starting django project, configuring
environments, downloading packages and etc.

Solution is based on pip and virtualenv and has minimal requirements

Installation
============

To install this package:

::

    pip install django-pip-starter


Quick start
===========

To create new project use the following command:

::

    django-pip-starter.py <dest>

Where <dest> is destination folder where starter should create files.

After than you can go into <dest> directory and type

::

    make

This will download and setup development virtualenv, download latest stable django and create
sqlite3 database, load initial data.

To run development server you can use:

::

    make run

Initial logins for django are u: admin p: admin

You can also use default django commands as usual:

::

    project/manage.py runserver

and etc.

History
=======

Idea for this project came from Mantas Zimickas (sirex, https://bitbucket.org/sirex/django-starter/overview).
This was based on zc.buildout solution. After some time using django-starter we had problems deploying it
and Petras Zdanavičius (petraszd) made a fork of django-starter that used only pip. This was simple and elegant solution
that Marius Grigaitis (marltu) expanded and packaged it into this project.
