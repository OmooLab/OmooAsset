from . import auto_load
from . import menu


bl_info = {
    "name": "Omoo Asset",
    "author": "MaNan",
    "description": "",
    "blender": (4, 0, 0),
    "version": (0, 1, 0),
    "location": "File > Import-Export",
    "warning": "",
    "category": "Import-Export"
}

auto_load.init()


def register():
    auto_load.register()
    menu.create_menu()


def unregister():
    try:
        menu.remove_menu()
        auto_load.unregister()
    except RuntimeError:
        pass
