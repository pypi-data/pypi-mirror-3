#! /usr/bin/env python
"""
Sub-Package INI of Package PLIB -- Python INI Objects
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

The idea behind these classes is to provide a platform-independent system for
handling INI options.

The PIniInterface class handles platform-specific stuff so the other classes
don't have to worry about it; they just call that class's generic methods.

The PIniFileOption, PIniFileSection, and PIniFileBase classes implement the
platform-independent option-handling system. They can be used on their own,
but it will generally be easier to use PIniFile with its easier interface.

The PIniFile class is set up to give a simple "list of lists" interface that
links the variables in your app with the correct INI file section and option,
so all you have to do is set up the list to be passed to buildini().

The buildlist parameter of buildini() is a list of tuples (one per section),
each of which also stores a list of tuples (one per option), thusly:

    buildlist = [s-tuple, ...]

    s-tuple = (sectionname, optionlist)

    optionlist = [o-tuple, ...]

    o-tuple = (optionname, optiontype, optiondefault, optionget, optionset)
    - or -  = (optionname, optiontype, optiondefault, attrname)
    - or -  = (optionname, optiontype, optiondefault)

where sectionname is the name of the INI section, optionname is the name of
the INI option, optiontype is one of the three data type flags below,
optiondefault is the default value of the option, and optionget and optionset
are functions that read and write the app variable for the option; or,
attrname is a string giving the name of the attribute on the INI file object
to be used to store the value of the option. If neither of these is present,
the default attribute name <sectionname>_<optionname> is used to store the
value.

The get and set functions, if used, should be of the following form:

    def optionget(): return optionvar
    def optionset(value): optionvar = value

Typical usage: create an instance of PIniFile; then call buildini() on it with
a "list of lists" giving the sections and options, then call readini() to load
the INI data. Call writeini() to save the INI data, typically either when the
app closes or when the user selects "Save Preferences" or suchlike.
"""

import os

from defs import *

# Only OS's currently comprehended are POSIX and NT

if os.name == "posix":
    # In Unix/Linux we use config files, default is appname.ini in
    # the user's home directory (tweak this by changing the inipath
    # and/or iniext globals before creating any class instances)
    from ConfigParser import *
    inipath = "~"
    iniext = ".ini"

elif os.name == "nt":
    # In Windows we access the Registry, so we need to map data types to
    # what the Registry understands; default root key for options is
    # HKEY_CURRENT_USER\Software\MyAppName, this can be tweaked by
    # changing the inipath global before creating any class instances
    # (the iniext global can also be changed to append something to
    # MyAppName but this is very rare)
    from _winreg import *
    regtypes = {
        INI_INTEGER: REG_DWORD,
        INI_BOOLEAN: REG_DWORD,
        INI_STRING: REG_SZ }
    inipath = "Software"
    iniext = ""


class PIniInterface(object):
    """Low-level interface with the OS mechanisms for storing preferences.
    
    The intent is to hide all OS-dependent code in this class so the
    other classes see a single consistent API.
    """
    
    falsestr = 'no'
    truestr = 'yes'
    
    def __init__(self):
        object.__init__(self)
        if os.name == "posix":
            self.parser = SafeConfigParser()
            self.inifile = None
        else:
            self.parser = None
        
        self.regkey = None
        self.openkey = None
        
        self.openiname = ''
        self.opensname = ''
    
    def ininame(self, iname):
        if os.name == "posix":
            return os.path.expanduser(os.path.join(inipath, iname + iniext))
        
        elif os.name == "nt":
            return os.path.normpath(os.path.join(inipath, iname + iniext))
        
        else:
            return iname
    
    def initialize(self, iname):
        if self.parser is not None:
            ininame = self.ininame(iname)
            if os.path.isfile(ininame):
                self.inifile = open(ininame, 'rU')
                try:
                    self.parser.readfp(self.inifile)
                finally:
                    self.inifile.close()
            self.inifile = None
        
        else:
            self.regkey = CreateKey(HKEY_CURRENT_USER, self.ininame(iname))
        
        self.openiname = iname
    
    def shutdown(self, iname, dosave = False):
        if self.parser is not None:
            if dosave:
                self.inifile = file(self.ininame(iname), "w")
                self.parser.write(self.inifile)
                self.inifile.close()
                self.inifile = None
        
        elif self.regkey is not None:
            CloseKey(self.regkey)
            self.regkey = None
        
        self.openiname = ''
    
    def opensection(self, sname):
        if self.parser is not None:
            if not self.parser.has_section(sname):
                self.parser.add_section(sname)
        
        elif self.regkey is not None:
            self.openkey = CreateKey(self.regkey, sname)
        
        self.opensname = sname
    
    def closesection(self, sname):
        if self.openkey is not None:
            CloseKey(self.openkey)
            self.openkey = None
        
        self.opensname = ''
    
    def readvalue(self, oname, vtype, adefault):
        if self.parser is not None:
            if self.parser.has_option(self.opensname, oname):
                if vtype == INI_INTEGER:
                    return self.parser.getint(self.opensname, oname)
                elif vtype == INI_BOOLEAN:
                    return self.parser.getboolean(self.opensname, oname)
                else:
                    return self.parser.get(self.opensname, oname)
            else:
                return adefault
        
        elif self.openkey is not None:
            try:
                retval = QueryValueEx(self.openkey, oname)[0]
            except WindowsError:
                retval = adefault
            if vtype == INI_INTEGER:
                return int(retval)
            elif vtype == INI_BOOLEAN:
                return bool(retval)
            else:
                return retval
        
        else:
            return None
    
    def writevalue(self, oname, vtype, avalue):
        if self.parser is not None:
            # Dunno why ConfigParser doesn't have setint, setboolean
            # corresponding to getint, getboolean above, but oh well...
            if vtype == INI_BOOLEAN:
                avalue = (self.falsestr, self.truestr)[avalue]
            else:
                avalue = str(avalue)
            self.parser.set(self.opensname, oname, avalue)
        
        elif self.openkey is not None:
            # SetValueEx wants to see a value of the appropriate type
            # even though it's going to convert it to a string anyway
            # (and even though QueryValueEx always returns a string)
            if vtype in (INI_BOOLEAN, INI_INTEGER):
                avalue = int(avalue)
            else:
                avalue = str(avalue)
            SetValueEx(self.openkey, oname, 0, regtypes[vtype], avalue)


class PIniFileOption(object):
    """OS-independent class for a single preference option.
    
    Option must have a name, data type, value, and default (used if option is
    not yet read or not present in the preferences file). Expects to be given
    a PIniFileInterface instance to read or write its value.
    """
    
    def __init__(self, oname, vtype, adefault):
        object.__init__(self)
        self.optname = oname
        self.opttype = vtype
        self.optvalue = adefault
        self.optdefault = adefault
    
    def getvalue(self):
        return self.optvalue
    
    def setvalue(self, avalue):
        self.optvalue = avalue
    
    def read(self, intf):
        self.optvalue = intf.readvalue(self.optname, self.opttype,
            self.optdefault)
    
    def write(self, intf):
        intf.writevalue(self.optname, self.opttype, self.optvalue)


class PIniFileSection(object):
    """OS-independent class for preferences section with multiple options.
    
    Section has a name and a dictionary of names (keys) vs.
    PIniFileOption instances. Expects to be given a PIniFileInterface
    instance to read or write its options.
    """
    
    # The option class can be changed by resetting this class field.
    _optclass = PIniFileOption
    
    def __init__(self, sname):
        object.__init__(self)
        self.sectname = sname
        self.options = {}
    
    def addoption(self, oname, vtype, adefault):
        self.options[oname] = self._optclass(oname, vtype, adefault)
    
    def getvalue(self, oname):
        if oname in self.options:
            return self.options[oname].getvalue()
        else:
            return None
    
    def setvalue(self, oname, avalue):
        if oname in self.options:
            self.options[oname].setvalue(avalue)
    
    def read(self, intf):
        intf.opensection(self.sectname)
        for oname in self.options.iterkeys():
            self.options[oname].read(intf)
        intf.closesection(self.sectname)
    
    def write(self, intf):
        intf.opensection(self.sectname)
        for oname in self.options.iterkeys():
            self.options[oname].write(intf)
        intf.closesection(self.sectname)


class PIniFileBase(object):
    """OS-independent base class for a preferences file.
    
    Has a name (which denotes the entire file), a dictionary of section
    names (keys) vs. PIniFileSection instances, and a PIniInterface to use
    for the actual reading/writing of preferences (the actual read/write
    mechanics walk the section/option hierarchy for simplicity of coding).
    
    Note this base class is factored out from PIniFile below to allow
    different methods of accessing the INI file structure. PIniFile uses
    the "dict of lists of tuples" method described above, but other
    methods are possible.
    """
    
    # The interface and section classes can be changed by
    # resetting these class fields.
    _intfclass = PIniInterface
    _sectclass = PIniFileSection
    
    def __init__(self, iname):
        object.__init__(self)
        self.ininame = iname
        self.sections = {}
        self.intf = self._intfclass()
    
    def addsection(self, sname):
        self.sections[sname] = self._sectclass(sname)
    
    def addoption(self, sname, oname, vtype, adefault):
        if sname not in self.sections:
            self.addsection(sname)
        self.sections[sname].addoption(oname, vtype, adefault)
    
    def getvalue(self, sname, oname):
        if sname in self.sections:
            return self.sections[sname].getvalue(oname)
        else:
            return None
    
    def setvalue(self, sname, oname, avalue):
        if sname in self.sections:
            self.sections[sname].setvalue(oname, avalue)
    
    def readvalues(self):
        self.intf.initialize(self.ininame)
        for sname in self.sections.iterkeys():
            self.sections[sname].read(self.intf)
        self.intf.shutdown(self.ininame)
    
    def writevalues(self):
        self.intf.initialize(self.ininame)
        for sname in self.sections.iterkeys():
            self.sections[sname].write(self.intf)
        self.intf.shutdown(self.ininame, True)


class PIniFile(PIniFileBase):
    """OS-independent class for an actual preferences file.
    
    Keeps a dictionary of (section name, option name) tuples vs. get/set
    functions to link the preferences to program actions. Provides
    three API methods for applications to use, as noted in the
    module documentation above: buildini, readini, and writeini.
    Also provides options parameter to constructor and _optionlist
    class field to allow automatic loading of options by either method.
    The _autoload and _autosave class fields allow control of whether
    options are loaded/saved when the class instance is
    constructed/destructed (normally the default behavior is fine
    but there may be cases where the timing of these events needs to
    be altered).
    
    FIXME: calling writeini() in __del__ causes a TypeError
    exception 'unsubscriptable object', so _autosave is currently
    not functional if True.
    """
    
    _optionlist = None
    _autoload = True
    _autosave = False
    
    def __init__(self, iname, options=None):
        PIniFileBase.__init__(self, iname)
        self.vardict = {}
        if options:
            self._optionlist = options
        if self._optionlist is not None:
            self.buildini(self._optionlist)
            if self._autoload:
                self.readini()
    
    #def __del__(self):
    #    if self._autosave:
    #        self.writeini()
    
    def buildini(self, buildlist):
        """ Called with a "list of lists" of sections and options to
        set up the preferences file """
        for sect in buildlist:
            self.addsection(sect[0])
            for opt in sect[1]:
                self.addoption(sect[0], opt[0], opt[1], opt[2])
                if len(opt) > 4:
                    entry = (opt[3], opt[4])
                elif len(opt) > 3:
                    entry = opt[3]
                else:
                    entry = "%s_%s" % (sect[0], opt[0])
                self.vardict[(sect[0], opt[0])] = entry
    
    def readini(self):
        """Read preferences from file and feed them to the program.
        """
        self.readvalues()
        for key in self.vardict.iterkeys():
            entry = self.vardict[key]
            value = self.getvalue(key[0], key[1])
            if isinstance(entry, tuple):
                entry[1](value)
            else:
                setattr(self, entry, value)
    
    def writeini(self):
        """Get preferences data from the program and write to file.
        """
        for key in self.vardict.iterkeys():
            entry = self.vardict[key]
            if isinstance(entry, tuple):
                value = entry[0]()
            else:
                value = getattr(self, entry)
            self.setvalue(key[0], key[1], value)
        self.writevalues()
