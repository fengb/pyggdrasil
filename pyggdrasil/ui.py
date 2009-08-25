import wx
import wx.lib.newevent
import cmath

import pyggdrasil


TreeChangedEvent, TREE_CHANGED_EVENT = wx.lib.newevent.NewEvent()
GraphSelectedEvent, GRAPH_SELECTED_EVENT = wx.lib.newevent.NewEvent()
ConfigChangedEvent, CONFIG_CHANGED_EVENT = wx.lib.newevent.NewEvent()


class Main(wx.Frame):
    def __init__(self, root=None, graphoptions=None, filename=None, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.root = root or pyggdrasil.model.Node('root', None)
        self.graphoptions = graphoptions or {}
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

        close = file.Append(wx.ID_CLOSE, 'Close\tCtrl-W')
        self.Bind(wx.EVT_MENU, self.OnClose, close)
        save = file.Append(wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        saveas = file.Append(wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveas)
        export = file.Append(wx.ID_ANY, 'Export...')
        self.Bind(wx.EVT_MENU, self.OnExport, export)
        file.AppendSeparator()

        file.Append(wx.ID_EXIT)
        menubar.Append(file, '&File')

        return menubar

    def _createsizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        notebook = wx.Notebook(self, id=wx.ID_ANY)

        self._tree = Tree(self.root, parent=notebook)
        self._tree.Bind(TREE_CHANGED_EVENT, self.OnTreeChange)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelected)
        notebook.AddPage(self._tree, 'Tree')

        self._config = Config(self.graphoptions, parent=notebook)
        self._config.Bind(CONFIG_CHANGED_EVENT, self.OnConfigChange)
        notebook.AddPage(self._config, 'Config')

        sizer.Add(notebook, 0, wx.EXPAND)

        self._graph = Graph(self.root, self.graphoptions, parent=self)
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
                root, graphoptions = pyggdrasil.serialize.load(file)
                frame = Main(root, graphoptions, filename,
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
            pyggdrasil.serialize.dump(file, self.root, self._config.graphoptions)
        finally:
            file.close()

    def OnExport(self, event):
        # TODO: Remove hardcoded reference to SVG
        filename = wx.SaveFileSelector('SVG', extension='svg', parent=self)
        if filename:
            if '.' not in filename:
                filename += '.svg'
            file = open(filename, 'w')
            try:
                file.write(pyggdrasil.export.svg.export(self._graph.graph))
            finally:
                file.close()

    def OnClose(self, event):
        self.Close()

    def OnTreeChange(self, event):
        self._graph.Reload()

    def OnConfigChange(self, event):
        self._graph.Reload()

    def OnTreeSelected(self, event):
        self._graph.selected = self._tree.selected

    def OnGraphSelected(self, event):
        self._tree.selected = event.target


class Graph(wx.ScrolledWindow):
    def __init__(self, root, graphoptions, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.graphoptions = graphoptions
        self._selected = None

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
            self.graph = pyggdrasil.graph.generate(self.root, **self.graphoptions)
            self._drawgraph = self.graph
            self.SetVirtualSize((self._drawgraph.width, self._drawgraph.height))
        else:
            self.graph = pyggdrasil.graph.generate(self.root, **self.graphoptions)
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
        dc.Clear()

        lines = []
        polygons = []
        for node in self._drawgraph:
            if self._drawgraph.hasline(node):
                spos = self._drawgraph.linestart(node)
                epos = self._drawgraph.lineend(node)
                direction = self._drawgraph.linedir(node)

                # Relational line
                lines.append((spos.real, spos.imag, epos.real, epos.imag))

                # Little arrow at the end
                # Base arrowhead is horizontal (looks like >)
                pos1 = -self._drawgraph.arrowlength - 1j*self._drawgraph.arrowwidth/2.0
                pos1 = (pos1 * cmath.exp(1j*direction)) + epos
                pos2 = -self._drawgraph.arrowlength + 1j*self._drawgraph.arrowwidth/2.0
                pos2 = (pos2 * cmath.exp(1j*direction)) + epos
                polygons.append([(epos.real, epos.imag),
                                 (pos1.real, pos1.imag), (pos2.real, pos2.imag)])

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


class Tree(wx.Panel):
    def __init__(self, root, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._tree = wx.TreeCtrl(self, wx.ID_ANY,
                                 style=(wx.TR_EDIT_LABELS | wx.TR_DEFAULT_STYLE))
        self._tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnRename)
        self._tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self._tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        sizer.Add(self._tree, 1, wx.EXPAND)

        sizer.Add(self._buttoncontrols())

        self.SetSizer(sizer)

        self.root = root
        self.Reload()

    def _buttoncontrols(self):
        sizer = wx.GridSizer(rows=0, cols=2)

        self._childinput = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self._childinput.Bind(wx.EVT_TEXT_ENTER, self.OnAdd)
        sizer.Add(self._childinput, 1, wx.EXPAND)

        add = wx.Button(self, wx.ID_ADD, 'Add Child')
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        sizer.Add(add, 1, wx.EXPAND)

        sizer.AddStretchSpacer()

        remove = wx.Button(self, wx.ID_REMOVE)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        sizer.Add(remove, 1, wx.EXPAND)

        sizer.AddStretchSpacer()
        sizer.AddStretchSpacer()

        sort = wx.Button(self, wx.ID_ANY, 'Sort')
        sort.Bind(wx.EVT_BUTTON, self.OnSort)
        sizer.Add(sort, 1, wx.EXPAND)

        self._autosort = wx.CheckBox(self, wx.ID_ANY, 'Auto Sort')
        self._autosort.Bind(wx.EVT_CHECKBOX, self.OnSort)
        sizer.Add(self._autosort)

        return sizer

    def getselected(self):
        return self.nodes[self._tree.GetSelection()]
    def setselected(self, value):
        item = self.nodes.getkey(value)
        self._tree.SelectItem(item)
    selected = property(getselected, setselected)

    @property
    def autosort(self):
        return self._autosort.IsChecked()

    def Reload(self):
        self._tree.DeleteAllItems()
        self.nodes = pyggdrasil.model.EqualsDict()
        self._populatetree(self.root, None)

    def _populatetree(self, node, parent):
        if parent:
            treeitem = self._tree.AppendItem(parent, node.id)
        else:
            treeitem = self._tree.AddRoot(node.id)
        self.nodes[treeitem] = node

        for child in node.children:
            self._populatetree(child, treeitem)

        return treeitem

    def _sorttree(self, item):
        self._tree.SortChildren(item)
        self.nodes[item].sort()

        # I want an iterator
        child = self._tree.GetFirstChild(item)[0]
        while child.IsOk():
            self._sorttree(child)
            child = self._tree.GetNextSibling(child)

    def OnSort(self, event):
        self._sorttree(self._tree.GetRootItem())
        wx.PostEvent(self, TreeChangedEvent())

    def OnRename(self, event):
        nodeid = event.GetLabel()
        if not nodeid:
            event.Veto()
            return

        item = self._tree.GetSelection()
        self.nodes[item].id = str(nodeid)

        wx.PostEvent(self, TreeChangedEvent())

    def OnAdd(self, event):
        item = self._tree.GetSelection()
        nodeid = self._childinput.GetValue()

        if nodeid:
            node = pyggdrasil.model.Node(str(nodeid), None, self.nodes[item])

            newitem = self._tree.AppendItem(item, nodeid)
            self.nodes[newitem] = node
            self._tree.Expand(item)

            self._childinput.Clear()

            if self.autosort:
                self._sorttree(item)

            wx.PostEvent(self, TreeChangedEvent())

    def OnRemove(self, event):
        #TODO: Deal with children somehow
        item = self._tree.GetSelection()

        # Do not let root node get removed
        if not self.nodes[item].parent:
            return

        node = self.nodes[item]
        node.parent.children.remove(node)
        del self.nodes[item]
        self._tree.Delete(item)

        wx.PostEvent(self, TreeChangedEvent())

    def OnBeginDrag(self, event):
        self._dragitem = event.GetItem()
        if self._dragitem.IsOk():
            event.Allow()

    def OnEndDrag(self, event):
        parentitem = event.GetItem()
        olditem = self._dragitem

        if not parentitem.IsOk():
            return
        if parentitem == olditem:
            return
        if parentitem == self._tree.GetItemParent(olditem):
            return

        try:
            node = self.nodes[olditem]
            node.parent = self.nodes[parentitem]
        except pyggdrasil.model.CircularTreeException:
            pass
        else:
            del self.nodes[olditem]
            self._tree.Delete(olditem)
            newitem = self._populatetree(node, parentitem)
            self._tree.SelectItem(newitem)
            self._tree.Expand(parentitem)

            wx.PostEvent(self, TreeChangedEvent())


class Config(wx.Panel):
    def __init__(self, graphoptions, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.graphoptions = graphoptions

        sizer = wx.FlexGridSizer(rows=0, cols=2)
        sizer.AddGrowableCol(1, 1)

        # TODO: Move config fields to graph
        self._keys = pyggdrasil.model.EqualsDict()
        self._inputs = {}
        for (name, default) in [('Radius', 40), ('Padding', 5),
                                ('Arrow Width', 5), ('Arrow Length', 5)]:
            key = name.replace(' ', '').lower()
            text = wx.StaticText(self, wx.ID_ANY, name)
            sizer.Add(text)

            input = wx.TextCtrl(self, wx.ID_ANY)
            self._keys[input.GetId()] = key
            self._inputs[key] = input
            if key in self.graphoptions:
                input.SetValue(str(self.graphoptions[key]))
            else:
                self.graphoptions[key] = default
                input.SetValue(str(default))
            input.Bind(wx.EVT_KILL_FOCUS, self.OnChange)

            sizer.Add(input, 1, wx.EXPAND)

        self.SetSizer(sizer)

    def OnChange(self, event):
        key = self._keys[event.GetId()]
        try:
            self.graphoptions[key] = float(self._inputs[key].GetValue())
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
