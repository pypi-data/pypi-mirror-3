# coding: utf-8
"""
========================
MikuMikuDance PMD format
========================

file format
~~~~~~~~~~~
* http://blog.goo.ne.jp/torisu_tetosuki/e/209ad341d3ece2b1b4df24abf619d6e4 

specs
~~~~~
* textencoding: bytes(cp932)
* coordinate: left handed y-up(DirectX)
* uv origin: 
* face: only triangle
* backculling: 

"""
import os
import sys
import struct
import warnings
from .. import common


class Vertex(object):
    """pmd vertex struct.

    Attributes:
        pos: Vector3
        normal: Vector3
        uv: Vector2
        bone0: bone index
        bone1: bone index
        weight0: bone0 influence
        edge_flag: int flag
    """
    __slots__=['pos', 'normal', 'uv', 'bone0', 'bone1', 'weight0', 'edge_flag']
    def __init__(self, pos, normal, uv, 
            bone0, bone1, weight0, edge_flag):
        self.pos=pos
        self.normal=normal
        self.uv=uv
        self.bone0=bone0
        self.bone1=bone1
        self.weight0=weight0
        self.edge_flag=edge_flag

    def __str__(self):
        return "<%s %s %s, (%d, %d, %d)>" % (
                str(self.pos), 
                str(self.normal), 
                str(self.uv), 
                self.bone0, self.bone1, self.weight0)

    def __eq__(self, rhs):
        return (
                self.pos==rhs.pos
                and self.normal==rhs.normal
                and self.uv==rhs.uv
                and self.bone0==rhs.bone0
                and self.bone1==rhs.bone1
                and self.weight0==rhs.weight0
                and self.edge_flag==rhs.edge_flag
                )

    def __getitem__(self, key):
        if key==0:
            return self.pos.x
        elif key==1:
            return self.pos.y
        elif key==2:
            return self.pos.z
        else:
            assert(False)


class Material(object):
    """pmd material struct.

    Attributes:
        diffuse_color: RGB
        alpha: float
        specular_factor: float
        specular_color: RGB
        ambient_color: RGB
        toon_index: int
        edge_flag: int
        vertex_count: indices length
        texture_file: texture file path
    """
    __slots__=[
            'diffuse_color', 'alpha', 
            'specular_factor', 'specular_color', 'ambient_color', 
            'toon_index', 'edge_flag',
            'vertex_count', 'texture_file', 
            ]
    def __init__(self, diffuse_color, alpha,
            specular_factor, specular_color, ambient_color,
            toon_index, edge_flag, vertex_count, texture_file):
        self.diffuse_color=diffuse_color
        self.alpha=alpha
        self.specular_factor=specular_factor
        self.specular_color=specular_color
        self.ambient_color=ambient_color
        self.toon_index=toon_index
        self.edge_flag=edge_flag
        self.vertex_count=vertex_count
        self.texture_file=texture_file

    def __str__(self):
        return "<Material [%f, %f, %f, %f]>" % (
                self.diffuse[0], self.diffuse[1], 
                self.diffuse[2], self.diffuse[3],
                )

    def __eq__(self, rhs):
        return (
                self.diffuse_color==rhs.diffuse_color
                and self.alpha==rhs.alpha
                and self.specular_factor==rhs.specular_factor
                and self.specular_color==rhs.specular_color
                and self.ambient_color==rhs.ambient_color
                and self.toon_index==rhs.toon_index
                and self.edge_flag==rhs.edge_flag
                and self.vertex_count==rhs.vertex_count
                and self.texture_file==rhs.texture_file
                )


class Bone(object):
    """pmd material struct.

    Attributes:
        _name: 
        index:
        type:
        ik:
        pos:
        _english_name:
        ik_index:
        parent_index:
        tail_index:

        parent:
        tail:
        children:
    """
    # kinds
    ROTATE = 0
    ROTATE_MOVE = 1
    IK = 2
    IK_ROTATE_INFL = 4
    ROTATE_INFL = 5
    IK_TARGET = 6
    UNVISIBLE = 7
    # since v4.0
    ROLLING=8 # ?
    TWEAK=9
    __slots__=['name', 'index', 'type', 'parent', 'ik', 'pos',
            'children', 'english_name', 'ik_index',
            'parent_index', 'tail_index', 'tail',
            ]
    def __init__(self, name=b'bone', type=0):
        self.name=name
        self.index=0
        self.type=type
        self.parent_index=0xFFFF
        self.tail_index=0
        self.tail=common.Vector3(0, 0, 0)
        self.parent=None
        self.ik_index=0xFFFF
        self.pos=common.Vector3(0, 0, 0)
        self.children=[]
        self.english_name=''

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.index==rhs.index
                and self.type==rhs.type
                and self.parent_index==rhs.parent_index
                and self.tail_index==rhs.tail_index
                and self.tail==rhs.tail
                and self.ik_index==rhs.ik_index
                and self.pos==rhs.pos
                and self.children==rhs.children
                and self.english_name==rhs.english_name
                )

    def hasParent(self):
        return self.parent_index!=0xFFFF

    def hasChild(self):
        return self.tail_index!=0

    def display(self, indent=[]):
        if len(indent)>0:
            prefix=''
            for i, is_end in enumerate(indent):
                if i==len(indent)-1:
                    break
                else:
                    prefix+='  ' if is_end else ' |'
            uni='%s +%s(%s)' % (prefix, unicode(self), self.english_name)
            print(uni.encode(ENCODING))
        else:
            uni='%s(%s)' % (unicode(self), self.english_name)
            print(uni.encode(ENCODING))

        child_count=len(self.children)
        for i in range(child_count):
            child=self.children[i]
            if i<child_count-1:
                child.display(indent+[False])
            else:
                # last
                child.display(indent+[True])

# 0
class Bone_Rotate(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Rotate, self).__init__(name, 0)
    def __str__(self):
        return '<ROTATE %s>' % (self.name)
# 1
class Bone_RotateMove(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_RotateMove, self).__init__(name, 1)
    def __str__(self):
        return '<ROTATE_MOVE %s>' % (self.name)
# 2
class Bone_IK(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_IK, self).__init__(name, 2)
    def __str__(self):
        return '<IK %s>' % (self.name)
# 4
class Bone_IKRotateInfl(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_IKRotateInfl, self).__init__(name, 4)
    def __str__(self):
        return '<IK_ROTATE_INFL %s>' % (self.name)
# 5
class Bone_RotateInfl(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_RotateInfl, self).__init__(name, 5)
    def __str__(self):
        return '<ROTATE_INFL %s>' % (self.name)
# 6
class Bone_IKTarget(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_IKTarget, self).__init__(name, 6)
    def __str__(self):
        return '<IK_TARGET %s>' % (self.name)
# 7
class Bone_Unvisible(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Unvisible, self).__init__(name, 7)
    def __str__(self):
        return '<UNVISIBLE %s>' % (self.name)
# 8
class Bone_Rolling(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Rolling, self).__init__(name, 8)
    def __str__(self):
        return '<ROLLING %s>' % (self.name)
# 9
class Bone_Tweak(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Tweak, self).__init__(name, 9)
    def __str__(self):
        return '<TWEAK %s>' % (self.name)


def createBone(name, type):
    if type==0:
        return Bone_Rotate(name)
    elif type==1:
        return Bone_RotateMove(name)
    elif type==2:
        return Bone_IK(name)
    elif type==3:
        raise Exception("no used bone type: 3(%s)" % name)
    elif type==4:
        return Bone_IKRotateInfl(name)
    elif type==5:
        return Bone_RotateInfl(name)
    elif type==6:
        return Bone_IKTarget(name)
    elif type==7:
        return Bone_Unvisible(name)
    elif type==8:
        return Bone_Rolling(name)
    elif type==9:
        return Bone_Tweak(name)
    else:
        raise Exception("unknown bone type: %d(%s)", type, name)


class IK(object):
    __slots__=['index', 'target', 'iterations', 'weight', 'length', 'children']
    def __init__(self, index=0, target=0):
        self.index=index
        self.target=target
        self.iterations=None
        self.weight=None
        self.children=[]

    def __str__(self):
        return "<IK index: %d, target: %d, iterations: %d, weight: %f, children: %s(%d)>" %(self.index, self.target, self.iterations, self.weight, '-'.join([str(i) for i in self.children]), len(self.children))

    def __eq__(self, rhs):
        return (
                self.index==rhs.index
                and self.target==rhs.target
                and self.iterations==rhs.iterations
                and self.weight==rhs.weight
                and self.children==rhs.children
                )


class Morph(object):
    __slots__=['name', 'type', 'indices', 'pos_list', 'english_name',
            'vertex_count']
    def __init__(self, name):
        self.name=name
        self.type=None
        self.indices=[]
        self.pos_list=[]
        self.english_name=''
        self.vertex_count=0

    def append(self, index, x, y, z):
        self.indices.append(index)
        self.pos_list.append(common.Vector3(x, y, z))

    def __str__(self):
        return '<Skin name: "%s", type: %d, vertex: %d>' % (
            self.name, self.type, len(self.indices))

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.type==rhs.type
                and self.indices==rhs.indices
                and self.pos_list==rhs.pos_list
                and self.english_name==rhs.english_name
                and self.vertex_count==rhs.vertex_count
                )


class BoneGroup(object):
    __slots__=['name', 'english_name']
    def __init__(self, name=b'group', english_name=b'center'): 
        self.name=name
        self.english_name=english_name

    def __eq__(self, rhs):
        return self.name==rhs.name and self.english_name==rhs.english_name


SHAPE_SPHERE=0
SHAPE_BOX=1
SHAPE_CAPSULE=2

RIGIDBODY_KINEMATICS=0
RIGIDBODY_PHYSICS=1
RIGIDBODY_PHYSICS_WITH_BONE=2


class RigidBody(object):
    __slots__=['name', 
            'bone_index', 
            'collision_group', 
            'no_collision_group', 
            'shape_type',
            'shape_size',
            'shape_position', 
            'shape_rotation', 
            'mass',
            'linear_damping', 
            'angular_damping', 
            'restitution', 
            'friction', 
            'mode'
            ]
    def __init__(self, name,
            bone_index, 
            collision_group, 
            no_collision_group, 
            mass,
            linear_damping, 
            angular_damping, 
            restitution, 
            friction, 
            mode,
            shape_type=0,
            shape_size=common.Vector3(),
            shape_position=common.Vector3(), 
            shape_rotation=common.Vector3() 
            ):
        self.name=name
        self.bone_index=bone_index
        self.collision_group=collision_group 
        self.no_collision_group=no_collision_group 
        self.shape_type=shape_type
        self.shape_size=shape_size
        self.shape_position=shape_position
        self.shape_rotation=shape_rotation
        self.mass=mass
        self.linear_damping=linear_damping
        self.angular_damping=angular_damping
        self.restitution=restitution
        self.friction=friction
        self.mode=mode

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.bone_index==rhs.bone_index
                and self.collision_group==rhs.collision_group
                and self.no_collision_group==rhs.no_collision_group
                and self.shape_type==rhs.shape_type
                and self.shape_size==rhs.shape_size
                and self.shape_position==rhs.shape_position
                and self.shape_rotation==rhs.shape_rotation
                and self.mass==rhs.mass
                and self.linear_damping==rhs.linear_damping
                and self.angular_damping==rhs.angular_damping
                and self.restitution==rhs.restitution
                and self.friction==rhs.friction
                and self.mode==rhs.mode
                )


class Joint(object):
    __slots__=[ 'name', 'rigidbody_index_a', 'rigidbody_index_b', 
            'position', 'rotation',
            'translation_limit_max', 'translation_limit_min',
            'rotation_limit_max', 'rotation_limit_min',
            'spring_constant_translation', 'spring_constant_rotation',
            ]
    def __init__(self, name,
            rigidbody_index_a, rigidbody_index_b,
            position, rotation,
            translation_limit_max, translation_limit_min,
            rotation_limit_max, rotation_limit_min,
            spring_constant_translation, spring_constant_rotation
            ):
        self.name=name
        self.rigidbody_index_a=rigidbody_index_a
        self.rigidbody_index_b=rigidbody_index_b
        self.position=position
        self.rotation=rotation
        self.translation_limit_max=translation_limit_max
        self.translation_limit_min=translation_limit_min
        self.rotation_limit_max=rotation_limit_max
        self.rotation_limit_min=rotation_limit_min
        self.spring_constant_translation=spring_constant_translation
        self.spring_constant_rotation=spring_constant_rotation

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.rigidbody_index_a==rhs.rigidbody_index_a
                and self.rigidbody_index_b==rhs.rigidbody_index_b
                and self.position==rhs.position
                and self.rotation==rhs.rotation
                and self.translation_limit_max==rhs.translation_limit_max
                and self.translation_limit_min==rhs.translation_limit_min
                and self.rotation_limit_max==rhs.rotation_limit_max
                and self.rotation_limit_min==rhs.rotation_limit_min
                and self.spring_constant_translation==rhs.spring_constant_translation
                and self.spring_constant_rotation==rhs.spring_constant_rotation
                )


class Model(object):
    """pmd loader class.

    Attributes:
        io: internal use.
        end: internal use.
        pos: internal user.

        version: pmd version number
        _name: internal
    """
    __slots__=[
            'version', 'name', 'comment',
            'english_name', 'english_comment',
            'vertices', 'indices', 'materials', 'bones', 
            'ik_list', 'morphs',
            'morph_indices', 'bone_group_list', 'bone_display_list',
            'toon_textures',
            'rigidbodies', 'joints',

            'no_parent_bones',
            ]
    def __init__(self, version):
        self.version=version
        self.name=b''
        self.comment=b''
        self.english_name=b''
        self.english_comment=b''
        self.vertices=[]
        self.indices=[]
        self.materials=[]
        self.bones=[]
        self.ik_list=[]
        self.morphs=[]
        self.morph_indices=[]
        self.bone_group_list=[]
        self.bone_display_list=[]
        # extend
        self.toon_textures=[b'']*10
        self.rigidbodies=[]
        self.joints=[]
        # innner use
        self.no_parent_bones=[]

    def each_vertex(self): return self.vertices
    def getUV(self, i): return self.vertices[i].uv

    def __str__(self):
        return '<pmd-%g, "%s" vertex: %d, face: %d, material: %d, bone: %d ik: %d, skin: %d>' % (
            self.version, self.name, len(self.vertices), len(self.indices),
            len(self.materials), len(self.bones), len(self.ik_list), len(self.morph_list))

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.comment==rhs.comment
                and self.english_name==rhs.english_name
                and self.english_comment==rhs.english_comment
                and self.vertices==rhs.vertices
                and self.indices==rhs.indices
                and self.materials==rhs.materials
                and self.bones==rhs.bones
                and self.ik_list==rhs.ik_list
                and self.morphs==rhs.morphs
                and self.morph_indices==rhs.morph_indices
                and self.bone_group_list==rhs.bone_group_list
                and self.bone_display_list==rhs.bone_display_list
                and self.toon_textures==rhs.toon_textures
                and self.rigidbodies==rhs.rigidbodies
                and self.joints==rhs.joints
                )

    def diff(self, rhs):
        if self.name!=rhs.name: 
            print(self.name, rhs.name)
            return
        if self.comment!=rhs.comment: 
            print(self.comment, rhs.comment)
            return
        if self.english_name!=rhs.english_name: 
            print(self.english_name, rhs.english_name)
            return
        if self.english_comment!=rhs.english_comment: 
            print(self.english_comment, rhs.english_comment)
            return
        if self.vertices!=rhs.vertices: 
            print(self.vertices, rhs.vertices)
            return
        if self.indices!=rhs.indices: 
            print(self.indices, rhs.indices)
            return
        if self.materials!=rhs.materials: 
            print(self.materials, rhs.materials)
            return
        if self.bones!=rhs.bones: 
            print(self.bones, rhs.bones)
            return
        if self.ik_list!=rhs.ik_list: 
            print(self.ik_list, rhs.ik_list)
            return
        if self.morphs!=rhs.morphs: 
            print(self.morphs, rhs.morphs)
            return
        if self.morph_indices!=rhs.morph_indices: 
            print(self.morph_indices, rhs.morph_indices)
            return
        if self.bone_group_list!=rhs.bone_group_list: 
            print(self.bone_group_list, rhs.bone_group_list)
            return
        if self.bone_display_list!=rhs.bone_display_list: 
            print(self.bone_display_list, rhs.bone_display_list)
            return
        if self.toon_textures!=rhs.toon_textures: 
            print(self.toon_textures, rhs.toon_textures)
            return
        if self.rigidbodies!=rhs.rigidbodies: 
            print(self.rigidbodies, rhs.rigidbodies)
            return
        if self.joints!=rhs.joints: 
            print(self.joints, rhs.joints)
            return

