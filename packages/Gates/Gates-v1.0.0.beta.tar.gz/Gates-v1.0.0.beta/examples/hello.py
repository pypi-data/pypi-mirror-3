"""
Author: I (iroiso@live.com)
Copyright 2012, June Inc.
"""
from gates.core import Resource, Application, Path, Route, GET,  run

@Path("/hello")
class HelloResource(Resource):
    '''Hello world through Gates'''

    @GET
    @Route("/{name}")
    def hello(self, name):
        self.response.write("Hello %s!" % name)


if __name__ == "__main__":
    application = Application(resources=[HelloResource,])
    run(application)
