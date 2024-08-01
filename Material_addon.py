import bpy

# Получаем все материалы в сцене
materials = bpy.data.materials

# Выводим список всех материалов
for material in materials:
    print(f"Material: {material.name}")

