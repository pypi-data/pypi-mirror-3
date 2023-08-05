Introduction
============

This is a product (tested with plone >= 3.0) that allows site
managers to set quotas on containers. By default it comes with a special
content type, quota folder, derived from ATFolder, usable as a quota aware
replacement for ATFolder, and also useful as an example to make other
container types quota aware. Basically, what is needed to make a container
type quota aware is for it to implement the IQuotaAware interface.

The quota can be set globally (in quota settings in the plone control panel)
or locally in the metadata (properties) tab of any quota aware container. There
are two settings: max size and size threshold. If the contained size of a
quota aware containers goes up between max size and max size + size threshold,
the user will get a warning; if it goes up over max size + size threshold,
the user will get an error.

If the local quota is set, it will take precedence over the global quota;
additionally, you can check "enforce quota" in the global control panel, so
that any local settings that set a higher quota than the global quota will be
overridden by the global settings.

Caveat: non AT content will not be properly sized. In order to take into
account the size of non archetype content, custom IQuotaSizer adapters should
be developed for those content types. For an example, see ATQuotaSizer in
adapters.py in package root folder or dexterity subfolder.

