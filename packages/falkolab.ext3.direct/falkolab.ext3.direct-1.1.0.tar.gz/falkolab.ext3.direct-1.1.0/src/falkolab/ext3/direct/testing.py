from falkolab.ext3.direct.decorator import directMethod
__docformat__ = "reStructuredText"

import os
from zope.app.testing.functional import ZCMLLayer

class AlbumList(object):
  
    @directMethod()
    def getAll(self):
        return [1,2,3]

    @directMethod(formHandler=True)
    def add(self):
        return "ok"
  
class Contact(object):
 
    @directMethod()
    def getInfo(self, id):
        if id==1:
            return {'name': 'Albert', 'age': 23}
        else:
            return {'name': 'Ivan', 'age': 30}

ExtDirectFunctionalTestsLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ExtDirectFunctionalTestsLayer', allow_teardown=True)


