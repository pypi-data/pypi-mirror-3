$(call enable-bindings,apiextractor)

generatorrunner = generatorrunner-0.6.16
generatorrunnerurl = $(pysidedownloads)/$(generatorrunner).tar.bz2
havegeneratorrunner = $(call checkpackage,generatorrunner)

$(call prepare,$(generatorrunnerurl),$(generatorrunner).tar.bz2,$(generatorrunner))

build-generatorrunner: apiextractor $(call builddir,$(generatorrunner))
	$(call cmake,$(generatorrunner))

$(call binding-rule,generatorrunner)
