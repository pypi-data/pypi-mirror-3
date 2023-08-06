
# NSPython - Cocoa for Python
# 
# http://bitbucket.org/sukop/nspython
# 
# Copyright (c) 2012 Juraj Sukop
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import cffi as _cffi
import re as _re

__version__ = '0.3'

_ffi = _cffi.FFI()
_ffi.cdef('''
    
    typedef long NSInteger;
    typedef unsigned long NSUInteger;
    
    typedef struct _NSRange {
        NSUInteger location;
        NSUInteger length;
    } NSRange;
    
    typedef double CGFloat;
    struct CGPoint {
        CGFloat x;
        CGFloat y;
    };
    typedef struct CGPoint CGPoint;
    struct CGSize {
        CGFloat width;
        CGFloat height;
    };
    typedef struct CGSize CGSize;
    struct CGRect {
        CGPoint origin;
        CGSize size;
    };
    typedef struct CGRect CGRect;
    
    typedef CGPoint NSPoint;
    typedef CGSize NSSize;
    typedef CGRect NSRect;
    
    typedef struct objc_class *Class;
    typedef struct objc_object {
        Class isa;
    } *id;
    
    typedef struct objc_selector *SEL;
    typedef id (*IMP)(id, SEL, ...);
    typedef signed char BOOL;
    
    typedef struct objc_method *Method;
    
    const char * class_getName(Class cls);
    Class class_getSuperclass(Class cls);
    BOOL class_addMethod(Class cls, SEL name, IMP imp, const char *types);
    Method class_getInstanceMethod(Class aClass, SEL aSelector);
    Method class_getClassMethod(Class aClass, SEL aSelector);
    
    Class objc_allocateClassPair(Class superclass, const char *name, size_t extraBytes);
    void objc_registerClassPair(Class cls);
    
    const char *object_getClassName(id obj);
    id objc_getClass(const char *name);
    
    typedef uintptr_t objc_AssociationPolicy;
    void objc_setAssociatedObject(id object, void *key, id value, objc_AssociationPolicy policy);
    
    Class object_getClass(id object);
    
    IMP method_getImplementation(Method method);
    const char * method_getTypeEncoding(Method method);
    SEL sel_registerName(const char *str);
    
''')

load = _ffi.dlopen

_objc = load('objc')
_nil = _ffi.NULL


_OBJC_ASSOCIATION_RETAIN = 01401
sel = _objc.sel_registerName

NSMakeRange = lambda loc, len: _ffi.new('NSRange *', (loc, len))[0]
NSMakeRangePointer = lambda loc, len: _ffi.new('NSRange *', (loc, len))
NSMaxRange = lambda rng: rng.location + rng.length

NSMakePoint = lambda x, y: _ffi.new('NSPoint *', (x, y))[0]
NSMakeSize = lambda w, h: _ffi.new('NSSize *', (w, h))[0]
NSMakeRect = lambda x, y, w, h: _ffi.new('NSRect *', ((x, y), (w, h)))[0]

NSZeroPoint = NSMakePoint(0, 0)
NSZeroSize = NSMakeSize(0, 0)
NSZeroRect = NSMakeRect(0, 0, 0, 0)


_type_decodings = {
    'c': 'BOOL',
    '^c': 'BOOL *',
    'i': 'int',
    's': 'short',
    'l': 'long',
    'q': 'long long',
    '^q': 'long long *',
    'C': 'unsigned char',
    'I': 'unsigned int',
    'S': 'unsigned short',
    '^S': 'unsigned short *',
    'r^S': 'const unsigned short *',
    'L': 'unsigned long',
    'Q': 'unsigned long long',
    '^Q': 'unsigned long long *',
    'f': 'float',
    'd': 'double',
    '^d': 'double *',
    'v': 'void',
    '^v': 'void *',
    'r^v': 'const void *',
    '*': 'char *',
    '^*': 'char **',
    'r*': 'const char *',
    '@': 'id',
    '^@': 'id *',
    '#': 'Class',
    ':': 'SEL',
    '{_NSRange=QQ}': 'NSRange',
    '^{_NSRange=QQ}': 'NSRange *',
    '{CGPoint=dd}': 'CGPoint',
    '{CGSize=dd}': 'CGSize',
    '{CGRect={CGPoint=dd}{CGSize=dd}}': 'CGRect'}

_type_encodings = dict((v, k) for k, v in _type_decodings.items())

_type_decodings.update({
    'B': 'BOOL',
    'Vv': 'void'})

class types(object):
    
    @staticmethod
    def decode(string):
        return [_type_decodings[s] for s in _re.split(r'\d+', string)[:-1]]
        
    @staticmethod
    def signature(ret, args, variadic=False):
        return ('%s (*)(%s, ...)' if variadic else '%s (*)(%s)') % (
            ret, ', '.join(args))

    @staticmethod
    def encode(ret, args):
        codes, offset = [], 0
        for a in args:
            codes.append('%s%d' % (_type_encodings[a], offset))
            offset += max(4, _ffi.sizeof(a))
        return '%s%d' % (_type_encodings[ret], offset) + ''.join(codes)
    
    def __init__(self, ret, *args):
        t = {
            'NSInteger': 'long',
            'NSUInteger': 'unsigned long',
            'unichar *': 'unsigned short *',
            'const unichar *': 'const unsigned short *',
            'NSRangePointer': 'NSRange *',
            'NSPoint': 'CGPoint',
            'NSSize': 'CGSize',
            'NSRect': 'CGRect'}
        self.ret = t.get(ret, ret)
        self.args = ('id', 'SEL') + tuple(t.get(a, a) for a in args)
    
    def __call__(self, f):
        return _Callback(f, self.ret, self.args)

def IBAction(f):
    return types('void', 'id')(f)


_variadic_methods = set([
    'arrayWithObjects_', # Foundation
    'initWithObjects_',
    'handleFailureInFunction_file_lineNumber_description_',
    'handleFailureInMethod_object_file_lineNumber_description_',
    'decodeValuesOfObjCTypes_',
    'encodeValuesOfObjCTypes_',
    'dictionaryWithObjectsAndKeys_',
    'initWithObjectsAndKeys_',
    'raise_format_',
    'appendFormat_',
    'predicateWithFormat_',
    'initWithObjects_',
    'setWithObjects_',
    'initWithFormat_',
    'initWithFormat_locale_',
    'localizedStringWithFormat_',
    'stringByAppendingFormat_',
    'stringWithFormat_',
    'alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_', # AppKit
    'initWithColorsAndLocations_'])

class _Method(object):
    
    def __init__(self, classname, methodname, is_instance_method, receiver=None):
        c = _ffi.cast('Class', _objc.objc_getClass(classname))
        self.selector = sel(methodname.replace('_', ':'))
        if is_instance_method:
            m = _objc.class_getInstanceMethod(c, self.selector)
        else:
            m = _objc.class_getClassMethod(c, self.selector)
        self.receiver = receiver
        assert m, '"%s" has no "%s" method.' % (classname, methodname)
        i = _objc.method_getImplementation(m)
        t = types.decode(_ffi.string(_objc.method_getTypeEncoding(m)))
        d = types.signature(t[0], t[1:], methodname in _variadic_methods)
        self.imp = _ffi.cast(d, i)
        self.ret = t[0]
    
    def __call__(self, *args):
        args = [getattr(a, 'instance', _nil if a is None else a) for a in args]
        r = self.imp(self.receiver, self.selector, *args)
        if self.ret == 'id':
            if not r:
                return None
            if r not in _instances:
                n = _objc.object_getClassName(r)
                _instances[r] = _classes[_ffi.string(n)](r)
            return _instances[r]
        elif self.ret == 'Class':
            n = _objc.class_getName(r)
            return _classes[_ffi.string(n)]
        return r
    
    def basic(self, receiver):
        return self.imp(receiver, self.selector)
    
    def clone(self, receiver):
        m = object.__new__(_Method)
        m.selector = self.selector
        m.receiver = receiver
        m.imp = self.imp
        m.ret = self.ret
        return m


class _Callback(object):
    
    def __init__(self, f, ret, args, direct=False):
        d = types.signature(ret, args)
        self.callback = _ffi.callback(d, f if direct else self)
        self.f = f
        self.ret = ret
        self.args = args
    
    def __call__(self, *args):
        args = list(args)
        for i, a in enumerate(args):
            if self.args[i] == 'id':
                if a:
                    if a not in _instances:
                        n = _objc.object_getClassName(a)
                        _instances[a] = _classes[_ffi.string(n)](a)
                    args[i] = _instances[a]
                else:
                    args[i] = None
        r = self.f(args[0], *args[2:])
        if self.ret == 'id':
            return r.instance if r else _nil
        elif self.ret == 'Class':
            return _ffi.cast('Class', _objc.objc_getClass(r.__name__))
        return r


def _register_class(name, basename, dict):
    b = _ffi.cast('Class', _objc.objc_getClass(basename))
    p = _objc.objc_allocateClassPair(b, name, 0)
    for k, v in dict.items():
        c, e = p, ''
        s = sel(k.replace('_', ':'))
        if isinstance(v, _Callback):
            if isinstance(v.f, classmethod):
                c = _objc.object_getClass(_ffi.cast('id', c))
            e = types.encode(v.ret, v.args)
        else:
            m = _objc.class_getInstanceMethod(b, s)
            if not m:
                m = _objc.class_getClassMethod(b, s)
                c = _objc.object_getClass(_ffi.cast('id', c))
            if m:
                e = _ffi.string(_objc.method_getTypeEncoding(m))
                t = types.decode(e)
                v = _Callback(v, t[0], t[1:])
        if e:
            _objc.class_addMethod(c, s, _ffi.cast('IMP', v.callback), e)
            del dict[k]
    _objc.objc_registerClassPair(p)

class _classes(dict):
    
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            n = _objc.class_getName(_objc.class_getSuperclass(
                _ffi.cast('Class', _objc.objc_getClass(key))))
            self[key] = type(key, (self[_ffi.string(n)],), {})
            return self[key]

_classes = _classes() # class name -> Python class
_instances = {} # ObjC instance -> Python instance

class _MetaClass(type):
    
    def __new__(meta, name, bases, dict):
        if name not in _classes:
            if not _objc.objc_getClass(name):
                _register_class(name, bases[0].__name__, dict)
            dict['_methods'] = {} # method name -> Python method
            _classes[name] = type.__new__(meta, name, bases, dict)
        return _classes[name]
        
    def __getattr__(cls, name):
        if name not in cls._methods:
            cls._methods[name] = _Method(
                cls.__name__, name, False, _objc.objc_getClass(cls.__name__))
        return cls._methods[name]

class NSObject(object):
    
    __metaclass__ = _MetaClass
    
    def __init__(self, instance):
        self.instance = instance
        _associate_destructor(instance)
    
    def __getattr__(self, name):
        if name in self._methods:
            m = self._methods[name].clone(self.instance)
        else:
            m = _Method(self.__class__.__name__, name, True, self.instance)
            self._methods[name] = m
        setattr(self, name, m)
        return m


_supers = {}

class _super(object):

    def __init__(self, other):
        self.other = other
    
    def __getattr__(self, name):
        n = self.other.__class__.__base__.__name__
        m = _Method(n, name, True, self.other.instance)
        setattr(self, name, m)
        return m

def get_super(other):
    if other not in _supers:
        _supers[other] = _super(other)
    return _supers[other]


_destructors = {}
_nsobject_dealloc = _Method('NSObject', 'dealloc', True).basic

def _dealloc(destructor, selector):
    instance = _destructors.pop(destructor)
    other = _instances.pop(instance)
    _supers.pop(other, None)
    _nsobject_dealloc(destructor)

class _associate_destructor(object):
    
    def __init__(self):
        self.callback = _Callback(_dealloc, 'void', ('id', 'SEL'), True)
        _register_class('Destructor', 'NSObject', {'dealloc': self.callback})
        self.c = _objc.objc_getClass('Destructor')
        self.new = _Method('Destructor', 'new', False).basic
        self.release = _Method('Destructor', 'release', True).basic
    
    def __call__(self, instance):
        r = self.new(self.c)
        _objc.objc_setAssociatedObject(instance, r, r, _OBJC_ASSOCIATION_RETAIN)
        self.release(r)
        _destructors[r] = instance

_associate_destructor = _associate_destructor()
