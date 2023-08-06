# determine package directory inclusion paths
BINDINGSDIR = $(dir $(lastword $(MAKEFILE_LIST)))

# build in temporary directory by default
DOWNLOADDIR = /tmp
BUILDDIR = /tmp

$(DOWNLOADDIR) :
	mkdir -p $(DOWNLOADDIR)

$(BUILDDIR) :
	mkdir -p $(BUILDDIR)

PYTHON = python
PYTHON_MAJOR := $(shell $(PYTHON) -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR := $(shell $(PYTHON) -c 'import sys; print(sys.version_info[1])')
PYTHON_VERSION := $(PYTHON_MAJOR).$(PYTHON_MINOR)
# full python executable name including the version, required for autotools
# support
PYTHON_FULL := python$(PYTHON_VERSION)
PYTHON_IMPLEMENTATION := $(shell $(PYTHON) -c \
	'import platform; print(platform.python_implementation())')
ifeq ($(PYTHON_IMPLEMENTATION),CPython)
PYTHON_CPYTHON := yes
else
PYTHON_CPYTHON :=
endif

PREFIX = $(shell $(PYTHON) -c 'import sys; sys.stdout.write(sys.prefix)')
LIBDIR = $(PREFIX)/lib

# some general environment variables
export LD_LIBRARY_PATH = $(LIBDIR)
export PKG_CONFIG_PATH = $(LIBDIR)/pkgconfig

checkmodule = $(shell $(PYTHON) -c 'import $(1); print("yes")')
checkprogram = $(shell which $(1))
checkpackage = $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) \
	pkg-config --exists $(1) && echo yes)

define download-rule-template
$$(DOWNLOADDIR)/$(2) : $$(DOWNLOADDIR)
	wget -c -O $$(DOWNLOADDIR)/$(2) $(1)
endef

# $(call download-rule,url,target)
download-rule = $(eval $(call download-rule-template,$(1),$(2)))

define builddir-rule-template
$$(BUILDDIR)/$(2) : $$(BUILDDIR) $$(DOWNLOADDIR)/$(1)
	tar xaf $$(DOWNLOADDIR)/$(1) -C $$(BUILDDIR)
endef

# $(call builddir-rule,archive,directory)
builddir-rule = $(eval $(call builddir-rule-template,$(1),$(2)))

define prepare-template
$(call download-rule,$(1),$(2))
$(call builddir-rule,$(2),$(3))
endef

# $(call prepare,url,archive,build-directory)
prepare = $(eval $(call prepare-template,$(1),$(2),$(3)))

builddir = $(BUILDDIR)/$(1)

define make
	$(MAKE) -C $(BUILDDIR)/$(1)
	$(MAKE) -C $(BUILDDIR)/$(1) install
endef

define cmake
	mkdir -p $(BUILDDIR)/$(1)/build
	cd $(BUILDDIR)/$(1)/build && cmake -DBUILD_TESTS=OFF \
		-DCMAKE_INSTALL_PREFIX=$(PREFIX) \
		-DCMAKE_BUILD_TYPE=RelWithDebInfo $(2) ..
	$(call make,$(1)/build)
endef

define autotools
# force autotools to use the full python version, otherwise headers won't be
# found due to version mismatch between local python executable from virtualenv
# and global python-config executable from system python
	cd $(BUILDDIR)/$(1) && \
		PYTHON=$(PYTHON_FULL) ./configure --prefix $(PREFIX) $(2)
	$(call make,$(1))
endef

define binding-rule-template
.PHONY: $(1)
ifndef PYTHON_CPYTHON
# do not build bindings on anything else than CPython
$(1) :
else
ifdef NO_CHECK
# force build, unconditionally depend on the build rule
$(1) : build-$(1)
else
# only depend on the corresponding build rule if the binding isn't available
$(1) : $$(if $$(have$(1)),,build-$(1))
endif
endif
endef

binding-rule = $(eval $(call binding-rule-template,$(1)))

# function to enable bindings
define enable-bindings-template
include $$(addprefix $$(BINDINGSDIR),$(addsuffix .mk,$(1)))
endef

enable-bindings = $(eval $(call enable-bindings-template,$(1)))
