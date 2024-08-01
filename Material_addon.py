import bpy

for ob in bpy.data.objects:
    print (ob.name)
    try:
        print (ob.name)
        material = ob.active_material
        print(material)
        
        material_slots = ob.material_slots
        for material in material_slots
            print(material1)
    except:
        print("Wrong")