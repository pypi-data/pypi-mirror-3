from Products.ATContentTypes.content import base

from dummy_schema import IEmptySchema

class DummyClass(base.ATCTContent):

    def getSchemaForTransition(self, transition):
        """Return a dummy schema interface"""
        if transition == 'empty':
            return IEmptySchema
