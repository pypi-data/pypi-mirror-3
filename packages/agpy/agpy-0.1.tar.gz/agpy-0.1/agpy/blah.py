## {{{ http://code.activestate.com/recipes/131495/ (r3)
#
# first solution:
#

class sample(object):
    def __init__(self):
        #class datastore(object):
        #    class one(object):
        #        def __get__(self, obj, type=None):
        #            print "computing ..."
        #            print "obj is ",obj
        #            obj.one = 1
        #            return 1
        #    one = one()
        #print "Before setting..."
        #self.datastore = datastore()
        #print "Declared datastore"
        #self.__dict__.update(self.datastore.__class__.__dict__)
        #print "After setting..."

        setattr(self.__class__,'one',property(lambda x: 'two'))

x1=sample()
print "x is ",x1
print "x.one: ",x1.one
print "x.one: ",x1.one

class sample2(object):
    def __init__(self):

        self.__dict__['one'] = property(lambda: 1)
    

x2 = sample2()
print "x2 is ",x2
print "x2.one: ",x2.one
print "x2.one: ",x2.one
        

class sample(object):
    class one(object):
        def __get__(self, obj, type=None):
            print "computing ... obj is ",obj
            obj.one = 1
            return 1
    one = one()

x=sample()
print "x is ",x
print "x.one: ",x.one
print "x.one: ",x.one



#
# other solution:
#  

# lazy attribute descriptor
class lazyattr(object):
    def __init__(self, fget, doc=''):
        self.fget = fget
        self.__doc__ = doc
    def __appoint__(self, name, cl_name):
        if hasattr(self,"name"):
            raise SyntaxError, "conflict between "+name+" and "+self.name
        self.name = name        
    def __get__(self, obj, cl=None):
        if obj is None:
            return self
        value = self.fget(obj)
        setattr(obj, self.name, value)
        return value

# appointer metaclass:
# call the members __appoint__ method 
class appointer(type):
    def __init__(self, cl_name, bases, namespace):
        for name,obj in namespace.iteritems():
            try:
                obj.__appoint__(name, cl_name)
            except AttributeError:
                pass
        super(appointer, self).__init__(cl_name, bases, namespace)

# base class for lazyattr users
class lazyuser(object):
    __metaclass__ = appointer

# usage sample
class sample(lazyuser):
    def one(self):
        print "computing ..."
        return 1
    one  = lazyattr(one, "one lazyattr")

x=sample()
print x.one
print x.one
del x.one
print x.one
## end of http://code.activestate.com/recipes/131495/ }}}

