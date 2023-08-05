Overview
--------

mr.igor is an extension to pyflakes that will learn where you import
things from, and then automatically fill in missing imports from the
place they are most often imported.

But how does it know?

  "It'th a knack."

Usage: igor [--print | --reap] filename

This script will record all imports from filename in Igor's database,
and then add imports at the top of the file for any names that were not
imported but were found in the database.

If the --print option is specified then the rewritten file will be
written to stdout. (This allows the use of igor as a filter for editors.)
Otherwise the file will be modified inplace.

If the --reap option is specified then imports will be added to the
database from the specified file, but nothing will be written to stdout
and the file will not be modified.

Only "from x import y" style imports are tracked and inserted.  Aliases
("from x import y as z") are not supported.

mr.igor stores its database in ~/.mr.igor.db.


Usage with TextMate
-------------------

Go to the TextMate Bundle Editor and add a new command with the following
settings:

 Save
   Current File
 Command(s)
   ::
   
    #!/bin/bash
    igor --print $TM_FILEPATH
 Input
   None
 Output
   Replace Document
 Activation
   Key Equivalent:  ⌘I
 Scope Selector
   source.python

Now you can save the current file and run it through Igor using the ⌘I
keyboard shortcut.

Usage with Vim
--------------

The following key mapping will configure ⌘I to run the current file through
Igor and then reload the current buffer::

  nmap <D-i> :!igor %<CR> <bar> :e!<CR>
