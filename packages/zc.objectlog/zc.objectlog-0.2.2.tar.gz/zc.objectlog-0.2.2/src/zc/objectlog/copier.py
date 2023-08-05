
import zope.component
import zope.interface
import zc.copy.interfaces
from zc.objectlog import interfaces, log

@zope.component.adapter(interfaces.ILog)
@zope.interface.implementer(zc.copy.interfaces.ICopyHook)
def objectlog_copyfactory(original):
    def factory(location, register):
        obj = log.Log(original.record_schema)
        def reparent(convert):
            obj.__parent__ = convert(original.__parent__)
            obj.__name__ = obj.__name__
        register(reparent)
        return obj
    return factory
