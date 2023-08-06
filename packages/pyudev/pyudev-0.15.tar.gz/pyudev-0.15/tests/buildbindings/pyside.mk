$(call enable-bindings,shiboken qt-base)

pyside = pyside-qt4.7+1.1.0
pysideurl = $(pysidedownloads)/$(pyside).tar.bz2
pyside-disabled-modules = $(call qt-disabled-modules,$(qt-all-modules))
pyside-enabled-modules = $(call qt-enabled-modules,$(qt-all-modules))
havepyside := $(call qt-check-modules,$(pyside-enabled-modules),PySide)

$(call prepare,$(pysideurl),$(pyside).tar.bz2,$(pyside))

ifeq ($(PYTHON_MAJOR),2)
build-pyside: shiboken $(call builddir,$(pyside))
	$(call cmake,$(pyside), \
		-DPython_ADDITIONAL_VERSIONS=$(PYTHON_VERSION) \
		$(foreach mod,$(pyside-disabled-modules),-DDISABLE_$(mod)=ON) \
		$(foreach mod,$(pyside-enabled-modules),-DDISABLE_$(mod)=OFF))
else
build-pyside:
endif

$(call binding-rule,pyside)
