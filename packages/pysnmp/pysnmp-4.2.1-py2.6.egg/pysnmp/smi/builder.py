# MIB modules loader
import os, sys, imp, struct, marshal, time
from pysnmp.smi import error
from pysnmp import debug

class __AbstractMibSource:
    def __init__(self, srcName):
        self._srcName = srcName
        self.__magic = imp.get_magic()
        self.__sfx = {}
        for sfx, mode, typ in imp.get_suffixes():
            if typ not in self.__sfx:
                self.__sfx[typ] = []
            self.__sfx[typ].append((sfx, len(sfx), mode))
        debug.logger & debug.flagBld and debug.logger('trying %s' % self)

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self._srcName)

    def _uniqNames(self, files):
        u = {}
        for f in files:
            if f[:9] == '__init__.':
                continue
            for typ in (imp.PY_SOURCE, imp.PY_COMPILED):
                for sfx, sfxLen, mode in self.__sfx[typ]:
                    if f[-sfxLen:] == sfx:
                        u[f[:-sfxLen]] = None
        return tuple(u.keys())

    # MibSource API follows
    
    def fullPath(self, f='', sfx=''):
        return self._srcName + (f and (os.sep + f + sfx) or '')
    
    def init(self): return self._init()
    def listdir(self): return self._listdir()
    def read(self, f):
        for pycSfx, pycSfxLen, pycMode in self.__sfx[imp.PY_COMPILED]:
            p = os.path.join(self._srcName, f) + pycSfx
            try:
                pycData = self._getData(p, pycMode)
            except IOError:
                pycTime = -1
            else:
                if self.__magic == pycData[:4]:
                    pycData = pycData[4:]
                    pycTime = struct.unpack('<L', pycData[:4])[0]
                    pycData = pycData[4:]
                    break
                else:
                    debug.logger & debug.flagBld and debug.logger(
                        'bad magic in %s' % p
                        )
                    pycTime = -1

        debug.logger & debug.flagBld and debug.logger(
            'file %s mtime %d' % (p, pycTime)
            )

        for pySfx, pySfxLen, pyMode in self.__sfx[imp.PY_SOURCE]:
            p = os.path.join(self._srcName, f) + pySfx
            try:
                pyTime = self._getTimestamp(p)
            except (IOError, OSError):
                pyTime = -1
            else:
                break

        debug.logger & debug.flagBld and debug.logger(
            'file %s mtime %d' % (p, pyTime)
            )

        if pycTime != -1 and pycTime >= pyTime:
            return marshal.loads(pycData), pycSfx
        if pyTime != -1:
            return self._getData(p, pyMode), pySfx

        raise IOError('No suitable module found')
            
class ZipMibSource(__AbstractMibSource):
    def _init(self):
        p = __import__(
            self._srcName, globals(),locals(), self._srcName.split('.')
            )
        if hasattr(p, '__loader__'):
            self.__loader = p.__loader__
            self._srcName = self._srcName.replace('.', os.sep)
            return self
        else:
            return DirMibSource(os.path.split(p.__file__)[0]).init()

    def _parseDosTime(self, dosdate, dostime):
        t = ( ((dosdate >> 9) & 0x7f) + 1980, # year
              ((dosdate >> 5) & 0x0f),  # month
              dosdate & 0x1f, # mday
              (dostime >> 11) & 0x1f, # hour
              (dostime >> 5) & 0x3f, # min
              (dostime & 0x1f) * 2, # sec
              -1, # wday
              -1, # yday
              -1  ) # dst
        return time.mktime(t)

    def _listdir(self):
        l = []
        for f in self.__loader._files.keys():
            d, f = os.path.split(f)
            if d == self._srcName:
                l.append(f)
        return tuple(self._uniqNames(l))

    def _getTimestamp(self, p):
        if p in self.__loader._files:
            return self._parseDosTime(
                self.__loader._files[p][6],
                self.__loader._files[p][5]
                )
        else:
            raise IOError('No file in ZIP: %s' % p)
        
    def _getData(self, p, mode=None): return self.__loader.get_data(p)
    
class DirMibSource(__AbstractMibSource):
    def _init(self):
        self._srcName = os.path.normpath(self._srcName)
        return self
    
    def _listdir(self):
        return self._uniqNames(os.listdir(self._srcName))

    def _getTimestamp(self, p):
        return os.stat(p)[8]
            
    def _getData(self, p, mode): return open(p, mode).read()

class MibBuilder:
    loadTexts = 0
    defaultCoreMibs = 'pysnmp.smi.mibs.instances:pysnmp.smi.mibs'
    defaultMiscMibs = 'pysnmp_mibs'
    def __init__(self):
        self.lastBuildId = self._autoName = 0
        sources = []
        for m in os.environ.get('PYSNMP_MIB_PKGS', self.defaultCoreMibs).split(':'):
            sources.append(ZipMibSource(m).init())
        # Compatibility variable
        if 'PYSNMP_MIB_DIR' in os.environ:
            os.environ['PYSNMP_MIB_DIRS'] = os.environ['PYSNMP_MIB_DIR']
        if 'PYSNMP_MIB_DIRS' in os.environ:
            for m in os.environ['PYSNMP_MIB_DIRS'].split(':'):
                sources.append(DirMibSource(m).init())
        if self.defaultMiscMibs:
            for m in self.defaultMiscMibs.split(':'):
                try:
                    sources.append(ZipMibSource(m).init())
                except ImportError:
                    pass
        self.mibSymbols = {}
        self.__modSeen = {}
        self.__modPathsSeen = {}
        self.setMibSources(*sources)
        
    # MIB modules management

    def setMibSources(self, *mibSources):
        self.__mibSources = mibSources
        debug.logger & debug.flagBld and debug.logger('setMibPath: new MIB sources %s' % (self.__mibSources,))

    def getMibSources(self): return self.__mibSources

    # Legacy/compatibility methods
    def setMibPath(self, *mibPaths):
        self.setMibSources(*[ DirMibSource(x) for x in mibPaths ])

    def getMibPath(self):
        l = []
        for mibSource in self.getMibSources():
            if isinstance(mibSource, DirMibSource):
                l.append(mibSource.fullPath())
        return tuple(l)
        
    def loadModules(self, *modNames):
        # Build a list of available modules
        if not modNames:
            modNames = {}
            for mibSource in self.__mibSources:
                for modName in mibSource.listdir():
                    modNames[modName] = None
            modNames = list(modNames.keys())
        if not modNames:
            raise error.SmiError(
                'No MIB module to load at %s' % (self,)
                )
        
        for modName in modNames:
            for mibSource in self.__mibSources:
                debug.logger & debug.flagBld and debug.logger('loadModules: trying %s at %s' % (modName, mibSource))
                try:
                    modData, sfx = mibSource.read(modName)
                except IOError:
                    debug.logger & debug.flagBld and debug.logger('loadModules: read %s from %s failed: %s' % (modName, mibSource, sys.exc_info()[1]))
                    continue

                modPath = mibSource.fullPath(modName, sfx)
                
                if modPath in self.__modPathsSeen:
                    debug.logger & debug.flagBld and debug.logger('loadModules: seen %s' % modPath)
                    break
                else:
                    self.__modPathsSeen[modPath] = 1

                debug.logger & debug.flagBld and debug.logger('loadModules: evaluating %s' % modPath)
                
                g = { 'mibBuilder': self }

                try:
                    exec(modData, g)
                except Exception:
                    del self.__modPathsSeen[modPath]
                    raise error.SmiError(
                        'MIB module \"%s\" load error: %s' % (modPath, sys.exc_info()[1])
                        )

                self.__modSeen[modName] = modPath

                debug.logger & debug.flagBld and debug.logger('loadModules: loaded %s' % modPath)

                break

            if modName not in self.__modSeen:
                raise error.SmiError(
                    'MIB file \"%s\" not found in search path' % (modName and modName + ".py[co]")
                    )

        return self
                
    def unloadModules(self, *modNames):
        if not modNames:
            modNames = list(self.mibSymbols.keys())
        for modName in modNames:
            if modName not in self.mibSymbols:
                raise error.SmiError(
                    'No module %s at %s' % (modName, self)
                    )
            self.unexportSymbols(modName)
            del self.__modPathsSeen[self.__modSeen[modName]]
            del self.__modSeen[modName]
            
            debug.logger & debug.flagBld and debug.logger('unloadModules: ' % (modName))
            
        return self

    def importSymbols(self, modName, *symNames):
        if not modName:
            raise error.SmiError(
                'importSymbols: empty MIB module name'
            )
        r = ()
        for symName in symNames:
            if modName not in self.mibSymbols:
                self.loadModules(modName)
            if modName not in self.mibSymbols:
                raise error.SmiError(
                    'No module %s loaded at %s' % (modName, self)
                    )
            if symName not in self.mibSymbols[modName]:
                raise error.SmiError(
                    'No symbol %s::%s at %s' % (modName, symName, self)
                    )
            r = r + (self.mibSymbols[modName][symName],)
        return r

    def exportSymbols(self, modName, *anonymousSyms, **namedSyms):
        if modName not in self.mibSymbols:
            self.mibSymbols[modName] = {}
        mibSymbols = self.mibSymbols[modName]
        
        for symObj in anonymousSyms:
            debug.logger & debug.flagBld and debug.logger('exportSymbols: anonymous symbol %s::__pysnmp_%ld'  % (modName, self._autoName))
            mibSymbols['__pysnmp_%ld' % self._autoName] = symObj
            self._autoName = self._autoName + 1
        for symName, symObj in namedSyms.items():
            if symName in mibSymbols:
                raise error.SmiError(
                    'Symbol %s already exported at %s' % (symName, modName)
                    )

            # XXX needs improvement
            try:
                symName = symObj.label or symName # class
            except AttributeError:
                pass
            try:
                symName = symObj.getLabel() or symName # class instance
            except (AttributeError, TypeError):
                pass
            
            mibSymbols[symName] = symObj
            
            debug.logger & debug.flagBld and debug.logger('exportSymbols: symbol %s::%s' % (modName, symName))
            
        self.lastBuildId = self.lastBuildId + 1

    def unexportSymbols(self, modName, *symNames):
        if modName not in self.mibSymbols:
            raise error.SmiError(
                'No module %s at %s' % (modName, self)
                )
        mibSymbols = self.mibSymbols[modName]
        if not symNames:
            symNames = list(mibSymbols.keys())
        for symName in symNames:
            if symName not in mibSymbols:
                raise error.SmiError(
                    'No symbol %s::%s at %s' % (modName, symName, self)
                    )
            del mibSymbols[symName]
            
            debug.logger & debug.flagBld and debug.logger('unexportSymbols: symbol %s::%s' % (modName, symName))
            
        if not self.mibSymbols[modName]:
            del self.mibSymbols[modName]

        self.lastBuildId = self.lastBuildId + 1
            
