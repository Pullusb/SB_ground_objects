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
"version": (1, 0, 0),
"blender": (2, 83, 0),
"location": "Sidebar > Tool > Ground object",
"warning": "",
"doc_url": "",#2.8 > 2.82 : "wiki_url":"",
"category": "3D View",
}

import bpy
from mathutils import Vector


def to_zero(o):
    points = [o.matrix_world @ Vector(b) for b in o.bound_box]
    points.sort(key=lambda x: x[2])
    o.location.z -= points[0][2]

class MESH_OT_ground_object(bpy.types.Operator):
    """Ground all selected object keepong offset"""
    bl_idname = "object.ground_selected_objects"
    bl_label = "Ground all objects"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    all_to_zero : bpy.props.BoolProperty(
        name="All to zero", description="", default=False)

    def execute(self, context):
        if self.all_to_zero:
            for o in context.selected_objects:
                to_zero(o)
            self.report({'INFO'}, f'Grounded {len(context.selected_objects)} objects')
            return {'FINISHED'}

        points = []
        for o in context.selected_objects:
            for b in o.bound_box:
                points.append(o.matrix_world @ Vector(b))

        points.sort(key=lambda x: x[2])
        z_altitude = points[0][2]

        for o in context.selected_objects:
            o.location.z -= z_altitude

        self.report({'INFO'}, f'Z moved by {z_altitude}')#WARNING, ERROR
        return {'FINISHED'}

class MESH_PT_ground_object_UI(bpy.types.Panel):
    bl_label = "Ground object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    # bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.ground_selected_objects", text = 'Ground objects with offset').all_to_zero = False
        layout.operator("object.ground_selected_objects", text = 'Ground all to zero').all_to_zero = True



### --- REGISTER ---
classes = (
MESH_OT_ground_object,
MESH_PT_ground_object_UI,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
