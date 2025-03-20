import ctypes
import wx
import os  # Add import

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

app = wx.App(False)

# Add constant ID
ID_SELECT_SAVE_DIR = wx.NewId()

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.savesTree = None
        self.SetTitle("Minecraft Git Manager")
        self.SetSize((1000, 650))
        
        # Save references to current directory and important controls
        self.current_save_dir = ""
        self.current_save_label = None  # Reference to the current save name label
        self.save_path_label = None     # Reference to the save path label
        
        self.InitUI()

    def InitUI(self):
        # Menu Bar
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        # Use our custom ID
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

        # Bind remove button event
        btnRemove.Bind(wx.EVT_BUTTON, self.OnRemoveSave)
        # Bind tree selection event
        self.savesTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSaveSelected)

        # Populate Saves Tree
        rootItem = self.savesTree.AddRoot("Saves")
        self.savesTree.AppendItem(rootItem, "MyWorld1")
        self.savesTree.AppendItem(rootItem, "Survival Server")
        self.savesTree.AppendItem(rootItem, "Creative Build")
        self.savesTree.Expand(rootItem)

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
        # Save label reference
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
        # Save path label reference
        self.save_path_label = wx.StaticText(panel, label="Not selected")
        infoSizer.Add(self.save_path_label, flag=wx.LEFT | wx.BOTTOM, border=5)
        lblModified = wx.StaticText(panel, label="Last Modified:")
        infoSizer.Add(lblModified, flag=wx.LEFT, border=5)
        lblModifiedVal = wx.StaticText(panel, label="Today at 14:32")
        infoSizer.Add(lblModifiedVal, flag=wx.LEFT | wx.BOTTOM, border=5)
        lblCommit = wx.StaticText(panel, label="Last Commit:")
        infoSizer.Add(lblCommit, flag=wx.LEFT, border=5)
        lblCommitVal = wx.StaticText(panel, label="Added new farm area (12 hours ago)")
        infoSizer.Add(lblCommitVal, flag=wx.LEFT | wx.BOTTOM, border=5)
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
        
    def OnSelectSaveDirectory(self, event):
        """Open directory selection dialog and update savesTree"""
        dlg = wx.DirDialog(
            self, 
            "Select save path:",
            defaultPath=self.current_save_dir,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath()
            self.current_save_dir = save_path
            self.UpdateSavesTree(save_path)
            
            # Update path info in Overview tab
            self.UpdateSavePathDisplay(save_path)
        
        dlg.Destroy()
    
    def UpdateSavesTree(self, directory):
        # Get root item
        rootItem = self.savesTree.GetRootItem()
        
        # Check if directory is valid
        if os.path.exists(directory) and os.path.isdir(directory):
            # Get directory name as save name
            save_name = os.path.basename(directory)
            
            # Check if it already exists
            existing = False
            child, cookie = self.savesTree.GetFirstChild(rootItem)
            while child.IsOk():
                if self.savesTree.GetItemText(child) == save_name:
                    existing = True
                    selected_item = child
                    break
                child, cookie = self.savesTree.GetNextChild(rootItem, cookie)
            
            # If it doesn't exist, add it to the tree
            if not existing:
                new_item = self.savesTree.AppendItem(rootItem, save_name)
                self.savesTree.SetItemData(new_item, directory)
                selected_item = new_item
                self.SetStatusText(f"Added save: {save_name}")
            else:
                self.SetStatusText(f"Save already exists: {save_name}")
            
            # Select the item and update display
            self.savesTree.SelectItem(selected_item)
            self.UpdateSaveDisplay(save_name, directory)
        else:
            wx.MessageBox(f"Invalid directory: {directory}", "Error", wx.OK | wx.ICON_ERROR)
        
        # Ensure root node is expanded
        self.savesTree.Expand(rootItem)
    
    def UpdateSavePathDisplay(self, directory):
        # Get directory name as save name
        save_name = os.path.basename(directory)
        self.UpdateSaveDisplay(save_name, directory)

    def UpdateSaveDisplay(self, save_name, directory):
        # Update labels
        if self.current_save_label:
            self.current_save_label.SetLabel(f"Current Save: {save_name}")
        
        # Update path
        if self.save_path_label:
            self.save_path_label.SetLabel(directory)
        
        # Update current directory
        self.current_save_dir = directory

    def OnRemoveSave(self, event):
        selected = self.savesTree.GetSelection()
        if selected.IsOk() and selected != self.savesTree.GetRootItem():
            save_name = self.savesTree.GetItemText(selected)
            
            # Confirm removal
            dlg = wx.MessageDialog(
                self,
                f"Are you sure you want to remove '{save_name}' from the list?\n(This will not delete files from disk)",
                "Confirm Removal",
                wx.YES_NO | wx.ICON_QUESTION
            )
            
            if dlg.ShowModal() == wx.ID_YES:
                self.savesTree.Delete(selected)
                # Reset display
                if self.current_save_label:
                    self.current_save_label.SetLabel("Current Save: None")
                if self.save_path_label:
                    self.save_path_label.SetLabel("Not selected")
                self.current_save_dir = ""
                self.SetStatusText(f"Removed from list: {save_name}")
            
            dlg.Destroy()

    def OnSaveSelected(self, event):
        """Triggered when a save is selected in the tree"""
        item = event.GetItem()
        # Confirm it's a valid item and not root
        if item.IsOk() and item != self.savesTree.GetRootItem():
            save_name = self.savesTree.GetItemText(item)
            directory = self.savesTree.GetItemData(item)
            if directory:
                self.UpdateSaveDisplay(save_name, directory)

if __name__ == '__main__':
    default_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    default_font.SetFaceName("Segoe UI")

    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
