# -*- Makefile -*-

-include $(buildTop)/share/dws/prefix.mk

srcDir        ?= .
installTop    ?= $(VIRTUAL_ENV)
binDir        ?= $(installTop)/bin
CONFIG_DIR    ?= $(srcDir)
# XXX CONFIG_DIR should really be $(installTop)/etc/testsite
LOCALSTATEDIR ?= $(installTop)/var

installDirs   ?= install -d
installFiles  ?= install -p -m 644
NPM           ?= npm
PYTHON        := TESTSITE_SETTINGS_LOCATION=$(CONFIG_DIR) $(binDir)/python

RUN_DIR       ?= $(srcDir)
DB_NAME       ?= $(RUN_DIR)/db.sqlite

MANAGE        := TESTSITE_SETTINGS_LOCATION=$(CONFIG_DIR) RUN_DIR=$(RUN_DIR) $(PYTHON) manage.py

# Django 1.7,1.8 sync tables without migrations by default while Django 1.9
# requires a --run-syncdb argument.
# Implementation Note: We have to wait for the config files to be installed
# before running the manage.py command (else missing SECRECT_KEY).
RUNSYNCDB     = $(if $(findstring --run-syncdb,$(shell cd $(srcDir) && $(PYTHON) manage.py migrate --help 2>/dev/null)),--run-syncdb,)

install::
	cd $(srcDir) && $(PIP) install .


install-conf:: $(DESTDIR)$(CONFIG_DIR)/credentials \
                $(DESTDIR)$(CONFIG_DIR)/gunicorn.conf
	install -d $(DESTDIR)$(LOCALSTATEDIR)/db
	install -d $(DESTDIR)$(LOCALSTATEDIR)/run
	install -d $(DESTDIR)$(LOCALSTATEDIR)/log/gunicorn

build-assets: vendor-assets-prerequisites


clean:: clean-dbs
	[ ! -f $(srcDir)/package-lock.json ] || rm $(srcDir)/package-lock.json
	find $(srcDir) -name '__pycache__' -exec rm -rf {} +
	find $(srcDir) -name '*~' -exec rm -rf {} +

clean-dbs:
	[ ! -f $(DB_NAME) ] || rm $(DB_NAME)
	[ ! -f $(srcDir)/testsite-app.log ] || rm $(srcDir)/testsite-app.log


vendor-assets-prerequisites: $(srcDir)/testsite/package.json


$(DESTDIR)$(CONFIG_DIR)/credentials: $(srcDir)/testsite/etc/credentials
	install -d $(dir $@)
	[ -f $@ ] || \
		sed -e "s,\%(SECRET_KEY)s,`$(PYTHON) -c 'import sys ; from random import choice ; sys.stdout.write("".join([choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^*-_=+") for i in range(50)]))'`," $< > $@


$(DESTDIR)$(CONFIG_DIR)/gunicorn.conf: $(srcDir)/testsite/etc/gunicorn.conf
	install -d $(dir $@)
	[ -f $@ ] || sed \
		-e 's,%(LOCALSTATEDIR)s,$(LOCALSTATEDIR),' $< > $@


initdb: clean-dbs install-conf
	cd $(srcDir) && $(MANAGE) migrate $(RUNSYNCDB) --noinput
	cd $(srcDir) && $(MANAGE) loaddata testsite/fixtures/test_data.json

doc: install-conf
	$(installDirs) docs
	cd $(srcDir) && sphinx-build -b html ./docs $(PWD)/docs

vendor-assets-prerequisites: $(installTop)/.npm/djaodjin-rules-packages

$(installTop)/.npm/djaodjin-rules-packages: $(srcDir)/testsite/package.json
	$(installFiles) $^ $(installTop)
	$(NPM) install --loglevel verbose --cache $(installTop)/.npm --tmp $(installTop)/tmp --prefix $(installTop)
	$(installDirs) -d $(srcDir)/testsite/static/vendor
	$(installFiles) $(installTop)/node_modules/jquery/dist/jquery.js $(srcDir)/testsite/static/vendor
	$(installFiles) $(installTop)/node_modules/moment/moment.js $(srcDir)/testsite/static/vendor
	$(installFiles) $(installTop)/node_modules/moment-timezone/builds/moment-timezone-with-data.js $(srcDir)/testsite/static/vendor
	$(installFiles) $(installTop)/node_modules/vue/dist/vue.js $(srcDir)/testsite/static/vendor
	touch $@
