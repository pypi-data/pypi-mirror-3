#
# Jasy - Web Tooling Framework
# Copyright 2010-2012 Zynga Inc.
#

import shelve, time, os, os.path, sys, pickle, dbm, uuid

from jasy.core.Logging import *
from jasy import __version__ as version
from jasy.core.Util import getKey

hostId = uuid.getnode()

class Cache:
    """ 
    A cache class based on shelve feature of Python. Supports transient in-memory 
    storage, too. Uses memory storage for caching requests to DB as well for 
    improved performance. Uses keys for identification of entries like a normal
    hash table / dictionary.
    """
    
    __shelve = None
    
    def __init__(self, path):
        self.__transient = {}
        self.__file = os.path.join(path, "jasycache")
        
        self.open()
        
        
    def open(self):
        """Opens a cache file in the given path"""
        
        try:
            if os.path.exists(self.__file):
                self.__shelve = shelve.open(self.__file, flag="w")
            
                storedVersion = getKey(self.__shelve, "jasy-version")
                storedHost = getKey(self.__shelve, "jasy-host")
            
                if storedVersion == version and storedHost == hostId:
                    return
                    
                info("Jasy version or host has been changed. Recreating cache...")
                self.__shelve.close()
                    
            self.__shelve = shelve.open(self.__file, flag="n")
            self.__shelve["jasy-version"] = version
            self.__shelve["jasy-host"] = hostId
            
        except dbm.error as dbmerror:
            errno = None
            try:
                errno = dbmerror.errno
            except:
                pass
                
            if errno is 35:
                raise IOError("Cache file is locked by another process!")
                
            elif "type could not be determined" in str(dbmerror):
                error("Could not detect cache file format: %s" % self.__file)
                warn("Recreating cache database...")
                self.clear()
                
            elif "module is not available" in str(dbmerror):
                error("Unsupported cache file format: %s" % self.__file)
                warn("Recreating cache database...")
                self.clear()
                
            else:
                raise error
    
    
    def clear(self):
        """
        Clears the cache file through re-creation of the file
        """
        
        if self.__shelve != None:
            debug("Closing cache file %s..." % self.__file)
            
            self.__shelve.close()
            self.__shelve = None

        debug("Clearing cache file %s..." % self.__file)
        self.__shelve = shelve.open(self.__file, flag="n")
        self.__shelve["jasy-version"] = version
        
        
    def read(self, key, timestamp=None):
        """ 
        Reads the given value from cache.
        Optionally support to check wether the value was stored after the given 
        time to be valid (useful for comparing with file modification times).
        """
        
        if key in self.__transient:
            return self.__transient[key]
        
        timeKey = key + "-timestamp"
        if key in self.__shelve and timeKey in self.__shelve:
            if not timestamp or timestamp <= self.__shelve[timeKey]:
                value = self.__shelve[key]
                
                # Useful to debug serialized size. Often a performance
                # issue when data gets to big.
                # rePacked = pickle.dumps(value)
                # print("LEN: %s = %s" % (key, len(rePacked)))
                
                # Copy over value to in-memory cache
                self.__transient[key] = value
                return value
                
        return None
        
    
    def store(self, key, value, timestamp=None, transient=False):
        """
        Stores the given value.
        Default timestamp goes to the current time. Can be modified
        to the time of an other files modification date etc.
        Transient enables in-memory cache for the given value
        """
        
        self.__transient[key] = value
        if transient:
            return
        
        if not timestamp:
            timestamp = time.time()
        
        try:
            self.__shelve[key+"-timestamp"] = timestamp
            self.__shelve[key] = value
        except pickle.PicklingError as err:
            error("Failed to store enty: %s" % key)

        
    def sync(self):
        """ Syncs the internal storage database """
        
        if self.__shelve is not None:
            self.__shelve.sync() 
      
      
    def close(self):
        """ Closes the internal storage database """
        
        if self.__shelve is not None:
            self.__shelve.close()  
            self.__shelve = None

      