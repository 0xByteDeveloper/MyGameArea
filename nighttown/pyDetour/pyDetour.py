from dbg import LogBox
import sys


def GetModuleByAttrName(searchfor):
    for module in sys.modules:
        module = sys.modules[module]
        for attr in dir(module):
            if attr == searchfor:
                return module
    return None

class DetourError(Exception):
    pass

class DetourFunction(object):
    """
    detour(tohook, hook):
        hook can take 1 or 3 arguments
        the best is to use it with 1 argument like it's described below
        alternativ u can use it so hook = func(self, args, oFunc, globalz)

    easy detour class for python.

    examples:
        - detour HP of target VID
        - block quests to open
        - instant recv of inventory (for Switchbot)
    """

    class data(object):
        """
        data-attrs:
            _self = self Object of the detoured function
            args = EVERY args, also self
            oFunc = original Function, calling call or () is easier
            globalz = globals() of the original function
            original_globals = just ignore ;D
            backuped_globals = just ignore ;D

        """
        __slots__ = ("_self", "args", "kwargs", "oFunc", "globalz", "original_globals", "backuped_globals", "detour")

        def __init__(self, **kwargs):
            if kwargs.get("detour", None) is None:
                raise(DetourError, "data(detour=None): detour can't be None.")
            self.args = ()
            self.kwargs = {}
            self._self = None
            self.oFunc = None
            self.globalz = None
            self.original_globals = None
            self.backuped_globals = None
            for key in kwargs:
                try:
                    self.__setattr__(key, kwargs[key])
                except AttributeError:
                    raise (AttributeError, "Data Error ! Unkown attribute %s" % key)

            self.args = list(self.args)

        def call(self, *args, **kwargs):
            if not args:
                args = self.args
            if args[0] != self._self:
                return self.oFunc(self._self, *args, **kwargs)
            return self.oFunc(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            self.call(*args, **kwargs)

        def WriteGlobals(self, d):
            self.original_globals = d
            self.backuped_globals = d.copy()
            for key in self.globalz:
                d[key] = self.globalz[key]

            return self.backuped_globals

        def RestoreGlobals(self):
            g = self.original_globals
            g.clear()
            for k in self.backuped_globals:
                g[k] = self.backuped_globals[k]

    def __init__(self, tohook, hook, UseTuple=0):
        if not callable(tohook):
            raise (TypeError, "tohook (arg0) is not callable")
        if not callable(hook):
            raise (TypeError, "hook (arg1) is not callable")

        self.UseTuple = UseTuple
        self.originalFunc = tohook
        self.tocall = hook
        
        self.IsInstance = 0
        try:
            self.owner = tohook.im_class
            self.IsClassFunction = 1
        except AttributeError:
            self.owner = self.GetModule(tohook)
            self.IsClassFunction = 0

        if self.IsClassFunction:
            self.manipulatedFunc = lambda *args: self.__hook(*args)
            try:
                if tohook.im_self is not None:
                    self.IsInstance = 1
                    self.Instance = tohook.im_self
            except AttributeError:
                pass

        else:
            self.IsInstance = 0
            self.manipulatedFunc = self.__hook

    def attach(self):
        setattr(self.owner, self.originalFunc.__name__, self.manipulatedFunc)

        return self

    def detach(self):
        setattr(self.owner, self.originalFunc.__name__, self.originalFunc)
        return self

    def __hook(self, *args, **kwargs):
        GLOBALS = self.GetModule(self.owner).__dict__
        ARGS = list(args)
        if self.tocall.func_code.co_argcount <= 2:
            if self.UseTuple:
                if self.IsClassFunction:
                    if self.IsInstance:
                        self.tocall((self.Instance, ARGS, self.originalFunc, GLOBALS), )
                    else:
                        self.tocall((args[0], ARGS, self.originalFunc, GLOBALS), )
                else:
                    self.tocall((None, ARGS, self.originalFunc, GLOBALS), )
            else:

                if self.IsInstance:
                    data = self.data(_self=self.Instance, args=args, kwargs=kwargs, oFunc=self.originalFunc, globalz=GLOBALS, detour=self)
                else:
                    data = self.data(_self=args[0], args=args, kwargs=kwargs, oFunc=self.originalFunc, globalz=GLOBALS, detour=self)
                self.tocall(data)
        else:
            if self.IsClassFunction:
                def genialFunc(*args2, **kwargs):
                    if not isinstance(args2[0], self.owner):
                        return self.originalFunc(args[0], *args2, **kwargs)
                    return self.originalFunc(*args2, **kwargs)

                if self.IsInstance:
                    self.tocall(self.Instance, ARGS, genialFunc, GLOBALS)
                else:
                    self.tocall(args[0], ARGS, genialFunc, GLOBALS)
            else:
                if self.tocall.func_code.co_argcount == 3:
                    self.tocall(ARGS, self.originalFunc, GLOBALS)
                elif self.tocall.func_code.co_argcount == 4:
                    self.tocall(None, ARGS, self.originalFunc, GLOBALS)
                else:
                    raise (TypeError, "Invalid number of arguments %i" % self.tocall.func_code.co_argcount)

    def GetModule(self, bla):
        try:
            return sys.modules[bla.__module__]
        except AttributeError:
            return GetModuleByAttrName(bla.__name__)


class DetourClass(object):
    __slots__ = ("functionList",)

    magicDict = {
        "__init__": "__0init__",
        "__del__": "__0del__"


    }

    def __init__(self, _victim, _src, UseTuple=0):
        funcList = []
        for victimAttr in self.GetFunctionList(_src):
            try:
                strAttr = self.magicDict.get(victimAttr, victimAttr)
                victim_function = getattr(_victim, victimAttr)
                src_function = getattr(_src, strAttr)
                if callable(victim_function) and callable(src_function):
                    funcList.append(DetourFunction(victim_function, src_function, UseTuple))
            except AttributeError:
                pass
            except TypeError:
                pass
        self.functionList = funcList

    def GetFunctionList(self, c):
        return dir(c)

    def attach(self):
        for f in self.functionList:
            f.attach()
        return self

    def detach(self):
        for f in self.functionList:
            f.detach()
        return self


class c_exampleDetourClass(object):
    """
     example for using detours for fast detouring

    """

    def __init__(self):
        pass

    def __0init__(self, data):
        """
        called if anything calls the detoured class.__init__ func
        """
        data._self.checkedSum = 4.3

    def checkValue(self, data):
        self_of_detoured = data._self  # self=data.args[0]
        data.WriteGlobals(globals())  # only read supported, write is undefined.

        data.globalz["x"] = 3
        data.args[1] = 1.3

        # calling data without any args will call data with data.args as arguments
        data()

        # scanns if the first argument is SELF, if not it will be pasted,
        # u don't need to care ;)
        data(1.3)

        # Set the first argument of data.WriteGlobals to the original
        data.RestoreGlobals()


class c_exampleDetourClass2(object):
    """
     example for using detours for silly people

    """

    def __init__(self):
        pass

    def __0init__(self, (self_of_detoured, args, oFunc, globalz)):
        """
        called if anything calls the detoured class.__init__ func
        """
        self_of_detoured.checkedSum = 4.3

    def checkValue(self, (self_of_detoured, args, oFunc, globalz)):
        globalz["x"] = 3
        args[1] = 1.3

        return oFunc(*args)


def exampleDetourFunc(data):
    self_of_detoured = data._self   # self=data.args[0]
    data.WriteGlobals(globals())   # only read supported, write is undefined.

    # two examples how you can modify it
    data.globalz["x"] = 3
    data.args[1] = 1.3

    # calling data without any args will call data with data.args as arguments
    data()
    # scanns if the first argument is SELF, if not it will be pasted,
    # u don't need to care ;)
    data(1.3)

    # Set the first argument of data.WriteGlobals to the original
    data.RestoreGlobals()

    LogBox(str(self_of_detoured))


import hackme


def exampleDetourFunction():
    d = DetourFunction(hackme.hackme.checkValue, exampleDetourFunc, UseTuple=0).attach()

    h = hackme.hackme()
    h.checkValue(1.43)
    d.detach()
    h.checkValue(1.33)


def exampleDetourClass():
    d = DetourClass(hackme.hackme, c_exampleDetourClass(), UseTuple=0).attach()

    h = hackme.hackme()
    h.checkValue(1.43)
    d.detach()


def exampleDetourClassSilly():
    d = DetourClass(hackme.hackme, c_exampleDetourClass2(), UseTuple=1).attach()

    h = hackme.hackme()
    h.checkValue(1.43)
    d.detach()
    h.checkValue(1.33)
    d.detach()


def detourSendItemUsePacket(data):
    LogBox("using item %i" % data.args[0])
    data()


def exampleDetourBuiltin():
    import net

    d = DetourFunction(net.SendItemUsePacket, detourSendItemUsePacket).attach()

#init_basic_for_detour()
#exampleDetourBuiltin()