import bpy
import os
import io
import math
from xpsound import bl_info

# Define the export function for .snd file
def export_snapshot_attachment(f, collection, obj, snapshot):
    "Writes snapshot condition data to a .snd file for snapshot type attachments."

    f.write(f"# {collection.name + ' -> ' if collection != bpy.context.scene.collection else ''}{obj.name} -> {snapshot.name}\n")
    f.write("BEGIN_SOUND_ATTACHMENT\n")
    # Write event name
    f.write(f"\tSNAPSHOT_NAME {snapshot.guid}\n")

    # Write param dataref index
    f.write(f"\tPARAM_DREF_IDX {snapshot.event_param_idx}\n")

    # Write sound conditions
    for snapshot_condition in snapshot.event_list:
        comparison_value = round(snapshot_condition.comparison_value, 4)
        if snapshot_condition.event_type == "START":
            f.write(f"\tEVENT_START_COND {snapshot_condition.dataref_name} {snapshot_condition.comparison_operator} {comparison_value}\n")
        elif snapshot_condition.event_type == "END":
            f.write(f"\tEVENT_END_COND {snapshot_condition.dataref_name} {snapshot_condition.comparison_operator} {comparison_value}\n")
        elif snapshot_condition.event_type == "ALWAYS":
            f.write(f"\tEVENT_ALWAYS {snapshot_condition.dataref_name}\n")
        elif snapshot_condition.event_type.startswith("CMND"):
            f.write(f"\tEVENT_COMMAND {snapshot_condition.event_type}\n")

    # Write If event auto end from start condition
    if snapshot.event_auto_end_from_start_cond == True:
        f.write("\tEVENT_AUTO_END_FROM_START_COND\n")

    # Write end directive
    f.write("END_SOUND_ATTACHMENT\n\n")
    
# Define the export function for .snd file
def export_sound_attachment(f, collection, obj, sound):
    "Writes sound condition data to a .snd file for sound type attachments."
    
    f.write(f"# {collection.name + ' -> ' if collection != bpy.context.scene.collection else ''}{obj.name} -> {sound.name}\n")
    f.write("BEGIN_SOUND_ATTACHMENT\n")

    # Write event name
    f.write(f"\tEVENT_NAME {sound.guid}\n")

    # Write object position
    f.write(f"\tVEH_XYZ {round(obj.location.x, 4)} {round(obj.location.z, 4)} {-round(obj.location.y, 4)}\n")

    # Write object orientation (Euler angles)

    # Roll
    phi = math.degrees(obj.rotation_euler.x)
    if phi != 0:
        f.write(f"\tVEH_PHI {round(phi, 2)}\n")

    # Pitch        
    theta = math.degrees(obj.rotation_euler.y)
    if theta != 0:
        f.write(f"\tVEH_THETA {round(theta, 2)}\n")

    # Heading    
    psi = math.degrees(obj.rotation_euler.z)
    if psi != 0:
        f.write(f"\tVEH_PSI {round(psi, 2)}\n")

    # Write param dataref index
    f.write(f"\tPARAM_DREF_IDX {sound.event_param_idx}\n")

    # Write if event is polyphonic
    if sound.event_polyphonic:
        f.write(f"\tEVENT_POLYPHONIC\n")

    # Write If event is allowed for AI
    if sound.event_allowed_for_ai:
        f.write(f"\tEVENT_ALLOWED_FOR_AI\n")

    # Write sound conditions
    for sound_condition in sound.event_list:
        comparison_value = round(sound_condition.comparison_value, 4)
        if sound_condition.event_type == "START":
            f.write(f"\tEVENT_START_COND {sound_condition.dataref_name} {sound_condition.comparison_operator} {comparison_value}\n")
        elif sound_condition.event_type == "END":
            f.write(f"\tEVENT_END_COND {sound_condition.dataref_name} {sound_condition.comparison_operator} {comparison_value}\n")
        elif sound_condition.event_type == "ALWAYS":
            f.write(f"\tEVENT_ALWAYS {sound_condition.dataref_name}\n")
        elif sound_condition.event_type.startswith("CMND"):
            f.write(f"\tEVENT_COMMAND {sound_condition.event_type}\n")

    # Write If event auto end from start condition
    if sound.event_auto_end_from_start_cond == True:
        f.write("\tEVENT_AUTO_END_FROM_START_COND\n")

    # Write end directive
    f.write("END_SOUND_ATTACHMENT\n\n")


def export_sound_space(f, collection, obj):
    "Writes sound space data to a .snd file for space type objects."

    f.write(f"# {collection.name + ' -> ' if collection != bpy.context.scene.collection else ''}{obj.name}\n")
    f.write("BEGIN_SOUND_SPACE\n")

    # Write space index
    f.write(f"\tSOUND_INDEX {obj.xp_sound_data.space_index}\n")

    # Write blend depth
    f.write(f"\tBLEND_DEPTH {obj.xp_sound_data.space_blend_depth}\n")

    if obj.empty_display_type == "CUBE":
        # Write bounding box dimensions
        minx = obj.location.x - obj.empty_display_size * obj.scale.x
        miny = obj.location.z - obj.empty_display_size * obj.scale.z
        minz = -obj.location.y - obj.empty_display_size * obj.scale.y
        maxx = obj.location.x + obj.empty_display_size * obj.scale.x
        maxy = obj.location.z + obj.empty_display_size * obj.scale.z
        maxz = -obj.location.y + obj.empty_display_size * obj.scale.y
        f.write(f"\tAABB {round(minx, 4)} {round(miny, 4)} {round(minz, 4)} {round(maxx, 4)} {round(maxy, 4)} {round(maxz, 4)}\n")

    if obj.empty_display_type == "SPHERE":
        # Write sphere center and radius
        f.write(f"\tSPHERE {round(obj.location.x, 4)} {round(obj.location.z, 4)} {round(obj.location.y, 4)} {obj.empty_display_size}\n")

    f.write("END_SOUND_SPACE\n\n")


# Define the export operator to write sound event data to a .snd file
class XPSOUND_export_snd(bpy.types.Operator):
    "Export sound conditions to a .snd file."

    bl_idname = "xpsound.export_snd"
    bl_label = "Export to .snd"

    def execute(self, context):
        scene = context.scene

        # Construct the path to snd file
        snd_file_path = bpy.path.abspath(os.path.join("//", context.scene.xp_sound_global.fmod_path, context.scene.xp_sound_global.snd_filename))
        snd_file_path = os.path.normpath(snd_file_path)

        print(snd_file_path)

        with open(snd_file_path, "w") as f:
            # Write header
            f.write("A\n1000\nACF_SOUNDS\n\n")

            if (scene.xp_sound_global.disable_legacy_alerts == True):
                f.write("DISABLE_LEGACY_ALERT_SOUNDS \n");
                
            # Write Ref Point
            f.write(f"REF_POINT_ACF {scene.xp_sound_global.ref_point_y} {scene.xp_sound_global.ref_point_z} \n\n")
            
            soundsIO = io.StringIO();
            snapshotsIO = io.StringIO();
            spacesIO = io.StringIO();
    
            # Recursively process collections
            self.process_collections(soundsIO, snapshotsIO, spacesIO, bpy.context.scene.collection)
            
            if (spacesIO.getvalue() != ""):
                f.write("############## \n");
                f.write("### SPACES ### \n");
                f.write("############## \n\n");
                f.write(spacesIO.getvalue());
                
            if (snapshotsIO.getvalue() != ""):
                f.write("################# \n");
                f.write("### SNAPSHOTS ### \n");
                f.write("################# \n\n");
                f.write(snapshotsIO.getvalue());
                
            if (soundsIO.getvalue() != ""):
                f.write("############## \n");
                f.write("### SOUNDS ### \n");
                f.write("############## \n\n");
                f.write(soundsIO.getvalue());

            # Write Info
            plugin_name = bl_info["name"]
            plugin_version = bl_info["version"]
            f.write(f"### Generated by {plugin_name} -> Version:{plugin_version}\n\n")
            
        self.report({"INFO"}, f"Exported sound conditions to {snd_file_path}")
        return {"FINISHED"}

    def process_collections(self, soundsIO, snapshotsIO, spacesIO, collection):
        "Recursively processes collections to find and export sound conditions."
        
        # Check if the collection is hidden
        if (collection.hide_viewport):
            return
        
        # Check if the collection contains any empties with xpsound attributes
        has_xpsound_empties = False
        for obj in collection.objects:
            if (
                obj.type == "EMPTY"
                and hasattr(obj, "xp_sound_data")
                and obj.xp_sound_data.event_type != "NONE"
                and not obj.hide_get()
            ):
                has_xpsound_empties = True
                break

        # Iterate through objects in the collection
        for obj in collection.objects:
            if obj.type == "EMPTY" and hasattr(obj, "xp_sound_data") and not obj.hide_get():
                
                if obj.xp_sound_data.event_type == "SOUND":
                    for sound in obj.xp_sound_data.xp_sound_list:
                        export_sound_attachment(soundsIO, collection, obj, sound)                    
                
                if obj.xp_sound_data.event_type == "SNAPSHOT":
                    for snapshot in obj.xp_sound_data.xp_snapshot_list:
                        export_snapshot_attachment(snapshotsIO, collection, obj, snapshot)
                
                if obj.xp_sound_data.event_type == "SPACE":                    
                    export_sound_space(spacesIO, collection, obj)                    


        # Recursively process child collections
        for child in collection.children:
            self.process_collections(soundsIO, snapshotsIO, spacesIO, child)

def register():
    bpy.utils.register_class(XPSOUND_export_snd)

def unregister():
    bpy.utils.unregister_class(XPSOUND_export_snd)

if __name__ == "__main__":
    register()
