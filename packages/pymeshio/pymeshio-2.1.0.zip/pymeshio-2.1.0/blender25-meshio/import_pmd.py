#!BPY
# coding:utf-8
"""
 Name: 'MikuMikuDance model (.pmd)...'
 Blender: 248
 Group: 'Import'
 Tooltip: 'Import PMD file for MikuMikuDance.'
"""
__author__= ["ousttrue"]
__url__=()
__bpydoc__="""
pmd Importer

This script imports a pmd into Blender for editing.

20091126: first implement.
20091209: implement IK.
20091210: implement morph target.
20100305: use english name.
20100408: cleanup not used vertices.
20100416: fix fornt face. texture load fail safe. add progress.
20100506: C extension.
20100521: add shape_key group.
20100530: add invisilbe bone tail(armature layer 2).
20100608: integrate 2.4 and 2.5.
20100616: implement rigid body.
20100619: fix for various models.
20100623: fix constraint name.
20100626: refactoring.
20100629: sphere map.
20100703: implement bone group.
20100710: implement toon texture.
20100718: keep model name, comment.
20100724: update for Blender2.53.
20100731: add full python module.
20101005: update for Blender2.54.
20101228: update for Blender2.55.
20110429: update for Blender2.57b.
20110522: implement RigidBody and Constraint.
20110918: update for Blender2.59.
20111002: update for pymeshio-2.1.0
"""
bl_addon_info = {
        'category': 'Import/Export',
        'name': 'Import: MikuMikuDance Model Format (.pmd)',
        'author': 'ousttrue',
        'version': (2, 2),
        'blender': (2, 5, 3),
        'location': 'File > Import',
        'description': 'Import from the MikuMikuDance Model Format (.pmd)',
        'warning': '', # used for warning icon and text in addons panel
        'wiki_url': 'http://sourceforge.jp/projects/meshio/wiki/FrontPage',
        'tracker_url': 'http://sourceforge.jp/ticket/newticket.php?group_id=5081',
        }


###############################################################################
# import
###############################################################################
import os
import sys
import math

from .pymeshio import pmd
from .pymeshio.pmd import reader
from .pymeshio import englishmap

# for 2.5
import bpy
import mathutils

# wrapper
from . import bl25 as bl

xrange=range

def createPmdMaterial(m, index):
    material = bpy.data.materials.new("Material")
    # diffuse
    material.diffuse_shader='FRESNEL'
    material.diffuse_color=([m.diffuse_color.r, m.diffuse_color.g, m.diffuse_color.b])
    material.alpha=m.alpha
    # specular
    material.specular_shader='TOON'
    material.specular_color=([m.specular_color.r, m.specular_color.g, m.specular_color.b])
    material.specular_toon_size=int(m.specular_factor)
    # ambient
    material.mirror_color=([m.ambient_color.r, m.ambient_color.g, m.ambient_color.b])
    # flag
    material.subsurface_scattering.use=True if m.edge_flag==1 else False
    # other
    material.name="m_%02d" % index
    material.preview_render_type='FLAT'
    material.use_transparency=True
    return material

def poseBoneLimit(n, b):
    if n.endswith("_t"):
        return
    if n.startswith("knee_"):
        b.lock_ik_y=True
        b.lock_ik_z=True
        b.lock_ik_x=False
        # IK limit
        b.use_ik_limit_x=True
        b.ik_min_x=0
        b.ik_max_x=180
    elif n.startswith("ankle_"):
        #b.ik_dof_y=False
        pass

def setSphereMap(material, index, blend_type='MULTIPLY'):
    slot=material.texture_slots[index]
    slot.texture_coords='NORMAL'
    slot.mapping='SPHERE'
    slot.blend_type=blend_type


###############################################################################
def VtoV(v):
    return bl.createVector(v.x, v.y, v.z)


def convert_coord(pos):
    """
    Left handed y-up to Right handed z-up
    """
    return (pos.x, pos.z, pos.y)


def to_radian(degree):
    return math.pi * degree / 180


def get_bone_name(l, index):
    if index==0xFFFF:
        return l.bones[0].name.decode('cp932')

    if index < len(l.bones):
        name=englishmap.getEnglishBoneName(l.bones[index].name.decode('cp932'))
        if name:
            return name
        return l.bones[index].name.decode('cp932')
    print('invalid bone index', index)
    return l.bones[0].name.decode('cp932')


def get_group_name(g):
    group_name=englishmap.getEnglishBoneGroupName(g.decode('cp932').strip())
    if not group_name:
        group_name=g.decode('cp932').strip()
    return group_name


def __importToonTextures(io, tex_dir):
    mesh, meshObject=bl.mesh.create(bl.TOON_TEXTURE_OBJECT)
    material=bl.material.create(bl.TOON_TEXTURE_OBJECT)
    bl.mesh.addMaterial(mesh, material)
    for i in range(10):
        toon=io.toon_textures[i]
        path=os.path.join(tex_dir, toon.decode('cp932'))
        texture, image=bl.texture.create(path)
        bl.material.addTexture(material, texture, False)
    return meshObject, material


def __importShape(obj, l, vertex_map):
    if len(l.morphs)==0:
        return

    # set shape_key pin
    bl.object.pinShape(obj, True)

    # find base
    base=None
    for s in l.morphs:
        if s.type==0:
            base=s

            # create vertex group
            bl.object.addVertexGroup(obj, bl.MMD_SHAPE_GROUP_NAME)
            hasShape=False
            for i in s.indices:
                if i in vertex_map:
                    hasShape=True
                    bl.object.assignVertexGroup(
                            obj, bl.MMD_SHAPE_GROUP_NAME, vertex_map[i], 0)
            if not hasShape:
                return
    assert(base)

    # create base key
    baseShapeBlock=bl.object.addShapeKey(obj, bl.BASE_SHAPE_NAME)
    # mesh
    mesh=bl.object.getData(obj)
    mesh.update()

    # each skin
    for s in l.morphs:
        if s.type==0:
            continue

        # name
        name=englishmap.getEnglishSkinName(s.name.decode('cp932'))
        if not name:
            name=s.name.decode('cp932')

        # 25
        new_shape_key=bl.object.addShapeKey(obj, name)

        for index, offset in zip(s.indices, s.pos_list):
            try:
                base_index=base.indices[index]
            except IndexError as msg:
                print(name)
                print(msg)
                print("invalid index %d/%d" % (index, len(base.indices)))
                continue
            vertex_index=vertex_map[base_index]
            bl.shapekey.assign(new_shape_key, vertex_index,
                    mesh.vertices[vertex_index].co+
                    bl.createVector(*convert_coord(offset)))

    # select base shape
    bl.object.setActivateShapeKey(obj, 0)


def __build(armature, b, p, parent):
    name=englishmap.getEnglishBoneName(b.name.decode('cp932'))
    if not name:
        name=b.name.decode('cp932')

    bone=bl.armature.createBone(armature, name)

    if parent and (b.tail_index==0 or b.type==6 or b.type==7 or b.type==9):
        # 先端ボーン
        bone.head = bl.createVector(*convert_coord(b.pos))
        bone.tail=bone.head+bl.createVector(0, 1, 0)
        bone.parent=parent
        if bone.name=="center_t":
            # センターボーンは(0, 1, 0)の方向を向いていないと具合が悪い
            parent.tail=parent.head+bl.createVector(0, 1, 0)
            bone.head=parent.tail
            bone.tail=bone.head+bl.createVector(0, 1, 0)
        else:
            if parent.tail==bone.head:
                pass
            else:
                print('diffurence with parent.tail and head', name)

        if b.type!=9:
            bl.bone.setConnected(bone)
        # armature layer 2
        bl.bone.setLayerMask(bone, [0, 1])
    else:
        # 通常ボーン
        bone.head = bl.createVector(*convert_coord(b.pos))
        bone.tail = bl.createVector(*convert_coord(b.tail))
        if parent:
            bone.parent=parent
            if parent.tail==bone.head:
                bl.bone.setConnected(bone)

    if bone.head==bone.tail:
        bone.tail=bone.head+bl.createVector(0, 1, 0)

    for c in b.children:
        __build(armature, c, b, bone)


def __importArmature(l):
    armature, armature_object=bl.armature.create()

    # build bone
    bl.armature.makeEditable(armature_object)
    for b in l.bones:
        if not b.parent:
            __build(armature, b, None, None)
    bl.armature.update(armature)
    bl.enterObjectMode()

    # IK constraint
    pose = bl.object.getPose(armature_object)
    for ik in l.ik_list:
        target=l.bones[ik.target]
        name = englishmap.getEnglishBoneName(target.name.decode('cp932'))
        if not name:
            name=target.name.decode('cp932')
        p_bone = pose.bones[name]
        if not p_bone:
            print('not found', name)
            continue
        if len(ik.children) >= 16:
            print('over MAX_CHAINLEN', ik, len(ik.children))
            continue
        effector_name=englishmap.getEnglishBoneName(
                l.bones[ik.index].name.decode('cp932'))
        if not effector_name:
            effector_name=l.bones[ik.index].name.decode('cp932')

        constraint=bl.armature.createIkConstraint(armature_object,
                p_bone, effector_name, ik)

    bl.armature.makeEditable(armature_object)
    bl.armature.update(armature)
    bl.enterObjectMode()

    # create bone group
    for i, g in enumerate(l.bone_group_list):
        name=get_group_name(g.name)
        bl.object.createBoneGroup(armature_object, name, "THEME%02d" % (i+1))

    # assign bone to group
    for b_index, g_index in l.bone_display_list:
        # bone
        b=l.bones[b_index]
        bone_name=englishmap.getEnglishBoneName(b.name.decode('cp932'))
        if not bone_name:
            bone_name=b.name.decode('cp932')
        # group
        g=l.bone_group_list[g_index-1]
        group_name=get_group_name(g.name)

        # assign
        pose.bones[bone_name].bone_group=pose.bone_groups[group_name]

    bl.enterObjectMode()

    return armature_object


def __import16MaerialAndMesh(meshObject, l,
        material_order, face_map, tex_dir, toon_material):

    mesh=bl.object.getData(meshObject)
    ############################################################
    # material
    ############################################################
    bl.progress_print('create materials')
    mesh_material_map={}
    textureMap={}
    imageMap={}
    index=0

    for material_index in material_order:
        try:
            m=l.materials[material_index]
            mesh_material_map[material_index]=index
        except KeyError:
            break

        material=createPmdMaterial(m, material_index)

        # main texture
        texture_name=m.texture_file.decode('cp932')
        if texture_name!='':
            for i, t in enumerate(texture_name.split('*')):
                if t in textureMap:
                    texture=textureMap[t]
                else:
                    path=os.path.join(tex_dir, t)
                    texture, image=bl.texture.create(path)
                    textureMap[texture_name]=texture
                    imageMap[material_index]=image
                texture_index=bl.material.addTexture(material, texture)
                if t.endswith('sph'):
                    # sphere map
                    setSphereMap(material, texture_index)
                elif t.endswith('spa'):
                    # sphere map
                    setSphereMap(material, texture_index, 'ADD')

        # toon texture
        toon_index=bl.material.addTexture(
                material,
                bl.material.getTexture(
                    toon_material,
                    0 if m.toon_index==0xFF else m.toon_index
                    ),
                False)

        bl.mesh.addMaterial(mesh, material)

        index+=1

    ############################################################
    # vertex
    ############################################################
    bl.progress_print('create vertices')
    # create vertices
    vertices=[]
    for v in l.each_vertex():
        vertices.append(convert_coord(v.pos))

    ############################################################
    # face
    ############################################################
    bl.progress_print('create faces')
    # create faces
    mesh_face_indices=[]
    mesh_face_materials=[]
    used_vertices=set()

    for material_index in material_order:
        face_offset=face_map[material_index]
        m=l.materials[material_index]
        material_faces=l.indices[face_offset:face_offset+m.vertex_count]

        def degenerate(i0, i1, i2):
            """
            縮退しているか？
            """
            return i0==i1 or i1==i2 or i2==i0

        for j in xrange(0, len(material_faces), 3):
            i0=material_faces[j]
            i1=material_faces[j+1]
            i2=material_faces[j+2]
            # flip
            triangle=[i2, i1, i0]
            if degenerate(*triangle):
                continue
            mesh_face_indices.append(triangle[0:3])
            mesh_face_materials.append(material_index)
            used_vertices.add(i0)
            used_vertices.add(i1)
            used_vertices.add(i2)

    ############################################################
    # create vertices & faces
    ############################################################
    bl.mesh.addGeometry(mesh, vertices, mesh_face_indices)

    ############################################################
    # vertex bone weight
    ############################################################
    # create vertex group
    vertex_groups={}
    for v in l.each_vertex():
        vertex_groups[v.bone0]=True
        vertex_groups[v.bone1]=True
    for i in vertex_groups.keys():
        bl.object.addVertexGroup(meshObject, get_bone_name(l, i))

    # vertex params
    bl.mesh.useVertexUV(mesh)
    for i, v, mvert in zip(xrange(len(l.vertices)),
        l.each_vertex(), mesh.vertices):
        # normal, uv
        bl.vertex.setNormal(mvert, convert_coord(v.normal))
        # bone weight
        w1=float(v.weight0)/100.0
        w2=1.0-w1
        bl.object.assignVertexGroup(meshObject, get_bone_name(l, v.bone0),
            i,  w1)
        bl.object.assignVertexGroup(meshObject, get_bone_name(l, v.bone1),
            i,  w2)

    ############################################################
    # face params
    ############################################################
    used_map={}
    bl.mesh.addUV(mesh)
    for i, (face, material_index) in enumerate(
            zip(mesh.faces, mesh_face_materials)):
        try:
            index=mesh_material_map[material_index]
        except KeyError as message:
            print(message, mesh_material_map, m)
            assert(False)
        bl.face.setMaterial(face, index)
        material=mesh.materials[index]
        used_map[index]=True
        if bl.material.hasTexture(material):
            uv_array=[l.getUV(i) for i in bl.face.getIndices(face)]
            bl.mesh.setFaceUV(mesh, i, face,
                    # fix uv
                    [(uv.x, 1.0-uv.y) for uv in uv_array],
                    imageMap.get(index, None))

        # set smooth
        bl.face.setSmooth(face, True)

    mesh.update()

    ############################################################
    # clean up not used vertices
    ############################################################
    bl.progress_print('clean up vertices not used')
    remove_vertices=[]
    vertex_map={}
    for i, v in enumerate(l.each_vertex()):
        if i in used_vertices:
            vertex_map[i]=len(vertex_map)
        else:
            remove_vertices.append(i)

    bl.mesh.vertsDelete(mesh, remove_vertices)

    bl.progress_print('%s created' % mesh.name)
    return vertex_map


def __importMaterialAndMesh(io, tex_dir, toon_material):
    """
    @param l[in] mmd.PMDLoader
    @param filename[in]
    """
    ############################################################
    # shpaeキーで使われるマテリアル優先的に前に並べる
    ############################################################
    # shapeキーで使われる頂点インデックスを集める
    shape_key_used_vertices=set()
    if len(io.morphs)>0:
        # base
        base=None
        for s in io.morphs:
            if s.type!=0:
                continue
            base=s
            break
        assert(base)

        for index in base.indices:
            shape_key_used_vertices.add(index)

    # マテリアルに含まれる頂点がshape_keyに含まれるか否か？
    def isMaterialUsedInShape(offset, m):
        for i in xrange(offset, offset+m.vertex_count):
            if io.indices[i] in shape_key_used_vertices:
                return True

    material_with_shape=set()

    # 各マテリアルの開始頂点インデックスを記録する
    face_map={}
    face_count=0
    for i, m in enumerate(io.materials):
        face_map[i]=face_count
        if isMaterialUsedInShape(face_count, m):
            material_with_shape.add(i)
        face_count+=m.vertex_count

    # shapeキーで使われる頂点のあるマテリアル
    material_with_shape=list(material_with_shape)
    material_with_shape.sort()

    # shapeキーに使われていないマテリアル
    material_without_shape=[]
    for i in range(len(io.materials)):
        if not i in material_with_shape:
            material_without_shape.append(i)

    # メッシュの生成
    def __splitList(l, length):
        for i in range(0, len(l), length):
            yield l[i:i+length]

    def __importMeshAndShape(material16, name):
        mesh, meshObject=bl.mesh.create(name)

        # activate object
        bl.object.deselectAll()
        bl.object.activate(meshObject)

        # shapeキーで使われる順に並べなおしたマテリアル16個分の
        # メッシュを作成する
        vertex_map=__import16MaerialAndMesh(
                meshObject, io, material16, face_map, tex_dir, toon_material)

        # crete shape key
        __importShape(meshObject, io, vertex_map)

        mesh.update()
        return meshObject

    mesh_objects=[__importMeshAndShape(material16, 'with_shape')
        for material16 in __splitList(material_with_shape, 16)]

    mesh_objects+=[__importMeshAndShape(material16, 'mesh')
        for material16 in __splitList(material_without_shape, 16)]

    return mesh_objects


def __importConstraints(io):
    print("create constraint")
    container=bl.object.createEmpty('Constraints')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bl.material.create('constraint')
    material.diffuse_color=(1, 0, 0)
    constraintMeshes=[]
    for i, c in enumerate(io.joints):
        bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8,
                ring_count=4,
                size=0.1,
                location=(c.position.x, c.position.z, c.position.y),
                layers=layers
                )
        meshObject=bl.object.getActive()
        constraintMeshes.append(meshObject)
        mesh=bl.object.getData(meshObject)
        bl.mesh.addMaterial(mesh, material)
        meshObject.name='c_%03d' % i
        #meshObject.draw_transparent=True
        #meshObject.draw_wire=True
        meshObject.draw_type='SOLID'
        rot=c.rotation
        meshObject.rotation_euler=(-rot.x, -rot.z, -rot.y)

        meshObject[bl.CONSTRAINT_NAME]=c.name.decode('cp932')
        meshObject[bl.CONSTRAINT_A]=io.rigidbodies[c.rigidbody_index_a].name.decode('cp932')
        meshObject[bl.CONSTRAINT_B]=io.rigidbodies[c.rigidbody_index_b].name.decode('cp932')
        meshObject[bl.CONSTRAINT_POS_MIN]=VtoV(c.translation_limit_min)
        meshObject[bl.CONSTRAINT_POS_MAX]=VtoV(c.translation_limit_max)
        meshObject[bl.CONSTRAINT_ROT_MIN]=VtoV(c.rotation_limit_min)
        meshObject[bl.CONSTRAINT_ROT_MAX]=VtoV(c.rotation_limit_max)
        meshObject[bl.CONSTRAINT_SPRING_POS]=VtoV(c.spring_constant_translation)
        meshObject[bl.CONSTRAINT_SPRING_ROT]=VtoV(c.spring_constant_rotation)

    for meshObject in reversed(constraintMeshes):
        bl.object.makeParent(container, meshObject)

    return container


def __importRigidBodies(io):
    print("create rigid bodies")

    container=bl.object.createEmpty('RigidBodies')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bl.material.create('rigidBody')
    rigidMeshes=[]
    for i, rigid in enumerate(io.rigidbodies):
        if rigid.bone_index==0xFFFF:
            # no reference bone
            bone=io.bones[0]
        else:
            bone=io.bones[rigid.bone_index]
        pos=bone.pos+rigid.shape_position

        if rigid.shape_type==pmd.SHAPE_SPHERE:
            bpy.ops.mesh.primitive_ico_sphere_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=rigid.shape_size.to_a())
        elif rigid.shape_type==pmd.SHAPE_BOX:
            bpy.ops.mesh.primitive_cube_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=rigid.shape_size.to_a())
        elif rigid.shape_type==pmd.SHAPE_CAPSULE:
            bpy.ops.mesh.primitive_cylinder_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=rigid.shape_size.to_a())
        else:
            assert(False)

        meshObject=bl.object.getActive()
        mesh=bl.object.getData(meshObject)
        rigidMeshes.append(meshObject)
        bl.mesh.addMaterial(mesh, material)
        meshObject.name='r_%03d' % i
        meshObject[bl.RIGID_NAME]=rigid.name.decode('cp932')
        #meshObject.draw_transparent=True
        #meshObject.draw_wire=True
        meshObject.draw_type='WIRE'
        rot=rigid.shape_rotation
        meshObject.rotation_euler=(-rot.x, -rot.z, -rot.y)

        # custom properties
        meshObject[bl.RIGID_SHAPE_TYPE]=rigid.shape_type
        meshObject[bl.RIGID_PROCESS_TYPE]=rigid.mode

        bone_name = englishmap.getEnglishBoneName(bone.name.decode('cp932'))
        if not bone_name:
            bone_name=bone.name.decode('cp932')
        meshObject[bl.RIGID_BONE_NAME]=bone_name

        meshObject[bl.RIGID_GROUP]=rigid.collision_group
        meshObject[bl.RIGID_INTERSECTION_GROUP]=rigid.no_collision_group
        meshObject[bl.RIGID_WEIGHT]=rigid.mass
        meshObject[bl.RIGID_LINEAR_DAMPING]=rigid.linear_damping
        meshObject[bl.RIGID_ANGULAR_DAMPING]=rigid.angular_damping
        meshObject[bl.RIGID_RESTITUTION]=rigid.restitution
        meshObject[bl.RIGID_FRICTION]=rigid.friction

    for meshObject in reversed(rigidMeshes):
        bl.object.makeParent(container, meshObject)

    return container


def _execute(filepath=""):
    """
    load pmd file to context.
    """

    # load pmd
    bl.progress_set('load %s' % filepath, 0.0)

    model=reader.read_from_file(filepath)
    if not model:
        bl.message("fail to load %s" % filepath)
        return
    bl.progress_set('loaded', 0.1)

    # create root object
    model_name=model.english_name.decode('cp932')
    if len(model_name)==0:
        model_name=model.name.decode('cp932')
    root=bl.object.createEmpty(model_name)
    root[bl.MMD_MB_NAME]=model.name.decode('cp932')
    root[bl.MMD_MB_COMMENT]=model.comment.decode('cp932')
    root[bl.MMD_COMMENT]=model.english_comment.decode('cp932')

    # toon textures
    tex_dir=os.path.dirname(filepath)
    toonTextures, toonMaterial=__importToonTextures(model, tex_dir)
    bl.object.makeParent(root, toonTextures)

    # import mesh
    mesh_objects=__importMaterialAndMesh(model, tex_dir, toonMaterial)
    for o in mesh_objects:
        bl.object.makeParent(root, o)

    # import armature
    armature_object=__importArmature(model)
    if armature_object:
        bl.object.makeParent(root, armature_object)
        armature = bl.object.getData(armature_object)

        # add armature modifier
        for o in mesh_objects:
            bl.modifier.addArmature(o, armature_object)

        # Limitation
        for n, b in bl.object.getPose(armature_object).bones.items():
            poseBoneLimit(n, b)

    # import rigid bodies
    rigidBodies=__importRigidBodies(model)
    if rigidBodies:
        bl.object.makeParent(root, rigidBodies)

    # import constraints
    constraints=__importConstraints(model)
    if constraints:
        bl.object.makeParent(root, constraints)

    bl.object.activate(root)

