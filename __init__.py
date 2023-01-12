# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
"name": "Ground objects",
"description": "Ground selected objects (Using lowest point of bounding box)",
"author": "Samuel Bernou",
"version": (1, 2, 0),
"blender": (2, 83, 0),
"location": "Sidebar > Tool > Ground object",
"warning": "",
"doc_url": "https://github.com/Pullusb/SB_ground_objects",
"category": "3D View",
}

import bpy
from mathutils import Vector


class MESH_OT_ground_object(bpy.types.Operator):
    """Ground all selected object keepong offset"""
    bl_idname = "object.ground_selected_objects"
    bl_label = "Ground all objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        settings = context.scene.grd_objs_toolsettings

        if not settings.use_active and settings.affect_individually:
            for o in context.selected_objects:
                points = [o.matrix_world @ Vector(b) for b in o.bound_box]
                points.sort(key=lambda x: x[2])
                z_altitude = points[0][2]
                if settings.use_3d_cursor:
                    z_altitude -= context.scene.cursor.location.z
                o.location.z -= z_altitude

            self.report({'INFO'}, f'Grounded {len(context.selected_objects)} objects')
            return {'FINISHED'}

        points = []
        if settings.use_active:# consider active object Bbox
            points = [context.object.matrix_world @ Vector(b) for b in context.object.bound_box]

        else: # All obj bbox
            for o in context.selected_objects:
                for b in o.bound_box:
                    points.append(o.matrix_world @ Vector(b))

        points.sort(key=lambda x: x[2])
        z_altitude = points[0][2]
        if settings.use_3d_cursor:
            z_altitude -= context.scene.cursor.location.z

        for o in context.selected_objects:
            o.location.z -= z_altitude

        self.report({'INFO'}, f'Z moved by {z_altitude}')
        return {'FINISHED'}


class MESH_OT_center_on_axis(bpy.types.Operator):
    """Put the model at center of defined axis"""
    bl_idname = "object.center_on_axis"
    bl_label = "Center on one axis"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    individually : bpy.props.BoolProperty(
        name="Individually", description="", default=False)


    axis : bpy.props.IntProperty(default=0)

        #(key, label, descr, id[, icon])
    def to_center(self, o, axis=1):
        '''If no axis is given, on Y axis'''
        points = [o.matrix_world @ Vector(b) for b in o.bound_box]
        points.sort(key=lambda x: x[axis])
        # all course to zero minus half the distance between min and max (max - min)/2 (equivalent to o.dimensions[axis]/2)
        # o.location[axis] -= points[0][axis] + (points[-1][axis] - points[0][axis])/2

        offset = points[0][axis] + o.dimensions[axis]/2
        if bpy.context.scene.grd_objs_toolsettings.use_3d_cursor:
            offset -= bpy.context.scene.cursor.location[axis]

        o.location[axis] -= offset

    def execute(self, context):
        axis = self.axis
        settings =  context.scene.grd_objs_toolsettings
        if not settings.use_active and settings.affect_individually:
            for o in context.selected_objects:
                self.to_center(o, axis)
            self.report({'INFO'}, f'Centered {len(context.selected_objects)} objects')
            return {'FINISHED'}

        points = []
        if settings.use_active: # consider active object Bbox
            points = [context.object.matrix_world @ Vector(b) for b in context.object.bound_box]

        else:# consider all selected object Bbox
            for o in context.selected_objects:
                for b in o.bound_box:
                    points.append(o.matrix_world @ Vector(b))


        points.sort(key=lambda x: x[axis])
        min_axis_dist = points[0][axis]
        max_axis_dist = points[-1][axis]
        offset = min_axis_dist + ((max_axis_dist - min_axis_dist)/2)

        if settings.use_3d_cursor:
            offset -= context.scene.cursor.location[axis]

        for o in context.selected_objects:
            o.location[axis] -= offset

        self.report({'INFO'}, f"Axis {['X','Y','Z'][axis]} moved by {offset}")
        return {'FINISHED'}

class MESH_PT_ground_object_UI(bpy.types.Panel):
    bl_label = "Ground objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    # bl_context = "object"

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True

        ## Options
        layout.prop(context.scene.grd_objs_toolsettings, 'use_3d_cursor')
        layout.prop(context.scene.grd_objs_toolsettings, 'use_active')

        # if not context.scene.grd_objs_toolsettings.use_active:
            # layout.prop(context.scene.grd_objs_toolsettings, 'affect_individually')
        col = layout.column()
        col.active = not context.scene.grd_objs_toolsettings.use_active
        col.prop(context.scene.grd_objs_toolsettings, 'affect_individually')

        ## Ground
        layout.operator("object.ground_selected_objects", text = 'Ground objects')
        
        # layout.separator()
        
        ## Center
        ### commented:  layout.prop(context.scene, 'grd_object_center_axis')
        # layout.operator("object.center_on_axis", text = 'Center on Axis').use_active = True

        row = layout.row(align=True)
        row.label(text='Center on')
        row.operator("object.center_on_axis", text = 'X').axis = 0
        row.operator("object.center_on_axis", text = 'Y').axis = 1
        row.operator("object.center_on_axis", text = 'Z').axis = 2


class GRD_PGT_toolsettings(bpy.types.PropertyGroup) :
    affect_individually : bpy.props.BoolProperty(
        name="Individually",
        description="Affect objects in selection individually instead of considering as a group",
        default=False)

    use_active : bpy.props.BoolProperty(
        name="Offset From Active", description="Consider only active object to move with all other objects following along\n(incompatible with individual mode)", default=False)
    
    use_3d_cursor : bpy.props.BoolProperty(
        name="On 3d Cursor", description="Use 3d cursor as reference (Instead of world center)", default=True)
    
    # bpy.types.Scene.grd_object_center_axis = bpy.props.EnumProperty(
    #     name="Axis", description="Axis to align to", default='Y',
    #     items=(
    #         ('X', 'X', 'Center on X "lateral" axis', 'AXIS_SIDE', 0),
    #         ('Y', 'Y', 'Center on Y "depth" axis', 'AXIS_FRONT', 1),
    #         ('Z', 'Z', 'Center on Z "height" axis', 'AXIS_TOP', 2),
    #         ))


### --- REGISTER ---
classes = (
GRD_PGT_toolsettings,
MESH_OT_ground_object,
MESH_OT_center_on_axis,
MESH_PT_ground_object_UI,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.grd_objs_toolsettings = bpy.props.PointerProperty(type = GRD_PGT_toolsettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.grd_objs_toolsettings

if __name__ == "__main__":
    register()
