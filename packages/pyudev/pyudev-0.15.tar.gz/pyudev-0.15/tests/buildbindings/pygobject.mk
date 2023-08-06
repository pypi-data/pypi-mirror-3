gnomedownloads = http://ftp.gnome.org/pub/GNOME/sources
pygobject = pygobject-2.28.6
pygobjecturl = $(gnomedownloads)/pygobject/2.28/$(pygobject).tar.bz2
havepygobject = $(and $(call checkmodule,glib),$(call checkmodule,gobject))

$(call prepare,$(pygobjecturl),$(pygobject).tar.bz2,$(pygobject))

build-pygobject: $(call builddir,$(pygobject))
# disable introspection to avoid dependency against pycairo, and to fix Python
# 3 builds
	$(call autotools,$(pygobject),--disable-introspection)

$(call binding-rule,pygobject)
