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

def check_material_nodes():
    materials = bpy.data.materials
    for material in materials:
        if material.use_nodes:
            print(f"Material: {material.name} uses nodes")
            unused_nodes = check_node_usage(material.node_tree)
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
useless_nodes_from_groups =check_all_node_groups(node_groups_usage)
