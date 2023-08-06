$(call enable-bindings,generatorrunner)

shiboken = shiboken-1.1.0
shibokenurl = $(pysidedownloads)/$(shiboken).tar.bz2
haveshiboken = $(call checkpackage,shiboken)

$(call prepare,$(shibokenurl),$(shiboken).tar.bz2,$(shiboken))

build-shiboken: generatorrunner $(call builddir,$(shiboken))
	$(call cmake,$(shiboken),-DPython_ADDITIONAL_VERSIONS=$(PYTHON_VERSION))

$(call binding-rule,shiboken)
