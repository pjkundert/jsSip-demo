SHELL		= /bin/bash

cert.pem:
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem


serve:		cert.pem lib/jssip.js
	./https.py


lib/jssip.js: ../jsSip
	cd $< && ./node_modules/gulp/node_modules/.bin/gulp dist
	cp $</dist/jssip.js $@


PY3		?= $(shell python3 --version >/dev/null 2>&1 && echo python3 || echo python)
PYTESTOPTS	= -v # --capture=no  --log-cli-level=DEBUG
PY3TEST		= $(PY3) -m pytest $(PYTESTOPTS)

GHUB_NAME	= jsSip-demo
GHUB_REPO	= git@github.com:pjkundert/$(GHUB_NAME).git

MODU_NAME	= jsSip_demo

# We'll agonizingly find the directory above this makefile's path
VENV_DIR	= $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/.. )
VENV_NAME	= $(GHUB_NAME)-$(VERSION)
VENV		= $(VENV_DIR)/$(VENV_NAME)
VENV_OPTS	= # --copies # Doesn't help; still references some system libs.

VERSION		= $(shell $(PY3) -c 'exec(open("$(MODU_NAME)/version.py").read()); print( __version__ )')

.PHONY: all help build build-check clean install install-dev FORCE

all:			help

help:
	@echo "GNUmakefile for $(MODU_NAME).  Targets:"
	@echo "  help			This help"
	@echo "  build			Build clean dist wheel and app under Python3"

build:			clean wheel

build-check:
	@$(PY3) -m build --version \
	    || ( \
		echo -e "\n\n!!! Missing Python modules; run:"; \
		echo -e "\n\n        $(PY3) -m pip install --upgrade pip setuptools wheel build\n"; \
	        false; \
	    )

clean:
	@rm -rf MANIFEST *.png build dist auto *.egg-info $(shell find . -name '__pycache__' )



.PHONY: venv venv-activate.sh venv-activate
venv:			$(VENV)
venv-activate.sh:	$(VENV)/venv-activate.sh
venv-activate:		$(VENV)/venv-activate.sh
	@echo; echo "*** Activating $< VirtualEnv for Interactive $(SHELL)"
	@bash --init-file $< -i

$(VENV):
	@echo; echo "*** Building $@ VirtualEnv..."
	@rm -rf $@ && $(PY3) -m venv $(VENV_OPTS) $@ \
	    && . $@/bin/activate \
	    && make install-dev install

# Activate a given VirtualEnv, and go to its routeros_ssh installation
# o Creates a custom venv-activate.sh script in the venv, and uses it start
#   start a sub-shell in that venv, with a CWD in the contained routeros_ssh installation
$(VENV)/venv-activate.sh: $(VENV)
	( \
	    echo "PS1='[\u@\h \W)]\\$$ '";	\
	    echo "[ ! -r ~/.git-completion.bash ] || source ~/.git-completion.bash"; \
	    echo "[ ! -r ~/.git-prompt.sh ] || source ~/.git-prompt.sh && PS1='[\u@\h \W\$$(__git_ps1 \" (%s)\")]\\$$ '"; \
	    echo "source $</bin/activate";	\
	) > $@


deps:
wheel:			deps dist/$(MODU_NAME)-$(VERSION)-py3-none-any.whl

dist/$(MODU_NAME)-$(VERSION)-py3-none-any.whl: build-check FORCE
	$(PY3) -m build
	@ls -last dist

# Install from wheel, including all optional extra dependencies (except dev)
install:		dist/$(MODU_NAME)-$(VERSION)-py3-none-any.whl FORCE
	$(PY3) -m pip install --force-reinstall $<

install-dev:
	$(PY3) -m pip install --upgrade -r requirements-tests.txt


#
# Target to allow the printing of 'make' variables, eg:
#
#     make print-CXXFLAGS
#
print-%:
	@echo $* = $($*)
	@echo $*\'s origin is $(origin $*)
echo-%:
	@echo $($*)
