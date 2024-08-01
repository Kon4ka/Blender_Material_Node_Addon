import bpy
import traceback


'''
Логирование:
Пишет логи или ошибки в файл в text editor
'''
def log_message(message):
    log_file = bpy.data.texts.get("addon_log")
    if log_file is None:
        log_file = bpy.data.texts.new("addon_log")
    log_file.write(message + "\n")


'''
Пороверка на неиспользуемые ноды.
Получает дерево нод из группы или материала.

Проходится по всем нодам, проверяет что нет входных связей, выходных связей и обьект не фрейм.
Собирает и возвращает лист из неиспользуемых нодов этого дерева.
'''
def check_node_usage(node_tree):
    unused_nodes = []
    try:
        for node in node_tree.nodes:
            is_output_linked = any(output.is_linked for output in node.outputs)
            is_input_linked = any(input.is_linked for input in node.inputs)
            is_frame = node.type == 'FRAME'

            if not (is_output_linked or is_input_linked) and not is_frame:
                unused_nodes.append(node)
    except Exception as e:
        log_message(f"Error in check_node_usage: {str(e)}")
        log_message(traceback.format_exc())
    return unused_nodes


'''
Вычисление в каких материалах учавствует какая группа нод.
Проходится по всем материалам и ищет помеченные как GROUP, 

На выходе словарь с именем группы и списком материалов где она встречается.
'''
def collect_node_groups_usage():
    node_groups_usage = {}
    try:
        materials = bpy.data.materials
        for material in materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'GROUP':
                        group_name = node.node_tree.name
                        if group_name not in node_groups_usage:
                            node_groups_usage[group_name] = []
                        node_groups_usage[group_name].append(material.name)
    except Exception as e:
        log_message(f"Error in collect_node_groups_usage: {str(e)}")
        log_message(traceback.format_exc())
    return node_groups_usage


'''
Вычисление позиции фрейма чтобы было без пересечений с основным деревом нодов.
Ищем минимум по х (самую левую ноду), и максимум по y (самую верхнюю ноду).
Релоцируем фрейм.
'''
def position_unused_frame(node_tree, frame):
    try:
        min_x = min(node.location.x for node in node_tree.nodes)
        max_y = max(node.location.y for node in node_tree.nodes)

        frame.location = (min_x - 300, max_y + 200)
    except Exception as e:
        log_message(f"Error in position_unused_frame: {str(e)}")
        log_message(traceback.format_exc())


'''
Проверка на неиспользованные ноды в материалах.
Проходимся по всем материалам, смотрим, используют ли они систему нод, если да,
ищем неиспользуемые ноды, создаём и позиционируем фрейм если таковые есть и
перемещаем их внутрь.
'''
def check_material_nodes():
    unused_nodes = []
    try:
        materials = bpy.data.materials
        for material in materials:
            if material.use_nodes:
                log_message(f"Material: {material.name} uses nodes")
                unused_nodes = check_node_usage(material.node_tree)
                if unused_nodes:
                    frame = create_unused_frame(
                        material.node_tree, unused_nodes)
                    position_unused_frame(material.node_tree, frame)
                    for node in unused_nodes:
                        log_message(
                            f"  Node: {node.name}, Type: {node.type} is not used. Located in material {material.name}")
            else:
                log_message(f"Material: {material.name} does not use nodes")
    except Exception as e:
        log_message(f"Error in check_material_nodes: {str(e)}")
        log_message(traceback.format_exc())
    return unused_nodes

'''
Проверка на неиспользованные ноды в группах нод.
Проходимся по всем группам, ищем неиспользуемые ноды, создаём и позиционируем фрейм если таковые есть и
перемещаем их внутрь.
'''
def check_all_node_groups(node_groups_usage):
    unused_nodes = []
    try:
        for node_group in bpy.data.node_groups:
            unused_nodes = check_node_usage(node_group)
            if unused_nodes:
                log_message(f"Node Group: {node_group.name}")
                frame = create_unused_frame(node_group, unused_nodes)
                position_unused_frame(node_group, frame)
                for node in unused_nodes:
                    log_message(
                        f"  Node: {node.name}, Type: {node.type} is not used in node group {node_group.name}")
                if node_group.name in node_groups_usage:
                    log_message(
                        f"  -- Used in materials: {', '.join(node_groups_usage[node_group.name])}")
    except Exception as e:
        log_message(f"Error in check_all_node_groups: {str(e)}")
        log_message(traceback.format_exc())
    return unused_nodes

'''
Создание фрейма неиспользуемых нод. 
Создаём фрейм, красим его и назначаем всем неиспользуемым нодам его как родителя.
Создаём атрибуты для каждого входа каждой ноды, смещаем их относительно неиспользуемой 
ноды и создаём атрибуты со смещением друг относительно друга.
'''
def create_unused_frame(node_tree, unused_nodes):
    frame = None
    try:
        frame = node_tree.nodes.new(type="NodeFrame")
        frame.label = "Unused"
        frame.name = "Unused"
        frame.use_custom_color = True
        frame.color = (4.0, 0.15, 0.15)

        for node in unused_nodes:
            node.parent = frame
            offset = 0

            for input_socket in node.inputs:
                if not input_socket.is_linked:
                    attr_node = node_tree.nodes.new(type="ShaderNodeAttribute")
                    attr_node.name = f"Attr_{node.name}_{input_socket.name}"
                    attr_node.label = f"Attr_{node.name}_{input_socket.name}"
                    attr_node.location = (
                        node.location.x - 200, node.location.y - offset)

                    if input_socket.type == 'VECTOR':
                        node_tree.links.new(
                            attr_node.outputs['Vector'], input_socket)
                    elif input_socket.type == 'VALUE':
                        node_tree.links.new(
                            attr_node.outputs['Fac'], input_socket)
                    elif input_socket.type == 'RGBA':
                        node_tree.links.new(
                            attr_node.outputs['Color'], input_socket)
                    elif input_socket.type == 'OTHER':
                        pass  # TODO more types?

                    attr_node.parent = frame

                    offset += 180
    except Exception as e:
        log_message(f"Error in create_unused_frame: {str(e)}")
        log_message(traceback.format_exc())
    return frame


'''
Регистрация Аддона в системе Блендера.
'''
bl_info = {
    "name": "Blender Material Node Addon",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "Node",
    "author": "Kon4ka",
    "description": "Addon for quick management of unused nodes in materials and adding custom attributes to them.",
    "location": "Node Editor > Sidebar > Material Node Addon",
    "warning": "",
    "wiki_url": "https://github.com/Kon4ka/Blender_Material_Node_Addon",
    "tracker_url": "https://github.com/Kon4ka/Blender_Material_Node_Addon/issues",
    "support": "COMMUNITY",
}


class NODE_PT_unused_nodes_panel(bpy.types.Panel):
    bl_label = "Unused Nodes Checker"
    bl_idname = "NODE_PT_unused_nodes_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Unused Nodes'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("node.check_unused_nodes", icon='FILE_TEXT')
        row = layout.row()
        row.operator("node.group_unused_nodes", icon='NODE')


class NODE_OT_group_unused_nodes(bpy.types.Operator):
    bl_idname = "node.group_unused_nodes"
    bl_label = "Group Unused Nodes"

    def execute(self, context):
        node_groups_usage = collect_node_groups_usage()
        print("=== Start work with Materials ===")
        check_material_nodes()
        print("=== Start work with Node Groups ===")
        check_all_node_groups(node_groups_usage)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(NODE_PT_unused_nodes_panel)
    bpy.utils.register_class(NODE_OT_group_unused_nodes)


def unregister():
    bpy.utils.unregister_class(NODE_PT_unused_nodes_panel)
    bpy.utils.unregister_class(NODE_OT_group_unused_nodes)


if __name__ == "__main__":
    register()
