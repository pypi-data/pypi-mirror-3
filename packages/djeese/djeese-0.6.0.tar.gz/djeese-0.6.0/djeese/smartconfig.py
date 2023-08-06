# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from djeese.printer import Printer
from StringIO import StringIO


class Section(object):
    """
    Wrapper around ConfigParser to make a nicer interface
    """
    def __init__(self, parser, section):
        self.parser = parser
        self.section = section
    
    def items(self):
        """
        Return the items in this section as list of tuples
        """
        return self.parser.items(self.section)
        
    def as_dict(self):
        """
        Return the items in this section as dictionary
        """
        return dict(self.items())
    
    def get(self, item, default=None):
        """
        Get the item in this section
        """
        if item in self:
            return self[item]
        return default
        
    def getlist(self, item, default=None):
        """
        Get the item in this section as list
        """
        if item in self:
            return [line.strip() for line in self[item].splitlines() if line.strip()]
        if default:
            return default
        return []
    
    def getint(self, item, default=0):
        """
        Get the item in this section as integer
        """
        if item in self:
            return self.parser.getint(self.section, item)
        return default
    
    def getfloat(self, item, default=0.0):
        """
        Get the item in this section as float
        """
        if item in self:
            return self.parser.getfloat(self.section, item)
        return default
    
    def getboolean(self, item, default=False):
        """
        Get the item in this section as boolean
        """
        if item in self:
            return self.parser.getboolean(self.section, item)
        return default
    
    def __contains__(self, item):
        """
        Check if this section contains this item
        """
        return self.parser.has_option(self.section, item)
        
    def __getitem__(self, item):
        """
        Same as self.get, but without the ability to specify a default
        """
        return self.parser.get(self.section, item)
    
    def __setitem__(self, item, value):
        """
        Set an item in this section
        """
        self.parser.set(self.section, item, value)
        
    def __delitem__(self, item):
        """
        Remove an item from this section
        """
        self.parser.remove_option(self.section, item)

class SmartConfig(object):
    """
    Wrapper around SafeConfigParser to provide a nicer API
    """
    def __init__(self, verbosity=1, printer=None):
        self.parser = SafeConfigParser()
        self.printer = printer or Printer(verbosity)
        
    def __getitem__(self, item):
        """
        Get a section (Section instance) or create it if it doesn't exist.
        """
        if item not in self:
            self.parser.add_section(item)
        return Section(self.parser, item)
    
    def __contains__(self, item):
        """
        Check if this config has a section
        """
        return self.parser.has_section(item)
    
    def read_string(self, data):
        """
        Read the configuration from a string
        """
        sio = StringIO(data)
        sio.seek(0)
        self.parser.readfp(sio)
        
    def readfp(self, fp):
        self.parser.readfp(fp)
    
    def read(self, filepath):
        """
        Read the configuration from a filepath
        """
        self.parser.read(filepath)
    
    def write(self, filepath):
        """
        Write the configuration to a filepath
        """
        if not self.validate():
            return False
        with open(filepath, 'w') as fobj:
            self.parser.write(fobj)
        return True
    
    def write_file(self, fobj):
        if not self.validate():
            return False
        self.parser.write(fobj)
        return True
