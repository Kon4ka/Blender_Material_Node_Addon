import bpy
import os

def check_node_usage(node_tree):
    unused_nodes = []
    for node in node_tree.nodes:
        is_used = any(output.is_linked for output in node.outputs) or any(input.is_linked for input in node.inputs)
        if not is_used:
            unused_nodes.append(node)
    return unused_nodes



# Получаем все материалы в сцене
materials = bpy.data.materials
os.system('cls')
# Проверяем каждый материал на наличие нод
for material in materials:
    if material.use_nodes:
        print(f"Material: {material.name} uses nodes")
        for node in material.node_tree.nodes:
            
            # Проверяем, используется ли нода (подключены ли её выходы)
            is_used = any(output.is_linked for output in node.outputs) or any(input.is_linked for input in node.inputs)
            if is_used:
#                print(f"  Node: {node.name}, Type: {node.type} is used")
                # Если нода является группой, обрабатываем её отдельно
                pass
            else:
                print(f"  Node: {node.name}, Type: {node.type} is not used at material "
                      f"{material.name}") 
            
    else:
        print(f"Material: {material.name} does not use nodes")
        
for node_group in bpy.data.node_groups:
#        print(f"Node Group: {node_group.name}")
        unused_nodes = check_node_usage(node_group)
        for node in unused_nodes:
            print(f"  Node: {node.name}, Type: {node.type} is not used in node group {node_group.name}")