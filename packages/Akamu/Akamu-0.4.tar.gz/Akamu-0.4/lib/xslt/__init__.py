__author__ = 'chimezieogbuji'

import cgi, inspect
from cStringIO   import StringIO
from amara.xslt  import transform
from akara       import request, response, global_config
from Ft.Xml.Xslt import Processor
from Ft.Xml      import InputSource
from Ft.Lib      import Uri

from akamu.xslt.extensions import NS

def TransformWithAkamuExtensions(src,xform,manager,params=None,baseUri=NS):
    params = params if params else {}
    processor         = Processor.Processor()
    processor.manager = manager
    processor.registerExtensionModules(['akamu.xslt.extensions'])

    result = StringIO()
    source = InputSource.DefaultFactory.fromString(src,baseUri)
    isrc   = InputSource.DefaultFactory.fromString(xform,baseUri)
    processor.appendStylesheet(isrc)
    processor.run(
        source,
        outputStream=result,
        ignorePis=True,
        topLevelParams=params
    )
    return result.getvalue()

NOOPXML = u'<Root/>'

class xslt_rest(object):
    """
    Decorator of Akara services that will cause all invokations to
    route HTTP (query or form) parameters into the transform as
    xslt parameters.  The source of the transform (a string) is given by applying
    a user-specified function against the parameters and
    the result of the transformation of this (using a user-specified
    transform) is used as the result of the service
    """
    def __init__(self, transform, source = None, argRemap = None, parameters = None):
        self.argRemap  = argRemap if argRemap else {}
        self.transform = transform
        self.params    = parameters if parameters else {}
        self.source = source if source else None

    def __call__(self, func):
        def innerHandler(*args, **kwds):
            argNames = inspect.getargspec(func).args
            parameters = self.params
            isaPost = len(args) == 2 and list(argNames) == ['body','ctype']
            if isaPost:
                #Parameters in POST body
                for k,vals in cgi.parse_qs(args[0]).items():
                    if k in self.argRemap:
                        parameters[self.argRemap[k]] = vals[0]
                    else:
                        parameters[k] = vals[0]
            else:
                #parameters to service method are GET query arguments
                for idx,argName in enumerate(argNames):
                    if argName in self.argRemap:
                        parameters[self.argRemap[argName]] = args[idx] if len(args) > idx + 1 else kwds[argName]
                    elif len(args) > idx + 1 or argName in kwds:
                        parameters[argName] = args[idx] if len(args) > idx + 1 else kwds[argName]
                for k,v in kwds.items():
                    if k in self.argRemap:
                        parameters[self.argRemap[k]] = v
                    else:
                        parameters[k] = v

            argInfo = inspect.getargspec(func)
            if isaPost:
                src = func(**parameters
                ) if parameters else func() if not self.source else self.source
            elif argInfo.varargs and argInfo.keywords:
                src = func(*args, **kwds) if not self.source else self.source
            elif argInfo.varargs:
                src = func(*args) if not self.source else self.source
            elif argInfo.keywords:
                src = func(**kwds) if not self.source else self.source
            else:
                src = func() if not self.source else self.source
            isInfoResource = (isinstance(response.code,int) and
                              response.code == 200
                             ) or (isinstance(response.code,basestring) and
                                   response.code.lower()) == '200 ok'
            if not isInfoResource:
                #If response is not a 200 then we just return it (since we can't
                # be invoking an XSLT HTTP operation)
                return src
            else:
                if isinstance(src,tuple) and len(src)==2:
                    src,newParams = src
                    parameters.update(newParams)
                authenticatedUser = request.environ.get('REMOTE_USER')
                if authenticatedUser:
                    parameters[u'user'] = authenticatedUser
                return transform(src,self.transform,params=parameters)
        return innerHandler