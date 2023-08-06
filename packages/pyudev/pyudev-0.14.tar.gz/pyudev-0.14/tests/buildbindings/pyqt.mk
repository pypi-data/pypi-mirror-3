$(call enable-bindings,sip qt-base)

pyqt = PyQt-x11-gpl-4.9
pyqtarchive = $(pyqt).tar.gz
pyqturl = $(pyqtdownloads)/PyQt4/$(pyqt).tar.gz
# PyQt doesn't wrap QtUiTools module from Qt
pyqt-all-modules = $(filter-out QtUiTools,$(qt-all-modules))
pyqt-enabled-modules = $(call qt-enabled-modules,$(pyqt-all-modules))
havepyqt := $(call qt-check-modules,$(pyqt-enabled-modules),PyQt4)

QMAKE := $(or $(call checkprogram,qmake),$(call checkprogram,qmake-qt4))

$(call prepare,$(pyqturl),$(pyqt).tar.gz,$(pyqt))

build-pyqt : sip $(call builddir,$(pyqt))
	$(call sipconfigure,$(pyqt)) --confirm-license --concatenate \
		--no-designer-plugin --no-sip-files --no-qsci-api \
		--qmake $(QMAKE) \
		$(foreach mod,$(pyqt-enabled-modules),--enable $(mod))
	$(call make,$(pyqt))
	$(call mk-stamp,pyqt)

$(call binding-rule,pyqt)
