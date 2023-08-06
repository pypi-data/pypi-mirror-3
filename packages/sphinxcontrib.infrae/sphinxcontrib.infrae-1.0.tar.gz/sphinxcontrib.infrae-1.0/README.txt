====================
sphinxcontrib.infrae
====================

Infrae extension for Sphinx. This add:

- Color scheme for Buildout, because the Ini scheme doesn't work for
  multiple line option values.

  It defines the code type ``buildout`` for the directive ``code-block``.

- An directive ``autointerface`` to document Zope interfaces.

  Example: ``autointerface:: module.name.to.your.interface``.

  This create extra documentation if ``zope.schema`` fields are
  encountered on the interface.

- An directive ``autoevent`` to document Zope events.

  Example: ``autoevent:: module.name.to.your.event``.

