# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from .io import (
    OmooAssetMenu,
    ImportOmooAsset
)
from .aces import (
    FixColorSpaceAll,
    FixColorSpaceSelected,
    FixColorSpace_PT_Panel
)
import bpy


bl_info = {
    "name": "Omoo Asset",
    "author": "MaNan",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "File > Import-Export",
    "warning": "",
    "category": "Import-Export"
}


CLASSES = [
    ImportOmooAsset,
    FixColorSpaceAll,
    FixColorSpaceSelected,
    FixColorSpace_PT_Panel
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    OmooAssetMenu.register()


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    OmooAssetMenu.unregister()
