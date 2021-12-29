
# master/develop

bl_info = {
    'name': 'virtual driver',
    'author': 'phellutone',
    'version': (0, 0, 1),
    'blender': (2, 93, 0),
    'location': 'View3D > Sidebar > Tool Tab',
    'description': 'virtual driver',
    'support': 'TESTING',
    'tracker_url': 'https://github.com/phellutone/virtual_driver/issues',
    'category': 'Object'
}

from . import virtual_driver

def register():
    virtual_driver.register()

def unregister():
    virtual_driver.unregister()
