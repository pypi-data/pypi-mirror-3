# -*- coding: UTF-8 -*-
## Copyright 2011-2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""

This is a simplistic method for generating XML strings.

Primary design goal is to avoid redundancy and to allow for concise code.

There are probably still important lacks. Some known issues:

- no structure checking is done
- it is not possible to generate XML strings with tags or attributes 
  consisting of non-asci characters

Usage example
-------------

>>> from lino.utils.xmlgen import *

First we define the equivalent of an XML Schema by creating a set 
of Namespace subclasses.

For example, here is the definition of a SOAP envelope:

>>> class soap(Namespace):
...   url = "http://schemas.xmlsoap.org/soap/envelope/"

>>> class Envelope(Container):
...     namespace = soap
...     class Body(Container):
...         pass

And here the definition of a :term:`BCSS` connector:

>>> class bcss(Namespace):
...     url = "http://ksz-bcss.fgov.be/connectors/WebServiceConnector"

>>> class xmlString(Container):
...     namespace = bcss
...

Then we instantiate these classes to create our XML tree:

>>> env = Envelope(Envelope.Body(xmlString(CDATA("FooBar"))))

We render the XML string by calling the :meth:`Element.tostring` 
method on the root element:

>>> print env.tostring(pretty=True)
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
<bcss:xmlString xmlns:bcss="http://ksz-bcss.fgov.be/connectors/WebServiceConnector">
<![CDATA[FooBar]]>
</bcss:xmlString>
</soap:Body>
</soap:Envelope>

If you set a default namespace, another :meth:`Element.tostring()` 
call on the same tree instance
will return slightly different result:

>>> set_default_namespace(soap)
>>> print env.tostring(pretty=True)
<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
<Body>
<bcss:xmlString xmlns:bcss="http://ksz-bcss.fgov.be/connectors/WebServiceConnector">
<![CDATA[FooBar]]>
</bcss:xmlString>
</Body>
</Envelope>

>>> set_default_namespace(bcss)
>>> print env.tostring(pretty=True)
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
<xmlString xmlns="http://ksz-bcss.fgov.be/connectors/WebServiceConnector">
<![CDATA[FooBar]]>
</xmlString>
</soap:Body>
</soap:Envelope>

The prefix of a Namespace is the class's name by default, 
but it is possible to give another value:

>>> soap.set_prefix('foo')
>>> print env.tostring(pretty=True)
<foo:Envelope xmlns:foo="http://schemas.xmlsoap.org/soap/envelope/">
<foo:Body>
<xmlString xmlns="http://ksz-bcss.fgov.be/connectors/WebServiceConnector">
<![CDATA[FooBar]]>
</xmlString>
</foo:Body>
</foo:Envelope>



Notes
-----

Another example:

>>> class Foo(Container): 
...   class Bar(Container):
...     class Name(String): pass
...   class Baz(Container):
...     class Name(String): pass
...     class Period(String): pass

>>> print Foo(Foo.Baz.Name("Luc")).tostring(True)
<Foo>
<Name>Luc</Name>
</Foo>

>>> print Foo(Foo.Bar(Foo.Baz.Period("1968-2011"))).tostring(True)
<Foo>
<Bar>
<Period>1968-2011</Period>
</Bar>
</Foo>



"""

unused = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<xmlString xmlns="http://ksz-bcss.fgov.be/connectors/WebServiceConnector">
<![CDATA[FooBar]]>
</xmlString>
</soap:Body>
</soap:Envelope>

"""

import datetime
import types
from xml.dom.minidom import parseString
from lino.utils import isiterable

def assert_equivalent(s1,s2,write_diag_files=False):
    if s1 == s2:
        return
    dom1 = parseString(s1)
    dom2 = parseString(s2)
    if dom1 != dom2:
        s1 = s1.replace('><','>\n<')
        s2 = s2.replace('><','>\n<')
        l1 = s1.splitlines()
        l2 = s2.splitlines()
        if l1 == l2 : return
        from difflib import Differ
        d = Differ()
        result = list(d.compare(l1, l2))
        print '\n'.join(result)
        if write_diag_files:
            open('s1.xml','w').write(s1)
            open('s2.xml','w').write(s2)
        raise Exception("XML strings are different")



def quote(x):
    if isinstance(x,int):
        return '"'+str(x)+'"'
    if isinstance(x,bool):
        return '"'+str(x).lower()+'"'
    if isinstance(x,basestring):
        assert not '"' in x
        return '"' + x + '"'
    raise Exception("%s not handled" % str(type(x)))


class UniStringIO:
    def __init__(self,s=u''):
        self.buffer = s
    def write(self,s):
        #self.s += s.encode('utf-8')
        self.buffer += unicode(s)
    def getvalue(self):
        return self.buffer
    def __str__(self):
        return repr(self.buffer)


        
        
        
class Attribute(object):
    def __init__(self,name=None,**kw):
        self.name = name
        
class Node(object):
    def __xml__(self,wr):
        raise NotImplementedError()
    
class CDATA(Node):
    def __init__(self,data):
        self.data = data
    def __xml__(self,wr):
        wr.write("<![CDATA[%s]]>" % self.data)
    
class TEXT(Node):
    def __init__(self,data):
        self.data = data
    def __xml__(self,r):
        r.py2xml(self.data)
        #~ wr.write(self.data)
    
        
class ElementMetaClass(type):
    def __new__(meta, classname, bases, classDict):
      
        classDict.setdefault('elementname',classname)
        #~ classDict['allowedAttribs'] = allowedAttribs
        #~ classDict['used_namespaces'] = []
        cls = type.__new__(meta, classname, bases, classDict)
        allowedAttribs = {}
        def collect(cl,to):
            for b in cl.__bases__:
                collect(b,to)
            for k,v in cl.__dict__.items():
                if isinstance(v,Attribute):
                    to[k] = v
        collect(cls,allowedAttribs)                
        for k,v in cls.__dict__.items():
            if isinstance(v,Attribute):
                if not v.name:
                    v.name = k
                allowedAttribs[k] = v
        cls.allowedAttribs = allowedAttribs
        return cls
    
class Element(Node):
    __metaclass__ = ElementMetaClass
    elementname = None
    namespace = None
    parent = None
    allowedValues = None
    #~ is_root = False
    #~ default_namespace = None
    used_namespaces = []
    
    def __init__(self,value=None,**kw):
        #~ if self.elementname is None:
            #~ self.elementname = self.__class__.__name__
        self.value = self.validate(value)
        self._attribs = {}
        self.update(**kw)
        
    def validate(self,v):
        if self.allowedValues and not v in self.allowedValues:
            raise Exception(
              "Invalid value %r (must be one of %s)" % (
                v,self.allowedValues))
        return v
        

    def update(self,**kw):
        # the default namespace is stored separately
        #~ ns = kw.pop('defaultns',None)
        #~ if ns:
            #~ self.default_namespace = ns
        for k,v in kw.items():
            #assert not k in self.defaultAttribs.keys()
            try:
                xmlname = self.allowedAttribs[k]
            except KeyError,e:
                raise Exception(
                    "%s attribute not allowed for %s (%s)." % (
                    repr(k), self.__class__.__name__,self.allowedAttribs))
            self._attribs[k] = v
            
    def __getattr__(self,name):
        try:
            return self._attribs[name]
        except KeyError:
            if self.allowedAttribs.has_key(name):
                return None
            raise AttributeError(
                "%s instance has no attribute '%s'" % (
                self.__class__.__name__, name))
        
    def set_parent(self,p):
        self.parent = p
        
    def get_namespace(self):
        if self.namespace is not None:
            return self.namespace
        if self.parent is not None:
            return self.parent.get_namespace()
        return None
            
    def tag(self):
        ns = self.get_namespace()
        if ns is None or ns == _default_namespace:
            return self.elementname
            #~ if self.parent and self.parent.default_namespace != self.namespace:
            #~ if not self.namespace.isdefault:
        return ns.prefix+ ":" + self.elementname
    
    def writeAttribs(self,wr):
        #~ if self.parent is None: # it's the root element
        if self.namespace is not None:
            if self.namespace == _default_namespace:
                wr.write(' xmlns="%s"' % self.namespace.url)
            for ns in self.used_namespaces:
                if ns != _default_namespace:
                    wr.write(' xmlns:%s="%s"' % (ns.prefix,ns.url))
        for k,v in self._attribs.items():
            a = self.allowedAttribs.get(k)
            wr.write(' %s=%s' % (a.name,quote(v)))
            
    def __xml__(self,wr):
        wr.write("<" + self.tag())
        self.writeAttribs(wr)
        
        if self.value is None:
            wr.write('/>')
        else:
            wr.write('>')
            wr.py2xml(self.value2string(self.value))
            wr.write("</"+self.tag()+">" )
            
    def value2string(self,v):
        return v
        
        
    def tostring(self,pretty=False,**kw):
        """
        Generate and return the XML string.
        """
        u = UniStringIO()
        wr = Writer(u)
        self.__xml__(wr,**kw)
        if pretty:
            return u.getvalue().replace("><",">\n<")
            #~ return parseString(u.getvalue()).toprettyxml()
        return u.getvalue()
        
#~ class Javascript(Element):
    #~ def __xml__(self,wr):
        #~ wr.write("<" + self.tag())
        #~ self.writeAttribs(wr)
        
        #~ if self.value is None:
            #~ wr.write('/>')
        #~ else:
            #~ wr.write('>')
            
            #~ wr.py2xml(self.value2string(self.value))
            #~ wr.write("</"+self.tag()+">" )
    
        
        
from django.utils.functional import Promise
from django.utils.encoding import force_unicode

class Writer(object):
  
    def __init__(self,file=None):
        self.file = file
        
    def write(self,s):
        self.file.write(s)
        
    def writeln(self,s):
        self.file.write(s+'\n')
        
    def tostring(self,x):
        oldfile = self.file
        self.file = UniStringIO()
        #~ wr = cls(u)
        self.render(x)
        v = self.file.getvalue()
        self.file = oldfile
        return v
        
    def py2xml(self,value): # ,indent='',addindent='',newl=''
        #~ if isinstance(value,(list,tuple)):
        if isinstance(value,basestring):
            self.write(value)
        elif isinstance(value,types.GeneratorType):
            for e in value:
                #~ self.write('\n')
                self.py2xml(e)
        elif isiterable(value):
            for e in value:
                self.py2xml(e)
        elif isinstance(value,Node):
            value.__xml__(self)
        elif isinstance(value,Promise):
            self.write(force_unicode(value))
        else:
            #~ raise Exception("Invalid value %r" % value)
            self.write(str(value))
    render = py2xml

class ContainerMetaClass(ElementMetaClass):
    def __new__(meta, classname, bases, classDict):
      
        if not classDict.has_key('allowedChildren'):
            allowedChildren = []
            for k,v in classDict.items():
                if isinstance(v,type) and issubclass(v,Element):
                    allowedChildren.append(v)
            classDict['allowedChildren'] = allowedChildren
        cls = ElementMetaClass.__new__(meta, classname, bases, classDict)
        return cls


class Container(Element):
    __metaclass__ = ContainerMetaClass
    """
    A Container is an Element whose `value` 
    is the list of the contained elements.
    """
    allowedChildren = None
    
    def __init__(self,*nodes,**attribs):
        # note that we remove the '*'
        self.used_namespaces = []
        if self.namespace is not None:
            self.used_namespaces.append(self.namespace)
        for e in nodes:
            if isinstance(e,Element):
                e.set_parent(self)
                if e.namespace is None:
                    for ns in e.used_namespaces:
                        if not ns in self.used_namespaces:
                            self.used_namespaces.append(ns)
        Element.__init__(self,list(nodes),**attribs)
        #~ Element.__init__(self,nodes,**attribs)
        
    def add_child(self,e):
        self.value.append(e)
        return e
        
    def find_node(self,cl):
        """
        Find the first child of specified class.
        """
        for n in self.value:
            if isinstance(n,cl): 
                return n
        return self.add_child(cl())
        
    #~ def __xml__(self,wr):
        #~ wr("<" + self.tag())
        #~ self.writeAttribs(wr)
        
        #~ if len(self.value) == 0:
            #~ wr('/>')
        #~ else:
            #~ wr('>')
            #~ for e in self.value:
                #~ e.__xml__(wr)
            #~ wr("</"+self.tag()+">" )


    #~ @classmethod
    #~ def collect_children(cls,ns,classname):
        #~ for k,v in cls.__dict__.items():
            #~ if k != 'parent':
                #~ if isinstance(v,type) and issubclass(v,Element):
                    #~ v.parent = cls
                    #~ if ns.has_key(k):
                        #~ raise Exception(
                            #~ "Duplicate element name %s in namespace %s"
                            #~ % (k,classname))
                    #~ ns[k] = v
                    #~ if issubclass(v,Container):
                        #~ v.collect_children(ns,classname)
                




class NamespaceMetaClass(type):
    def __new__(meta, classname, bases, classDict):
        if classname != 'Namespace':
          
            if not classDict.has_key('prefix'):
                classDict['prefix'] = classname
                
            #~ classDict.setdefault('prefix',classname)
            
            #~ for k,v in classDict.items():
                #~ if isinstance(v,type) and issubclass(v,Element):
                    #~ v.collect_children(classDict,classname)
                    
            # verify that there is only one root element.
            #~ root = None
            #~ for k,v in classDict.items():
                #~ if isinstance(v,type) and issubclass(v,Element):
                    #~ if root is None:
                        #~ root = v
                    #~ else:
                        #~ raise Exception(
                          #~ "More than one root elements in namespace %s" 
                          #~ % classname)
          
            #~ if root is None:
                #~ raise Exception(
                  #~ "No root element found in namespace %s" 
                  #~ % classname)

            #~ root.collect_children(classDict,classname)
            
            #~ children = {}
            #~ extract_elements(ns,classDict,False)
            
        
            #~ for k,v in children.items():
                #~ if classDict.has_key(k):
                    #~ raise Exception(
                        #~ "Duplicate element name %r in namespace %r" 
                        #~ % (k,classname))
                #~ classDict[k] = v
        
        cls = type.__new__(meta, classname, bases, classDict)
        
        for k,v in classDict.items():
            if isinstance(v,type) and issubclass(v,Element):
                assert v.namespace is None
                v.namespace = cls
          
        return cls
  

class Namespace(object):
    prefix = None
    url = None
    __metaclass__ = NamespaceMetaClass
    
    @classmethod
    def set_prefix(cls,prefix):
        cls.prefix = prefix
    

#~ # currently not used:
#~ class xsi(Namespace):
    #~ url = "http://www.w3.org/2001/XMLSchema-instance"
#~ class xsd(Namespace):
    #~ url = "http://www.w3.org/2001/XMLSchema"
    
_default_namespace = None

def set_default_namespace(ns):
    """
    Declares the specified namespace as default namespace.
    """
    global _default_namespace
    _default_namespace = ns
    
    

class String(Element):
    pass
  

class Integer(Element):
  
    def validate(self,v):
        if not isinstance(v,int):
            raise Exception("%r is not an integer" % v)
        return Element.validate(self,v)
        
    def value2string(self,v):
        return str(v)
        
class DateTime(Element):
  
    def validate(self,v):
        if not isinstance(v,datetime.datetime):
            raise Exception("%r is not a datetime instance" % v)
        return Element.validate(self,v)
        
    def value2string(self,v):
        return v.strftime("%Y%m%dT%H%M%S")
        
class Date(Element):
    def validate(self,v):
        if isinstance(v,datetime.date):
            return Element.validate(self,v)
        raise Exception("%r is not a valid value for Date element" % v)
    def value2string(self,v):
        return v.strftime("%Y-%m-%d")


      
class EmailAddress(String): pass
  

    
        

__all__ = [
    'Namespace', 
    'String', 'Integer', 
    'EmailAddress', 'Date',
    'CDATA', 'Container', 
    'set_default_namespace',
    'assert_equivalent' ]

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

