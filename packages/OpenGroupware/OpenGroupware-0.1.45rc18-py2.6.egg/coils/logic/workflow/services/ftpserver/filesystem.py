import ftpserver

class FSObject(object):

    def __init__(self, name, owner=9999, size=0, atime=0, ctime=0, mtime=0):
        self._name  = name
        self._owner = owner
        self._size  = size
        self._atime = atime
        self._ctime = ctime
        self._mtime = mtime

    @property
    def name(self):
        return self._name

    @property
    def owner(self):
        return self._owner

    @property
    def size(self):
        return self._size

    @property
    def ctime(self):
        return self._ctime

    @property
    def mtime(self):
        return self._mtime

    @property
    def atime(self):
        return self._atime

    @property
    def st_ino(self):
        return 100

    @property
    def st_dev(self):
        return 64770L

    @property
    def st_nlink(self):
        return 1

    @property
    def st_mode(self):
        return 770

    @property
    def st_uid(self):
        return self.owner

    @property
    def st_gid(self):
        return 10003

    @property
    def st_size(self):
        return self.size

    @property
    def st_atime(self):
        return self.atime

    @property
    def st_mtime(self):
        return self.mtime

    @property
    def st_ctime(self):
        return self.ctime


class CoilsFolder(FSObject):

    def __init__(self, name, owner=9999, size=0, atime=0, ctime=0, mtime=0):
        FSObject.__init__(self, name, owner=owner, size=size, atime=atime, ctime=ctime, mtime=mtime)
        self._children = {}

    def add_child(self,  obj):
        self._children[obj.name] = obj

    @property
    def keys(self):
        return self._children.keys()

    def get_child(self, name):
        return self._children.get(name, None)


class CoilsFile(FSObject):
    pass

ROOT = CoilsFolder('/')
ROOT.add_child(CoilsFile('file1.txt'))
ROOT.add_child(CoilsFolder('tmp'))
ROOT.get_child('tmp').add_child(CoilsFile('file2.txt'))

class CoilsFilesystem(ftpserver.AbstractedFS):

    def __init__(self, root, cmd_channel):
        print 'CoilsFilesystem ctor'
        ftpserver.AbstractedFS.__init__(self, root, cmd_channel)

    def chdir(self, path):
        cwd = self._walk_to(path)

    def _walk_to(self, path):
        cwd = ROOT
        for component in path.split('/'):
            if (isinstance(cwd, CoilsFolder)):
                if (component in cwd.keys):
                    cwd = cwd.get_child(component)
        return cwd


    def listdir(self, path):
        cwd = self._walk_to(path)
        return cwd.keys
    
    def rmdir(self, path):
        pass
    
    def remove(self, path):
        pass
    
    def rename(self, src, dst):
        pass

    def isfile(self, path):
        # TODO: Implement    
        x = self._walk_to(path)
        return (isinstance(x, CoilsFile))

    def islink(self, path):
        # TODO: Implement
        return False

    def isdir(self, path):
        # TODO: Implement
        x = self._walk_to(path)
        return (isinstance(x, CoilsFolder))

    def getsize(self, path):
        x = self._walk_to(path)
        return x.size

    def getmtime(self, path):
        x = self._walk_to(path)
        return x.mtime

    def stat(self, path):
        """Perform a stat() system call on the given path."""
        x = self._walk_to(path)
        return x
        
    def lstat(self, path):
        return self.stat(path)
        
    def lexists(self, path):
        """Return True if path refers to an existing path, including
        a broken or circular symbolic link.
        """
        x = self._walk_to(path)
        if (x is None):
            return False
        return True
       
    def get_user_by_uid(self, uid):
        return 'unknown'
        
    def get_group_by_gid(self, gid):
        return 'unknown'
