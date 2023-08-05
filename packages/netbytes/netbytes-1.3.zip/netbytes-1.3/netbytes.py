from __future__ import with_statement

#
# Copyright (C) 2011    Nicolas DAVID (nicolas.david.mail@gmail.com)
# Licensed under LGPL
#

__doc__ = '''net_talk module

    A manager for string data exchanged via network. It doesn't intend to
    replace socket, threading, or any such modules. It does provides a way to
    encode an "action"[*] into a string ready to be sent over the network, and
    it does provide an easy way for the receiver to respond to these
    actions.

    [*] for example, in a multiplayer board game, a client wanna tell the
    server that the player has click on a cell at coords (x,y), this is an
    action.

    see the package docs for further details'''

__all__ = ('build', 'p_build', 'data_decode', 'data_encode', 'p_data_decode', 'p_data_encode')

import re
import cPickle as pickle
import hashlib
import os

class ModelLineError(Exception):
    def __init__(s, line, reason = None):
        s.line = line
        s.reason = reason
    def __str__(s):
        return '%s in the model is Illegal%s'%(repr(s.line), '' if s.reason is None else '\ncause : %s'%s.reason)

class InssuficientBytesError(Exception):
    def __init__(s, val, num_bytes):
        s.val = val
        s.nb = num_bytes
    def __str__(s):
        return '%s needs %s bytes, not %s'%(s.val,_needed_bytes(s.val),s.nb)

class IllegalCallError(Exception):
    def __init__(s, word, _not='not '):
        s.word = word
        s._not = _not
    def __str__(s):
        return 'Node is %sa tree\'s %s'%(s._not, s.word)

class UnknownActionError(Exception):
    def __init__(s,_bytes):
        s._bytes = _bytes
    def __str__(s):
        return 'No corresponding action for bytes %s'%repr(s._bytes)

class EncoderError(Exception):
    def __init__(s,val):
        s._type_val = type(val)
    def __str__(s):
        return 'encoders must return a %s, but returned a %s'%(repr(str),repr(s._type_val))

class HandlerError(Exception):
    def __str__(s):
        return 'handlers must callable objects, and must take exactly 1 argument (self argument in case of class\' instances not taken in account)'


def _byted_size(val, num_bytes=2):
    # converts an int *val* into a string of *num_bytes* characters. (Big Endian) --> Returns a str
    if not isinstance(val,int):
        raise TypeError('val must be an %s, have%s'%(repr(int), repr(type(val))))
    if val >> (8*num_bytes):
        raise InssuficientBytesError(val, num_bytes)
    return ''.join(chr((val>>(8*i))&0xff) for i in range(num_bytes))

def _embyte_string(string, num_bytes=2):
    # --> Returns an str
    # the returned str is *string* preceded by *num_bytes* bytes representing its size
    if not isinstance(string,str):
        raise TypeError('string parameter must be %s, have %s'%(repr(str),repr(type(string))))
    return _byted_size(len(string), num_bytes)+string

def _needed_bytes(val):
    r = 0
    if not val : return 1
    while val:
        r += 1
        val >>= 8
    return r

def _unbyte_size(byted_size):
    # do the opposite of _byted_size
    return sum(ord(c)<<(8*i) for i, c in enumerate(byted_size))


class Node(object):

    def __init__(s,bytecode=None, parent=None, children_bytecode_size=1):
        if bytecode is None:
            parent = None
            bytecode = ''
        if not isinstance(bytecode, str):
            raise TypeError('bytecode must be a %s, have %s'%(repr(str), repr(bytecode)))
        if parent is not None and not isinstance(parent, Node):
            raise TypeError('parent must be a %s or %s, have %s'%(repr(Node), repr(None), repr(type(parent))))
        if not isinstance(children_bytecode_size, int):
            raise TypeError('bytecode_size must be %s not %s'%(repr(int), repr(type(children_bytecode_size))))
        s._bytecode = bytecode
        s._children_bytecode_size = children_bytecode_size
        s._parent = parent
        s._handler = None
        s._encoder = None
        s._children = 0

    def _gen_bytecode(s):
        # returns a bytecode
        v = s._children
        r = _byted_size(v, s._children_bytecode_size)
        s._children += 1
        return r

    def _add_child(s,name,cbs):
        # adds a child to the instance *s* named *name*. The *cbs* tells the
        # bytecode size of the child's future children
        if s._handler is not None or s._encoder is not None:
            raise IllegalCallError('action','')
        elif name in s.__dict__:
            raise AttributeError('A child named %s already exists'%repr(name))
        node = Node(s._gen_bytecode(), s, cbs)
        object.__setattr__(s, name, node)
        return node

    def __setattr__(s, k, v):
        if not (k[0] == '_') :
            raise AttributeError('attribue setting on %s forbidden'%repr(Node))
        object.__setattr__(s, k, v)

    def __iter__(s):
        # yield the childs of the instance *s*
        for key, obj in s.__dict__.items():
            if key[0]!='_' and isinstance(obj, Node):
                yield obj

    def __str__(s):
        # returns the bytecodes of all its parents, from the oldest, to itself
        if not s._is_root():
            return str(s._parent)+s._bytecode
        return s._bytecode

    def _is_action(s):
        # tells if it is an end of the tree
        return (not s._children) and (not s._is_root())

    def _is_root(s):
        return s._parent is None

    def _is_node(s):
        return not s._is_root() and not s._is_action() and s._handler is None and s._encoder is None

    def _find(s, _bytes):
        # returns the action Node represented in *_bytes*
        for child in s:
            if _bytes.startswith(str(child)):
                if child._is_action():
                    return child
                return child._find(_bytes)
        raise UnknownActionError(_bytes)

    def _handle(s, _bytes):
        # if *s* is an action Node, call its handler. Otherwise, search the action Node represented in *_bytes*
        if not s._is_action():
            action = s._find(_bytes)
            return action._handle(_bytes)
        elif not _bytes.startswith(str(s)):
            raise UnknownActionError(_bytes)
        else:
            return s._handler(_bytes.lstrip(str(s))) if s._handler else None

    def __call__(s, *args, **kwargs):
        # call the encoder associated to the action Node. But only if *s* is an action Node
        if s._is_action():
            r = s._encoder(*args, **kwargs) if s._encoder else ''
            if not isinstance(r, str):
                raise EncoderError(r)
            return str(s) + r
        raise IllegalCallError('action')

    def HANDLER(s,_callable):
        # decorator used to assign a hanlder
        if not s._is_action():
            raise IllegalCallError('action')
        elif not callable(_callable):
            raise HandlerError
        else:
            try:
                arg_count = _callable.func_code.co_argcount
            except AttributeError:
                try:
                    arg_count = _callable.__call__.im_func.func_code.co_argcount - 1
                except AttributeError:
                    raise HandlerError
            finally:
                if arg_count != 1 :
                    raise HandlerError
        def wrapper(_bytes):
            return _callable(_bytes)
        s._handler = wrapper
        return wrapper

    def ENCODER(s, _callable):
        # decorator used to assign an encoder
        if not s._is_action():
            raise IllegalCallError('action')
        def wrapper(*args, **kwargs):
            return _callable(*args, **kwargs)
        s._encoder = wrapper
        return wrapper

    def _build(s, model):
        # parse *model* and create the actions tree according to it
        if not s._is_root():
            raise IllegalCallError('root')
        _ident_pat = re.compile('^\s*')
        _line_pat = re.compile('^\s*(?:(\d?)\s|\s?)([a-z]\w{2}\w*).*$')
        def _get_cbs_and_name(string):
            match = _line_pat.match(string)
            if match is None:
                raise ModelLineError(string)
            cbs, name = match.groups()
            if cbs is None:
                cbs = 1
            else:
                cbs = int(cbs)
            return cbs, name
        cbs = 1
        parents = {0:s}
        last_ident = 0
        last_node = None
        for line in model.splitlines():
            if not line.strip():
                continue
            ident = len(_ident_pat.match(line).group())
            cbs, name = _get_cbs_and_name(line)
            if ident > last_ident:
                parents[ident] = last_node
            if ident not in parents :
                raise ModelLineError(line, 'Unexcpected Ident')
            parents[ident]._add_child(name, cbs)
            last_ident = ident
            last_node = getattr(parents[ident], name)


def build(model, bytecode_size=1):
    '''build(model, bytecode_size=1) -> Node
    model           <-- string  representing the tree language
    bytecode_size   <-- int     indicate the size (in bytes) of the bycodes attributed
                                to the Node's direct children'''
    tree = Node(children_bytecode_size=bytecode_size)
    tree._build(model)
    return tree

def data_encode(iterable, size_num_bytes=2):
    # see package docs
    if not hasattr(iterable, '__iter__'):
        iterable = [iterable]
    if not all(isinstance(obj, str) for obj in iterable):
        raise TypeError('Not all elements in the \'iterable\' parameter are %s'%repr(str))
    return ''.join(_embyte_string(x, size_num_bytes) for x in iterable)

def data_decode(data, size_num_bytes=2, _data=None):
    # see package docs
    sb = size_num_bytes
    if _data is None:
        _data = []
    size = _unbyte_size(data[:sb])
    data_end = sb+size
    _data.append(data[sb:data_end])
    data = data[data_end:]
    if data:
        data_decode(data, sb, _data)
    if len(_data) == 1:
        return _data[0]
    return _data

def p_data_encode(iterable, size_num_bytes=2):
    # see package docs
    if not hasattr(iterable, '__iter__'):
        iterable = [iterable]
    iterable = [pickle.dumps(obj,2) for obj in iterable]
    return data_encode(iterable, size_num_bytes)

def p_data_decode(data, size_num_bytes=2, _data=None):
    # see package docs
    return [pickle.loads(obj) for obj in  data_decode(data, size_num_bytes, _data)]

def p_build(model, filename='.actions_tree'):
    # see package docs
    model_hash = hashlib.sha512()
    model_hash.update(model)
    model_hash = model_hash.digest()
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename,'rb') as f_in:
            hash_size = _unbyte_size(f_in.read(2))
            file_model_hash = f_in.read(hash_size)
            if file_model_hash == model_hash:
                return pickle.loads(f_in.read())
    with open(filename,'wb') as f_out:
        tree = build(model)
        f_out.write(_embyte_string(model_hash) + pickle.dumps(tree,2))
        return tree







if __name__=='__main__':
    import sys
    def assert_error(error, _callable, *args, **kwargs):
        try :
            _callable(*args, **kwargs)
        except error:
            return
        except:
            n,v,t = sys.exc_info()
            n = repr(n.__name__)
        else :
            n = 'nothing'
        print 'assertion of exception %s failed, caught %s'%(repr(error.__name__), n)
        raise

    def assert_no_error(_callable, *args, **kwargs):
        try :
            _callable(*args, **kwargs)
        except:
            n,v,t = sys.exc_info()
            raise AssertionError('error %s caught, value : %s'%(repr(n.__name__), repr(v)))

    def test_decorator(decorator):
        @decorator
        def test(x):
            return x

    def assert_eq(a,b):
        try :
            assert a == b
        except AssertionError:
            raise AssertionError('%s != %s'%(a,b))

    #test _byted_size
    assert_eq(_byted_size(0x01), '\x01\x00')
    assert_error(InssuficientBytesError, _byted_size, 0x100, 1)
    assert_eq(_byted_size(0x100), '\x00\x01')
    assert_error(TypeError, _byted_size, 'a')

    #test _embyte_string
    assert_no_error(_embyte_string, 'ab')
    assert_error(TypeError, _embyte_string, 35)

    #test _needed_bytes
    assert_error(TypeError, _needed_bytes, 'a')
    assert_eq(_needed_bytes(0xff), 1)
    assert_eq(_needed_bytes(0xffffff), 3)

    #test _unbyte_size
    assert_eq(_unbyte_size('\x00\x01'), 0x100)
    assert_eq(_unbyte_size('\xff\xe4\x66'), 0x66e4ff)
    assert_error(TypeError, _unbyte_size, 3.2)

    #test Node.__init__
    assert_error(TypeError, Node, bytecode=2)
    assert_error(TypeError, Node, '\x00', 56)
    assert_error(TypeError, Node, None, None, 'a')

    #test Node._gen_bytecode
    node = Node()
    assert_no_error(Node._gen_bytecode,node)
    assert_eq(Node._gen_bytecode(node), '\x01')
    assert_eq(Node._gen_bytecode(node), '\x02')
    node._children_bytecode_size = 2
    assert_eq(Node._gen_bytecode(node), '\x03\x00')
    node._children = 0x100
    node._children_bytecode_size = 1
    assert_error(InssuficientBytesError, Node._gen_bytecode, node)

    #test Node._add_child
    node = Node()
    assert_error(TypeError, node._add_child, 25,1)
    assert_error(TypeError, node._add_child, 'fooo','a')
    assert_no_error(node._add_child, 'foo', 1)
    assert_error(AttributeError, node._add_child, 'foo', 1)
    node._handler = lambda:None
    assert_error(IllegalCallError, node._add_child, 'fooo', 1)

    #test Node.__setattr__
    node = Node()
    assert_no_error(node.__setattr__, '_sdf', 58)
    assert_error(AttributeError, node.__setattr__, 'sdf',58)

    #test Node.__iter__
    node = Node()
    node._add_child('foo', 1)
    node._add_child('foo2', 1)
    assert all(isinstance(child, Node) for child in node)

    #test Node.__str__
    assert_eq(str(node.foo), '\x00')
    node.foo._add_child('foo',1)
    assert_eq(str(node.foo.foo), '\x00\x00')

    #test Node._is_action
    assert_eq(node.foo.foo._is_action(), True)
    assert_eq(node.foo._is_action(), False)
    assert_eq(node._is_action(), False)

    #test Node._is_root
    assert_eq(node._is_root(), True)
    assert_eq(node.foo._is_root(), False)
    assert_eq(node.foo.foo._is_root(), False)

    #test Node._is_node
    assert_eq(node._is_node(), False)
    assert_eq(node.foo._is_node(), True)
    assert_eq(node.foo.foo._is_node(), False)

    #test Node._find
    assert_no_error(node._find, '\x00\x00test')
    assert_eq(node._find('\x00\x00test'), node.foo.foo)
    assert_error(UnknownActionError, node._find, '\x00\x05')

    #test Node._handle
    node.foo.foo.HANDLER(lambda s: s)
    _bytes = '\x00\x00test'
    assert_no_error(node._handle, _bytes)
    assert_no_error(node.foo._handle,_bytes)
    assert_no_error(node.foo.foo._handle, _bytes)
    assert_eq(node._handle(_bytes), 'test')
    assert_eq(node.foo._handle(_bytes), 'test')
    assert_eq(node.foo.foo._handle(_bytes), 'test')
    assert_error(UnknownActionError, node._handle,'\x07')

    node = Node()
    node._add_child('foo',1)
    node.foo._add_child('test',1)

    #test Node.ENCODER
    assert_no_error(test_decorator, node.foo.test)
    assert_error(IllegalCallError, test_decorator, node.foo)

    #test Node.HANDLER
    assert_no_error(test_decorator, node.foo.test)
    assert_no_error(IllegalCallError, test_decorator, node.foo)
    assert_error(HandlerError, node.foo.test.HANDLER, 1)
    assert_error(HandlerError, node.foo.test.HANDLER, lambda a,b:None)
    class Foo(object):
        def __call__(s,a):pass
    assert_no_error(node.foo.test.HANDLER, Foo())
    class Foo(object):
        def __call__(s,a,b):pass
    assert_error(HandlerError, node.foo.test.HANDLER, Foo())

    node = Node()
    node._add_child('foo', 1)
    node.foo._add_child('test', 1)
    node.foo.test._encoder = lambda x: x

    #test Node.__call__
    assert_no_error(node.foo.test, 'test')
    assert_eq(node.foo.test('test'), str(node.foo.test)+'test')
    assert_error(EncoderError, node.foo.test, 5)
    assert_error(IllegalCallError, node.foo)

    #test Node._build
    node = Node()
    assert_no_error(Node()._build, 'foo')
    assert_no_error(Node()._build, 'foo\n test')
    assert_no_error(Node()._build, '1 foo\n test')
    assert_no_error(Node()._build, 'foo\ntest')
    assert_no_error(Node()._build, '1 foo\n test\n test2')
    assert_error(ModelLineError, Node()._build, 'he')
    assert_error(ModelLineError, Node()._build, 'Hey')
    assert_error(ModelLineError, Node()._build, '2 ')
    assert_error(ModelLineError, Node()._build, '_hey')
    assert_error(ModelLineError, Node()._build, '13 hey')
    assert_error(ModelLineError, Node()._build, '13 hey\n  foo\n bad')

    #test build
    assert_no_error(build, 'foo')
    assert_no_error(build, 'foo\n test')
    assert_no_error(build, '1 foo\n test')
    assert_no_error(build, 'foo\ntest')
    assert_no_error(build, '1 foo\n test\n test2')
    assert_error(ModelLineError, build, 'he')
    assert_error(ModelLineError, build, 'Hey')
    assert_error(ModelLineError, build, '2 ')
    assert_error(ModelLineError, build, '_hey')
    assert_error(ModelLineError, build, '13 hey')
    assert_error(ModelLineError, build, '13 hey\n  foo\n bad')

    #test data_encode
    datas = list('abc')
    assert_eq(data_encode(datas, 1), '\x01a\x01b\x01c')
    assert_eq(data_encode(datas), '\x01\x00a\x01\x00b\x01\x00c')
    assert_eq(data_encode([' '*0x100]), '\x00\x01'+' '*0x100)
    assert_error(TypeError, data_encode,['a', 1])
    assert_no_error(data_encode, 'a')

    #test data_decode
    datas = list('abc')
    assert_no_error(data_decode, data_encode(datas))
    assert_eq(data_decode(data_encode(datas)),datas)

    #test p_data_encode & p_data_decode
    data = [(),{'a':1,'b':2}]
    assert_no_error(p_data_decode, p_data_encode(data))
    assert_eq(p_data_decode(p_data_encode(data)), data)

    #test p_build
    model = 'hey\n joe'
    assert_no_error(p_build, model)
    assert_no_error(p_build, model)
    model = 'hey\n joey'
    assert_no_error(p_build, model)



