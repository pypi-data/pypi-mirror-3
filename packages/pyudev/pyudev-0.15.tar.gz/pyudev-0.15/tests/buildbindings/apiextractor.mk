pysidedownloads = http://www.pyside.org/files

apiextractor = apiextractor-0.10.10
apiextractorurl = $(pysidedownloads)/$(apiextractor).tar.bz2
haveapiextractor = $(call checkpackage,apiextractor)

$(call prepare,$(apiextractorurl),$(apiextractor).tar.bz2,$(apiextractor))

build-apiextractor : $(call builddir,$(apiextractor),$(haveapiextractor))
	$(call cmake,$(apiextractor))

$(call binding-rule,apiextractor)
