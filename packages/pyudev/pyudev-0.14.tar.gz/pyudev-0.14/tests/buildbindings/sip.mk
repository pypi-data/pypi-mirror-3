pyqtdownloads = http://www.riverbankcomputing.com/static/Downloads/
sip = sip-4.13.1
sipurl = $(pyqtdownloads)/sip4/$(sip).tar.gz
havesip = $(call checkmodule,sip)

sipconfigure = cd $(BUILDDIR)/$(1) && $(PYTHON) configure.py

$(call prepare,$(sipurl),$(sip).tar.gz,$(sip))

build-sip : $(call builddir,$(sip))
	$(call sipconfigure,$(sip)) --incdir $(PREFIX)/include/sip
	$(call make,$(sip))

$(call binding-rule,sip)
