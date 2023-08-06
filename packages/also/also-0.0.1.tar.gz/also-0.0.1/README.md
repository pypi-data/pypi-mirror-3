Also
====

Ever had lots of methods that do the same thing?!
You want to set them to the same thing but dont want to do something lame like
```python
   def method(self):
       pass

   othermethod = method
```

Rather you want to do it with style like

```python
   @also('othermethod')
   def method(self):
       pass
```

Then do I have a solution for you!

###### Basic Usage
```python
from also import also, AlsoMetaClass

class Foo:
    __metaclass__ = AlsoMetaClass

    @also('getThing')
    @also('get_thing')
    def getthing(self):
        return 'go bears'

foo = Foo()
assert (foo.getthing() == foo.get_thing() == 
        foo.getThing() == 'go bears')
```
