import bpy
import os

def check_node_usage(node_tree):
    unused_nodes = []
    for node in node_tree.nodes:
        is_used = any(output.is_linked for output in node.outputs) or any(input.is_linked for input in node.inputs)
        if not is_used:
            unused_nodes.append(node)
    return unused_nodes



os.system('cls')
materials = bpy.data.materials
print("=== Start work with Materials ===")
for material in materials:
    if material.use_nodes:
        print(f"Material: {material.name} uses nodes")
        unused_nodes = check_node_usage(material.node_tree)
        for node in unused_nodes:
            print(f"  Node: {node.name}, Type: {node.type} is not used in material {material.name}")
    else:
        print(f"Material: {material.name} does not use nodes")
        
print("=== Start work with Node Groups ===")
for node_group in bpy.data.node_groups:
        unused_nodes_at_groups = check_node_usage(node_group)
        if unused_nodes_at_groups:
            print(f"Node Group: {node_group.name}")
            for node in unused_nodes_at_groups:
                print(f"Node: {node.name}, Type: {node.type} is not used in node group {node_group.name}")