import functools

import wx
import wx.lib.newevent

import pyggdrasil

try:
    from multiprocessing import Process
except ImportError:
    from threading import Thread as Process


GraphSelectedEvent, GRAPH_SELECTED_EVENT = wx.lib.newevent.NewEvent()
ConfigChangedEvent, CONFIG_CHANGED_EVENT = wx.lib.newevent.NewEvent()
ProgressUpdatedEvent, PROGRESS_UPDATED_EVENT = wx.lib.newevent.NewEvent()


class Main(wx.Frame):
    def __init__(self, root=None, options=None, filename=None, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.root = root or pyggdrasil.model.Node('root', None)
        self.options = options or {}
        self.filename = filename

        self.SetMenuBar(self._createmenubar())
        self.SetSizer(self._createsizer())

    def _createmenubar(self):
        menubar = wx.MenuBar()

        file = wx.Menu()
        new = file.Append(wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnNew, new)
        open = file.Append(wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnOpen, open)
        file.AppendSeparator()

        close = file.Append(wx.ID_CLOSE, '&Close Window\tCtrl-W')
        self.Bind(wx.EVT_MENU, self.OnClose, close)
        save = file.Append(wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        saveas = file.Append(wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveas)
        file.AppendSeparator()

        self._exports = {}
        export = wx.Menu()
        for (module, available) in pyggdrasil.export.ALL:
            menuitem = export.Append(wx.ID_ANY, pyggdrasil.export.name(module))
            if available:
                self.Bind(wx.EVT_MENU, self.OnExport, menuitem)
                self._exports[menuitem.GetId()] = module
            else:
                export.Enable(menuitem.GetId(), False)
        file.AppendSubMenu(export, '&Export')
        file.AppendSeparator()

        file.Append(wx.ID_EXIT)
        menubar.Append(file, '&File')

        edit = wx.Menu()
        undo = edit.Append(wx.ID_UNDO, '&Undo\tCtrl-Z')
        edit.Enable(undo.GetId(), False)
        redo = edit.Append(wx.ID_REDO, '&Redo\tShift-Ctrl-Z')
        edit.Enable(redo.GetId(), False)
        edit.AppendSeparator()

        cut = edit.Append(wx.ID_CUT)
        edit.Enable(cut.GetId(), False)
        copy = edit.Append(wx.ID_COPY)
        edit.Enable(copy.GetId(), False)
        paste = edit.Append(wx.ID_PASTE)
        edit.Enable(paste.GetId(), False)
        pastefrom = edit.Append(wx.ID_ANY, 'Paste From...')
        edit.Enable(pastefrom.GetId(), False)
        edit.AppendSeparator()

        add = edit.Append(wx.ID_ANY, '&Insert Child\tCtrl-I')
        self.Bind(wx.EVT_MENU, self.OnAdd, add)
        rename = edit.Append(wx.ID_ANY, 'Rename Selected\tF2')
        self.Bind(wx.EVT_MENU, self.OnRename, rename)
        delete = edit.Append(wx.ID_DELETE, '&Delete Selected\tCtrl-K')
        self.Bind(wx.EVT_MENU, self.OnDelete, delete)
        menubar.Append(edit, '&Edit')

        return menubar

    def _createsizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        notebook = wx.Notebook(self, id=wx.ID_ANY)

        self._config = Config(self.options, parent=notebook)
        self._config.Bind(CONFIG_CHANGED_EVENT, self.OnConfigChange)
        notebook.AddPage(self._config, 'Config')

        self._tree = Tree(self.root, self.options, parent=notebook)
        self._tree.Bind(TREE_CHANGED_EVENT, self.OnTreeChange)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelected)
        notebook.InsertPage(0, self._tree, 'Tree')
        notebook.SetSelection(0)

        sizer.Add(notebook, 0, wx.EXPAND)

        self._graph = Graph(self.root, self.options, parent=self)
        self._graph.Bind(GRAPH_SELECTED_EVENT, self.OnGraphSelected)
        sizer.Add(self._graph, 1, wx.EXPAND)

        return sizer

    def getfilename(self):
        return self._filename
    def setfilename(self, value):
        self._filename = value
        self.SetTitle('Pyggdrasil - ' + (self.filename or 'new'))
    filename = property(getfilename, setfilename)

    def OnNew(self, event):
        frame = Main(parent=self.GetParent(), id=wx.ID_ANY)
        frame.Show(True)

    def OnOpen(self, event):
        filename = wx.LoadFileSelector('Pyggdrasil', extension='pyg', parent=self)
        if filename:
            file = open(filename)
            try:
                root, options = pyggdrasil.serialize.load(file)
                frame = Main(root, options, filename,
                             self.GetParent(), wx.ID_ANY)
                frame.Show(True)
            finally:
                file.close()

    def OnSave(self, event):
        if self.filename:
            self._save()
        else:
            self.OnSaveAs(event)

    def OnSaveAs(self, event):
        filename = wx.SaveFileSelector('Pyggdrasil', extension='pyg', parent=self)
        if filename:
            if '.' not in filename:
                filename += '.pyg'
            self.filename = filename
            self._save()

    def _save(self):
        file = open(self.filename, 'w')
        try:
            pyggdrasil.serialize.dump(file, self.root, self._config.options)
        finally:
            file.close()

    def OnExport(self, event):
        module = self._exports[event.GetId()]
        name = pyggdrasil.export.name(module)
        extension = pyggdrasil.export.extension(module)

        filename = wx.SaveFileSelector(name, extension=extension, parent=self)
        if filename:
            if '.' not in filename:
                filename += '.' + extension
            func = functools.partial(pyggdrasil.export.run,
                                     module, self._graph.graph, filename)
            progress = Progress(func, parent=self, title='Export',
                                message=''.join(['Exporting ', name, '...']))

    def OnClose(self, event):
        self.Close()

    def OnTreeChange(self, event):
        self._graph.Reload()

    def OnConfigChange(self, event):
        self._tree.ReloadOptions()
        self._graph.Reload()

    def OnTreeSelected(self, event):
        self._graph.selected = self._tree.selected

    def OnGraphSelected(self, event):
        self._tree.selected = event.target

    def OnAdd(self, event):
        self._tree.AddChild()

    def OnRename(self, event):
        self._tree.RenameSelected()

    def OnDelete(self, event):
        self._tree.RemoveSelected()


class Progress(wx.EvtHandler):
    def __init__(self, func, title, message, parent, *args, **kwargs):
        wx.EvtHandler.__init__(self, *args, **kwargs)
        self._dialog = wx.ProgressDialog(title, message, parent=parent, style=wx.PD_AUTO_HIDE | wx.PD_SMOOTH)
        def newfunc():
            func(self.callback)
        self.Bind(PROGRESS_UPDATED_EVENT, self.OnProgress)
        process = Process(target=newfunc)
        process.start()

    def callback(self, value):
        # Callback is for fixing thread problems
        wx.PostEvent(self, ProgressUpdatedEvent(value=value*100))

    def OnProgress(self, event):
        self._dialog.Update(event.value)


class Graph(wx.ScrolledWindow):
    def __init__(self, root, options, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.options = options
        self.selected = root

        self._drawtimer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        self.root = root
        self.Reload()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetScrollRate(1, 1)

    def getselected(self):
        return self._selected
    def setselected(self, value):
        self._selected = value
        self.Refresh()
    selected = property(getselected, setselected)

    def Reload(self):
        try:
            self._oldgraph = self.graph
        except AttributeError:
            self.graph = pyggdrasil.graph.generate(self.root, **self.options['graph'])
            self._drawgraph = self.graph
            self.SetVirtualSize((self._drawgraph.width, self._drawgraph.height))
        else:
            self.graph = pyggdrasil.graph.generate(self.root, **self.options['graph'])
            self._drawgraph = self._oldgraph

            self._drawtimer.Start(15)
            self._timeramount = 0

        if self.selected not in self.graph:
            self.selected = None

        pos = self.GetViewStart()

    def OnTimer(self, event):
        # TODO: Remove hardcode
        self._timeramount += 1
        if self._timeramount < 20:
            self._drawgraph = pyggdrasil.graph.transition(self._oldgraph, self.graph,
                                                          self._timeramount / 20.0)
        else:
            self._drawtimer.Stop()
            self._drawgraph = self.graph

        self.SetVirtualSize((self._drawgraph.width, self._drawgraph.height))
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        self.PrepareDC(dc)
        dc.BeginDrawing()

        if dc.GetBackground().GetColour() == (0, 0, 0, 255):
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        lines = []
        polygons = []
        for node in self._drawgraph:
            if self._drawgraph.hasline(node):
                spos = self._drawgraph.linestart(node)
                epos = self._drawgraph.lineend(node)

                # Relational line
                lines.append((spos.real, spos.imag, epos.real, epos.imag))

                # Little arrow at the end
                polygons.append([(pos.real, pos.imag)
                                     for pos in self._drawgraph.arrowpoints(node)])

        if lines:
            dc.DrawLineList(lines)
            dc.SetBrush(wx.Brush('#000000'))
            dc.DrawPolygonList(polygons)

        dc.SetBrush(wx.Brush('#FFFFFF'))
        for node in self._drawgraph:
            self._drawnode(node, dc)

        if self.selected:
            dc.SetBrush(wx.Brush('#FFFF80'))
            self._drawnode(self.selected, dc)

        dc.EndDrawing()

    def _drawnode(self, node, dc):
        pos = self._drawgraph.pos(node)
        dc.DrawCircle(pos.real, pos.imag, self.graph.radius)

        w, h = dc.GetTextExtent(node.id)
        dc.DrawText(node.id, pos.real - w/2.0, pos.imag - h/2.0)

    def OnMouseClick(self, event):
        dc = wx.ClientDC(self)
        self.DoPrepareDC(dc)
        click = tuple(event.GetLogicalPosition(dc))

        for node in self.graph:
            pos = self.graph.pos(node)
            if (pos.real - self.graph.radius) <= click[0] <= (pos.real + self.graph.radius) and \
               (pos.imag - self.graph.radius) <= click[1] <= (pos.imag + self.graph.radius):
                wx.PostEvent(self, GraphSelectedEvent(target=node))
                return


TreeChangedEvent, TREE_CHANGED_EVENT = wx.lib.newevent.NewEvent()

class Tree(wx.Panel):
    def __init__(self, root, options, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._tree = wx.TreeCtrl(self, wx.ID_ANY,
                                 style=(wx.TR_EDIT_LABELS | wx.TR_DEFAULT_STYLE))
        self._tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnRename)
        self._tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self._tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        sizer.Add(self._tree, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.root = root
        self.options = options
        self.ReloadNodes()
        self.ReloadOptions()

        self.selected = self.root

    def getselected(self):
        return self.nodes[self._tree.GetSelection()]
    def setselected(self, value):
        item = self.nodes.getkey(value)
        self._tree.SelectItem(item)
    selected = property(getselected, setselected)

    def AddChild(self):
        nodeid = 'New'

        parent = self._tree.GetSelection()
        node = pyggdrasil.model.Node(str(nodeid), None, self.nodes[parent])

        item = self._tree.AppendItem(parent, nodeid)
        self.nodes[item] = node
        self._tree.Collapse(parent)
        self._tree.Expand(parent)
        self._tree.EditLabel(item)

        wx.PostEvent(self, TreeChangedEvent())

    def RemoveSelected(self):
        #TODO: Deal with children somehow
        item = self._tree.GetSelection()
        if not self.nodes[item].parent:
            return

        node = self.nodes[item]
        node.parent.children.remove(node)
        del self.nodes[item]
        self._tree.Delete(item)

        wx.PostEvent(self, TreeChangedEvent())

    def RenameSelected(self):
        self._tree.EditLabel(self._tree.GetSelection())

    def ReloadNodes(self):
        self._tree.DeleteAllItems()
        self.nodes = pyggdrasil.model.EqualsDict()
        self._populatenode(self.root)

    def ReloadOptions(self):
        if self.options['tree']['sort']:
            self._sorttree(self._tree.GetRootItem())

    def _populatenode(self, node, parent=None):
        if parent:
            treeitem = self._tree.AppendItem(parent, node.id)
        else:
            treeitem = self._tree.AddRoot(node.id)
        self.nodes[treeitem] = node

        for child in node.children:
            self._populatenode(child, treeitem)

        return treeitem

    def _moveitem(self, item, newparent):
        # TODO: Push down to wxTreeCtrl (as a patch maybe)
        newitem = self._tree.AppendItem(newparent, self._tree.GetItemText(item))
        self.nodes[newitem] = self.nodes[item]

        for child in self._children(item):
            self._moveitem(child, newitem)

        if self._tree.IsExpanded(item):
            self._tree.Expand(newitem)

        self._tree.Delete(item)
        del self.nodes[item]
        return newitem

    def _sorttree(self, item):
        self._tree.SortChildren(item)
        self.nodes[item].sort()

        for child in self._children(item):
            self._sorttree(child)

    def _children(self, item):
        # Not an iterator because deleting items confuses GetNextSibling
        children = []
        child = self._tree.GetFirstChild(item)[0]
        while child.IsOk():
            children.append(child)
            child = self._tree.GetNextSibling(child)
        return children

    def OnRename(self, event):
        nodeid = event.GetLabel()
        if not nodeid:
            event.Veto()
            return

        item = event.GetItem()
        self.nodes[item].id = str(nodeid)

        if self.options['tree']['sort']:
            # Triggered version has not renamed before sort
            self._tree.SetItemText(item, nodeid)
            self._sorttree(self._tree.GetItemParent(item))

        wx.PostEvent(self, TreeChangedEvent())

    def OnBeginDrag(self, event):
        self._dragitem = event.GetItem()
        if self._dragitem.IsOk():
            event.Allow()

    def OnEndDrag(self, event):
        parent = event.GetItem()
        olditem = self._dragitem

        if not parent.IsOk() or \
           parent == olditem or \
           parent == self._tree.GetItemParent(olditem):
            event.Veto()
            return

        try:
            node = self.nodes[olditem]
            node.parent = self.nodes[parent]
        except pyggdrasil.model.CircularTreeException:
            event.Veto()
            pass
        else:
            newitem = self._moveitem(olditem, parent)
            self._tree.SelectItem(newitem)

            if self.options['tree']['sort']:
                self._sorttree(parent)

            wx.PostEvent(self, TreeChangedEvent())


class Config(wx.Panel):
    # TODO: Make this class less sucktastic
    def __init__(self, options, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.options = options

        sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.GridSizer(rows=0, cols=2)

        self._keys = {}
        self._inputs = {}

        if 'tree' not in self.options:
            self.options['tree'] = {}
        sort = wx.CheckBox(self, wx.ID_ANY, 'Sort')
        self._keys[sort.GetId()] = 'sort'
        self._inputs['sort'] = sort
        if 'sort' in self.options['tree']:
            sort.SetValue(self.options['tree']['sort'])
        else:
            self.options['tree']['sort'] = False
            sort.SetValue(False)
        sort.Bind(wx.EVT_CHECKBOX, self.OnCheckboxChange)
        grid.Add(sort)

        grid.AddStretchSpacer()
        grid.AddStretchSpacer()
        grid.AddStretchSpacer()

        if 'graph' not in self.options:
            self.options['graph'] = {}
        for (name, default) in [('Radius', 40), ('Padding', 5),
                                ('Arrow Width', 5), ('Arrow Length', 5)]:
            key = name.replace(' ', '').lower()
            text = wx.StaticText(self, wx.ID_ANY, name)
            grid.Add(text)

            input = wx.TextCtrl(self, wx.ID_ANY)
            self._keys[input.GetId()] = key
            self._inputs[key] = input
            if key in self.options['graph']:
                input.SetValue(str(self.options['graph'][key]))
            else:
                self.options['graph'][key] = default
                input.SetValue(str(default))
            input.Bind(wx.EVT_KILL_FOCUS, self.OnFloatChange)

            grid.Add(input)

        sizer.Add(grid)
        self.SetSizer(sizer)

    def OnCheckboxChange(self, event):
        key = self._keys[event.GetId()]
        self.options['tree'][key] = self._inputs[key].GetValue()
        wx.PostEvent(self, ConfigChangedEvent())

    def OnFloatChange(self, event):
        key = self._keys[event.GetId()]
        try:
            self.options['graph'][key] = float(self._inputs[key].GetValue())
            self._inputs[key].SetBackgroundColour('#FFFFFF')
        except ValueError:
            self._inputs[key].SetBackgroundColour('#FF6060')

        wx.PostEvent(self, ConfigChangedEvent())


class App(wx.App):
    def OnInit(self):
        self.SetAppName('Pyggdrasil')
        frame = Main(parent=None, id=wx.ID_ANY)
        frame.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)
        frame.Show(True)
        return True

    def OnMenuExit(self, event):
        self.ExitMainLoop()
