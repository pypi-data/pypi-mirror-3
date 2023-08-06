#!/usr/bin/env python
"""
Sub-Package CLASSES of Package PLIB -- Python Class Objects
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains a variety of useful classes. We
use the ModuleProxy class in this sub-package to have all
of the classes appear as attributes of the sub-package,
while only actually importing their modules when used. This
means that you can write:

    from plib.classes import AClass

instead of having to write:

    from plib.classes.AClass import AClass

as you would under the normal Python import mechanics; but
under the hood, each class lives in its own module that is
only imported if you actually use it (which would not be
the case if they were all statically imported here).

Note that, although this seems like a lot of black magic for
what is actually not all that much gain (none of the modules
in this sub-package use *that* much memory), the real reason
for doing it is to improve maintainability of the code. With
normal static importing in Python, every time a class module
was added to this sub-package, I would have to manually add
an import for it here; not only is that repetitive work, but
it adds the potential for error because now the import name
and the module file name must be kept in sync. With the
ModuleProxy class, once I add the module file to the
directory for this sub-package, everything else happens
automatically--less work and no error. And while that may
not be all that much gain for this simple sub-package, more
elaborate sub-package layouts (such as the one in the
PLIB.GUI sub-package) can make the gain much greater.
"""

from plib.utils import ModuleProxy

# We define these here because after the ModuleProxy they
# wouldn't be directly importable from StateMachine.py

class StateMachineException(Exception): pass

class InvalidState(StateMachineException): pass
class InvalidInput(StateMachineException): pass
class RecursiveTransition(StateMachineException): pass

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals())

# Now clean up our namespace
del ModuleProxy
