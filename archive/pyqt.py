import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Minecraft Git Manager")
        self.resize(1150, 650)
        self.init_ui()

    def init_ui(self):
        self.create_menu_bar()
        self.create_toolbar()

        # Central widget with splitter
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, central_widget)

        # Left Panel: Minecraft Saves Tree
        left_panel = QtWidgets.QWidget(splitter)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        lbl_saves = QtWidgets.QLabel("Minecraft Saves", left_panel)
        font = QtGui.QFont()
        font.setBold(True)
        lbl_saves.setFont(font)
        left_layout.addWidget(lbl_saves)
        btn_refresh = QtWidgets.QPushButton("Refresh Saves", left_panel)
        left_layout.addWidget(btn_refresh)
        self.saves_tree = QtWidgets.QTreeWidget(left_panel)
        self.saves_tree.setHeaderHidden(True)
        root = QtWidgets.QTreeWidgetItem(self.saves_tree, ["Saves"])
        QtWidgets.QTreeWidgetItem(root, ["MyWorld1"])
        QtWidgets.QTreeWidgetItem(root, ["Survival Server"])
        QtWidgets.QTreeWidgetItem(root, ["Creative Build"])
        self.saves_tree.expandItem(root)
        left_layout.addWidget(self.saves_tree)

        # Right Panel: Tab Widget
        right_panel = QtWidgets.QWidget(splitter)
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        self.tabs = QtWidgets.QTabWidget(right_panel)
        self.create_overview_tab()
        self.create_translation_tab()
        self.create_history_tab()
        self.create_settings_tab()
        right_layout.addWidget(self.tabs)

        # Adjust splitter sizes
        splitter.setSizes([250, 750])

        # Status Bar
        self.statusBar().showMessage("Ready")

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        action_select_dir = QtWidgets.QAction("Select Save Directory", self)
        file_menu.addAction(action_select_dir)
        file_menu.addAction("Open Repository")
        file_menu.addAction("Create New Repository")
        file_menu.addSeparator()
        action_exit = QtWidgets.QAction("Exit", self)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        repo_menu = menubar.addMenu("Repository")
        repo_menu.addAction("Build Save")
        repo_menu.addAction("Commit Changes")
        repo_menu.addAction("View History")

        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Manual Translation")
        tools_menu.addAction("Settings")

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Documentation")

    def create_toolbar(self):
        toolbar = self.addToolBar("Icon Toolbar")
        toolbar.setIconSize(QtCore.QSize(32, 32))
        action_add = QtWidgets.QAction(QtGui.QIcon.fromTheme("list-add"), "Add Save", self)
        toolbar.addAction(action_add)
        action_translate = QtWidgets.QAction(QtGui.QIcon.fromTheme("view-refresh"), "Translate", self)
        toolbar.addAction(action_translate)
        action_build = QtWidgets.QAction(QtGui.QIcon.fromTheme("applications-development"), "Build", self)
        toolbar.addAction(action_build)

    def create_overview_tab(self):
        overview = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(overview)
        lbl_current = QtWidgets.QLabel("Current Save: MyWorld1", overview)
        current_font = QtGui.QFont()
        current_font.setPointSize(16)
        current_font.setBold(True)
        lbl_current.setFont(current_font)
        layout.addWidget(lbl_current)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_build = QtWidgets.QPushButton("Build Save", overview)
        btn_commit = QtWidgets.QPushButton("Commit Changes", overview)
        btn_history = QtWidgets.QPushButton("View History", overview)
        btn_layout.addWidget(btn_build)
        btn_layout.addWidget(btn_commit)
        btn_layout.addWidget(btn_history)
        layout.addLayout(btn_layout)

        # Split area for Modified Files and Save Information
        group_layout = QtWidgets.QHBoxLayout()
        # Modified Files Group
        grp_modified = QtWidgets.QGroupBox("Modified Files", overview)
        mod_layout = QtWidgets.QVBoxLayout(grp_modified)
        list_modified = QtWidgets.QListWidget(grp_modified)
        mod_layout.addWidget(list_modified)
        group_layout.addWidget(grp_modified)

        # Save Information Group
        grp_info = QtWidgets.QGroupBox("Save Information", overview)
        info_layout = QtWidgets.QVBoxLayout(grp_info)
        lbl_path = QtWidgets.QLabel("Save Path:", grp_info)
        txt_path = QtWidgets.QLabel(r"C:\Users\Username\AppData\Roaming\.minecraft\saves\MyWorld1", grp_info)
        lbl_modified = QtWidgets.QLabel("Last Modified:", grp_info)
        txt_modified = QtWidgets.QLabel("Today at 14:32", grp_info)
        lbl_commit = QtWidgets.QLabel("Last Commit:", grp_info)
        txt_commit = QtWidgets.QLabel("Added new farm area (12 hours ago)", grp_info)
        info_layout.addWidget(lbl_path)
        info_layout.addWidget(txt_path)
        info_layout.addWidget(lbl_modified)
        info_layout.addWidget(txt_modified)
        info_layout.addWidget(lbl_commit)
        info_layout.addWidget(txt_commit)
        group_layout.addWidget(grp_info)

        layout.addLayout(group_layout)
        self.tabs.addTab(overview, "Overview")

    def create_translation_tab(self):
        translation = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(translation)
        layout.addWidget(QtWidgets.QLabel("Manual translation tools will be here", translation))
        self.tabs.addTab(translation, "Translation")

    def create_history_tab(self):
        history = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(history)
        layout.addWidget(QtWidgets.QLabel("Commit history will be displayed here", history))
        self.tabs.addTab(history, "Commit History")

    def create_settings_tab(self):
        settings = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(settings)
        lbl_dir = QtWidgets.QLabel("Minecraft Directory:", settings)
        font = QtGui.QFont()
        font.setBold(True)
        lbl_dir.setFont(font)
        layout.addWidget(lbl_dir)
        dir_layout = QtWidgets.QHBoxLayout()
        line_dir = QtWidgets.QLineEdit(r"C:\Users\Username\AppData\Roaming\.minecraft", settings)
        line_dir.setReadOnly(True)
        btn_browse = QtWidgets.QPushButton("Browse...", settings)
        dir_layout.addWidget(line_dir)
        dir_layout.addWidget(btn_browse)
        layout.addLayout(dir_layout)
        chk_auto = QtWidgets.QCheckBox("Auto-build save on commit", settings)
        chk_backup = QtWidgets.QCheckBox("Create backup before changes", settings)
        layout.addWidget(chk_auto)
        layout.addWidget(chk_backup)
        self.tabs.addTab(settings, "Settings")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    baseFont = QtGui.QFont("Segoe UI", 10)
    baseFont.setStyleStrategy(QtGui.QFont.PreferAntialias)
    app.setFont(baseFont)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())