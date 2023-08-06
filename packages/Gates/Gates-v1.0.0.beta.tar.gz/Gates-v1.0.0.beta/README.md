Author: I (iroiso at live dot com)  
License: Apache License 2.0  
&copy; 2011, June inc.  

Gates 
=====
Minimal, fast and intuitive REST HTTP services in python.  
features:  

+ Plain, JAX-RS like http verb mapping and routing.
+ WSGI 1.0 compatibility.
+ Plain simple form handling.
+ No inbuilt templating, Use your favorite.
+ No built in session management.
+ Database agnostic. [Check out "http://github.com/junery/homer" for persistence]


Sample Code:  
------------  
Hello world through the Gates,

```python
from gates.core import run, Application, Resource, Path, Route, GET

@Path("/hello")
class HelloResource(Resource):
    '''The simplest resource you can conceive'''

    @GET
    @Route("/{name}")
    def hello(self, name):
        self.response.write("Hello %s !" % name)

#Deploying and running.
root = Application(base="/", resources=[HelloResource,])
run(root)

```
Now visit http://localhost:8080/hello/iroiso in your browser.

Notes:
------
Another opensource project made with love in the Junery; pragmatic, simple,  
beautiful and pleasurable to use.
