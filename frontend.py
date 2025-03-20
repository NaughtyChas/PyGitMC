import ctypes
import wx
import os
from backend import SaveManager

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Add constant ID
ID_SELECT_SAVE_DIR = wx.NewId()

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.savesTree = None
        self.SetTitle("Minecraft Git Manager")
        self.SetSize((1500, 850))
        
        # Initialize backend
        self.save_manager = SaveManager()
        self.save_manager.load_config()
        
        # Save references to important controls
        self.current_save_label = None
        self.save_path_label = None
        
        self.InitUI()
        self.LoadSavesIntoTree()

    def InitUI(self):
        # Menu Bar
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenu.Append(ID_SELECT_SAVE_DIR, "Select Save Directory")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_ANY, "Preferences")
        fileMenu.Append(wx.ID_EXIT, "Exit")
        menuBar.Append(fileMenu, "File")

        repoMenu = wx.Menu()
        repoMenu.Append(wx.ID_ANY, "Translate Save")
        repoMenu.Append(wx.ID_ANY, "Commit Changes")
        repoMenu.Append(wx.ID_ANY, "Commit and Translate")
        repoMenu.Append(wx.ID_ANY, "Build Save")
        repoMenu.Append(wx.ID_ANY, "View History")
        menuBar.Append(repoMenu, "Repository")

        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ANY, "Documentation")
        helpMenu.Append(wx.ID_ANY, "About")
        menuBar.Append(helpMenu, "Help")

        self.SetMenuBar(menuBar)

        # Toolbar
        toolbar = self.CreateToolBar(style=wx.TB_HORIZONTAL | wx.TB_TEXT | wx.NO_BORDER)
        toolbar.AddTool(wx.ID_ADD, "Add Save", wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR))
        toolbar.AddTool(wx.ID_ANY, "Translate", wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_TOOLBAR))
        toolbar.AddTool(wx.ID_ANY, "Build", wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR))
        toolbar.Realize()

        # Bind event handlers
        self.Bind(wx.EVT_MENU, self.OnSelectSaveDirectory, id=ID_SELECT_SAVE_DIR)
        self.Bind(wx.EVT_TOOL, self.OnSelectSaveDirectory, id=wx.ID_ADD)
        
        # Splitter window for left and right panels
        splitter = wx.SplitterWindow(self)
        leftPanel = wx.Panel(splitter)
        rightPanel = wx.Panel(splitter)

        # Left Panel: Minecraft Saves tree
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        lblSaves = wx.StaticText(leftPanel, label="Minecraft Saves")
        lblSaves.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
        leftSizer.Add(lblSaves, flag=wx.ALL, border=5)

        # Create button row with refresh and remove buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnRefresh = wx.Button(leftPanel, label="Refresh Saves")
        btnRemove = wx.Button(leftPanel, label="Remove Save")
        buttonSizer.Add(btnRefresh, proportion=1, flag=wx.RIGHT, border=5)
        buttonSizer.Add(btnRemove, proportion=1)

        leftSizer.Add(buttonSizer, flag=wx.EXPAND | wx.ALL, border=5)
        self.savesTree = wx.TreeCtrl(leftPanel)
        leftSizer.Add(self.savesTree, 1, wx.EXPAND | wx.ALL, 5)
        leftPanel.SetSizer(leftSizer)

        # Bind button events
        btnRemove.Bind(wx.EVT_BUTTON, self.OnRemoveSave)
        btnRefresh.Bind(wx.EVT_BUTTON, self.OnRefreshSaves)
        
        # Bind tree selection event
        self.savesTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSaveSelected)

        # Initialize Saves Tree
        self.savesTree.AddRoot("Saves")

        # Right Panel: Notebook Tabs
        notebook = wx.Notebook(rightPanel)
        self.CreateOverviewTab(notebook)
        self.CreateTranslationTab(notebook)
        self.CreateHistoryTab(notebook)
        self.CreateSettingsTab(notebook)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)
        rightPanel.SetSizer(rightSizer)

        splitter.SplitVertically(leftPanel, rightPanel, 250)

        # Main Sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(mainSizer)

        # Status Bar
        self.CreateStatusBar()
        self.SetStatusText("Ready")

    def CreateOverviewTab(self, notebook):
        panel = wx.Panel(notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.current_save_label = wx.StaticText(panel, label="Current Save: None")
        font = self.current_save_label.GetFont()
        font.PointSize += 4
        font.Weight = wx.FONTWEIGHT_BOLD
        self.current_save_label.SetFont(font)
        sizer.Add(self.current_save_label, flag=wx.ALL, border=10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnBuild = wx.Button(panel, label="Build Save")
        btnCommit = wx.Button(panel, label="Commit Changes")
        btnHistory = wx.Button(panel, label="View History")
        btnSizer.Add(btnBuild, flag=wx.ALL, border=5)
        btnSizer.Add(btnCommit, flag=wx.ALL, border=5)
        btnSizer.Add(btnHistory, flag=wx.ALL, border=5)
        sizer.Add(btnSizer, flag=wx.LEFT, border=10)

        # Split area for Modified Files and Save Information
        gridSizer = wx.GridSizer(1, 2, 10, 10)

        # Modified Files group
        modBox = wx.StaticBox(panel, label="Modified Files")
        modSizer = wx.StaticBoxSizer(modBox, wx.VERTICAL)
        modList = wx.ListBox(panel)
        modSizer.Add(modList, 1, wx.EXPAND | wx.ALL, 5)
        gridSizer.Add(modSizer, 1, wx.EXPAND)

        # Save Information group
        infoBox = wx.StaticBox(panel, label="Save Information")
        infoSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        lblPath = wx.StaticText(panel, label="Save Path:")
        infoSizer.Add(lblPath, flag=wx.TOP | wx.LEFT, border=5)
        
        self.save_path_label = wx.StaticText(panel, label="Not selected")
        infoSizer.Add(self.save_path_label, flag=wx.LEFT | wx.BOTTOM, border=5)
        lblModified = wx.StaticText(panel, label="Last Modified:")
        infoSizer.Add(lblModified, flag=wx.LEFT, border=5)
        self.last_modified_label = wx.StaticText(panel, label="N/A")
        infoSizer.Add(self.last_modified_label, flag=wx.LEFT | wx.BOTTOM, border=5)
        lblCommit = wx.StaticText(panel, label="Last Commit:")
        infoSizer.Add(lblCommit, flag=wx.LEFT, border=5)
        self.last_commit_label = wx.StaticText(panel, label="N/A")
        infoSizer.Add(self.last_commit_label, flag=wx.LEFT | wx.BOTTOM, border=5)
        gridSizer.Add(infoSizer, 1, wx.EXPAND)

        sizer.Add(gridSizer, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(sizer)
        notebook.AddPage(panel, "Overview")

    def CreateTranslationTab(self, notebook):
        panel = wx.Panel(notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(panel, label="Manual translation tools will be here")
        sizer.Add(lbl, flag=wx.ALL, border=10)
        panel.SetSizer(sizer)
        notebook.AddPage(panel, "Translation")

    def CreateHistoryTab(self, notebook):
        panel = wx.Panel(notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(panel, label="Commit history will be displayed here")
        sizer.Add(lbl, flag=wx.ALL, border=10)
        panel.SetSizer(sizer)
        notebook.AddPage(panel, "Commit History")

    def CreateSettingsTab(self, notebook):
        panel = wx.Panel(notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        lblDir = wx.StaticText(panel, label="Minecraft Directory:")
        font = lblDir.GetFont()
        font.Weight = wx.FONTWEIGHT_BOLD
        lblDir.SetFont(font)
        sizer.Add(lblDir, flag=wx.ALL, border=10)

        dirSizer = wx.BoxSizer(wx.HORIZONTAL)
        txtDir = wx.TextCtrl(panel, value=r"C:\Users\Username\AppData\Roaming\.minecraft", style=wx.TE_READONLY)
        btnBrowse = wx.Button(panel, label="Browse...")
        dirSizer.Add(txtDir, 1, wx.EXPAND | wx.ALL, 5)
        dirSizer.Add(btnBrowse, 0, wx.ALL, 5)
        sizer.Add(dirSizer, flag=wx.EXPAND)

        chkAuto = wx.CheckBox(panel, label="Auto-build save on commit")
        sizer.Add(chkAuto, flag=wx.LEFT | wx.TOP, border=10)
        chkBackup = wx.CheckBox(panel, label="Create backup before changes")
        sizer.Add(chkBackup, flag=wx.LEFT | wx.TOP, border=10)

        panel.SetSizer(sizer)
        notebook.AddPage(panel, "Settings")
    
    def LoadSavesIntoTree(self):
        """Load all saves into the tree view"""
        rootItem = self.savesTree.GetRootItem()
        self.savesTree.DeleteChildren(rootItem)
        
        all_saves = self.save_manager.get_all_saves()
        for save_name, save_path in all_saves.items():
            item = self.savesTree.AppendItem(rootItem, save_name)
            self.savesTree.SetItemData(item, save_path)
        
        self.savesTree.Expand(rootItem)
        
        # Select current save if available
        current_save, _ = self.save_manager.get_current_save()
        if current_save:
            self.SelectSaveInTree(current_save)
    
    def SelectSaveInTree(self, save_name):
        """Select a save in the tree view by name"""
        rootItem = self.savesTree.GetRootItem()
        
        child, cookie = self.savesTree.GetFirstChild(rootItem)
        while child.IsOk():
            if self.savesTree.GetItemText(child) == save_name:
                self.savesTree.SelectItem(child)
                return True
            child, cookie = self.savesTree.GetNextChild(rootItem, cookie)
        
        return False
        
    def OnSelectSaveDirectory(self, event):
        """Open a dialog to select a save directory"""
        current_save, current_path = self.save_manager.get_current_save()
        defaultPath = current_path if current_path else ""
        
        dlg = wx.DirDialog(
            self, 
            "Select save path:",
            defaultPath=defaultPath,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath()
            success, message = self.save_manager.add_save(save_path)
            
            self.SetStatusText(message)
            if success:
                self.LoadSavesIntoTree()
                self.UpdateSaveDisplay()
                self.save_manager.save_config()
            else:
                wx.MessageBox(message, "Error", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def OnRefreshSaves(self, event):
        """Refresh the list of saves in the tree view"""
        self.LoadSavesIntoTree()
        self.SetStatusText("Saves refreshed")
    
    def OnRemoveSave(self, event):
        """Remove the selected save from the list"""
        selected = self.savesTree.GetSelection()
        if selected.IsOk() and selected != self.savesTree.GetRootItem():
            save_name = self.savesTree.GetItemText(selected)
            
            dlg = wx.MessageDialog(
                self,
                f"Are you sure you want to remove '{save_name}' from the list?\n(This will not delete files from disk)",
                "Confirm Removal",
                wx.YES_NO | wx.ICON_QUESTION
            )
            
            if dlg.ShowModal() == wx.ID_YES:
                success, message = self.save_manager.remove_save(save_name)
                
                if success:
                    self.savesTree.Delete(selected)
                    self.UpdateSaveDisplay()
                    self.save_manager.save_config()
                
                self.SetStatusText(message)
            
            dlg.Destroy()

    def OnSaveSelected(self, event):
        """Triggered when a save is selected in the tree view"""
        item = event.GetItem()
        if item.IsOk() and item != self.savesTree.GetRootItem():
            save_name = self.savesTree.GetItemText(item)
            self.save_manager.set_current_save(save_name)
            self.UpdateSaveDisplay()
            self.save_manager.save_config()
    
    def UpdateSaveDisplay(self):
        """Update the current save display"""
        current_save, current_path = self.save_manager.get_current_save()
        
        if current_save:
            # Update save name
            if self.current_save_label:
                self.current_save_label.SetLabel(f"Current Save: {current_save}")
            
            # Update save path
            if self.save_path_label:
                self.save_path_label.SetLabel(current_path)
            
            # Get and update additional save info
            save_info = self.save_manager.get_save_info(current_save)
            if save_info:
                self.last_modified_label.SetLabel(save_info["last_modified"])
                self.last_commit_label.SetLabel(save_info["last_commit"])
        else:
            # Reset labels when no save is selected
            if self.current_save_label:
                self.current_save_label.SetLabel("Current Save: None")
            if self.save_path_label:
                self.save_path_label.SetLabel("Not selected")
            self.last_modified_label.SetLabel("N/A")
            self.last_commit_label.SetLabel("N/A")