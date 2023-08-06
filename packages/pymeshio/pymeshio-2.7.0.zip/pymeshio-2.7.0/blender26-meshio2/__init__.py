# coding: utf-8

bl_info={
        'category': 'Import-Export',
        'name': 'meshio. (.pmd)(.pmx)(.mqo)',
        'author': 'ousttrue',
        'version': (3, 0, 0),
        'blender': (2, 6, 4),
        'location': 'File > Import-Export',
        'description': 'Import-Export PMD/PMX/MQO meshes',
        #'warning': 'pmx importer/exporter is under development', 
        'wiki_url': 'http://meshio.sourceforge.jp/',
        'support': 'COMMUNITY',
        }


# To support reload properly, try to access a package var, if it's there, reload everything
if 'bpy' in locals():
    import imp
    if 'pymeshio_blender' in locals():
        if name in locals():
            imp.reaload(pymeshio_blender)
   

import bpy
import bpy_extras.io_utils
from .pymeshio import blender as pymeshio_blender


"""
importはpmd, pmx, mqo兼用
"""
class ImportMeshIO(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from PMD/PMX/MQO file format (.pmd|.pmx|.mqo)'''
    bl_idname = 'import_scene.meshio_mesh'
    bl_label = 'Import PMD/PMX/MQO'
    bl_options={'UNDO'}
    filename_ext = '.pmd;.pmx;.mqo'
    filter_glob = bpy.props.StringProperty(
            default='*.pmd;*.pmx;*.mqo', options={'HIDDEN'})

    """
    import_mesh=bpy.props.BoolProperty(
            name='import mesh', 
            description='import polygon mesh',
            default=True)

    import_physics=bpy.props.BoolProperty(
            name='import physics objects', 
            description='import rigid body and constraints',
            default=True)

    use_englishmap=bpy.props.BoolProperty(
            name='use english map', 
            description='Convert name to english(not implemented)',
            default=False)

    scale = bpy.props.FloatProperty(
            name='Scale',
            description='Scale the MQO by this value',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=0.1)
    """

    def execute(self, context):
        pymeshio_blender.import_file(context.scene, 
                **self.as_keywords(ignore=('filter_glob',)))
        return  {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname, 
                text='Pymeshio support model (.pmx)(.pmd)(.mqo)',
                icon='PLUGIN'
                )


class ExportPmd(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export to PMD file format (.pmd)'''
    bl_idname = 'export_scene.mmd_pmd'
    bl_label = 'Export PMD'
    filename_ext = '.pmd'
    filter_glob = bpy.props.StringProperty(
            default='*.pmd', options={'HIDDEN'})

    """
    use_selection = bpy.props.BoolProperty(
            name='Selection Only', 
            description='Export selected objects only', 
            default=False)
    """

    def execute(self, context):
        from . import export_pmd
        pymeshio_blender.export_pmd(context.scene,
                **self.as_keywords(
                    ignore=('check_existing', 'filter_glob')))
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.pmd')
        self.layout.operator(klass.bl_idname,
                text='Miku Miku Dance Model(.pmd)',
                icon='PLUGIN'
                ).filepath=default_path


class ExportPmx(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export to PMX file format (.pmx)'''
    bl_idname = 'export_scene.mmd_pmx'
    bl_label = 'Export PMX'

    filename_ext = '.pmx'
    filter_glob = bpy.props.StringProperty(
            default='*.pmx', options={'HIDDEN'})

    def execute(self, context):
        from . import export_pmx
        pymeshio_blenderxport_pmx(context.scene,
                **self.as_keywords(
                    ignore=('check_existing', 'filter_glob', 'use_selection')))
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.pmx')
        self.layout.operator(klass.bl_idname,
                text='Miku Miku Dance Model(.pmx)',
                icon='PLUGIN'
                ).filepath=default_path


class ExportMqo(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Save a Metasequoia MQO file.'''
    bl_idname = 'export_scene.metasequioa_mqo'
    bl_label = 'Export MQO'

    filename_ext = '.mqo'
    filter_glob = bpy.props.StringProperty(
            default='*.mqo', options={'HIDDEN'})

    scale = bpy.props.FloatProperty(
            name='Scale',
            description='Scale the MQO by this value',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=10.0)

    apply_modifier = bpy.props.BoolProperty(
            name='ApplyModifier',
            description='Would apply modifiers',
            default=False)

    def execute(self, context):
        pymeshio_blender.export(context.scene,
                **self.as_keywords(
                    ignore=('check_existing', 'filter_glob', 'use_selection')))
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.mqo')
        self.layout.operator(klass.bl_idname,
                text='Metasequoia (.mqo)',
                icon='PLUGIN'
                ).filepath=default_path


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(ImportMeshIO.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportPmd.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportPmx.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportMqo.menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(ImportMeshIO.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportPmd.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportPmx.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportMqo.menu_func)


if __name__=='__main__':
    register()

