plone.app.event-ploneintegration
================================

This package integrates plone.app.event into Plone 4 releases, where
plone.app.event is not in the core. This is the case for all Plone 4 releases
at the time of this release.


Installation for Plone 4.1
--------------------------

To install plone.app.event for Plone 4.1, please use the
plone.app.event-ploneintegration package. Include it in your buildout config or
in your integration package's setup.py and apply the 
"plone.app.event Plone4 integration" profile.
The plone.app.event-ploneintegration package pulls all dependencies, which are
needed for plone.app.event.


Warning
-------

!!!
Backup! Don't do this on a Plone setups in production, only install
plone.app.event for new setups or report any upgrade issues. Upgrading is yet
not tested and no upgrade steps are provided - this is still a task to do.
Expect weired behavior regarding date/time/timezones and any other bugs.
!!!


Bug reporting
-------------

Please report bugs here: https://github.com/collective/plone.app.event

This url may change to https://github.com/plone/plone.app.event some time soon!


More information
----------------

See: https://python.org/pypi/plone.app.event
