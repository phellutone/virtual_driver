
from . import property_tracer

def register():
    property_tracer.preregister()
    property_tracer.register()

def unregister():
    property_tracer.unregister()
