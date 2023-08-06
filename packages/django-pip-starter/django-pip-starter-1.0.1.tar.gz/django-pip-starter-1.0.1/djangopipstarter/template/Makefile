SHELL := /bin/bash

TESTS = sample_app1 sample_app2

ifeq (1, $(shell [ -f project/production.py ] && echo 1 ))
ENV_NAME = prod
else
ENV_NAME = devel
endif

ENV = ./$(ENV_NAME)-env
PYTHON = $(ENV)/bin/python
PIP = $(ENV)/bin/pip
EASY_INSTALL = $(ENV)/bin/easy_install
PIP_FLAGS =
STARTER_DIR = ${PWD}
BASENAME = $(shell basename $(STARTER_DIR))

MANAGE_PY = project/manage.py

.PHONY: run syncdb requirements upgrade test ctags collectstatic

ifeq ($(ENV_NAME), prod)
all: virtualenv.py $(ENV) var/static requirements collectstatic
else
all: virtualenv.py $(ENV) development.py var/static requirements syncdb
endif

virtualenv.py:
	wget https://raw.github.com/pypa/virtualenv/develop/virtualenv.py;

$(ENV): virtualenv.py
	python virtualenv.py --system-site-packages $(ENV);


development.py:
	if [ ! -f project/development.py ] ; then cp project/development.py.sample project/development.py; fi

var/static:
	mkdir -p var/htdocs/static var/htdocs/media var/mail;
	chmod 0777 var/htdocs/media;

requirements: $(ENV)
	$(EASY_INSTALL) -U pip
	$(PIP) install $(PIP_FLAGS) -r config/requirements.txt;
	if [ -f project/production.py ] && [ -f config/prod-requirements.txt ] ; then $(PIP) -r config/prod-requirements.txt; fi
	if [ ! -f project/production.py ] ; then $(PIP) install $(PIP_FLAGS) -r config/devel-requirements.txt; fi

upgrade:
	make PIP_FLAGS="--upgrade" requirements

run: $(ENV)
	$(PYTHON) $(MANAGE_PY) runserver;

syncdb: $(ENV)
	rm -rf var/development.db;
	$(PYTHON) $(MANAGE_PY) syncdb --all --noinput;
	$(PYTHON) $(MANAGE_PY) migrate --fake;
	$(PYTHON) $(MANAGE_PY) loaddata project/initial_data.json;
	$(PYTHON) $(MANAGE_PY) loaddata initial_data;
	
ctags: $(ENV)
	ctags -R `$(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"` project

test: $(ENV)
	$(PYTHON) $(MANAGE_PY) test

collectstatic: $(ENV) var/static
	$(PYTHON) $(MANAGE_PY) collectstatic --noinput

config/apache2.conf:
	cat config/apache2.conf.sample | sed 's/\__DOMAIN__/$(BASENAME)/' | sed 's/\__STARTER_DIR__/$(shell echo $(STARTER_DIR) | sed 's/\//\\\//g'; )/' > config/apache2.conf
