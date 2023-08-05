Changelog
=========

.. Use the following to start a new version entry:

   |version| (unreleased)
   ----------------------

   - change message [author]

1.1 (2011-10-25)
----------------

- Monkeypatching zc.buildout.easy_install.Installer's install method in order
  to post-process the distributions. Otherwise, we run into an order of
  operations problem (e.g. obtaining eggs before some eggs have been marked
  for development). [pumazi]


1.0 (2011-10-21)
----------------

- Initial release. [pumazi]
