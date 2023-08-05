#!/usr/bin/env python2
# -*- coding: utf-8 -*-
r"""katagami - a very simple xml template engine.
=============================================


setup...skip to next chapter:

    >>> def renderString_(t):
    ...     return renderString('<html xmlns:py="http://pypi.python.org/pypi/katagami" py:feature="strip-space"><body>%s</body></html>' % t)
    >>> def echo(name, body):
    ...     with open(os.path.join(tmpdir, name), 'w') as fp:
    ...         fp.write(body)
    >>> def echoxml(name, body):
    ...     echo(name, '<html xmlns:py="http://pypi.python.org/pypi/katagami" py:feature="strip-space"><body>%s</body></html>' % body)


Pythonic evaluation
-------------------

scriping
~~~~~~~~

`CDATA` is required and use `print`:

    >>> renderString_('''
    ... <py:script><![CDATA[
    ...     print '<p>hello, world</p>'
    ... ]]></py:script>
    ... ''')
    '<html><body><p>hello, world</p>\n</body></html>'


Include python script file:

    >>> echo('sub-script.py', '''print "hello, world"''')
    >>> echoxml('template.html', '''
    ...     <p><py:script src="sub-script.py"/></p>
    ... ''')
    >>> renderFile(os.path.join(tmpdir, 'template.html'))
    '<html><body><p>hello, world\n</p></body></html>'


evaluate XML attributes, textContent, innerXML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

XML attributes (attribute value starts with XML namespace):

    >>> renderString_('''<p class="py:'python-expr'">hello, world</p>''')
    '<html><body><p class="python-expr">hello, world</p></body></html>'

textContent:

    >>> renderString_('''<p py:text="'hello, world'"/>''')
    '<html><body><p>hello, world</p></body></html>'

innerXML:

    >>> renderString_('''<div py:content="'hello, world&lt;hr/&gt;'"/>''')
    '<html><body><div>hello, world<hr/></div></body></html>'


Python syntax as XML attributes
-------------------------------

`if`, `elif`, `else` statements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> renderString_('''
    ... <p py:if="0"/>
    ... <p py:elif="0"/>
    ... <p py:else="">output here</p>
    ... ''')
    '<html><body><p>output here</p></body></html>'


loop statements
~~~~~~~~~~~~~~~

`for` statement (attribute value is Pythonic `for` style):

    >>> renderString_('''<p py:for="i, j in enumerate(range(3))" py:text="i, j"/>''')
    '<html><body><p>(0, 0)</p><p>(1, 1)</p><p>(2, 2)</p></body></html>'

`for`'s `else` is not supported.


`while` statement:

    >>> renderString_('''
    ... <py:script><![CDATA[ i = [1, 2, 3] ]]></py:script>
    ... <p py:while="i">
    ...     <py:_ py:text="i[0]"/>
    ...     <py:script><![CDATA[ i = i[1:] ]]></py:script>
    ... </p>
    ... ''')
    '<html><body><p>1</p><p>2</p><p>3</p></body></html>'

`while`'s `else` is not supported.


And there is special variable named `__loop__`, it is loop counter:

    >>> renderString_('''
    ... <p py:for="i in range(0)" py:text="i"/>
    ... <p py:if="not __loop__">no for loop</p>
    ... <p py:while="0"/>
    ... <p py:if="not __loop__">no while loop</p>
    ... ''')
    '<html><body><p>no for loop</p><p>no while loop</p></body></html>'


`try` statement
~~~~~~~~~~~~~~~~~~

    >>> renderString_('''
    ... <p py:try="" py:text="not_found"/>
    ... <p py:except="NameError as e" py:text="e"/>
    ... <p py:try="" py:text="'try'"/>
    ... <p py:except="" py:text="e"/>
    ... <p py:else="">no error</p>
    ... ''')
    "<html><body><p>name 'not_found' is not defined</p><p>try</p><p>no error</p></body></html>"


`with` statement
~~~~~~~~~~~~~~~~

    >>> echo('msg.txt', 'hello, world')
    >>> renderString_('''
    ... <py:_ py:with="open(r'%s') as fp">
    ...     <p py:text="fp.read()"/>
    ...     <p py:text="fp.closed"/>
    ... </py:_>
    ... <p py:text="fp.closed"/>
    ... ''' % os.path.join(tmpdir, 'msg.txt'))
    '<html><body><p>hello, world</p><p>False</p><p>True</p></body></html>'

Multi items are supported (ex. 'with a, b: pass').

    >>> echo('msg2.txt', 'hello, world')
    >>> renderString_('''
    ... <py:_ py:with="open(r'%s') as fp, open(r'%s') as fp2">
    ...     <p py:text="fp.read()"/>
    ...     <p py:text="fp2.read()"/>
    ... </py:_>
    ... ''' % (os.path.join(tmpdir, 'msg.txt'), os.path.join(tmpdir, 'msg2.txt')))
    '<html><body><p>hello, world</p><p>hello, world</p></body></html>'


`def` statement
~~~~~~~~~~~~~~~

Give the context by keyword arguments:

    >>> renderString_('''
    ... <p py:def="myfunc">hello, <py:_ py:text="msg"/></p>
    ... <py:_ py:content="myfunc(msg='world')"/>
    ... ''')
    '<html><body><p>hello,world</p></body></html>'


Include another template
------------------------

Simply, include all elements:

    >>> echoxml('sub-template.html', '<p>hello, world</p>')
    >>> echoxml('template.html', '<py:include src="sub-template.html"/>')
    >>> renderFile(os.path.join(tmpdir, 'template.html'))
    '<html><body><html><body><p>hello, world</p></body></html></body></html>'

XUL like XML overlay:

    >>> echoxml('sub-template.html', '''
    ... <p py:insertbefore="myid">before</p>
    ... <p py:replace="myid">hello, world</p>
    ... <p py:insertafter="myid">after</p>
    ... ''')
    >>> echoxml('template.html', '''
    ...     <py:overlay src="sub-template.html"/>
    ...     <p id="myid"/>
    ... ''')
    >>> renderFile(os.path.join(tmpdir, 'template.html'))
    '<html><body><p>before</p><p id="myid">hello, world</p><p>after</p></body></html>'

`id` attribute is automatically set from `replace` attribute's value.

And special variable named `__file__` means that pathname of template file:

    >>> echoxml('sub-template.html', '<p py:replace="fragment" py:text="os.path.basename(__file__)"/>')
    >>> echoxml('template.html', '''
    ... <py:script><![CDATA[ import os ]]></py:script>
    ... <p py:text="os.path.basename(__file__)"/>
    ... <py:overlay src="sub-template.html"/>
    ... <p id="fragment"/>
    ... ''')
    >>> renderFile(os.path.join(tmpdir, 'template.html'))
    '<html><body><p>template.html</p><p id="fragment">sub-template.html</p></body></html>'


namespace (scope)
-----------------

The namespace is flat like python module and nested in function:

    >>> renderString_('''
    ... <py:script><![CDATA[ a = b = 0 ]]></py:script>
    ... <py: py:def="myfunc">
    ...     <py:script><![CDATA[
    ...         global a
    ...         print 'a=%d,' % a
    ...         print 'b=%d,' % b
    ...         a = b = 1
    ...     ]]></py:script>
    ... </py:>
    ... <py: py:text="myfunc()"/>
    ... (a, b)=<py: py:text="a, b"/>
    ... ''')
    '<html><body>a=0,\nb=0,\n(a, b)=(1, 0)</body></html>'


In included script file:

    >>> echo('sub-script.py', '''
    ... global msg
    ... msg = 'hello, world'
    ... msg2 = 'hello, world'
    ... global myfunc
    ... def myfunc(name):
    ...     return 'hello, ' + name
    ... ''')
    >>> echoxml('template.html', '''
    ...     <py:script src="sub-script.py"/>
    ...     <p py:text="msg"/>
    ...     <p py:try="" py:text="msg2"/>
    ...     <p py:except="NameError as e" py:text="e"/>
    ...     <p py:text="myfunc('world')"/>
    ... ''')
    >>> renderFile(os.path.join(tmpdir, 'template.html'))
    "<html><body><p>hello, world</p><p>name 'msg2' is not defined</p><p>hello, world</p></body></html>"


In included template file:

    >>> echoxml('sub-template.html', '''
    ...     <p py:replace="myid">hello, world</p>
    ...     <py:script><![CDATA[
    ...         global msg
    ...         msg = 'hello, world'
    ...     ]]></py:script>
    ...     <p py:def="global myfunc" py:text="text"/>
    ... ''')
    >>> echoxml('template.html', '''
    ...     <py:overlay src="sub-template.html"/>
    ...     <p id="myid"/>
    ...     <p py:text="msg"/>
    ...     <py: py:content="myfunc(text='hello, world')"/>
    ... ''')
    >>> renderFile(os.path.join(tmpdir, 'template.html'))
    '<html><body><p id="myid">hello, world</p><p>hello, world</p><p>hello, world</p></body></html>'


Features
--------

strip-space
~~~~~~~~~~~

    >>> renderString('''<html xmlns:py="http://pypi.python.org/pypi/katagami"
    ...                       py:feature="strip-space"><body>
    ...     <p> spaces after tag or before tag are stripped. </p>
    ... </body></html>''')
    '<html><body><p>spaces after tag or before tag are stripped.</p></body></html>'


strip-comment
~~~~~~~~~~~~~

    >>> renderString('''<html xmlns:py="http://pypi.python.org/pypi/katagami"
    ...                       py:feature="strip-space strip-comment"><body>
    ...     <!-- comment will be strippd. -->
    ... </body></html>''')
    '<html><body></body></html>'


entity-variable
~~~~~~~~~~~~~~~

Expand entity starts with special xmlns prefix:

    >>> renderString('''<html xmlns:py="http://pypi.python.org/pypi/katagami"
    ...                       py:feature="strip-space entity-variable"><body>
    ...     <py:script><![CDATA[
    ...         msg = 'hello,world'
    ...     ]]></py:script>
    ...     &py:msg;
    ... </body></html>''')
    '<html><body>hello,world</body></html>'


compile-coffeescript
~~~~~~~~~~~~~~~~~~~~

If CoffeeScrip compiler (coffee) is installed and `compile-cofeescript`
feature flag is set, template engine converts
'<script type="text/coffeescript"/>' to
'<script type="application/javascript"/>' by coffee. But `src` attributes is
not supported.


compile-scss
~~~~~~~~~~~~

If pyScss (http://pypi.python.org/pypi/pyScss) is installed and `compile-scss`
feature flag is set, template engine converts '<style type="text/scss"/>' to
'<style type="text/css"/>' by pyScss.


Encoding
--------

Template engine detects file encoding and encodes to unicode for inner use,
returns unicode or decoded str. Python script file encoding is PEP 0263 style,
XML file encoding is XML header ('<?xml encoding="NAME"?>').


Techniques and notices
----------------------

This module is wrote under assuming that sys.setdefaultencoding('utf-8').


The attribute order is important:

    >>> renderString_('''
    ... <p py:if="0" py:for="i in range(2)" py:text="i"/>
    ... <p py:for="i in range(2)" py:if="i > 0" py:text="i"/>
    ... ''')
    '<html><body><p>1</p></body></html>'


If you need closing tag, then write below (This trick is not required for
`html`'s `textarea`):

    >>> renderString_('''
    ... <textarea></textarea>
    ... <div></div>
    ... <div><py:/></div>
    ... ''')
    '<html><body><textarea></textarea><div/><div></div></body></html>'


Entities will not be expanded:

    >>> renderString_('''&nbsp;&unknown_entity;''')
    '<html><body>&nbsp;&unknown_entity;</body></html>'


All unsupported tags will be stripped:

    >>> renderString_('''<py:unknownTag/><py:>not strip</py:>''')
    '<html><body>not strip</body></html>'

But unsupported attributes will occur exception:

    >>> renderString_('''<p py:unknown_attr_0123456789=""/>''')
    Traceback (most recent call last):
    ...
    SyntaxError: unknown statement unknown_attr_0123456789


Special variables are available in some cases:
 * __file__ = str -> path of file (template or script)
 * __noloop__ = bool -> whether loop statements executed
 * _ = object -> temporary value when extracting variables

Special utility functions are available, see default_namespace.

Special string codecs:
 * percent, uri - known as encodeURIComponent, decodeURIComponent
 * xml - escape '<', '>', '&'

For more information, see `Element` class implementation.

History
-------
* 0.3.0 change specification (required xmlns, for_ -> for, remove python tag,
        add script tag, add include tag, add text attribute, add content
        attribute, add overlay tag, add insertbefore attribute, add
        insertafter attribute, add replace attribute), this version is not
        compatible with version 0.2.0
* 0.2.0 change exception handling, fix encoding handling
* 0.1.2 fix encoding handling, add new commandline handling
* 0.1.1 update document for PyPI
* 0.1.0 first release
"""
__version__ = '0.3.0'
__author__ = __author_email__ = 'chrono-meter@gmx.net'
__license__ = 'PSF'
__url__ = 'http://pypi.python.org/pypi/katagami'
__all__ = ('Renderer', 'renderString', 'renderFile', 'Template')

import __future__
import sys
import types
import ast #; assert ast.__version__ == 82160 # Python 2.7.2
import os
import re
import collections
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from xml.parsers import expat
from xml.sax import saxutils
import distutils.util
import math
import itertools
import encodings
import codecs
import subprocess
import tempfile
import shutil
if __debug__:
    import traceback
    import warnings
    _ = encodings.normalize_encoding(sys.getdefaultencoding())
    if _ != 'utf_8':
        warnings.warn('sys.getdefaultencoding() may be "utf-8", but %r.' % _,
                      UnicodeWarning)
    del _

try:
    # http://pypi.python.org/pypi/pyScss
    import scss
except ImportError:
    scss = None


PyCOMPILER_FLAGS_MASK = sum(
    getattr(__future__, i).compiler_flag for i in __future__.all_feature_names)


def annotate(**kwargs):
    def result(function):
        for i in kwargs.items():
            setattr(function, *i)
        return function
    return result


def locate(function, filename='', firstlineno=0, name=''):
    """duplicate function with custom location"""
    if isinstance(filename, unicode):
        filename = filename.encode(sys.getfilesystemencoding())
    if isinstance(name, unicode):
        name = str(name)

    _function = function
    if isinstance(_function, types.MethodType):
        function = _function.im_func

    co = function.func_code
    function = types.FunctionType(
        types.CodeType(
            co.co_argcount,
            co.co_nlocals,
            co.co_stacksize,
            co.co_flags,
            co.co_code,
            co.co_consts,
            co.co_names,
            co.co_varnames,
            filename or co.co_filename,
            name or co.co_name,
            firstlineno or co.co_firstlineno,
            '', #co.co_lnotab, # ignore line info
            co.co_freevars,
            co.co_cellvars,
            ),
        function.func_globals,
        name or function.func_name,
        function.func_defaults,
        function.func_closure,
        )

    if isinstance(_function, types.MethodType):
        function = types.MethodType(
            function, _function.im_self, _function.im_class)

    return function


def findpyencoding(fp, default='ascii'):
    """PEP 0263 -- Defining Python Source Code Encodings
    http://www.python.org/dev/peps/pep-0263/
    """
    result = default
    pos = fp.tell()
    try:
        fp.seek(0)
        for i, line in enumerate(fp.readlines()):
            if i >= 2: break
            r = re.match('\s*#.*coding\W+(\S+)', line)
            if r:
                result = r.group(1)
    finally:
        fp.seek(pos)
    ''.decode(result)
    return result


def findxmlencoding(file, default='ascii'):
    """find xml encoding definition
    """
    # get the first line
    if isinstance(file, basestring):
        m = re.match('.*\n', file)
        if m:
            data = m.group(0)
        else:
            data = ''
    else:
        pos = file.tell()
        file.seek(0)
        try:
            data = file.readline().strip()
        finally:
            file.seek(pos)

    result = default
    if data.startswith('<?xml') and data.endswith('?>'):
        result = \
            re.search('encoding\s*=\s*["\']([^"\']*)["\']', data).group(1)
    ''.decode(result)
    return result


class Element(object):
    # `Element` is reusable, but not thread safe.

    nsuri = {
        'http://www.w3.org/1999/xhtml': 'html',
        'http://www.w3.org/TR/REC-html40': 'html',
        __url__: __name__,
        }
    __slots__ = ('parent', 'name', 'attributes', 'children', 'column',
                 'firstlineno', 'lineno')

    def __init__(self, parent, name='', attributes={}):
        self.parent = parent
        self.name = name
        self.attributes = attributes
        self.children = []
        self.column = self.firstlineno = self.lineno = -1

    def evaluate(self, env=None, globals=None, locals=None):
        """
        env = {
            'feature': set([str, ...]), # user defined default features
            'globals': {}, # global namespace
            'locals': {}, # local namespace
            'files': ({ # template file informations
                'type': str,
                'filename': str,
                'encoding': str,
                'feature': set([str, ...]),  # see .handle_attr_feature()
                'codeflags': int, # compiler flags
                }, ...),
            'stack': [{ # frame stack of elements
                'condition': bool, # if, elif, else condition
                'contexts': [with_context_manager, ...],
                'statements': [[handler, ...]], # statements stack
                'xmlns': {
                    None: 'name', # default namespace
                    'prefix': 'name', # The name is such as 'html',
                                      # but is not URI.
                    },
                }, ...],
            'overlay': {
                'id': {
                    'insertbefore': [str, ...],
                    'replace': [str, ...],
                    'insertafter': [str, ...],
                    },
                ...
                },
            'stdout': StringIO(), # output buffer for write(),
            }
        """
        assert self.parent is None, 'call from topmost element'

        if env is None:
            env = {}

        if globals is None:
            env['globals'] = env['locals'] = {}
        elif locals is None:
            env['globals'] = env['locals'] = globals
        else:
            env['globals'], env['locals'] = globals, locals

        env.setdefault('files', ({}, ))
        env['files'][-1].setdefault('type', 'root')
        env['files'][-1].setdefault('filename', env['globals']['__file__'])
        env['files'][-1].setdefault('encoding', 'utf-8')
        env['files'][-1].setdefault('feature', set(env.get('feature', [])))
        env['files'][-1].setdefault('codeflags', 0)
        env.setdefault('stack', [])
        env.setdefault('overlay', {})
        env.setdefault('stdout', StringIO())

        env['stack'].append({
            'self': self,
            'statements': [],
            'xmlns': {},
            })
        try:
            result = self._stringify_children(env)
        finally:
            env['stack'].pop()
        assert isinstance(result, unicode)
        return result

    def _stringify_children(self, env, **handlers):
        result = ''
        for i in self.children:
            if isinstance(i, self.__class__):
                name = 'element'
            elif isinstance(i, dict):
                name = i.get('name', 'default')

            if name in handlers:
                result += handlers[name](env, i)
            elif name == 'text':
                i = i['textContent']
                if 'strip-space' in env['files'][-1]['feature']:
                    i = i.strip()
                result += saxutils.escape(i)
            elif name == 'entity':
                if 'entity-variable' in env['files'][-1]['feature']:
                    nsname, expr = self._splitname(
                        env, i['textContent'][1:-1])
                    if nsname == __name__:
                        handler = self._stringify_expr
                        if __debug__:
                            handler = locate(
                                handler, env['globals']['__file__'],
                                i['firstlineno'],
                                'Entity "%s"' % i['textContent'])
                        result += handler(env, expr)
                    else:
                        result += i['textContent']
                else:
                    result += i['textContent']
            elif name == 'element':
                handler = i._evaluate
                if __debug__:
                    handler = locate(handler, env['globals']['__file__'],
                                     i.firstlineno, 'Element "%s"' % i.name)
                result += handler(env)
            elif name == 'comment':
                if 'strip-comment' not in env['files'][-1]['feature']:
                    result += '<!--' + i['textContent'] + '-->'
            elif name == 'cdata':
                result += '<![CDATA[' + i['textContent'] + ']]>'
            elif name == 'default':
                if len(env['files']) < 2: # not included
                    result += i['textContent']
            else:
                result += i['textContent']

        self._endstatements(env, pos=-1)

        return result

    def _evaluate(self, env):
        if len(env['stack']) == 1 and ':' not in self.name:
            env['stack'][-1]['xmlns'][None] = self.name.lower()

        saved = self.attributes.copy(), self.children[:], \
                env['files'][-1]['feature']
        env['stack'].append({
            'self': self,
            'statements': [],
            'xmlns': env['stack'][-1]['xmlns'].copy(),
            })
        try:
            try:
                return self._stringify(env)
            except Exception as e:
                if self._endstatements(env, error=e):
                    return ''
                #if __debug__:
                #    print >>sys.stderr, traceback.format_exc(),
                raise
        finally:
            env['stack'].pop()
            self.attributes, self.children[:], env['files'][-1]['feature'] \
                = saved

    def _stringify(self, env):
        nested = []
        # syntax attributes
        for name in list(self.attributes):
            if name == 'xmlns':
                prefix = None
                env['stack'][-1]['xmlns'][prefix] = \
                    self.nsuri.get(self.attributes.pop(name).strip(), '')
                continue
            if name.startswith('xmlns:'):
                prefix = name.split(':', 1)[1]
                env['stack'][-1]['xmlns'][prefix] = \
                    self.nsuri.get(self.attributes.pop(name).strip(), '')
                continue

            nsname, localname = self._splitname(env, name)

            # normal attribute
            if nsname != __name__:
                continue

            handler = getattr(self, 'handle_attr_' + localname, None)
            if handler: # primary statement
                primary = handler
                if not nested:
                    self._endstatements(env)
                env['stack'][-2]['statements'].append([primary])
            else: # secondary statement or unknown
                self._endstatements(env, localname)
                primary = env['stack'][-2]['statements'][-1][0]
                handler = getattr(
                    self, primary.__name__ + '_' + localname, None)
                if not handler:
                    raise SyntaxError('unsupported statement %s' % localname)
                if nested:
                    raise SyntaxError('trailing statement %s must be first '
                                      'available attribute.' % localname)
                env['stack'][-2]['statements'][-1].append(handler)
            nested.append(localname)

            # call attribute handler
            value = self.attributes.pop(name).strip()
            if __debug__:
                handler = locate(handler, env['globals']['__file__'],
                                 self.firstlineno, 'Attribute "%s"' % name)
            result = handler(env, value)
            if result is not None:
                return result

        # no statements found, then clear all previous statements
        if not nested:
            self._endstatements(env)

        # special elements
        nsname, localname = self._splitname(env, self.name)
        handler = None
        if nsname == __name__:
            handler = getattr(self, 'handle_elem_' + localname, None)
        if not handler:
            handler = getattr(
                self, 'handle_elem_' + nsname + '_' + localname, None)
        if handler:
            result = handler(env)
            if result is not None:
                return result

        # dump
        layer = {}
        if env['files'][-1]['type'] != 'overlay':
            layer = \
                env['overlay'].get(self.attributes.get('id', '').strip(), {})

        try:
            result = layer['replace'][-1]
        except LookupError:
            opening, closing = self._tag(env)
            result = opening + self._stringify_children(env) + closing
        return ''.join(layer.get('insertbefore', [])) \
            + result + ''.join(layer.get('insertafter', []))

    def _endstatements(self, env, secondary=None, pos=-2, error=None):
        assert pos < 0
        for _ in range(pos + 2): env['stack'].append({})
        try:
            frame = env['stack'][-2]
            if error is None:
                while frame['statements']:
                    statements = frame['statements'][-1]
                    if secondary and \
                       secondary in getattr(statements[-1], 'trailings', ()):
                        break
                    if getattr(statements[0], 'secondary_required', False) \
                       and len(statements) < 2:
                        raise SyntaxError('%s must have trailing statement.'
                                          % statements[0].__name__)
                    handler = getattr(
                        self, statements[0].__name__ + '_exit', None)
                    if handler:
                        handler(env)
                    frame['statements'].pop()
                if secondary and not frame['statements']:
                    raise SyntaxError('unknown statement %s' % secondary)
            else:
                while frame['statements']:
                    statements = frame['statements'][-1]
                    handler = getattr(
                        self, statements[0].__name__ + '_error', None)
                    if handler and handler(env, error):
                        return True
                    frame['statements'].pop()
        finally:
            for _ in range(pos + 2): env['stack'].pop()

    def _tag(self, env):
        nsname, localname = self._splitname(env, self.name)
        if nsname == __name__:
            return '', ''
        opening, closing = '<%s' % self.name, ''
        for k in self.attributes:
            handler = self.eval_attr
            if __debug__:
                handler = locate(handler, env['globals']['__file__'],
                                 self.firstlineno, 'Attribute "%s"' % k)
            v = handler(env, k)
            opening += ' %s=%s' % (k, saxutils.quoteattr(v))
        if self.children \
           or self._splitname(env, self.name) == ('html', 'textarea'):
            opening += '>'
            closing += '</%s>' % self.name
        else:
            opening += '/>'
        return opening, closing

    def _splitname(self, env, name):
        name = name.strip()
        prefix, localname = name.split(':', 1) if ':' in name else (None, name)
        return env['stack'][-1]['xmlns'].get(prefix, ''), localname

    def _newscope(self, env, context={}):
        globals, locals = env['globals'], env['locals']
        if globals is locals:
            locals = {}
        else:
            locals = locals.copy()
        locals.update(context)
        return globals, locals

    def _exec_expr(self, env, expr, globals=None, locals=None):
        if globals is None:
            return eval(expr, env['globals'], env['locals'])
        elif locals is None:
            return eval(expr, globals)
        else:
            return eval(expr, globals, locals)

    def _stringify_expr(self, env, expr, globals=None, locals=None):
        result = self._exec_expr(env, expr, globals, locals)
        if not isinstance(result, basestring):
            result = saxutils.escape(str(result))
        if isinstance(result, str):
            result = result.decode(env['files'][-1]['encoding'])
        return result

    def _capture_exec(self, env, expr, globals=None, locals=None):
        # There is no way to show '<string>' source on traceback
        # http://hg.python.org/cpython/file/c3b063c82ae5/Python/traceback.c

        if isinstance(expr, (basestring, ast.Module)):
            expr = compile(
                expr, '<string>', 'exec', env['files'][-1]['codeflags'], True)
            env['files'][-1]['codeflags'] = \
                expr.co_flags & PyCOMPILER_FLAGS_MASK

        fp = env['stdout']
        fp.reset()
        fp.truncate()
        stdout = sys.stdout
        sys.stdout = fp
        try:
            if globals is None:
                exec expr in env['globals'], env['locals']
            elif locals is None:
                exec expr in globals
            else:
                exec expr in globals, locals
        finally:
            sys.stdout = stdout
        return fp.getvalue()

    def _joinpath(self, env, *names):
        dirname = env['globals']['__file__']
        if not os.path.isdir(dirname):
            dirname = os.path.dirname(dirname)
        return os.path.join(dirname, *names)

    def eval_attr(self, env, name):
        """<* *="python:expression"/>"""
        result = self.attributes[name]
        nsname, expr = self._splitname(env, result)
        if nsname == __name__:
            result = self._stringify_expr(env, expr)
        return result

    @annotate(trailings=('elif', 'else', ))
    def handle_attr_if(self, env, expr):
        """<* if="expression"/>"""
        env['stack'][-2]['condition'] = bool(self._exec_expr(env, expr))
        if not env['stack'][-2]['condition']:
            return ''

    def handle_attr_if_exit(self, env):
        del env['stack'][-2]['condition']

    @annotate(trailings=('elif', 'else', ))
    def handle_attr_if_elif(self, env, expr):
        """<* elif="expression"/>"""
        if env['stack'][-2]['condition']:
            return ''
        return self.handle_attr_if(env, expr)

    @annotate(trailings=('finally', ))
    def handle_attr_if_else(self, env, expr):
        """<* else="ignore"/>"""
        if env['stack'][-2]['condition']:
            return ''

    def handle_attr_for(self, env, expr):
        """<* for="symbols in iterable"/>"""
        result = []

        symbols, expr = re.split('\s+in\s+', expr, 1)
        env['locals']['__loop__'] = 0
        for item in self._exec_expr(env, expr):
            variables = {'_': item}
            exec '%s = _' % symbols in {}, variables
            env['locals'].update(variables)
            result.append(self._evaluate(env))
            env['locals']['__loop__'] += 1

        return ''.join(result)

    def handle_attr_while(self, env, expr):
        """<* while="expression"/>"""
        result = []

        env['locals']['__loop__'] = 0
        while bool(self._exec_expr(env, expr)):
            result.append(self._evaluate(env))
            env['locals']['__loop__'] += 1

        return ''.join(result)

    @annotate(secondary_required=True, trailings=('finally', 'except', ))
    def handle_attr_try(self, env, expr):
        env['stack'][-2]['condition'] = False

    def handle_attr_try_exit(self, env):
        del env['stack'][-2]['condition']
        env['stack'][-2].pop('error', None)

    def handle_attr_try_error(self, env, e):
        env['stack'][-2]['condition'] = True
        env['stack'][-2]['error'] = e
        return True

    @annotate(trailings=('except', 'else', 'finally', ))
    def handle_attr_try_except(self, env, expr):
        """<* except="errors as symbol"/>
        <* except="errors"/>
        """
        e = env['stack'][-2].get('error')
        if e is None:
            return ''

        if expr:
            try:
                expr, symbols = re.split('\s+as\s+', expr, 1)
            except ValueError:
                symbols = ''

            target = self._exec_expr(env, expr)
            if not isinstance(e, target):
                return ''

            if symbols:
                variables = {'_': e}
                exec '%s = _' % symbols in {}, variables
                env['locals'].update(variables)

    @annotate(trailings=('finally', ))
    def handle_attr_try_else(self, env, expr):
        if env['stack'][-2]['condition']:
            return ''

    def handle_attr_with(self, env, expr):
        """<* with="context as symbol"/>
        <* with="context"/>
        """
        env['stack'][-2]['contexts'] = []
        try:
            root = ast.parse('with %s: pass' % expr)
            node = root.body[0]
            while isinstance(node, ast.With):
                expr = compile(
                    ast.fix_missing_locations(
                        ast.Expression(body=node.context_expr)),
                    '<string>', 'eval', 0, True)
                env['stack'][-2]['contexts'].append(self._exec_expr(env, expr))
                enter = env['stack'][-2]['contexts'][-1].__enter__()
                if node.optional_vars:
                    expr = ast.Assign(
                        targets=[node.optional_vars],
                        value=ast.Name(id='_', ctx=ast.Load()),
                        )
                    expr = compile(
                        ast.fix_missing_locations(ast.Module(body=[expr])),
                        '<string>', 'exec', 0, True)
                    variables = {'_': enter}
                    exec expr in {}, variables
                    env['locals'].update(variables)
                node = node.body[0]
        except Exception as e:
            if self.handle_attr_with_error(env, e):
                return ''
            else:
                raise

    def handle_attr_with_exit(self, env):
        while env['stack'][-2]['contexts']:
            env['stack'][-2]['contexts'].pop().__exit__(None, None, None)
        del env['stack'][-2]['contexts']

    def handle_attr_with_error(self, env, e):
        result = False
        try:
            etype, value, tb = sys.exc_info()
            while env['stack'][-2]['contexts']:
                manager = env['stack'][-2]['contexts'].pop()
                result = manager.__exit__(etype, value, tb) or result
                if result:
                    etype = value = tb = None
            del env['stack'][-2]['contexts']
        finally:
            del etype, value, tb
        return result

    def handle_attr_def(self, env, expr):
        """<* def="funcname"/>"""
        attributes = self.attributes.copy()

        def function(**context):
            saved = self.attributes, env['locals']
            self.attributes = attributes.copy()
            env['globals'], env['locals'] = self._newscope(env, context)
            try:
                return self._evaluate(env)
            finally:
                self.attributes, env['locals'] = saved

        try:
            scope, symbol = expr.split()
        except ValueError:
            scope, symbol = 'local', expr
        function.__name__ = str(symbol.strip())

        if scope == 'global':
            env['globals'][function.__name__] = function
        elif scope == 'local':
            env['locals'][function.__name__] = function
        else:
            raise SyntaxError('unknown scope %s' % scope)

        return ''

    def handle_attr_feature(self, env, expr):
        """<* feature="feature-1 enable-feature-2 disable-feature-3"/>
        strip-space
        strip-comment
        entity-variable
        compile-coffeescript
        compile-scss
        """
        env['files'][-1]['feature'] = set(env['files'][-1]['feature'])
        for word in expr.split():
            if word.startswith('enable-'):
                env['files'][-1]['feature'].add(word.split('-', 1)[1])
            elif word.startswith('disable-'):
                env['files'][-1]['feature'].pop(word.split('-', 1)[1])
            else:
                env['files'][-1]['feature'].add(word)

    def handle_attr_content(self, env, expr):
        self.children[:] = [{
            'name': 'content',
            'textContent': self._stringify_expr(env, expr),
            }]

    def handle_attr_text(self, env, expr):
        self.handle_attr_content(env, expr)
        self.children[0]['textContent'] = \
            saxutils.escape(self.children[0]['textContent'])

    def _handle_attr_overlay(self, env, type, expr):
        assert env['files'][-1]['type'] == 'overlay', 'illegal use'
        if not expr:
            raise SyntaxError('attribute value is required')
        overlay = env['overlay'].setdefault(expr, {})
        overlay.setdefault(type, []).append(self._evaluate(env))

    def handle_attr_insertbefore(self, env, expr):
        self._handle_attr_overlay(env, 'insertbefore', expr)

    def handle_attr_insertafter(self, env, expr):
        self._handle_attr_overlay(env, 'insertafter', expr)

    def handle_attr_replace(self, env, expr):
        self.attributes['id'] = expr # auto fill id
        self._handle_attr_overlay(env, 'replace', expr)

    def handle_elem_script(self, env):
        if 'src' in self.attributes:
            __file__ = env['globals']['__file__']
            env['globals']['__file__'] = \
                self._joinpath(env, self.attributes['src'])
            try:
                with open(env['globals']['__file__'], 'Ur') as fp:
                    encoding = findpyencoding(fp, 'utf-8')
                    result = self._capture_exec(env, fp, *self._newscope(env))
                    return result.decode(encoding)
            finally:
                env['globals']['__file__'] = __file__

        else:
            def cdata(env, cdata):
                expr = cdata['textContent']
                # get firstmost invalid lines (spaces and comments)
                sep = re.match('^[\n\r]*(\s*#.*\n)*', expr).end()
                validexpr = expr[sep:]
                lineno = cdata['firstlineno'] + 1

                if validexpr.startswith((' ', '\t')) and validexpr.strip():
                    expr = 'if 1:' + '\n' * (lineno - 2) + expr.rstrip()
                    # ast.parse
                    expr = compile(
                        expr, env['globals']['__file__'], 'exec',
                        env['files'][-1]['codeflags'] | ast.PyCF_ONLY_AST,
                        True)
                    expr.body[:] = expr.body[0].body
                    # IronPython is bad at indentation and newline.

                else:
                    expr = '\n' * (lineno - 2) + expr

                handler = self._capture_exec
                if __debug__:
                    handler = locate(handler, env['globals']['__file__'],
                                     lineno, 'Cdata')
                result = handler(env, expr)
                result = result.decode(env['files'][-1]['encoding'])
                return result

            return self._stringify_children(env, cdata=cdata)

    def handle_elem_overlay(self, env):
        self.handle_elem_include(env)
        return ''

    def handle_elem_include(self, env):
        __file__ = env['globals']['__file__']
        env['globals']['__file__'] = \
            self._joinpath(env, self.attributes['src'])
        try:
            renderer = env['renderer']()
            renderer.ElementFactory = self.__class__
            renderer.parseFile(env['globals']['__file__'])

            _env = env.copy()
            _env['files'] += ({
                'type': self._splitname(env, self.name)[1],
                'encoding': renderer.encoding,
                }, )

            return renderer.element.evaluate(_env, *self._newscope(env))
        finally:
            env['globals']['__file__'] = __file__

    def handle_elem_html_script(self, env):
        # convert embedded CoffeeScript to JavaScript
        # coffee -c path/to/script.coffee -> path/to/script.js
        # https://github.com/alisey/CoffeeScript-Compiler-for-Windows
        if self.attributes.get('type').strip() == 'text/coffeescript' \
           and 'compile-coffeescript' in env['files'][-1]['feature']:

            if 'src' in self.attributes:
                return

            tmpdir = tempfile.mkdtemp()
            try:
                for i in self.children:
                    if not isinstance(i, dict) or i.get('name') != 'cdata':
                        continue
                    fd, filename = \
                        tempfile.mkstemp(suffix='.coffee', dir=tmpdir)
                    with os.fdopen(fd, 'wb') as fp:
                        fp.write(i['textContent'].encode(
                            env['files'][-1]['encoding']))
                    subprocess.check_call(['coffee', '-c', filename])
                    filename = os.path.splitext(filename)[0] + '.js'
                    with open(filename, 'rb') as fp:
                        i['textContent'] = fp.read()
            finally:
                shutil.rmtree(tmpdir)

            #self.attributes['type'] = 'text/javascript' # obsolete (RFC 4329)
            self.attributes['type'] = 'application/javascript'

    def handle_elem_html_style(self, env):
        if self.attributes.get('type').strip() == 'text/scss' and scss \
           and 'compile-scss' in env['files'][-1]['feature']:
            css = scss.Scss()
            result = css.compile(self._stringify_children(env))
            self.children[:] = [{'name': 'content', 'textContent': result}, ]
            self.attributes['type'] = 'text/css'


class Renderer(object):

    ElementFactory = Element
    encoding = 'utf-8'
    returns_unicode = True
    filename = '<string>'

    def __init__(self):
        pass

    def parseString(self, data):
        self.encoding = findxmlencoding(data, 'utf-8')
        self.returns_unicode = isinstance(data, unicode)
        self.filename = os.getcwdu()

        self.element = self.ElementFactory(None)
        self.parser = self._parser()
        try:
            self.parser.Parse(data, True)
        finally:
            del self.parser

    def parseFile(self, filename):
        with open(filename, 'rb') as fp:
            self.encoding = findxmlencoding(fp, 'utf-8')
            self.returns_unicode = False
            self.filename = filename

            self.element = self.ElementFactory(None)
            self.parser = self._parser()
            try:
                self.parser.Parse(fp.read().decode(self.encoding))
            finally:
                del self.parser

    def render(self, context=None, env=None, returns_unicode=None):
        if context is None:
            context = {}
        context.setdefault('__file__', self.filename)
        if env is None:
            env = {}
        env.setdefault('renderer', self.__class__)
        env.setdefault('files', ({}, ))
        env['files'][-1].setdefault('encoding', self.encoding)
        result = self.element.evaluate(env, context)
        if returns_unicode is None:
            returns_unicode = self.returns_unicode
        if not returns_unicode:
            result = result.encode(self.encoding)
        return result

    def renderString(self, data, *args, **kwargs):
        self.parseString(data)
        return self.render(*args, **kwargs)

    def renderFile(self, filename, *args, **kwargs):
        self.parseFile(filename)
        return self.render(*args, **kwargs)
        #TODO: cache by filename, stat.st_mtime

    def _parser(self):
        # http://docs.python.org/library/pyexpat.html
        result = expat.ParserCreate()
        result.ordered_attributes = True
        result.returns_unicode = True
        result.DefaultHandler = self.DefaultHandler
        result.StartElementHandler = self.StartElementHandler
        result.EndElementHandler = self.EndElementHandler
        result.StartCdataSectionHandler = self.StartCdataSectionHandler
        result.EndCdataSectionHandler = self.EndCdataSectionHandler
        result.CharacterDataHandler = self.CharacterDataHandler
        result.CommentHandler = self.CommentHandler
        result.UseForeignDTD() # inhibit expansion of entities
        return result

    def StartElementHandler(self, name, attributes):
        self.element = self.ElementFactory(self.element, name,
            collections.OrderedDict(zip(attributes[::2], attributes[1::2])))
        self.element.column = self.parser.CurrentColumnNumber
        self.element.firstlineno = self.parser.CurrentLineNumber

    def EndElementHandler(self, name):
        self.element.lineno = self.parser.CurrentLineNumber
        element = self.element
        self.element = self.element.parent
        self.element.children.append(element)

    def StartCdataSectionHandler(self):
        self.cdata = {
            'name': 'cdata',
            'textContent': '',
            'firstlineno': self.parser.CurrentLineNumber,
            'column': self.parser.CurrentColumnNumber,
            }

    def EndCdataSectionHandler(self):
        self.cdata['lineno'] = self.parser.CurrentLineNumber
        self.element.children.append(self.cdata)
        del self.cdata

    def DefaultHandler(self, data):
        if data.startswith('&') and data.endswith(';'):
            self.element.children.append({
                'name': 'entity',
                'textContent': data,
                'firstlineno': self.parser.CurrentLineNumber,
                'lineno': self.parser.CurrentLineNumber,
                'column': self.parser.CurrentColumnNumber,
                })
        else:
            self.element.children.append({
                'name': 'default',
                'textContent': data,
                'firstlineno': self.parser.CurrentLineNumber,
                'lineno': self.parser.CurrentLineNumber,
                'column': self.parser.CurrentColumnNumber,
                })

    def CharacterDataHandler(self, data):
        if not hasattr(self, 'cdata'):
            self.element.children.append({
                'name': 'text',
                'textContent': data,
                'firstlineno': self.parser.CurrentLineNumber,
                'lineno': self.parser.CurrentLineNumber,
                'column': self.parser.CurrentColumnNumber,
                })
        else:
            self.cdata['textContent'] += data

    def CommentHandler(self, data):
        self.element.children.append({
            'name': 'comment',
            'textContent': data,
            'firstlineno': self.parser.CurrentLineNumber,
            'column': self.parser.CurrentColumnNumber,
            })


def renderString(data, context={}, *args, **kwargs):
    ctx = default_namespace.copy()
    ctx.update(context)
    renderer = Renderer()
    return renderer.renderString(data, ctx, *args, **kwargs)


def renderFile(filename, context={}, *args, **kwargs):
    ctx = default_namespace.copy()
    ctx.update(context)
    renderer = Renderer()
    return renderer.renderFile(filename, ctx, *args, **kwargs)


class Template(object):

    def __init__(self, *path):
        self._path = list(path)
        self._suffixes = ('.html', '.htm', '.tmpl')
        self._namespace = default_namespace.copy()
        self._environ = {}
        self._Element = Element

    def _Renderer(self, filename):
        def result(_context={}, **kwargs):
            renderer = Renderer()
            renderer.ElementFactory = self._Element
            ctx = self._namespace.copy()
            ctx.update(_context)
            ctx.update(kwargs)
            return renderer.renderFile(filename, ctx, self._environ.copy())
        return result

    def __getattr__(self, name):
        for path in self._path:
            for root, dirs, files in os.walk(os.path.abspath(path)):
                del dirs[:]
                for file in files:
                    basename, ext = os.path.splitext(file)
                    if basename == name and ext.lower() in self._suffixes:
                        return self._Renderer(os.path.join(root, file))
        result = self.__class__(*[os.path.join(i, name) for i in self.path])
        result._suffixes = self._suffixes
        result._namespace = self._namespace
        result._environ = self._environ
        result._Element = self._Element
        return result


def open2(filename, mode='r', bufsize=-1):
    """__builtins__.open() with os.makedirs()"""
    if not mode.lstrip('U').startswith('r'):
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
    return open(filename, mode, bufsize)


def fssafe(filename, strict=False, replace=None):
    FORBIDDEN = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D'\
                '\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B'\
                '\x1C\x1D\x1E\x1F"*/:<>?\\|\x7f'
    result = ''
    for _c in filename:
        c = unichr(_c)
        if c in FORBIDDEN or (strict and not c.isalnum()):
            _c = replace(_c) if replace else ''
        result += _c
    return result


def overlay(*args):
    """
    >>> list(overlay((0, ), (1, 1, ), (2, 2, 2, ), (3, 3, 3, 3, ), ))
    [0, 1, 2, 3]
    """
    n = 0
    for it in args:
        for i, obj in enumerate(it):
            if n <= i:
                yield obj
                n += 1


def ring(iterable, beginning, reversed=False):
    """
    >>> list(ring(list(range(10)), 5))
    [5, 6, 7, 8, 9, 0, 1, 2, 3, 4]
    >>> list(ring(list(range(10)), 5, reversed=True))
    [5, 4, 3, 2, 1, 0, 9, 8, 7, 6]
    """
    length = len(iterable)
    if not reversed:
        it = itertools.chain(xrange(beginning, length), xrange(0, beginning))
    else:
        it = itertools.chain(
            xrange(beginning, -1, -1), xrange(length - 1, beginning, -1))
    for i in it:
        yield iterable[i]


def parity(i, marks=('even', 'odd')):
    """
    >>> parity(10)
    'even'
    >>> parity(50, ('un', 'deux', 'trois'))
    'trois'
    """
    return marks[i % len(marks)]


def toggle(**kwargs):
    """Utility function for html class attribute.
    >>> toggle(a=True, b=False, c=True)
    'a c'
    >>> toggle(a=False, b=False, c=True)
    'c'
    """
    return ' '.join(k for k, v in sorted(kwargs.items()) if v)


def countup(obj):
    """
    >>> countup(10)
    10
    >>> countup([1, ] * 10)
    10
    >>> countup(xrange(10))
    10
    """
    if isinstance(obj, int):
        return obj
    else:
        try:
            return len(obj)
        except TypeError:
            length = 0
            for i in obj:
                length += 1
            return length


def limit(number, *limitations):
    """
    >>> limit(10, 0, 9)
    9
    >>> limit(-1, 0, 9)
    0
    >>> limit(5, 0, 9)
    5
    """
    leftmost = min(*limitations)
    rightmost = max(*limitations)
    return max(leftmost, min(number, rightmost))


def _normpage(length, index, divisor):
    if length <= 0:
        return 0, 0
    pages = int(math.ceil(float(length) / divisor))
    if index < 0:
        index = (pages + index) % pages
    return pages, index


def paginate_items(iterable_or_length, index, divisor):
    """
    >>> items = range(100)
    >>> list(paginate_items(items, 0, 10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(paginate_items(items, 4, 10))
    [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
    >>> list(paginate_items(items, 10, 10))
    []
    >>> list(paginate_items(items, -1, 10))
    [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    """
    if isinstance(iterable_or_length, int):
        length = iterable_or_length
        pages, index = _normpage(length, index, divisor)
        for i in xrange(divisor * index, divisor * (index + 1)):
            yield i

    elif hasattr(iterable_or_length, '__getitem__'):
        length = len(iterable_or_length)
        pages, index = _normpage(length, index, divisor)
        for i in xrange(divisor * index, divisor * (index + 1)):
            try:
                yield iterable_or_length[i]
            except LookupError:
                break

    else:
        if index < 0:
            raise ValueError('negative index is not supported')
        for i, o in enumerate(iterable_or_length):
            if divisor * index > i:
                continue
            if i >= divisor * (index + 1):
                break
            yield o


def paginate_index(iterable_or_length, index, divisor, width=5,
                   left='&laquo;', right='&raquo;'):
    """
    >>> items = range(100)
    >>> list(paginate_index(items, 1, 10))
    [(0, '1', 'prev'), (1, '2', 'current'), (2, '3', 'next'), (3, '4', ''), (4, '5', ''), (5, '6', ''), (9, '&raquo;', 'rightmost')]
    >>> list(paginate_index(items, 5, 10))
    [(0, '&laquo;', 'leftmost'), (2, '3', ''), (3, '4', ''), (4, '5', 'prev'), (5, '6', 'current'), (6, '7', 'next'), (7, '8', ''), (9, '&raquo;', 'rightmost')]
    """
    length = countup(iterable_or_length)
    pages, index = _normpage(length, index, divisor)

    if pages < 2: # navigation is not required
        return
    elif pages <= width:
        for i in xrange(pages):
            yield i, str(i + 1), toggle(prev=i == (index - 1),
                                        current=i == index,
                                        next=i == (index + 1))
    else:
        if index > pages - width:
            median = pages - float(width) / 2
        elif index < width:
            median = float(width) / 2
        else:
            median = index
        leftmost = 0
        rightmost = pages - 1
        begin = int(limit(median - float(width) / 2, leftmost, rightmost))
        end = int(limit(begin + width, leftmost, rightmost))
        if left and begin != leftmost:
            yield leftmost, left, 'leftmost'
        for i in xrange(begin, end + 1):
            yield i, str(i + 1), toggle(prev=i == (index - 1),
                                        current=i == index,
                                        next=i == (index + 1))
        if right and end != rightmost:
            yield rightmost, right, 'rightmost'


def parse_ua(text):
    result = []
    for whole, product, comment in re.findall('((\S+)\s*(\([^)]+\))?)', text):
        result.append(whole)
        result.append(product)
        result.append(product.split('/')[0])
        for item in re.split(';\s*', comment[1:-1]):
            result.append(item)
            result.append(re.sub('(:?[^a-zA-Z])[\d.]+$', '', item))
    _result = set()
    for i in result:
        i = i.strip()
        if i:
            _result.add(i)
            _result.add(i.lower())
    return _result


default_namespace = {
    'renderString': renderString,
    'renderFile': renderFile,
    'open2': open2,
    'fssafe': fssafe,
    'overlay': overlay,
    'ring': ring,
    'parity': parity,
    'toggle': toggle,
    'limit': limit,
    'paginateItems': paginate_items,
    'paginateIndex': paginate_index,
    'parseUserAgent': parse_ua,
    #and others such as web.utils ...
    }


class Codec(object):
    """
    >>> import base64
    >>> class TestCodec(Codec):
    ...     name = 'test'
    ...     def _encode(self, input, errors):
    ...         return base64.encodestring(input)
    ...     def _decode(self, input, errors):
    ...         return base64.decodestring(input)
    >>> test = TestCodec()
    >>> test.register()
    >>> 'abc'.encode('test')
    'YWJj\\n'
    >>> test.unregister()
    """
    name = '' # codec name
    aliases = () # alias names

    def register(self):
        sys.modules['encodings.' + self.name] = self
        for alias in self.aliases:
            encodings.aliases.aliases[alias] = self.name

    def unregister(self):
        sys.modules.pop('encodings.' + self.name, None)
        for alias in self.aliases:
            encodings.aliases.aliases.pop(alias, None)

    def getregentry(self):
        return codecs.CodecInfo(
            name=self.name,
            encode=self.encode,
            decode=self.decode,
            #incrementalencoder=self.IncrementalEncoder,
            #incrementaldecoder=self.IncrementalDecoder,
            #streamwriter=self.StreamWriter,
            #streamreader=self.StreamReader,
            )

    def _encode(self, input, errors='strict'):
        raise NotImplemented

    def _decode(self, input, errors='strict'):
        raise NotImplemented

    def encode(self, input, errors='strict'):
        result = self._encode(input, errors)
        if isinstance(result, tuple):
            return result
        else:
            return result, len(input)

    def decode(self, input, errors='strict'):
        result = self._decode(input, errors)
        if isinstance(result, tuple):
            return result
        else:
            return result, len(input)

    #@property
    #def IncrementalEncoder(self):
    #    __module__ = self
    #    class IncrementalEncoder(codecs.IncrementalEncoder):
    #        def encode(self, input, final=False):
    #            return __module__.encode(input)[0]
    #    return IncrementalEncoder

    #@property
    #def IncrementalDecoder(self):
    #    __module__ = self
    #    class IncrementalDecoder(codecs.IncrementalDecoder):
    #        def decode(self, input, final=False):
    #            return __module__.decode(input)[0]
    #    return IncrementalDecoder

    #@property
    #def StreamReader(self):
    #    __module__ = self
    #    class StreamReader(codecs.StreamReader):
    #        def decode(self, input, errors='strict'):
    #            return __module__.decode(input, errors)
    #    return StreamReader

    #@property
    #def StreamWriter(self):
    #    __module__ = self
    #    class StreamWriter(codecs.StreamWriter):
    #        def decode(self, input, errors='strict'):
    #            return __module__.decode(input, errors)
    #    return StreamWriter


class PercentEscapeCodec(Codec):
    """
    >>> u'a, b, c'.encode('percent')
    'a,%20b,%20c'
    >>> u'?query'.encode('uri')
    '%3Fquery'
    >>> 'q%3Dkeyword'.decode('uri')
    u'q=keyword'
    """

    name = 'percent'
    aliases = ('uri', )

    def _encode(self, input, errors='strict'):
        assert isinstance(input, unicode)
        assert errors == 'strict'
        input = input.encode('utf-8')
        return re.sub('([^0-9A-Za-z_!\'()*-.~])',
                      lambda m: '%%%.2X' % ord(m.group()), input)

    def _decode(self, input, errors='strict'):
        assert isinstance(input, str)
        assert errors == 'strict'
        result = re.sub(
            '%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), input)
        return result.decode('utf-8')


class XMLEntityCodec(Codec):
    """
    >>> '<tag attr="val"/>'.encode('xml')
    '&lt;tag attr="val"/&gt;'
    >>> '&lt;tag attr="val"/&gt;'.decode('xml')
    '<tag attr="val"/>'
    """

    name = 'xml'

    def _encode(self, input, errors='strict'):
        assert errors == 'strict'
        return saxutils.escape(input)

    def _decode(self, input, errors='strict'):
        assert errors == 'strict'
        return saxutils.unescape(input)


percentescape = PercentEscapeCodec()
percentescape.register()
xmlentity = XMLEntityCodec()
xmlentity.register()


if __name__ == '__main__':
    # To upload to PyPI, run `katagami.py test check sdist upload`.

    if len(sys.argv) >= 2 and sys.argv[1] == 'run':
        if os.path.isfile(sys.argv[2]):
            result = renderFile(sys.argv[2], returns_unicode=True)
        else:
            data = sys.stdin.read()
            data = data.decode(sys.stdin.encoding or 'utf-8')
            result = renderString(data, returns_unicode=True)
        sys.stdout.write(result.encode(sys.stdout.encoding or 'utf-8'))
        raise SystemExit

    if 'check' in sys.argv:
        import doctest
        tmpdir = tempfile.mkdtemp()
        try:
            doctest.testmod()
        finally:
            shutil.rmtree(tmpdir)

    __name__ = os.path.splitext(os.path.basename(__file__))[0]
    sys.modules[__name__] = sys.modules['__main__']
    from distutils.core import setup
    setup(
        name=__name__,
        version=__version__,
        description=__doc__.splitlines()[0],
        long_description=__doc__,
        author=__author__,
        author_email=__author_email__,
        url=__url__,
        classifiers=[
            'Development Status :: 4 - Beta',
            #'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: Markup :: HTML',
            'Topic :: Text Processing :: Markup :: XML',
            ],
        license=__license__,
        py_modules=[__name__, ],
        )


