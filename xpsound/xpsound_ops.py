import bpy
import os

######################################################################################
# SOUNDS
######################################################################################

# Operator to add a new sound
class XP_SOUND_OT_SOUND_ADD(bpy.types.Operator):
    bl_idname = "object.xp_sound_add"
    bl_label = "Add X-Plane Sound"

    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_sound_list.add()
        obj.xp_sound_data.xp_sound_index = len(obj.xp_sound_data.xp_sound_list) - 1
        return {'FINISHED'}

# Operator to remove a sound
class XP_SOUND_OT_SOUND_REMOVE(bpy.types.Operator):
    bl_idname = "object.xp_sound_remove"
    bl_label = "Remove X-Plane Sound"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = context.object
        xp_sound_list = obj.xp_sound_data.xp_sound_list
        index = self.index
        xp_sound_list.remove(index)
        obj.xp_sound_data.xp_sound_index = min(max(0, index - 1), len(xp_sound_list) - 1)
        return {'FINISHED'}

# Operator to add a new sound condition
class XP_SOUND_OT_SOUND_CONDITION_ADD(bpy.types.Operator):
    "Defines an Operator to add a new sound condition to the selected object's sound conditions list."
    bl_idname = "xpsound.add_sound_condition"
    bl_label = "Add Sound Condition"

    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            xp_sound.event_list.add()
            xp_sound.event_index = len(xp_sound.event_list) - 1
        return {"FINISHED"}        

# Operator to remove the selected sound condition from the list
class XP_SOUND_OT_SOUND_CONDITION_REMOVE(bpy.types.Operator):
    "Remove the selected sound condition from the object's sound conditions list."
    bl_idname = "xpsound.remove_sound_condition"
    bl_label = "Remove Sound Condition"
    index: bpy.props.IntProperty(default=-1)
    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            
            # If default index is passed (-1), use the selected index
            if self.index < 0:
                self.index = xp_sound.event_index
                
            xp_sound.event_list.remove(self.index)
            xp_sound.event_index = min(max(0, self.index - 1), len(xp_sound.event_list) - 1)
        return {"FINISHED"}

# Operator to copy the selected sound
class XP_SOUND_OT_SOUND_COPY(bpy.types.Operator):
    bl_idname = "object.xp_sound_copy"
    bl_label = "Copy Sound"
    
    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
        copied_data = {
            'name': xp_sound.name,
            'guid': xp_sound.guid,
            'event_auto_end_from_start_cond': xp_sound.event_auto_end_from_start_cond,
            'event_polyphonic': xp_sound.event_polyphonic,
            'event_allowed_for_ai': xp_sound.event_allowed_for_ai,
            'event_param_idx': xp_sound.event_param_idx,
            'events': [(event.event_type, event.dataref_name, event.comparison_operator, event.comparison_value) for event in xp_sound.event_list]
        }
        context.window_manager.clipboard = str(copied_data)
        return {'FINISHED'}
    
# Operator to paste the selected sound
class XP_SOUND_OT_SOUND_PASTE(bpy.types.Operator):
    bl_idname = "object.xp_sound_paste"
    bl_label = "Paste Sound"
    
    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_sound_list.add()
        try:
            copied_data = eval(context.window_manager.clipboard)
            xp_sound.name = copied_data['name']
            xp_sound.guid = copied_data['guid']
            xp_sound.event_auto_end_from_start_cond = copied_data['event_auto_end_from_start_cond']
            xp_sound.event_polyphonic = copied_data['event_polyphonic']
            xp_sound.event_allowed_for_ai = copied_data['event_allowed_for_ai']
            xp_sound.event_param_idx = copied_data['event_param_idx']
            # Copy events
            for event_data in copied_data['events']:
                event = xp_sound.event_list.add()
                event.event_type, event.dataref_name, event.comparison_operator, event.comparison_value = event_data
        except Exception as e:
            self.report({'ERROR'}, f"Failed to paste sound: {e}")
        return {'FINISHED'}

# Operator to duplicate the selected sound
class XP_SOUND_OT_SOUND_DUPLICATE(bpy.types.Operator):
    bl_idname = "object.xp_sound_duplicate"
    bl_label = "Duplicate Sound"
    
    index: bpy.props.IntProperty()
     
    def execute(self, context):
        obj = context.object
        if self.index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[self.index]
            
            # Duplicate the sound
            new_xp_sound = obj.xp_sound_data.xp_sound_list.add()
            new_xp_sound.name = xp_sound.name
            new_xp_sound.guid = xp_sound.guid
            new_xp_sound.event_auto_end_from_start_cond = xp_sound.event_auto_end_from_start_cond
            new_xp_sound.event_polyphonic = xp_sound.event_polyphonic
            new_xp_sound.event_allowed_for_ai = xp_sound.event_allowed_for_ai
            new_xp_sound.event_param_idx = xp_sound.event_param_idx
            
            # Duplicate events
            for event in xp_sound.event_list:
                new_event = new_xp_sound.event_list.add()
                new_event.event_type = event.event_type
                new_event.dataref_name = event.dataref_name
                new_event.comparison_operator = event.comparison_operator
                new_event.comparison_value = event.comparison_value
        return {'FINISHED'}

# Operator to move sound up
class XP_SOUND_OT_SOUND_MOVE_UP(bpy.types.Operator):
    bl_idname = "object.xp_sound_move_up"
    bl_label = "Move Sound Up"
    
    def execute(self, context):
        obj = context.object
        index = obj.xp_sound_data.xp_sound_index
        if index > 0:
            obj.xp_sound_data.xp_sound_list.move(index, index - 1)
            obj.xp_sound_data.xp_sound_index = index - 1
        return {'FINISHED'}

# Operator to move sound down
class XP_SOUND_OT_SOUND_MOVE_DOWN(bpy.types.Operator):
    bl_idname = "object.xp_sound_move_down"
    bl_label = "Move Sound Down"
    
    def execute(self, context):
        obj = context.object
        index = obj.xp_sound_data.xp_sound_index
        if index < len(obj.xp_sound_data.xp_sound_list) - 1:
            obj.xp_sound_data.xp_sound_list.move(index, index + 1)
            obj.xp_sound_data.xp_sound_index = index + 1
        return {'FINISHED'}


######################################################################################
# SNAPSHOTS
######################################################################################

# Operator to add a snapshot
class XP_SOUND_OT_SNAPSHOT_ADD(bpy.types.Operator):
    bl_idname = "object.xp_snapshot_add"
    bl_label = "Add X-Plane Snapshot"

    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_snapshot_list.add()
        obj.xp_sound_data.xp_snapshot_index = len(obj.xp_sound_data.xp_snapshot_list) - 1
        return {'FINISHED'}

# Operator to remove a snapshot
class XP_SOUND_OT_SNAPSHOT_REMOVE(bpy.types.Operator):
    bl_idname = "object.xp_snapshot_remove"
    bl_label = "Remove X-Plane Snapshot"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = context.object
        xp_snapshot_list = obj.xp_sound_data.xp_snapshot_list
        index = self.index
        xp_snapshot_list.remove(index)
        obj.xp_sound_data.xp_snapshot_index = min(max(0, index - 1), len(xp_snapshot_list) - 1)
        return {'FINISHED'}    
    
# Operator to add a new snapshot condition
class XP_SOUND_OT_SNAPSHOT_CONDITION_ADD(bpy.types.Operator):
    "Defines an Operator to add a new snapshot condition."
    bl_idname = "xpsound.add_snapshot_condition"
    bl_label = "Add Snapshot Condition"

    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]
            xp_snapshot.event_list.add()
            xp_snapshot.event_index = len(xp_snapshot.event_list) - 1
        return {"FINISHED"}        

# Operator to remove the selected snapshot condition from the list
class XP_SOUND_OT_SNAPSHOT_CONDITION_REMOVE(bpy.types.Operator):
    "Remove the selected snapshot condition from the object's sound conditions list."
    bl_idname = "xpsound.remove_snapshot_condition"
    bl_label = "Remove Snapshot Condition"
    index: bpy.props.IntProperty(default=-1)
    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]        
            
            # If default index is passed (-1), use the selected index
            if self.index < 0:
                self.index = xp_snapshot.event_index

            xp_snapshot.event_list.remove(self.index)
            xp_snapshot.event_index = min(max(0, self.index - 1), len(xp_snapshot.event_list) - 1)
        return {"FINISHED"}

# Operator to move snapshot up
class XP_SOUND_OT_SNAPSHOT_MOVE_UP(bpy.types.Operator):
    bl_idname = "object.xp_snapshot_move_up"
    bl_label = "Move Snapshot Up"
    
    def execute(self, context):
        obj = context.object
        index = obj.xp_sound_data.xp_snapshot_index
        if index > 0:
            obj.xp_sound_data.xp_snapshot_list.move(index, index - 1)
            obj.xp_sound_data.xp_snapshot_index = index - 1
        return {'FINISHED'}

# Operator to move snapshot down
class XP_SOUND_OT_SNAPSHOT_MOVE_DOWN(bpy.types.Operator):
    bl_idname = "object.xp_snapshot_move_down"
    bl_label = "Move Snapshot Down"
    
    def execute(self, context):
        obj = context.object
        index = obj.xp_sound_data.xp_snapshot_index
        if index < len(obj.xp_sound_data.xp_snapshot_list) - 1:
            obj.xp_sound_data.xp_snapshot_list.move(index, index + 1)
            obj.xp_sound_data.xp_snapshot_index = index + 1
        return {'FINISHED'}


# SOUND CONDITION OPERATORS

class XP_SOUND_OT_SOUND_CONDITION_MOVE_UP(bpy.types.Operator):
    bl_idname = "xpsound.move_sound_condition_up"
    bl_label = "Move Sound Condition Up"
    
    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            index = xp_sound.event_index
            if index > 0:
                xp_sound.event_list.move(index, index - 1)
                xp_sound.event_index = index - 1
        return {'FINISHED'}

class XP_SOUND_OT_SOUND_CONDITION_MOVE_DOWN(bpy.types.Operator):
    bl_idname = "xpsound.move_sound_condition_down"
    bl_label = "Move Sound Condition Down"
    
    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            index = xp_sound.event_index
            if index < len(xp_sound.event_list) - 1:
                xp_sound.event_list.move(index, index + 1)
                xp_sound.event_index = index + 1
        return {'FINISHED'}

class XP_SOUND_OT_SOUND_CONDITION_COPY(bpy.types.Operator):
    bl_idname = "xpsound.copy_sound_condition"
    bl_label = "Copy Sound Condition"

    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            if xp_sound.event_index >= 0 and len(xp_sound.event_list) > 0:
                event = xp_sound.event_list[xp_sound.event_index]
                data = {
                    'type': 'CONDITION',
                    'event_type': event.event_type,
                    'dataref_name': event.dataref_name,
                    'comparison_operator': event.comparison_operator,
                    'comparison_value': event.comparison_value
                }
                context.window_manager.clipboard = str(data)
                self.report({'INFO'}, "Condition copied")
        return {'FINISHED'}

class XP_SOUND_OT_SOUND_CONDITION_PASTE(bpy.types.Operator):
    bl_idname = "xpsound.paste_sound_condition"
    bl_label = "Paste Sound Condition"

    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            try:
                data = eval(context.window_manager.clipboard)
                if isinstance(data, dict) and data.get('type') == 'CONDITION':
                    new_event = xp_sound.event_list.add()
                    new_event.event_type = data['event_type']
                    new_event.dataref_name = data['dataref_name']
                    new_event.comparison_operator = data['comparison_operator']
                    new_event.comparison_value = data['comparison_value']
                    xp_sound.event_index = len(xp_sound.event_list) - 1
                else:
                    self.report({'WARNING'}, "Clipboard does not contain a valid condition")
            except:
                self.report({'WARNING'}, "Clipboard does not contain valid data")
        return {'FINISHED'}


# SNAPSHOT CONDITION OPERATORS

class XP_SOUND_OT_SNAPSHOT_CONDITION_MOVE_UP(bpy.types.Operator):
    bl_idname = "xpsound.move_snapshot_condition_up"
    bl_label = "Move Snapshot Condition Up"
    
    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]
            index = xp_snapshot.event_index
            if index > 0:
                xp_snapshot.event_list.move(index, index - 1)
                xp_snapshot.event_index = index - 1
        return {'FINISHED'}

class XP_SOUND_OT_SNAPSHOT_CONDITION_MOVE_DOWN(bpy.types.Operator):
    bl_idname = "xpsound.move_snapshot_condition_down"
    bl_label = "Move Snapshot Condition Down"
    
    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]
            index = xp_snapshot.event_index
            if index < len(xp_snapshot.event_list) - 1:
                xp_snapshot.event_list.move(index, index + 1)
                xp_snapshot.event_index = index + 1
        return {'FINISHED'}

class XP_SOUND_OT_SNAPSHOT_CONDITION_COPY(bpy.types.Operator):
    bl_idname = "xpsound.copy_snapshot_condition"
    bl_label = "Copy Snapshot Condition"

    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]
            if xp_snapshot.event_index >= 0 and len(xp_snapshot.event_list) > 0:
                event = xp_snapshot.event_list[xp_snapshot.event_index]
                data = {
                    'type': 'CONDITION',
                    'event_type': event.event_type,
                    'dataref_name': event.dataref_name,
                    'comparison_operator': event.comparison_operator,
                    'comparison_value': event.comparison_value
                }
                context.window_manager.clipboard = str(data)
                self.report({'INFO'}, "Condition copied")
        return {'FINISHED'}

class XP_SOUND_OT_SNAPSHOT_CONDITION_PASTE(bpy.types.Operator):
    bl_idname = "xpsound.paste_snapshot_condition"
    bl_label = "Paste Snapshot Condition"

    def execute(self, context):
        obj = context.object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]
            try:
                data = eval(context.window_manager.clipboard)
                if isinstance(data, dict) and data.get('type') == 'CONDITION':
                    new_event = xp_snapshot.event_list.add()
                    new_event.event_type = data['event_type']
                    new_event.dataref_name = data['dataref_name']
                    new_event.comparison_operator = data['comparison_operator']
                    new_event.comparison_value = data['comparison_value']
                    xp_snapshot.event_index = len(xp_snapshot.event_list) - 1
                else:
                    self.report({'WARNING'}, "Clipboard does not contain a valid condition")
            except:
                self.report({'WARNING'}, "Clipboard does not contain valid data")
        return {'FINISHED'}

# Copy FMOD build files to root directory
class XP_SOUND_OT_COPY_FMOD_BUILD_FILES(bpy.types.Operator):
    "Copies GUIDs.txt and Master Bank.bank from build folders to FMOD root directory"
    bl_idname = "xpsound.copy_fmod_build_files"
    bl_label = "Copy Build Files"

    def execute(self, context):
        import shutil
        
        fmod_path = context.scene.xp_sound_global.fmod_path
        if not fmod_path:
            self.report({'ERROR'}, "FMOD directory not set")
            return {'CANCELLED'}
        
        # Construct absolute paths
        fmod_root = bpy.path.abspath(os.path.join("//", fmod_path))
        fmod_root = os.path.normpath(fmod_root)
        
        # Source files
        guids_source = os.path.join(fmod_root, "Build", "GUIDs.txt")
        bank_source = os.path.join(fmod_root, "Build", "Desktop", "Master Bank.bank")
        
        # Destination files
        guids_dest = os.path.join(fmod_root, "GUIDs.txt")
        bank_dest = os.path.join(fmod_root, "Master Bank.bank")
        
        copied_files = []
        
        # Copy GUIDs.txt
        if os.path.exists(guids_source):
            try:
                shutil.copy2(guids_source, guids_dest)
                copied_files.append("GUIDs.txt")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy GUIDs.txt: {e}")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, f"GUIDs.txt not found at: {guids_source}")
        
        # Copy Master Bank.bank
        if os.path.exists(bank_source):
            try:
                shutil.copy2(bank_source, bank_dest)
                copied_files.append("Master Bank.bank")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy Master Bank.bank: {e}")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, f"Master Bank.bank not found at: {bank_source}")
        
        if copied_files:
            self.report({'INFO'}, f"Copied: {', '.join(copied_files)}")
            # Refresh parsed events after copying GUIDs.txt
            if "GUIDs.txt" in copied_files:
                bpy.ops.object.xp_sound_refresh_parsed_events()
        else:
            self.report({'WARNING'}, "No files were copied")
        
        return {'FINISHED'}

# Refresh the list of events from GUIDs file    
class XP_SOUND_refresh_parsed_events(bpy.types.Operator):
    "Refreshes the list of parsed events from the GUIDS.txt file."
    bl_idname = "object.xp_sound_refresh_parsed_events"
    bl_label = "Refresh Parsed Events"

    def execute(self, context):
        obj = context.active_object

        # Construct the path to the GUIDS.txt file
        guids_file_path = bpy.path.abspath(os.path.join("//", context.scene.xp_sound_global.fmod_path, "GUIDS.txt"))
        guids_file_path = os.path.normpath(guids_file_path)

        # Clear the existing parsed events
        context.scene.xp_sound_global.parsed_events.clear()
        context.scene.xp_sound_global.parsed_snapshots.clear()

        if os.path.exists(guids_file_path):
            # Parse the GUIDS.txt file and add the events to the collection
            with open(guids_file_path, "r") as file:
                for line in file:
                    line = line.strip()
                    parts = line.split()
                    if len(parts) > 1:
                        guid = parts[0]
                        name = " ".join(parts[1:])
                        if "event:" in name:
                            event_name = name[name.index("event:") + len("event:") :]
                            new_event = context.scene.xp_sound_global.parsed_events.add()
                            new_event.name = event_name
                        if "snapshot:" in name:
                            event_name = name[
                                name.index("snapshot:") + len("snapshot:") :
                            ]
                            new_event = context.scene.xp_sound_global.parsed_snapshots.add()
                            new_event.name = event_name
            self.report({'INFO'}, f"Updated from GUIDS: {guids_file_path}")
            
        else:
            self.report({'WARNING'}, f"GUIDS file is missing at: {guids_file_path}")

        return {"FINISHED"}

# Register all classes and define global properties
classes = (
    XP_SOUND_OT_SOUND_ADD,
    XP_SOUND_OT_SOUND_REMOVE,
    XP_SOUND_OT_SOUND_CONDITION_ADD,
    XP_SOUND_OT_SOUND_CONDITION_REMOVE,
    XP_SOUND_OT_SOUND_COPY,
    XP_SOUND_OT_SOUND_PASTE,
    XP_SOUND_OT_SOUND_DUPLICATE,

    XP_SOUND_OT_SNAPSHOT_ADD,
    XP_SOUND_OT_SNAPSHOT_REMOVE,
    XP_SOUND_OT_SNAPSHOT_CONDITION_ADD,
    XP_SOUND_OT_SNAPSHOT_CONDITION_REMOVE,
    
    XP_SOUND_OT_SOUND_MOVE_UP,
    XP_SOUND_OT_SOUND_MOVE_DOWN,
    XP_SOUND_OT_SNAPSHOT_MOVE_UP,
    XP_SOUND_OT_SNAPSHOT_MOVE_DOWN,

    XP_SOUND_OT_COPY_FMOD_BUILD_FILES,
    XP_SOUND_refresh_parsed_events,
    
    XP_SOUND_OT_SOUND_CONDITION_MOVE_UP,
    XP_SOUND_OT_SOUND_CONDITION_MOVE_DOWN,
    XP_SOUND_OT_SOUND_CONDITION_COPY,
    XP_SOUND_OT_SOUND_CONDITION_PASTE,
    
    XP_SOUND_OT_SNAPSHOT_CONDITION_MOVE_UP,
    XP_SOUND_OT_SNAPSHOT_CONDITION_MOVE_DOWN,
    XP_SOUND_OT_SNAPSHOT_CONDITION_COPY,
    XP_SOUND_OT_SNAPSHOT_CONDITION_PASTE
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
