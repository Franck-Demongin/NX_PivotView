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

bl_info = {
    "name" : "NX_PivotView",
    "author" : "Franck Demongin",
    "description" : "Set pivot view by left click.",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "3D View > View > Set Pivot View",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

class OBJECT_OT_pivotView(bpy.types.Operator):
    """Set pivot view by left click"""
    bl_idname = "object.pivot_view"
    bl_label = "Pivot View"

    initial_tool: bpy.props.StringProperty()
    cursor_initial_loc: bpy.props.FloatVectorProperty()
    
    def reset_view(self, context):
        area = next(iter([area for area in context.screen.areas if area.type == 'VIEW_3D']))
        with context.temp_override(area=area):
            bpy.ops.wm.tool_set_by_id(name=self.initial_tool)
        context.scene.cursor.location = self.cursor_initial_loc
    
    def modal(self, context, event):        
        if event.type in {'LEFTMOUSE', 'WHEELDOWNMOUSE', 'WHEELUPMOUSE', 'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.reset_view(context)
            return {'CANCELLED'}
        
        elif event.type in {'SPACE', 'RET'}:
            object_active = context.object
            objects_selected = context.selected_objects
            
            areas = [area for area in context.screen.areas if area.type == 'VIEW_3D']
            for area in areas:
                region = next(iter([region for region in area.regions if region.type == 'WINDOW']))
                with context.temp_override(area=area, region=region):
                    bpy.ops.view3d.view_center_cursor()
            
            for obj in objects_selected:
                obj.select_set(True)
            context.view_layer.objects.active = object_active
            self.reset_view(context)
            
            return {'FINISHED'}        

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
       
        self.cursor_initial_loc = context.scene.cursor.location.copy()
        
        area = next(iter([area for area in context.screen.areas if area.type == 'VIEW_3D']))
        with context.temp_override(area=area):
            tool_initial = ToolSelectPanelHelper.tool_active_from_context(context)
            self.initial_tool = tool_initial.idname
            bpy.ops.wm.tool_set_by_id(name="builtin.cursor")
            tool = ToolSelectPanelHelper.tool_active_from_context(context)
            props = tool.operator_properties('view3d.cursor3d')
            props.use_depth = True
            props.orientation = 'GEOM'
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_pivotView.bl_idname, text=OBJECT_OT_pivotView.bl_label)

addon_keymaps = []

def register():
    bpy.utils.register_class(OBJECT_OT_pivotView)
    bpy.types.VIEW3D_MT_view.append(menu_func)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(OBJECT_OT_pivotView.bl_idname, type='SEMI_COLON', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_pivotView)
    bpy.types.VIEW3D_MT_view.remove(menu_func)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
