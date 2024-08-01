import bpy

# Получаем все материалы в сцене
materials = bpy.data.materials

# Проверяем каждый материал на наличие нод
for material in materials:
    if material.use_nodes:
        print(f"Material: {material.name} uses nodes")
        for node in material.node_tree.nodes:
            
            # Проверяем, используется ли нода (подключены ли её выходы)
            is_used = any(output.is_linked for output in node.outputs)
            if is_used:
#                print(f"  Node: {node.name}, Type: {node.type} is used")
                pass
            else:
                print(f"  Node: {node.name}, Type: {node.type} is not used at material "
                      f"{material.name}")
            
            # Если нода является группой, обрабатываем её отдельно
            if node.type == 'GROUP':
                group = node.node_tree
                print(f"  Node Group: {node.name} contains the following nodes:")
                for group_node in group.nodes:
                    print(f"    Group Node: {group_node.name}, Type: {group_node.type}")
    else:
        print(f"Material: {material.name} does not use nodes")
