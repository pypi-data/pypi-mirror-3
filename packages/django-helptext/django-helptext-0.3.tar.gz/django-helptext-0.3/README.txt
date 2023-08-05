======================
django-helptext README
======================

This is a simple django application that makes it possible to edit the
help text associated with django models in the admin, rather than in
source code, so that it can be edited by a site's managing producer
rather than by its programmer.

Usage
=====

1. add ``"helptext"`` to your project's ``INSTALLED_APPS``.
2. ``syncdb``.
3. somewhere in your code, register the models you are interested 
   in managing with ``helptext`` with ``helptext.register_model()``.
4. Edit the FieldHelp instances in the admin.  

In your settings file you can specify the following:

HELPTEXT_CONFIGURATION - The path to the file where you place your configured
values should you chose to save them to a file. For example,
'helptext_configuration.txt'.
HELPTEXT_USE_DATABASE - Whether or not helptext should attempt to use the
database. True or False. The default is True.

Issues
======

None so far.

License
=======

Copyright (c) 2008, Jacob Smullyan
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
