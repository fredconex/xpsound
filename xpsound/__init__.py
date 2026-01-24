bl_info = {
    "name": "Dreamfoil Utils: XPSound",
    "author": "Alfredo Fernandes",
    "version": (0, 9, 5),
    "blender": (2, 80, 0),
    "location": "Properties > Data",
    "description": "Addon for X-Plane .snd file creation",
    "warning": "",
    "wiki_url": "https://github.com/fredconex/xpsound",
    "category": "Object",
}

if "bpy" in locals():
    import importlib
    if "xpsound_props" in locals():
        importlib.reload(xpsound_props)
    if "xpsound_ops" in locals():
        importlib.reload(xpsound_ops)
    if "xpsound_ui" in locals():
        importlib.reload(xpsound_ui)
    if "xpsound_import" in locals():
        importlib.reload(xpsound_import)
    if "xpsound_export" in locals():
        importlib.reload(xpsound_export)
    if "xpsound_helper" in locals():
        importlib.reload(xpsound_helper)

import bpy
from . import xpsound_props, xpsound_ops, xpsound_ui, xpsound_export, xpsound_import, xpsound_helper

def register():
    xpsound_props.register()
    xpsound_ops.register()
    xpsound_ui.register()
    xpsound_import.register()
    xpsound_export.register()
    xpsound_helper.register()

def unregister():
    xpsound_props.unregister()
    xpsound_ops.unregister()
    xpsound_ui.unregister()
    xpsound_import.unregister()
    xpsound_export.unregister()
    xpsound_helper.unregister()

if __name__ == "__main__":
    register()
