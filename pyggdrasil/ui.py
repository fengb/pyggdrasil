import wx
import wx.lib.newevent
import cmath
import yaml

import pyggdrasil


TreeChangedEvent, TREE_CHANGED_EVENT = wx.lib.newevent.NewEvent()
GraphSelectedEvent, GRAPH_SELECTED_EVENT = wx.lib.newevent.NewEvent()


class Main(wx.Frame):
    def __init__(self, root=None, filename=None, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.root = root or pyggdrasil.model.Node('root', None)
        self.filename = filename

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

        self.SetMenuBar(menubar)

        box = wx.BoxSizer(wx.HORIZONTAL)

        self._tree = Tree(self.root, self)
        box.Add(self._tree, 0, wx.EXPAND)

        self.graph = Graph(self.root, 40, 5, self)
        box.Add(self.graph, 1, wx.EXPAND)

        self.SetSizer(box)

        self._tree.Bind(TREE_CHANGED_EVENT, self.OnTreeChange)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelected)
        self.graph.Bind(GRAPH_SELECTED_EVENT, self.OnGraphSelected)

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
                root = pyggdrasil.model.Node.from_raw(yaml.load(file))
                frame = Main(root, filename, self.GetParent(), wx.ID_ANY)
                frame.Show(True)
            finally:
                file.close()

    def OnSave(self, event):
        if self.filename:
            self._Save()
        else:
            self.OnSaveAs(event)

    def OnSaveAs(self, event):
        filename = wx.SaveFileSelector('Pyggdrasil', extension='pyg', parent=self)
        if filename:
            if '.' not in filename:
                filename += '.pyg'
            self.filename = filename
            self._Save()

    def _Save(self):
        file = open(self.filename, 'w')
        try:
            yaml.dump(self.root.raw(), file)
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
                file.write(pyggdrasil.export.svg.export(self.graph.graph))
            finally:
                file.close()

    def OnClose(self, event):
        self.Close()

    def OnTreeChange(self, event):
        self.graph.Reload()

    def OnTreeSelected(self, event):
        self.graph.selected = self._tree.selected

    def OnGraphSelected(self, event):
        self._tree.selected = event.target


class Graph(wx.ScrolledWindow):
    def __init__(self, root, radius, padding, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.radius = radius
        self.padding = padding
        self._selected = None

        self.root = root
        self.Reload()
        self.Bind(wx.EVT_PAINT, self.Redraw)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)

    def getselected(self):
        return self._selected
    def setselected(self, value):
        self._selected = value
        self.Refresh(eraseBackground=True)
    selected = property(getselected, setselected)

    def Reload(self):
        self.selected = None
        self.graph = pyggdrasil.graph.generate(self.root, radius=self.radius,
                                               padding=self.padding)

        pos = self.GetViewStart()
        self.SetScrollbars(1, 1, self.graph.width, self.graph.height)
        self.Scroll(*pos)

    def Redraw(self, event=None):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        dc.BeginDrawing()

        lines = []
        for node in self.graph:
            if self.graph.hasline(node):
                spos = self.graph.linestart(node)
                epos = self.graph.lineend(node)
                direction = self.graph.linedir(node)

                # Relational line
                lines.append((spos.real, spos.imag, epos.real, epos.imag))

                # Little arrow at the end
                pos1 = epos - self.padding * cmath.exp((direction + 0.5) * 1j)
                pos2 = epos - self.padding * cmath.exp((direction - 0.5) * 1j)
                lines.append((pos1.real, pos1.imag, epos.real, epos.imag))
                lines.append((pos2.real, pos2.imag, epos.real, epos.imag))

        if lines:
            dc.DrawLineList(lines)

        for node in self.graph:
            self.DrawNode(node, dc)

        if self.selected:
            self.DrawNode(self.selected, dc, bgcolor='#FFFF80')

        dc.EndDrawing()

    def DrawNode(self, node, dc, bgcolor=None):
        if bgcolor:
            dc.SetBrush(wx.Brush(bgcolor))

        pos = self.graph.pos(node)
        dc.DrawCircle(pos.real, pos.imag, self.radius)

        w, h = dc.GetTextExtent(node.id)
        dc.DrawText(node.id, pos.real - w/2.0, pos.imag - h/2.0)

    def OnMouseClick(self, event):
        dc = wx.ClientDC(self)
        self.DoPrepareDC(dc)
        click = tuple(event.GetLogicalPosition(dc))

        for node in self.graph:
            pos = self.graph.pos(node)
            if (pos.real - self.radius) <= click[0] <= (pos.real + self.radius) and \
               (pos.imag - self.radius) <= click[1] <= (pos.imag + self.radius):
                wx.PostEvent(self, GraphSelectedEvent(target=node))
                return


class Tree(wx.Panel):
    def __init__(self, root, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._tree = wx.TreeCtrl(self, wx.ID_ANY,
                                style=(wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS))
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
        self._PopulateTreeItem(self.root, None)

    def _PopulateTreeItem(self, node, parent):
        if parent:
            treeitem = self._tree.AppendItem(parent, node.id)
        else:
            treeitem = self._tree.AddRoot(node.id)
        self.nodes[treeitem] = node

        for child in node.children:
            self._PopulateTreeItem(child, treeitem)

    def _SortItem(self, item):
        self._tree.SortChildren(item)
        self.nodes[item].sort()

        # I want an iterator
        child = self._tree.GetFirstChild(item)[0]
        while child.IsOk():
            self._SortItem(child)
            child = self._tree.GetNextSibling(child)

    def OnSort(self, event):
        self._SortItem(self._tree.GetRootItem())
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
                self._SortItem(item)
            wx.PostEvent(self, TreeChangedEvent())

    def OnRemove(self, event):
        #TODO: Deal with children somehow
        item = self._tree.GetSelection()

        # Do not let root node get removed
        if not self.nodes[item].parent:
            return

        self.nodes[item].parent = None
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

        node = self.nodes[olditem]
        parentnode = self.nodes[parentitem]

        if parentnode.hasancestor(node):
            # Circular reference attempt
            # TODO: Display an error message
            return

        self._tree.Delete(olditem)
        del self.nodes[olditem]

        node.parent = parentnode
        self._PopulateTreeItem(node, parentitem)
        self._tree.Expand(parentitem)

        wx.PostEvent(self, TreeChangedEvent())

class App(wx.App):
    def OnInit(self):
        self.SetAppName('Pyggdrasil')
        root = pyggdrasil.model.Node('root', None)
        frame = Main(parent=None, id=wx.ID_ANY)
        frame.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)
        frame.Show(True)
        return True

    def OnMenuExit(self, event):
        self.ExitMainLoop()
