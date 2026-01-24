import bpy
import os
from mathutils import Vector
import math

def get_or_create_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    else:
        new_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(new_collection)
        return new_collection

def get_sound_path(guid):
    return '/'.join(guid.split('/')[:-1])

def euler_almost_equal(euler1, euler2, tolerance=0.001):
    return all(abs(a - b) < tolerance for a, b in zip(euler1, euler2))

def find_or_create_sound_object(context, position, rotation, type, collection, guid):
    sound_path = get_sound_path(guid)
    for obj in collection.objects:
        if obj.type == 'EMPTY' and obj.xp_sound_data.event_type == type:
            if (obj.location - position).length < 0.001 and euler_almost_equal(obj.rotation_euler, rotation):
                # Check if the existing object has a sound with the same base path
                for sound in obj.xp_sound_data.xp_sound_list:
                    if get_sound_path(sound.guid) == sound_path:
                        return obj
    
    # If no existing object found, create a new one
    new_obj = create_empty(context, collection)
    new_obj.xp_sound_data.event_type = type
    new_obj.location = position
    new_obj.rotation_euler = rotation
    return new_obj

def import_snd_file(context, filepath, group_by_position, import_spaces, import_snapshots, import_sounds):
    xpsounds_collection = get_or_create_collection("XPSounds")
    
    # Add a single empty object for all snapshots
    snapshot_object = None if not import_snapshots else create_empty(context, xpsounds_collection)
    if snapshot_object:
        snapshot_object.name = "All Snapshots"
        snapshot_object.xp_sound_data.event_type = 'SNAPSHOT'
    
    with open(filepath, 'r') as file:
        lines = file.readlines()

    current_object = None
    current_type = None
    current_position = None
    current_rotation = None
    current_guid = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('BEGIN_SOUND_SPACE'):
            if import_spaces:
                current_type = 'SPACE'
                current_object = create_empty(context, xpsounds_collection)
                current_object.xp_sound_data.event_type = 'SPACE'
            else:
                current_object = None
                current_type = None
                
        if line.startswith('BEGIN_SOUND_ATTACHMENT'):
            # Look ahead for SNAPSHOT_NAME/EVENT_NAME (FMOD events), VEH_XYZ, and rotation
            j = i + 1
            current_type = 'SOUND'
            current_position = None
            current_rotation = Vector((0, 0, 0))
            current_guid = None
            while j < len(lines) and not lines[j].strip().startswith('END_SOUND_ATTACHMENT'):
                if 'SNAPSHOT_NAME' in lines[j]:
                    current_type = 'SNAPSHOT'
                    current_guid = lines[j].split()[1]
                elif 'EVENT_NAME' in lines[j]:
                    current_guid = lines[j].split()[1]
                elif lines[j].strip().startswith('VEH_XYZ'):
                    parts = lines[j].split()
                    current_position = Vector((float(parts[1]), -float(parts[3]), float(parts[2])))
                elif lines[j].strip().startswith('VEH_PSI'):
                    current_rotation.z = math.radians(float(lines[j].split()[1]))
                elif lines[j].strip().startswith('VEH_THETA'):
                    current_rotation.x = math.radians(float(lines[j].split()[1]))
                elif lines[j].strip().startswith('VEH_PHI'):
                    current_rotation.y = math.radians(float(lines[j].split()[1]))
                j += 1
            
            if (current_type == 'SNAPSHOT' and import_snapshots) or (current_type == 'SOUND' and import_sounds):
                if current_type == 'SNAPSHOT':
                    current_object = snapshot_object
                elif group_by_position and current_position and current_guid:
                    current_object = find_or_create_sound_object(context, current_position, current_rotation, current_type, xpsounds_collection, current_guid)
                else:
                    current_object = create_empty(context, xpsounds_collection)
                    current_object.xp_sound_data.event_type = current_type
                    if current_position:
                        current_object.location = current_position
                    if current_rotation:
                        current_object.rotation_euler = current_rotation
            else:
                current_object = None
                current_type = None
        elif line.startswith('END_SOUND_SPACE') or line.startswith('END_SOUND_ATTACHMENT'):
            current_object = None
            current_type = None
            current_position = None
            current_guid = None
        elif current_object:
            process_line(context, line, current_object, current_type)
        
        i += 1

def create_empty(context, collection):
    empty = bpy.data.objects.new("XPSound", None)
    empty.empty_display_type = 'PLAIN_AXES'
    collection.objects.link(empty)
    return empty

def process_line(context, line, obj, type):
    parts = line.split()
    if not parts:
        return

    if type == 'SOUND':
        process_sound_line(obj, parts)
    elif type == 'SPACE':
        process_space_line(obj, parts)
    elif type == 'SNAPSHOT':
        process_snapshot_line(obj, parts)

def process_sound_line(obj, parts):
    if parts[0] == 'EVENT_NAME':
        sound = obj.xp_sound_data.xp_sound_list.add()
        sound.guid = parts[1]
        
        # Split the sound name into path and actual name
        path_parts = sound.guid.split('/')
        sound_name = path_parts[-1]
        path = '/'.join(path_parts[:-1])
        
        # Rename the empty object
        if len(obj.xp_sound_data.xp_sound_list) == 1:
            obj.name = f"Sound - {path}"
        elif path not in obj.name:
            obj.name += f"_{path}"
        
        # Rename the sound inside the list
        sound.name = sound_name
    elif parts[0] == 'VEH_PSI':
        obj.rotation_euler[2] = math.radians(float(parts[1]))  # Yaw (Z-axis rotation)
    elif parts[0] == 'VEH_THETA':
        obj.rotation_euler[0] = math.radians(float(parts[1]))  # Pitch (X-axis rotation)
    elif parts[0] == 'VEH_PHI':
        obj.rotation_euler[1] = math.radians(float(parts[1]))  # Roll (Y-axis rotation)
    elif parts[0] == 'PARAM_DREF_IDX':
        sound = obj.xp_sound_data.xp_sound_list[-1]
        sound.event_param_idx = int(parts[1])
    elif parts[0] == 'EVENT_ALLOWED_FOR_AI':
        sound = obj.xp_sound_data.xp_sound_list[-1]
        sound.event_allowed_for_ai = True
    elif parts[0] == 'EVENT_AUTO_END_FROM_START_COND':
        sound = obj.xp_sound_data.xp_sound_list[-1]
        sound.event_auto_end_from_start_cond = True
    elif parts[0] in ['EVENT_START_COND', 'EVENT_END_COND', 'EVENT_ALWAYS']:
        add_sound_condition(obj, parts)

def process_space_line(obj, parts):
    if parts[0] == 'SOUND_INDEX':
        obj.xp_sound_data.space_index = int(parts[1])
        obj.name = f"Space - {obj.xp_sound_data.space_index}"
    if parts[0] == 'BLEND_DEPTH':
        obj.xp_sound_data.space_blend_depth = float(parts[1])
    elif parts[0] == 'AABB':
        set_aabb(obj, parts)
    elif parts[0] == 'SPHERE':
        set_sphere(obj, parts)    

def process_snapshot_line(obj, parts):
    if parts[0] == 'SNAPSHOT_NAME':
        snapshot = obj.xp_sound_data.xp_snapshot_list.add()
        snapshot.guid = parts[1]
        snapshot.name = snapshot.guid.split('/')[-1]
    elif parts[0] == 'PARAM_DREF_IDX':
        snapshot = obj.xp_sound_data.xp_snapshot_list[-1]
        snapshot.event_param_idx = int(parts[1])
    elif parts[0] == 'EVENT_AUTO_END_FROM_START_COND':
        snapshot = obj.xp_sound_data.xp_snapshot_list[-1]
        snapshot.event_auto_end_from_start_cond = True        
    elif parts[0] in ['EVENT_START_COND', 'EVENT_END_COND', 'EVENT_ALWAYS']:
        add_snapshot_condition(obj, parts)

def set_aabb(obj, parts):
    obj.empty_display_type = 'CUBE'
    min_point = Vector((float(parts[1]), float(parts[3]), float(parts[2])))
    max_point = Vector((float(parts[4]), float(parts[6]), float(parts[5])))
    obj.location = (min_point + max_point) / 2
    obj.location.y = -obj.location.y
    obj.scale = (max_point - min_point) / 2
    
def set_sphere(obj, parts):
    obj.empty_display_type = 'SPHERE'
    obj.location = Vector((float(parts[1]), float(parts[3]), float(parts[2])))
    radius = float(parts[4])
    obj.scale = Vector((radius, radius, radius))
    
def add_sound_condition(obj, parts):
    sound = obj.xp_sound_data.xp_sound_list[-1]
    event = sound.event_list.add()
    event.event_type = parts[0].split('_')[1]
    if event.event_type != 'ALWAYS':
        event.dataref_name = parts[1]
        event.comparison_operator = parts[2] if len(parts) > 2 else '!='
        event.comparison_value = float(parts[3]) if len(parts) > 3 else 0

def add_snapshot_condition(obj, parts):
    snapshot = obj.xp_sound_data.xp_snapshot_list[-1]
    event = snapshot.event_list.add()
    event.event_type = parts[0].split('_')[1]
    if event.event_type != 'ALWAYS':
        event.dataref_name = parts[1]
        event.comparison_operator = parts[2] if len(parts) > 2 else '!='
        event.comparison_value = float(parts[3]) if len(parts) > 3 else 0

class XPSOUND_import_snd(bpy.types.Operator):
    bl_idname = "xpsound.import_snd"
    bl_label = "Import from .snd"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.snd",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    group_by_position: bpy.props.BoolProperty(
        name="Group by Position, Orientation and GUID",
        description="Group sounds by Position, Orientation and GUID similarity",
        default=True
    )
    import_spaces: bpy.props.BoolProperty(
        name="Spaces",
        description="Import Sound Spaces",
        default=True
    )
    import_snapshots: bpy.props.BoolProperty(
        name="Snapshots",
        description="Import Sound Snapshots",
        default=True
    )
    import_sounds: bpy.props.BoolProperty(
        name="Sounds",
        description="Import Sound Attachments",
        default=True
    )
    
    def execute(self, context):
        import_snd_file(context, self.filepath, self.group_by_position,
                        self.import_spaces, self.import_snapshots, self.import_sounds)
        self.report({'INFO'}, f"Imported sound conditions from {self.filepath}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Options:")
        layout.prop(self, "group_by_position")
        layout.label(text="Import Types:")
        layout.prop(self, "import_spaces")
        layout.prop(self, "import_snapshots")
        layout.prop(self, "import_sounds")

def register():
    bpy.utils.register_class(XPSOUND_import_snd)

def unregister():
    bpy.utils.unregister_class(XPSOUND_import_snd)

if __name__ == "__main__":
    register()