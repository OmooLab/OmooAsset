import bpy
from .io import ImportOmooAsset


def TOPBAR_FILE_IMPORT(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(ImportOmooAsset.bl_idname)


def create_menu():
    bpy.types.TOPBAR_MT_file_import.append(TOPBAR_FILE_IMPORT)


def remove_menu():
    bpy.types.TOPBAR_MT_file_import.remove(TOPBAR_FILE_IMPORT)
