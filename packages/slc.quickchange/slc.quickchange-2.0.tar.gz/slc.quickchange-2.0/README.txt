slc.quickchange
***************

.. contents::

.. Note!
   -----

   - code repository
   - questions/comments feedback mail


- Code repository: https://svn.syslab.com/svn/syslabcom/slc.quickchange/
- Questions and comments to info (at) syslab (dot) com

Search and Replace for Plone
============================

This package adds a view @@search-replace, that lets the user perform search
& replace operations. Available options:

- Recursive: If selected, not only the current object, but all children are searched as well
- For all languages: search not only the current object, but all translations of it as well
  (LinguaPlone is required)
- Use regular expression syntax: don't perform literal string matching, but use python's regex
- Ignore case: case insensitive search (only for regex)
- Dotall: search multiple lines (only for regex)

And there are two actions:

- Search only: will list all matching documents found, nothing gets modified
- Replace: do the actual replacement

Example for regex
-----------------

Imagine you have to change URLs that point to an old domain. Plus, the site
structure has changed, so you need to re-order the elements of the path.

Old link::

   http://osha.eu.int/publications/factsheets/de/index.html

For the new link, we need to change the domain, and also put the language-folder as first element::

  http://osha.europa.eu/de/publications/factsheets/index.html

For the search term, we use::

 osha.eu.int/(.*?)/(..)/(.*)

The contents of the brackets are availabe as variables in the order of their appearance, like \1, \2 etc.

For the replacement term, we use::

 osha.europa.eu/\2/\1/\3

That means, as first element after the domain, we take the second bracket (the language folder),
then the first, and lastly the third.

If this confuses you, look at the regex documentation :-)

Requirements and Installation
=============================

This package only works and makes sense if you have LinguaPlone installed.

Add "slc.quickchange" to the eggs section of your buildout
configuration. After running buildout and restarting your instance, go to the
Site Setup -> Add-on Products, choose slc.quickchange and click "install".

An new entry named "Search and replace" will then appear in the Actions drop-down
menu of all objects.

Disclaimer
==========

Beware, you can wreak havoc with this tool if you don't know what you're doing. There is no
documentation apart from this little text and the source code...

Credits
=======

Copyright European Agency for Health and Safety at Work and Syslab.com
GmbH.

slc.quickchange development was funded by the European Agency for
Health and Safety at Work.


License
=======

slc.quickchange is licensed under the GNU Lesser Generic Public
License, version 2 or later and EUPL version 1.1 only. The complete
license texts can be found in docs/LICENSE.GPL and docs/LICENSE.EUPL.
