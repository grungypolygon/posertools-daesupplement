import os.path

import numpy
import poser as P
import wx

import collada


AXIS_NORM = numpy.matrix([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
])

AXIS_Z_UP = numpy.matrix([
    [1, 0, 0, 0],
    [0, 0, -1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
])

# METER_TO_POSER_UNIT = (1 / 2.62128)

COLLADA_NAMESPACE = '''http://www.collada.org/2005/11/COLLADASchema'''


class OptionsDialog(wx.Dialog):
    def __init__(self, parent):

        wx.Dialog.__init__(self, parent, -1, title='COLLADA import adjustments', size=(500, -1),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._adjust_axis = 'Z_UP'
        self._adjust_scale = '2.62128'
        self._adjust_hierarchy = True

        self.axis_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_adjust_axis = wx.CheckBox(self, -1, 'Adjust axis')
        self.cb_adjust_axis.SetValue(True)
        self.cb_adjust_axis.Bind(wx.EVT_CHECKBOX, self.toggle_adjust_axis)
        self.db_adjust_axis = wx.Choice(self, -1, choices=['Z_UP', 'Y_UP'])
        self.db_adjust_axis.SetSelection(0)
        self.db_adjust_axis.Bind(wx.EVT_CHOICE, self.choose_adjust_axis)
        self.axis_sizer.Add(self.cb_adjust_axis, 1, wx.EXPAND | wx.RIGHT, 10)
        self.axis_sizer.Add(self.db_adjust_axis, 1, wx.EXPAND)

        self.scale_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_adjust_scale = wx.CheckBox(self, -1, 'Adjust scale')
        self.cb_adjust_scale.SetValue(True)
        self.cb_adjust_scale.Bind(wx.EVT_CHECKBOX, self.toggle_adjust_scale)
        self.tc_adjust_scale = wx.TextCtrl(self, -1, '2.62128')
        self.cb_adjust_scale.Bind(wx.EVT_TEXT, self.update_adjust_scale)
        self.scale_sizer.Add(self.cb_adjust_scale, 1, wx.EXPAND | wx.RIGHT, 10)
        self.scale_sizer.Add(self.tc_adjust_scale, 0, wx.EXPAND)

        self.cb_adjust_hierarchy = wx.CheckBox(self, -1, 'Adjust hierarchy')
        self.cb_adjust_hierarchy.SetValue(True)
        self.cb_adjust_hierarchy.Bind(wx.EVT_CHECKBOX, self.toggle_adjust_hierarchy)

        self.cb_import_animations = wx.CheckBox(self, -1, 'Import animation')
        self.cb_import_animations.Disable()

        self.buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_cancel = wx.Button(self, -1, 'Cancel')
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.btn_import = wx.Button(self, -1, 'Import')
        self.btn_import.Bind(wx.EVT_BUTTON, self.OnImport)
        self.buttons_sizer.Add(self.btn_cancel, 1, wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, 20)
        self.buttons_sizer.Add(self.btn_import, 1)

        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.axis_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.sizer.Add(self.scale_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.sizer.Add(self.cb_adjust_hierarchy, 1, wx.EXPAND | wx.ALL, 10)
        self.sizer.Add(self.cb_import_animations, 1, wx.EXPAND | wx.ALL, 10)
        self.sizer.Add(self.buttons_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.ShowModal()

        self._canceled = False

    def choose_adjust_axis(self, e):
        self._adjust_axis = self.db_adjust_axis.GetStringSelection()

    def toggle_adjust_axis(self, e):
        if self.cb_adjust_axis.GetValue():
            self._adjust_axis = self.db_adjust_axis.GetStringSelection()
        else:
            self._adjust_axis = None

    def update_adjust_scale(self, e):
        self._adjust_scale = self.db_adjust_scale.GetValue()

    def toggle_adjust_scale(self, e):
        if self.cb_adjust_scale.GetValue():
            self._adjust_scale = self.tc_adjust_scale.GetValue()
        else:
            self._adjust_scale = None

    def toggle_adjust_hierarchy(self, e):
        if self.cb_adjust_hierarchy.GetValue():
            self._adjust_hierarchy = self.tc_adjust_scale.GetValue()
        else:
            self._adjust_hierarchy = None

    def OnCancel(self, e):
        self.EndModal(wx.ID_CANCEL)

    def OnImport(self, e):
        self.EndModal(wx.ID_OK)

    @property
    def canceled(self):
        return self._canceled

    @property
    def adjust_axis(self):
        return self._adjust_axis

    @property
    def adjust_scale(self):
        return self._adjust_scale

    @property
    def adjust_hierarchy(self):
        return self._adjust_hierarchy


def get_vert_pos(vertex, extend=False):
    pos = []
    for val in [vertex.X(), vertex.Y(), vertex.Z()]:
        pos.append(val)
    if extend:
        pos.append(1)
    return pos


def set_vert_pos(vertex, pos):
    vertex.SetX(pos[0])
    vertex.SetY(pos[1])
    vertex.SetZ(pos[2])


def get_actor_pos(actor, extend=False):
    pos = []
    for param in [P.kParmCodeXTRAN, P.kParmCodeYTRAN, P.kParmCodeZTRAN]:
        pos.append(actor.ParameterByCode(param).Value())
    if extend:
        pos.append(1)
    return pos


def set_actor_pos(actor, pos):
    params = [P.kParmCodeXTRAN, P.kParmCodeYTRAN, P.kParmCodeZTRAN]
    for idx, param in enumerate(params):
        actor.ParameterByCode(param).SetValue(pos[idx])


def import_dae(file_path, dae_object, options):
    poser_dae_import_opts = {}
    P.Scene().ImExporter().Import('DAE', None, file_path)


def parse_dae_file(file_path):
    collada_root = collada.parse_collada_file(file_path)
    objs = collada.get_scene_objects(collada_root, 'Scene')
    return objs


def options_dialog(file_path):
    man = P.WxAuiManager()
    root = man.GetManagedWindow()
    return OptionsDialog(root)


def check_dae_file(file_path):
    file_name = os.path.basename(file_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as dae_file:
            for line in dae_file.readlines():
                if COLLADA_NAMESPACE in line:
                    return 0
            else:
                P.DialogSimple.MessageBox('''"{}" doesn't look like a COLLADA file.'''.format(file_name))
    else:
        P.DialogSimple.MessageBox('''"{}" is not a file.'''.format(file_name))
    return 1


def matrix_and_scale(options):
    if options.adjust_axis:
        adjust_matrices = {
            'Z_UP': AXIS_Z_UP
        }
        matrix = adjust_matrices.get(options.adjust_axis, AXIS_NORM)
    else:
        matrix = AXIS_NORM

    if options.adjust_scale:
        scale = (1.0 / float(options.adjust_scale))
    else:
        scale = 1.0

    return matrix, scale


def adjust_axis(actor, options):
    adjust_matrix, adjust_scale = matrix_and_scale(options)
    pos = get_actor_pos(actor, True)
    new_pos = numpy.multiply((pos * adjust_matrix), adjust_scale).A[0]
    set_actor_pos(actor, new_pos)


def adjust_vertices(actor, options):
    adjust_matrix, adjust_scale = matrix_and_scale(options)
    geo = actor.Geometry()
    for vert in geo.Vertices():
        pos = get_vert_pos(vert, True)
        new_pos = numpy.multiply((pos * adjust_matrix), adjust_scale).A[0]
        set_vert_pos(vert, new_pos)


def adjust_hierarchy(actor, obj):
    if obj.parent is not None:
        try:
            parent_actor = P.Scene().Actor(obj.parent.name)
            actor.SetParent(parent_actor)
        except P.error as err:
            print("Poser err on object '{}': {}".format(name, err))


def create_grouping(name):
    # Yes, it seems that this is the only way to create groupings
    # via Python with a custom name.
    # CreateGrouping() does not return an Actor or takes a name.
    prev_list = [x.Name() for x in P.Scene().Actors()]
    P.Scene().CreateGrouping()
    new_list = [x.Name() for x in P.Scene().Actors()]
    generated_grouping_name = (set(new_list) - set(prev_list)).pop()
    grouping = P.Scene().Actor(generated_grouping_name)
    grouping.SetName(name)
    return grouping


options = options_dialog(None)
if not options.GetReturnCode() == wx.ID_CANCEL:
    open_dialog = P.DialogFileChooser(
        P.kDialogFileChooserOpen,
        None,
        'Select Collada DAE file to import',
        P.ContentRootLocation()
    )
    result = open_dialog.Show()
    if result == 1:
        file_path = open_dialog.Path()
        check = check_dae_file(file_path)
        if check == 0:
            dae_objects = parse_dae_file(file_path)

            import_dae(file_path, dae_objects, options)
            if options.adjust_hierarchy:
                for name, obj in dae_objects.items():
                    if obj.mesh is None:
                        create_grouping(name)
            for name, obj in dae_objects.items():
                try:
                    actor = P.Scene().Actor(name)
                    if options.adjust_axis or options.adjust_scale:
                        adjust_axis(actor, options)
                        adjust_vertices(actor, options)
                    if options.adjust_hierarchy:
                        adjust_hierarchy(actor, obj)
                except P.error as err:
                    print("Poser err on object '{}': {}".format(name, err))
