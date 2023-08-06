# -*- coding: utf-8 -*-

import os
import shutil


class Store(object):
    def __init__(self, path):
        "Initialize this Store, given a path to store things in."
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)
    
    @classmethod
    def from_dict(cls, path, d):
        "Create a Store, given a dict."
        fs = cls(path)
        fs.update(d)
        return fs

    def __getitem__(self, name):
        "Get an item and raise an error if it doesn't exist."
        r = self.get(name)
        if r == None:
            raise KeyError(name)
        else:
            return r

    def get(self, name, default=None):
        """Get an item, or return the default if it doesn't exist.

        If this is expected to be a long string (something you wouldn't want to keep entirely
        in memory), you'll want to use something else.
        """
        d = self.get_path(name)
        # if it's a directory, return a Store of it.
        if os.path.isdir(d):
            return Store(d)
        # if it's a file, return its contents.
        elif os.path.isfile(d):
            with open(d, "r") as f:
                return f.read()
        else:
            return default
    
    def get_path(self, name):
        """A convenience method that returns the path to the file under this
        Store, given a key.
        """
        return os.path.join(self.path, name)

    def get_file(self, name, mode="r"):
        "Given a key, return the file object that points to its file."
        return open(self.get_path(name), mode)

    def keys(self):
        "Return an iterator of all the keys this thing has."
        for item in os.listdir(self.path):
            yield item

    def __setitem__(self, name, value):
        """Set an item and create a file or directory for it, depending what
        kind of thing it is.
        """
        d = self.get_path(name)
        # delete anything there already -- this is assignment, anyway.
        if os.path.isdir(d):
            shutil.rmtree(d)
        elif os.path.isfile(d):
            os.remove(d)
        # if it's a dictlike thing, make it into another FileStore
        if getattr(value, "keys", None) != None:
            shutil.rmtree
            Store.from_dict(d, value) 
        # otherwise, treat it like a stringlike thing.
        else:
            with open(d, "w") as f:
                f.write(value)

    def update(self, other):
        "Update this Store with another given dictionary."
        for k, v in other.iteritems():
            self[k] = v
