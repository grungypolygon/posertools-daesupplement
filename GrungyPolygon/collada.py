import xml.etree.ElementTree as ET


# #############
# XML related helper functions

def nspace(element_name, mask=False):
    name_space = '''http://www.collada.org/2005/11/COLLADASchema'''
    if mask:
        return '{{' + name_space + '}}' + element_name
    else:
        return '{' + name_space + '}' + element_name

# #############
# XPATH queries
xp_scenes = nspace('scene') \
            + '/' + nspace('instance_visual_scene')

xp_scene_nodes = nspace('library_visual_scenes', True) \
                 + '/' + nspace('visual_scene', True) \
                 + '[@id=\'{scene_url}\']' \
                 + '/' + nspace('node', True)

xp_subnodes = nspace('node')

xp_instance_geometry = nspace('instance_geometry')

xp_geometry = nspace('library_geometries', True) \
              + '/' + nspace('geometry', True) \
              + '[@id=\'{geometry_url}\']' \
              + '/' + nspace('mesh', True)

xp_node_location = nspace('translate') \
                   + '[@sid=\'location\']'

xp_node_rotation = nspace('rotate')

xp_node_scale = nspace('scale') \
                + '[@sid=\'scale\']'

xp_source = nspace('source', True) \
            + '[@id=\'{source_url}\']'

xp_source_accessor = nspace('technique_common') \
                     + '/' + nspace('accessor')

xp_source_accessor_params = nspace('param')

xp_geometry_vertices_input = nspace('vertices') \
                             + '/' + nspace('input') \
                             + '[@semantic=\'POSITION\']'


# ############
# Helper functions

def parse_value_sequence(string_sequence, casters):
    result = []
    s = string_sequence.split()
    if len(s) > 0:
        val_group = None
        for idx, value in enumerate(s):
            if idx % len(casters) == 0:
                if val_group:
                    # print("xxx " + str(val_group))
                    result.append(val_group)
                val_group = []
            val_group.append(casters[idx % len(casters)](value))
        if val_group:
            # print("xxx " + str(val_group))
            result.append(val_group)
    # print("xxx " + str(casters) + " xxx " + str(s) + " yyy " + str(result))
    return result


def read_source(source_node):
    type_casters = {
        'float': float,
        'name': str,
    }

    accessor = source_node.find(xp_source_accessor)
    if accessor is None:
        return None
    source_url = accessor.attrib['source'][1:]
    values_node = source_node.find('./*[@id=\'{}\']'.format(source_url))
    if values_node is None:
        return None
    accessor = source_node.find(xp_source_accessor)
    if accessor is None:
        return None
    casters = []
    names = []
    for param in accessor.findall(xp_source_accessor_params):
        casters.append(type_casters[param.attrib['type']])
        names.append(param.attrib['name'].lower())
    values = parse_value_sequence(values_node.text, casters)
    return names, values


# ############
# Parsing

def parse_collada_file(file_path):
    tree = ET.parse(file_path)
    collada_root = tree.getroot()
    return collada_root


def dae_object_from_node(node, collada_root, parent_object=None):
    name = node.attrib.get('name', None)
    scene_id = node.attrib.get('id', None)
    node_type = node.attrib.get('type', None)
    dae_obj = DaeObject(scene_id, name)

    if parent_object is not None:
        dae_obj.parent = parent_object

    loc = node.find(xp_node_location)
    if loc is not None:
        dae_obj.pos = parse_value_sequence(loc.text, [float, float, float])[0]

    scale = node.find(xp_node_scale)
    if scale is not None:
        dae_obj.scale = parse_value_sequence(scale.text, [float, float, float])[0]

    rotations = node.findall(xp_node_rotation)
    if len(rotations) > 0:
        rot = [0, 0, 0]
        for rotation in rotations:
            val = float(rotation.text.split()[3])
            axis = rotation.attrib['sid'][-1]
            if axis.lower() == 'x':
                rot[0] = val
            elif axis.lower() == 'y':
                rot[1] = val
            elif axis.lower() == 'z':
                rot[2] = val
        dae_obj.rot = rot

    instance_geometry = node.find(xp_instance_geometry)
    if instance_geometry is not None:
        url = instance_geometry.attrib['url'][1:]
        dae_obj.mesh = get_mesh_for_node(url, collada_root)

    return dae_obj


def dae_mesh_from_geometry(geometry_node, collada_root):
    vertices_input = geometry_node.find(xp_geometry_vertices_input)
    if vertices_input is None:
        return None
    source_node = geometry_node.find(xp_source.format(source_url=vertices_input.attrib['source'][1:]))
    names, values = read_source(source_node)
    dae_mesh = DaeMesh()
    dae_mesh.vertices = values
    return dae_mesh


def get_sub_nodes(node, parent_object, dae_objects, collada_root):
    for sub_node in node.findall(xp_subnodes):
        dae_obj = dae_object_from_node(sub_node, collada_root, parent_object)
        dae_objects[dae_obj.scene_id] = dae_obj
        get_sub_nodes(sub_node, dae_obj, dae_objects, collada_root)


def get_mesh_for_node(url, collada_root):
    mesh_node = collada_root.find(xp_geometry.format(geometry_url=url))
    if mesh_node is None:
        return None
    return dae_mesh_from_geometry(mesh_node, collada_root)


def get_scene_objects(collada_root, scene_url):
    result = {}
    nodes = collada_root.findall(
        xp_scene_nodes.format(
            scene_url=scene_url
        )
    )
    for node in nodes:
        dae_obj = dae_object_from_node(node, collada_root)
        result[dae_obj.scene_id] = dae_obj
        get_sub_nodes(node, dae_obj, result, collada_root)

    return result


# ############
# DAE object

class DaeObject(object):
    def __init__(self, scene_id, name):
        self._scene_id = scene_id
        self._name = name
        self._pos = [0, 0, 0]
        self._rot = [0, 0, 0]
        self._scale = [1, 1, 1]
        self._parent = None
        self._mesh = None

    @property
    def name(self):
        return self._name

    @property
    def scene_id(self):
        return self._scene_id

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def rot(self):
        return self._rot

    @rot.setter
    def rot(self, value):
        self._rot = value

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value

    def __repr__(self):
        if self._parent is not None:
            return '{} - {} - [{:.8g},{:.8g},{:.8g}] - {}'.format(self._name, self._parent.name, self.pos[0],
                                                                  self.pos[1],
                                                                  self.pos[2], self._mesh)
        else:
            return '{} - None - [{:.8g},{:.8g},{:.8g}] - {}'.format(self._name, self.pos[0], self.pos[1], self.pos[2],
                                                                    self._mesh)


class DaeMesh(object):

    def __init__(self):
        self._vertices = None

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        self._vertices = value


class DaeAnimation(object):
    @property
    def positions(self):
        pass

    @property
    def rotations(self):
        pass

    @property
    def scalings(self):
        pass


class KeyFrame(object):
    @property
    def value(self):
        return self._value

    @property
    def time(self):
        return self._time

    @property
    def frame_type(self):
        return "LINEAR"

