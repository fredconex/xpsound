import bpy
import os

# Sound List
class XP_SOUND_UL_SOUND_LIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, icon="SPEAKER")
        
        # Button to duplicate the sound
        button_duplicate = row.operator("object.xp_sound_duplicate", text="", icon="DUPLICATE")
        button_duplicate.index = index        

        # Button to remove the sound
        button_remove = row.operator("object.xp_sound_remove", text="", icon="TRASH")
        button_remove.index = index

# Snapshot List
class XP_SOUND_UL_SNAPSHOT_LIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, icon="SPEAKER")

        # Button to remove the sound
        button_remove = row.operator("object.xp_snapshot_remove", text="", icon="TRASH")
        button_remove.index = index        

# Condition List
class XP_SOUND_UL_CONDITION_LIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.scale_y = 1.25
        row = layout.row(align=True)
        row.scale_y = 0.8
        
        # Gap at front (5%)
        split = row.split(factor=0.01)
        split.separator()
        
        # Event Type (25%)
        split = split.split(factor=0.3)
        split.prop(item, "event_type", text="")
        
        # Dataref (40%)
        split = split.split(factor=0.5)
        split.prop(item, "dataref_name", text="")
        
        # Operator (15%)
        split = split.split(factor=0.4)
        split.prop(item, "comparison_operator", text="")
        
        # Value (Rest)
        split.prop(item, "comparison_value", text="")

# Panel on Tools
class XP_SOUND_PT_TOOLS_PANEL(bpy.types.Panel):
    bl_label = "Global Settings"
    bl_idname = "VIEW3D_PT_xp_sound_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPSound"
    
    def draw(self, context):
        layout = self.layout.box()
        scene = context.scene
        
        # Global properties
        col = layout.column()
        
        # Export/Import buttons in a row
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("xpsound.import_snd", text="Import", icon="IMPORT")
        row.operator("xpsound.export_snd", text="Export", icon="EXPORT")
        
        col.separator()
        col.label(text="General:")
        col.prop(scene.xp_sound_global, "snd_filename", text="SND Filename")
        
        # Custom drawing for FMOD path
        guids_file_path = bpy.path.abspath(os.path.join("//", context.scene.xp_sound_global.fmod_path, "GUIDS.txt"))
        guids_file_path = os.path.normpath(guids_file_path)
        guid_file_exists = os.path.isfile(guids_file_path)
        
        # Check if GUIDS.txt exists
        row = col.row()
        if not guid_file_exists:
            split = row.split(factor=0.4)
        else:
            split = row.split(factor=0.7)
        
        fmod_col = split.column()
        if not guid_file_exists:
            fmod_col.alert = True
        fmod_col.prop(scene.xp_sound_global, "fmod_path", text="FMOD directory")
        
        # Add copy build files button
        button_col = split.column()
        button_col.operator("xpsound.copy_fmod_build_files", text="Copy Build Files", icon="COPYDOWN")
        
        if not guid_file_exists:
            warning_col = split.column()
            warning_col.label(text="GUIDs.txt not found!", icon='ERROR')
        
        col.prop(scene.xp_sound_global, "ref_point_y")
        col.prop(scene.xp_sound_global, "ref_point_z")
        col.prop(scene.xp_sound_global, "disable_legacy_alerts")
        col.prop(scene.xp_sound_global, "draw_helper")
        
# Global Settings panel
class XP_SOUND_PT_GLOBAL_PANEL(bpy.types.Panel):
    bl_label = "XPSound Global"
    bl_idname = "OBJECT_PT_xp_sound_global_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == "EMPTY")
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Global properties
        col = layout.column()
        
        # Export/Import buttons in a row
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("xpsound.import_snd", text="Import", icon="IMPORT")
        row.operator("xpsound.export_snd", text="Export", icon="EXPORT")
        
        col.separator()
        col.label(text="General:")
        col.prop(scene.xp_sound_global, "snd_filename", text="SND Filename")
        
        # Custom drawing for FMOD path
        guids_file_path = bpy.path.abspath(os.path.join("//", context.scene.xp_sound_global.fmod_path, "GUIDS.txt"))
        guids_file_path = os.path.normpath(guids_file_path)
        guid_file_exists = os.path.isfile(guids_file_path)
        
        # Check if GUIDS.txt exists
        row = col.row()
        if not guid_file_exists:
            split = row.split(factor=0.4)
        else:
            split = row.split(factor=0.7)
        
        fmod_col = split.column()
        if not guid_file_exists:
            fmod_col.alert = True
        fmod_col.prop(scene.xp_sound_global, "fmod_path", text="FMOD directory")
        
        # Add copy build files button
        button_col = split.column()
        button_col.operator("xpsound.copy_fmod_build_files", text="Copy Build Files", icon="COPYDOWN")
        
        if not guid_file_exists:
            warning_col = split.column()
            warning_col.label(text="GUIDs.txt not found!", icon='ERROR')
        
        col.prop(scene.xp_sound_global, "ref_point_y")
        col.prop(scene.xp_sound_global, "ref_point_z")
        col.prop(scene.xp_sound_global, "disable_legacy_alerts")
        col.prop(scene.xp_sound_global, "draw_helper")

# Empty panel
class XP_SOUND_PT_PANEL(bpy.types.Panel):
    bl_label = "XPSound Settings"
    bl_idname = "OBJECT_PT_xp_sound_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == "EMPTY")
        
    def draw(self, context):
        layout = self.layout
        obj = context.object
        xp_data = obj.xp_sound_data
        
        # Object-specific properties
        layout.prop(xp_data, "event_type")
        
        if xp_data.event_type == 'SOUND':
            self.draw_sound_properties(context, layout, obj)
        elif xp_data.event_type == 'SNAPSHOT':
            self.draw_snapshot_properties(context, layout, obj)
        elif xp_data.event_type == 'SPACE':
            self.draw_space_properties(layout, xp_data)

    def draw_space_properties(self, col, obj):
        col = col.column()
        col.prop(obj, "space_index")
        col.prop(obj, "space_blend_depth")
        
    def draw_sound_properties(self, context, layout, obj):
        # Create a list with each X-Plane sound object
        row = layout.row()
        row.template_list("XP_SOUND_UL_SOUND_LIST", "", obj.xp_sound_data, "xp_sound_list", obj.xp_sound_data, "xp_sound_index")
        
        # Add side buttons (Add, Remove, Up, Down, Copy, Paste) to match Conditions list
        col = row.column(align=True)
        col.operator("object.xp_sound_add", text="", icon="ADD")
        col.operator("object.xp_sound_remove", text="", icon="REMOVE")
        col.separator()
        col.operator("object.xp_sound_move_up", text="", icon="TRIA_UP")
        col.operator("object.xp_sound_move_down", text="", icon="TRIA_DOWN")
        col.separator()
        col.operator("object.xp_sound_copy", text="", icon="COPYDOWN")
        col.operator("object.xp_sound_paste", text="", icon="PASTEDOWN")

        # Display the event_name property for the selected X-Plane sound object
        if (obj.xp_sound_data.xp_sound_index >= 0 and len(obj.xp_sound_data.xp_sound_list) > 0):
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            layout = layout.box()

            #layout.prop(xp_sound, "guid")
            row = layout.row()
            row.prop_search(xp_sound, "guid", context.scene.xp_sound_global, "parsed_events", text="Event GUID", icon="COLLAPSEMENU")    
            row.operator("object.xp_sound_refresh_parsed_events", text="", icon="FILE_REFRESH")        
            
            col = layout.column()
            col.prop(xp_sound, "event_auto_end_from_start_cond")
            col.prop(xp_sound, "event_polyphonic")
            col.prop(xp_sound, "event_allowed_for_ai")
            col.prop(xp_sound, "event_param_idx")            
            
            # Create tabs for each sound condition
            if len(xp_sound.event_list) > 0:
                events = layout.box()
                
                # Header labels
                row = events.row()
                row.label(text="Type") 
                row = row.split(factor=0.5)
                row.label(text="Dataref") 
                row = row.split(factor=0.3)
                row.label(text="Condition") 
                row = row.split(factor=0.8)
                row.label(text="Value") 
                
                # List with side bar
                row = events.row()
                row.template_list("XP_SOUND_UL_CONDITION_LIST", "", xp_sound, "event_list", xp_sound, "event_index")
                
                col = row.column(align=True)
                col.operator("xpsound.add_sound_condition", text="", icon="ADD")
                col.operator("xpsound.remove_sound_condition", text="", icon="REMOVE")
                col.separator()
                col.operator("xpsound.move_sound_condition_up", text="", icon="TRIA_UP")
                col.operator("xpsound.move_sound_condition_down", text="", icon="TRIA_DOWN")
                col.separator()
                col.operator("xpsound.copy_sound_condition", text="", icon="COPYDOWN")
                col.operator("xpsound.paste_sound_condition", text="", icon="PASTEDOWN")
            else:
                row = layout.row()
                row.operator("xpsound.add_sound_condition", text="Add Condition")  
            
    def draw_snapshot_properties(self, context, layout, obj):
        # Create a list with each X-Plane sound object
        row = layout.row()
        row.template_list("XP_SOUND_UL_SNAPSHOT_LIST", "", obj.xp_sound_data, "xp_snapshot_list", obj.xp_sound_data, "xp_snapshot_index")
        
        # Add move up/down buttons
        col = row.column(align=True)
        col.operator("object.xp_snapshot_move_up", text="", icon="TRIA_UP")
        col.operator("object.xp_snapshot_move_down", text="", icon="TRIA_DOWN")

        row = layout.row()
        row.operator("object.xp_snapshot_add", text="Add Snapshot")                    

        if (obj.xp_sound_data.xp_snapshot_index >= 0 and len(obj.xp_sound_data.xp_snapshot_list) > 0):
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]        

            layout = layout.box()
            row = layout.row()
            row.prop_search(xp_snapshot, "guid", context.scene.xp_sound_global, "parsed_snapshots", text="Event GUID", icon="COLLAPSEMENU")    
            row.operator("object.xp_sound_refresh_parsed_events", text="", icon="FILE_REFRESH")              
            
            col = layout.column()
            col.prop(xp_snapshot, "event_auto_end_from_start_cond")
            col.prop(xp_snapshot, "event_param_idx")            
            
            # Create tabs for each snapshot condition
            if len(xp_snapshot.event_list) > 0:
                events = layout.box()
                
                # Header labels
                row = events.row()
                row.label(text="Type") 
                row = row.split(factor=0.5)
                row.label(text="Dataref") 
                row = row.split(factor=0.3)
                row.label(text="Condition") 
                row = row.split(factor=0.8)
                row.label(text="Value") 
                
                # List
                row = events.row()
                row.template_list("XP_SOUND_UL_CONDITION_LIST", "", xp_snapshot, "event_list", xp_snapshot, "event_index")

                col = row.column(align=True)
                col.operator("xpsound.add_snapshot_condition", text="", icon="ADD")
                col.operator("xpsound.remove_snapshot_condition", text="", icon="REMOVE")
                col.separator()
                col.operator("xpsound.move_snapshot_condition_up", text="", icon="TRIA_UP")
                col.operator("xpsound.move_snapshot_condition_down", text="", icon="TRIA_DOWN")
                col.separator()
                col.operator("xpsound.copy_snapshot_condition", text="", icon="COPYDOWN")
                col.operator("xpsound.paste_snapshot_condition", text="", icon="PASTEDOWN")

            else:
                row = layout.row()
                row.operator("xpsound.add_snapshot_condition", text="Add Condition")  

            
def register():
    bpy.utils.register_class(XP_SOUND_PT_TOOLS_PANEL)
    bpy.utils.register_class(XP_SOUND_PT_GLOBAL_PANEL)
    bpy.utils.register_class(XP_SOUND_PT_PANEL)
    bpy.utils.register_class(XP_SOUND_UL_SOUND_LIST)
    bpy.utils.register_class(XP_SOUND_UL_SNAPSHOT_LIST)
    bpy.utils.register_class(XP_SOUND_UL_CONDITION_LIST)

def unregister():
    bpy.utils.unregister_class(XP_SOUND_PT_TOOLS_PANEL)
    bpy.utils.unregister_class(XP_SOUND_PT_GLOBAL_PANEL)
    bpy.utils.unregister_class(XP_SOUND_PT_PANEL)
    bpy.utils.unregister_class(XP_SOUND_UL_SOUND_LIST)    
    bpy.utils.unregister_class(XP_SOUND_UL_SNAPSHOT_LIST)
    bpy.utils.unregister_class(XP_SOUND_UL_CONDITION_LIST)


if __name__ == "__main__":
    register()
