import bpy

class XP_SOUND_ConditionItem(bpy.types.PropertyGroup):
    event_type: (
        bpy.props.EnumProperty(  # Type of the sound condition (START, END, ALWAYS, etc.)
            name="Condition Type",
            items=[
                ("START", "Start", "Condition to start the FMOD event"),
                ("END", "End", "Condition to end the FMOD event"),
                ("ALWAYS", "Always", "Always play FMOD event"),
                ("CUE_TRIGGER_COND", "Cue Trigger", "Sets conditions for cue triggering based on dataref"),
                ("CMND_DOWN", "Command Down", "Condition triggered on command press down"),
                ("CMND_UP", "Command Up", "Condition triggered on command release"),
                ("CMND_HOLD_STOP", "Command Hold Stop", "Condition triggered on command press and stopped on release"),
                ("CMND_HOLD_CUE", "Command Hold Cue", "Condition triggered on command press and cued on release"),
            ],
        )
    )

    # Dataref name for the sound condition
    dataref_name: bpy.props.StringProperty(name="Dataref Name")  

    # Comparison operator for the dataref value
    comparison_operator: (
        bpy.props.EnumProperty(  
            name="Comparison Operator",
            items=[
                ("<", "<", ""),
                ("<=", "<=", ""),
                ("==", "==", ""),
                ("!=", "!=", ""),
                (">=", ">=", ""),
                (">", ">", ""),
            ],
        )
    )

    # Comparison value for the sound condition
    comparison_value: bpy.props.FloatProperty(name="Comparison Value")  
    
        
# Define the PropertyGroup for snapshot objects
class XP_SNAPSHOT_item(bpy.types.PropertyGroup):
    guid: bpy.props.StringProperty(name="Event GUID", default="")
    name: bpy.props.StringProperty(name="Snapshot Name", default="New Snapshot")

    event_param_idx: bpy.props.IntProperty(name="Event Param Idx", description="Index of the parameter dataref for the FMOD event")
    event_auto_end_from_start_cond: bpy.props.BoolProperty(name="Event Auto End from Start Cond", description="Whether the FMOD event auto ends from start condition")

    # List
    event_list: bpy.props.CollectionProperty(type=XP_SOUND_ConditionItem)
    event_index: bpy.props.IntProperty()    

# Define the PropertyGroup for sound objects
class XP_SOUND_item(bpy.types.PropertyGroup):
    guid: bpy.props.StringProperty(name="Event GUID", default="")
    name: bpy.props.StringProperty(name="Sound Name", default="New Sound")

    event_param_idx: bpy.props.IntProperty(name="Event Param Idx", description="Index of the parameter dataref for the FMOD event")
    event_polyphonic: bpy.props.BoolProperty(name="Event Polyphonic", description="Whether the FMOD event is polyphonic")
    event_allowed_for_ai: bpy.props.BoolProperty(name="Event Allowed for AI", description="Whether the FMOD event is allowed for AI")
    event_auto_end_from_start_cond: bpy.props.BoolProperty(name="Event Auto End from Start Cond", description="Whether the FMOD event auto ends from start condition")

    # List
    event_list: bpy.props.CollectionProperty(type=XP_SOUND_ConditionItem)
    event_index: bpy.props.IntProperty()
    
# Define the PropertyGroup for sound objects
class XP_SOUND_data(bpy.types.PropertyGroup):
    event_type: (
        bpy.props.EnumProperty(  # Type of the sound event (SOUND, SNAPSHOT, SPACE)
            items=[
                ("NONE", "None", "None"),
                ("SOUND", "Sound", "Sound"),
                ("SNAPSHOT", "Snapshot", "Snapshot"),
                ("SPACE", "Space", "Space"),
            ],
            name="Type",
        )
    )    
    
    # Spaces
    space_index: bpy.props.IntProperty(name="Space Index", min=0, max=63, description="Space index for space type events: 0 - 63")
    space_blend_depth: bpy.props.FloatProperty(name="Space Blend Depth", min=0.0, max=10.0, description="Distance in meters used to blend interior-exterior space")
    
    # Snapshots
    xp_snapshot_list: bpy.props.CollectionProperty(type=XP_SNAPSHOT_item)    
    xp_snapshot_index: bpy.props.IntProperty() 
    
    # Sounds
    xp_sound_list: bpy.props.CollectionProperty(type=XP_SOUND_item)    
    xp_sound_index: bpy.props.IntProperty()

def refresh_parsed_events_on_path_change(self, context):
    bpy.ops.object.xp_sound_refresh_parsed_events()

class XP_SOUND_global(bpy.types.PropertyGroup):
    # Aircraft Reference Point
    ref_point_y: bpy.props.FloatProperty(name="Ref Point Y", description="Vertical Reference", unit="LENGTH")
    ref_point_z: bpy.props.FloatProperty(name="Ref Point Z", description="Longitudinal Reference", unit="LENGTH")    
    
    # Parsed items from GUIDS.txt
    parsed_events: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    parsed_snapshots: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)    
    
    # Paths
    snd_filename: bpy.props.StringProperty(name="SND FILENAME", default="aircraft.snd", description="This is the .snd filename, example: aircraft.snd")
    fmod_path: bpy.props.StringProperty(name="FMOD PATH", default="", update=refresh_parsed_events_on_path_change, description="Set this path to aircraft FMOD folder, example: ../fmod/")    
    
    # Global event properties
    disable_legacy_alerts: bpy.props.BoolProperty(name="Disable Legacy Alert Sounds")    
    
    # Helper that draw arrow to show direction
    draw_helper: bpy.props.BoolProperty(name="Draw Helper", description="Display an arrow on the selected empty pointing on sound direction", default=False)
    
def add_parsed_event(self, context):
    event = self.parsed_events.add()
    event.name = ""
    return event


def add_parsed_snapshot(self, context):
    event = self.parsed_snapshots.add()
    event.name = ""
    return event    

def register():
    bpy.utils.register_class(XP_SOUND_ConditionItem)
    bpy.utils.register_class(XP_SNAPSHOT_item)
    bpy.utils.register_class(XP_SOUND_item)
    bpy.utils.register_class(XP_SOUND_data)
    bpy.utils.register_class(XP_SOUND_global)
    
    # Global
    bpy.types.Scene.xp_sound_global = bpy.props.PointerProperty(type=XP_SOUND_global)
    
    # Object Data
    bpy.types.Object.xp_sound_data = bpy.props.PointerProperty(type=XP_SOUND_data)

def unregister():
    bpy.utils.unregister_class(XP_SNAPSHOT_item)
    bpy.utils.unregister_class(XP_SOUND_ConditionItem)
    bpy.utils.unregister_class(XP_SOUND_item)
    bpy.utils.unregister_class(XP_SOUND_data)

if __name__ == "__main__":
    register()
