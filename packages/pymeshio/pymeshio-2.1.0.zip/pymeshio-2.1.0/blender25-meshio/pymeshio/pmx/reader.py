# coding: utf-8
import io
import pymeshio.common
import pymeshio.pmx


class Reader(pymeshio.common.BinaryReader):
    """pmx reader
    """
    def __init__(self, ios,
            text_encoding,
            extended_uv,
            vertex_index_size,
            texture_index_size,
            material_index_size,
            bone_index_size,
            morph_index_size,
            rigidbody_index_size
            ):
        super(Reader, self).__init__(ios)
        self.read_text=self.get_read_text(text_encoding)
        if extended_uv>0:
            raise pymeshio.common.ParseException(
                    "extended uv is not supported", extended_uv)
        self.read_vertex_index=lambda : self.read_uint(vertex_index_size)
        self.read_texture_index=lambda : self.read_uint(texture_index_size)
        self.read_material_index=lambda : self.read_uint(material_index_size)
        self.read_bone_index=lambda : self.read_uint(bone_index_size)
        self.read_morph_index=lambda : self.read_uint(morph_index_size)
        self.read_rigidbody_index=lambda : self.read_uint(rigidbody_index_size)

    def __str__(self):
        return '<pymeshio.pmx.Reader>'

    def get_read_text(self, text_encoding):
        if text_encoding==0:
            def read_text():
                size=self.read_uint(4)
                return self.unpack("{0}s".format(size), size).decode("UTF16")
            return read_text
        elif text_encoding==1:
            def read_text():
                size=self.read_uint(4)
                return self.unpack("{0}s".format(size), size).decode("UTF8")
            return read_text
        else:
            print("unknown text encoding", text_encoding)

    def read_vertex(self):
        return pymeshio.pmx.Vertex(
                self.read_vector3(), # pos
                self.read_vector3(), # normal
                self.read_vector2(), # uv
                self.read_deform(), # deform(bone weight)
                self.read_float() # edge factor
                )

    def read_deform(self):
        deform_type=self.read_uint(1)
        if deform_type==0:
            return pymeshio.pmx.Bdef1(self.read_bone_index())
        elif deform_type==1:
            return pymeshio.pmx.Bdef2(
                    self.read_bone_index(),
                    self.read_bone_index(),
                    self.read_float()
                    )
        elif deform_type==2:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented Bdef4")
        else:
            raise pymeshio.common.ParseException(
                    "unknown deform type: {0}".format(deform_type))

    def read_material(self):
        material=pymeshio.pmx.Material(
                name=self.read_text(),
                english_name=self.read_text(),
                diffuse_color=self.read_rgb(),
                diffuse_alpha=self.read_float(),
                specular_color=self.read_rgb(),
                specular_factor=self.read_float(),
                ambient_color=self.read_rgb(),
                flag=self.read_uint(1),
                edge_color=self.read_rgba(),
                edge_size=self.read_float(),
                texture_index=self.read_texture_index(),
                sphia_texture_index=self.read_texture_index(),
                sphia_mode=self.read_uint(1),
                toon_sharing_flag=self.read_uint(1),
                )
        if material.toon_sharing_flag==0:
            material.toon_texture_index=self.read_texture_index()
        elif material.toon_sharing_flag==1:
            material.toon_texture_index=self.read_uint(1)
        else:
            raise pymeshio.common.ParseException(
                    "unknown toon_sharing_flag {0}".format(
                        material.toon_sharing_flag))
        material.comment=self.read_text()
        material.vertex_count=self.read_uint(4)
        return material

    def read_bone(self):
        bone=pymeshio.pmx.Bone(
                name=self.read_text(),
                english_name=self.read_text(),
                position=self.read_vector3(),
                parent_index=self.read_bone_index(),
                layer=self.read_uint(4),
                flag=self.read_uint(2)                
                )
        if bone.getConnectionFlag()==0:
            bone.tail_positoin=self.read_vector3()
        elif bone.getConnectionFlag()==1:
            bone.tail_index=self.read_bone_index()
        else:
            raise pymeshio.common.ParseException(
                    "unknown bone conenction flag: {0}".format(
                bone.getConnectionFlag()))

        if bone.getRotationFlag()==1 or bone.getTranslationFlag()==1:
            bone.effect_index=self.read_bone_index()
            bone.effect_factor=self.read_float()

        if bone.getFixedAxisFlag()==1:
            bone.fixed_axis=self.read_vector3()

        if bone.getLocalCoordinateFlag()==1:
            bone.local_x_vector=self.read_vector3()
            bone.local_z_vector=self.read_vector3()

        if bone.getExternalParentDeformFlag()==1:
            bone.external_key=self.read_uint(4)

        if bone.getIkFlag()==1:
            bone.ik=self.read_ik()

        return bone

    def read_ik(self):
        ik=pymeshio.pmx.Ik(
                target_index=self.read_bone_index(),
                loop=self.read_uint(4),
                limit_radian=self.read_float())
        link_size=self.read_uint(4)
        ik.link=[self.read_ik_link() 
                for _ in range(link_size)]

    def read_ik_link(self):
        link=pymeshio.pmx.IkLink(
                self.read_bone_index(),
                self.read_uint(1))
        if link.limit_angle==0:
            pass
        elif link.limit_angle==1:
            link.limit_min=self.read_vector3()
            link.limit_max=self.read_vector3()
        else:
            raise pymeshio.common.ParseException(
                    "invalid ik link limit_angle: {0}".format(
                link.limit_angle))
        return link

    def read_morgh(self):
        name=self.read_text()
        english_name=self.read_text()
        panel=self.read_uint(1)
        morph_type=self.read_uint(1)
        offset_size=self.read_uint(4)
        if morph_type==0:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented GroupMorph")
        elif morph_type==1:
            morph=pymeshio.pmx.Morph(name, english_name, 
                    panel, morph_type)
            morph.offsets=[self.read_vertex_morph_offset() 
                    for _ in range(offset_size)]
            return morph
        elif morph_type==2:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented BoneMorph")
        elif morph_type==3:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented UvMorph")
        elif morph_type==4:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented extended UvMorph1")
        elif morph_type==5:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented extended UvMorph2")
        elif morph_type==6:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented extended UvMorph3")
        elif morph_type==7:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented extended UvMorph4")
        elif morph_type==8:
            # todo
            raise pymeshio.common.ParseException(
                    "not implemented extended MaterialMorph")
        else:
            raise pymeshio.common.ParseException(
                    "unknown morph type: {0}".format(morph_type))

    def read_vertex_morph_offset(self):
        return pymeshio.pmx.VerexMorphOffset(
                self.read_vertex_index(), self.read_vector3())

    def read_display_slot(self):
        display_slot=pymeshio.pmx.DisplaySlot(self.read_text(), self.read_text(), 
                self.read_uint(1))
        display_count=self.read_uint(4)
        for _ in range(display_count):
            display_type=self.read_uint(1)
            if display_type==0:
                display_slot.refrences.append(
                        (display_type, self.read_bone_index()))
            elif display_type==1:
                display_slot.refrences.append(
                        (display_type, self.read_morph_index()))
            else:
                raise pymeshio.common.ParseException(
                        "unknown display_type: {0}".format(display_type))

    def read_rigidbody(self):
        return pymeshio.pmx.RigidBody(
                name=self.read_text(), 
                english_name=self.read_text(),
                bone_index=self.read_bone_index(),
                collision_group=self.read_uint(1),
                no_collision_group=self.read_uint(2),
                shape_type=self.read_uint(1),
                shape_size=self.read_vector3(),
                shape_position=self.read_vector3(),
                shape_rotation=self.read_vector3(),
                mass=self.read_float(),
                linear_damping=self.read_float(),
                angular_damping=self.read_float(),
                restitution=self.read_float(),
                friction=self.read_float(),
                mode=self.read_uint(1)
                )

    def read_joint(self):
        return pymeshio.pmx.Joint(
                name=self.read_text(),
                english_name=self.read_text(),
                joint_type=self.read_uint(1),
                rigidbody_index_a=self.read_rigidbody_index(),
                rigidbody_index_b=self.read_rigidbody_index(),
                position=self.read_vector3(),
                rotation=self.read_vector3(),
                translation_limit_min=self.read_vector3(),
                translation_limit_max=self.read_vector3(),
                rotation_limit_min=self.read_vector3(),
                rotation_limit_max=self.read_vector3(),
                spring_constant_translation=self.read_vector3(),
                spring_constant_rotation=self.read_vector3())


def read_from_file(path):
    return read(io.BytesIO(pymeshio.common.readall(path)))


def read(ios):
    assert(isinstance(ios, io.IOBase))
    reader=pymeshio.common.BinaryReader(ios)

    # header
    signature=reader.unpack("4s", 4)
    if signature!=b"PMX ":
        raise pymeshio.common.ParseException(
                "invalid signature", signature)

    version=reader.read_float()
    if version!=2.0:
        print("unknown version", version)
    model=pymeshio.pmx.Model(version)

    # flags
    flag_bytes=reader.read_uint(1)
    if flag_bytes!=8:
        raise pymeshio.common.ParseException(
                "invalid flag length", reader.flag_bytes)
    text_encoding=reader.read_uint(1)
    extended_uv=reader.read_uint(1)
    vertex_index_size=reader.read_uint(1)
    texture_index_size=reader.read_uint(1)
    material_index_size=reader.read_uint(1)
    bone_index_size=reader.read_uint(1)
    morph_index_size=reader.read_uint(1)
    rigidbody_index_size=reader.read_uint(1)
    
    # pmx custom reader
    reader=Reader(reader.ios,
            text_encoding,
            extended_uv,
            vertex_index_size,
            texture_index_size,
            material_index_size,
            bone_index_size,
            morph_index_size,
            rigidbody_index_size
            )

    # model info
    model.name = reader.read_text()
    model.english_name = reader.read_text()
    model.comment = reader.read_text()
    model.english_comment = reader.read_text()

    # model data
    model.vertices=[reader.read_vertex() 
            for _ in range(reader.read_uint(4))]
    model.indices=[reader.read_vertex_index() 
            for _ in range(reader.read_uint(4))]
    model.textures=[reader.read_text() 
            for _ in range(reader.read_uint(4))]
    model.materials=[reader.read_material() 
            for _ in range(reader.read_uint(4))]
    model.bones=[reader.read_bone() 
            for _ in range(reader.read_uint(4))]
    model.morphs=[reader.read_morgh() 
            for _ in range(reader.read_uint(4))]
    model.display_slots=[reader.read_display_slot() 
            for _ in range(reader.read_uint(4))]
    model.rigidbodies=[reader.read_rigidbody()
            for _ in range(reader.read_uint(4))]
    model.joints=[reader.read_joint()
            for _ in range(reader.read_uint(4))]

    return model

