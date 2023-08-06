qt-all-modules = QtCore QtGui QtMultimedia QtNetwork QtOpenGL QtScript \
	QtScriptTools QtSql QtSvg QtWebKit QtXml QtXmlPatterns QtDeclarative \
	phonon QtUiTools QtHelp QtTest

ifdef QT_MODULES
qt-disabled-modules = $(filter-out $(QT_MODULES),$(1))
qt-enabled-modules = $(filter $(QT_MODULES),$(1))
else
qt-disabled-modules =
qt-enabled-modules = $(1)
endif

# hack to escape space
private space :=
private space +=
private $(space) :=
private $(space) +=
# generate a list of all modules to import.  First substitute the spaces of
# foreach away, protecting the space in the statement with _, and than
# substitute _ with space again to generate valid imoprt statements
qt-check-imports = $(subst _,$( ),$(subst $( ),;,$(foreach m,$(1),import_$(2).$(m))))
# try to import all modules
qt-check-modules = $(shell $(PYTHON) -c '$(call qt-check-imports,$(1),$(2)); print("yes")')
