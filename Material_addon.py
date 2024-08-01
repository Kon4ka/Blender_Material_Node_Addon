import bpy
import os

def check_node_usage(node_tree):
    unused_nodes = []
    for node in node_tree.nodes:
        is_output_linked = any(output.is_linked for output in node.outputs)
        is_input_linked = any(input.is_linked for input in node.inputs)
        is_frame = node.type == 'FRAME'
        
        if not (is_output_linked or is_input_linked) and not is_frame:
            unused_nodes.append(node)
    return unused_nodes

def collect_node_groups_usage():
    node_groups_usage = {}
    materials = bpy.data.materials
    for material in materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'GROUP':
                    group_name = node.node_tree.name
                    if group_name not in node_groups_usage:
                        node_groups_usage[group_name] = []
                    node_groups_usage[group_name].append(material.name)
    return node_groups_usage

def create_unused_frame(node_tree, unused_nodes):
    frame = node_tree.nodes.new(type="NodeFrame")
    frame.label = "Unused"
    frame.name = "Unused"
    frame.use_custom_color = True
    frame.color = (1.0, 0.5, 0.5)  # Красный цвет для фрейма

    for node in unused_nodes:
        # Перемещение ноды внутрь фрейма
        node.parent = frame
        
        # Если у ноды есть свободные входы, создаем атрибутную ноду и подключаем
        for input_socket in node.inputs:
            if not input_socket.is_linked:
                attr_node = node_tree.nodes.new(type="ShaderNodeAttribute")
                attr_node.name = f"Attr_{node.name}_{input_socket.name}"
                attr_node.label = f"Attr_{node.name}_{input_socket.name}"
                attr_node.location = (node.location.x - 200, node.location.y)
                node_tree.links.new(attr_node.outputs[0], input_socket)
                # Перемещаем ноду атрибута тоже во фрейм
                attr_node.parent = frame

    return frame

def position_unused_frame(node_tree, frame):
    # Находим минимальные координаты всех нод, чтобы разместить фрейм сверху
    min_x = min(node.location.x for node in node_tree.nodes)
    max_y = max(node.location.y for node in node_tree.nodes)
    
    # Задаём позицию фрейма выше всех остальных нод
    frame.location = (min_x - 300, max_y + 200)

def check_material_nodes():
    materials = bpy.data.materials
    for material in materials:
        if material.use_nodes:
            print(f"Material: {material.name} uses nodes")
            unused_nodes = check_node_usage(material.node_tree)
            if unused_nodes:
                frame = create_unused_frame(material.node_tree, unused_nodes)
                position_unused_frame(material.node_tree, frame)
                for node in unused_nodes:
                    print(f"  Node: {node.name}, Type: {node.type} is not used. Located in material {material.name}")
        else:
            print(f"Material: {material.name} does not use nodes")
    return unused_nodes

def check_all_node_groups(node_groups_usage):
    for node_group in bpy.data.node_groups:
        unused_nodes = check_node_usage(node_group)
        if unused_nodes:
            print(f"Node Group: {node_group.name}")
            frame = create_unused_frame(node_group, unused_nodes)
            position_unused_frame(node_group, frame)
            for node in unused_nodes:
                print(f"  Node: {node.name}, Type: {node.type} is not used in node group {node_group.name}")
            if node_group.name in node_groups_usage:
                print(f"  Used in materials: {', '.join(node_groups_usage[node_group.name])}")
    return unused_nodes

os.system('cls')

node_groups_usage = collect_node_groups_usage()

print("=== Start work with Materials ===")
useless_nodes = check_material_nodes()

print("=== Start work with Node Groups ===")
useless_nodes_from_groups = check_all_node_groups(node_groups_usage)
