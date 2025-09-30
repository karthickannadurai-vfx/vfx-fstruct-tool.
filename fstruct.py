# fstruct_qt.py
import sys, os
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

APP_NAME = "FStruct - VFX Folder Builder"
FOOTER_TEXT = "Created by Karthick Annadurai"

# -------------------------
# File-system helpers
# -------------------------
def get_next_version(out_path: str, shot: str) -> int:
    """
    Scan out_path for existing <shot>_roto_vNNN directories and return next version (int).
    """
    version = 1
    while True:
        candidate = f"{shot}_roto_v{version:03}"
        if not os.path.exists(os.path.join(out_path, candidate)):
            return version
        version += 1

def create_shot_tree(base_path: str, show: str, shot: str, artist: str) -> str:
    """
    Create in/ and mid/ folders and versioned out/ structure. Returns path to created out version folder.
    """
    # base shot path
    shot_path = os.path.join(base_path, show, shot)
    # in/
    os.makedirs(os.path.join(shot_path, "in", "feedback"), exist_ok=True)
    os.makedirs(os.path.join(shot_path, "in", "plate"), exist_ok=True)
    os.makedirs(os.path.join(shot_path, "in", "ref"), exist_ok=True)
    # mid/
    os.makedirs(os.path.join(shot_path, "mid", artist, "sfx"), exist_ok=True)
    os.makedirs(os.path.join(shot_path, "mid", artist, "nuke", "shapes"), exist_ok=True)
    os.makedirs(os.path.join(shot_path, "mid", artist, "nuke", "scripts"), exist_ok=True)
    os.makedirs(os.path.join(shot_path, "mid", artist, "silhouette", "shapes"), exist_ok=True)
    os.makedirs(os.path.join(shot_path, "mid", artist, "pre_render"), exist_ok=True)

    # out/
    out_root = os.path.join(shot_path, "out")
    os.makedirs(out_root, exist_ok=True)

    version = get_next_version(out_root, shot)
    root_name = f"{shot}_roto_v{version:03}"
    root_path = os.path.join(out_root, root_name)
    os.makedirs(root_path, exist_ok=True)

    # required subfolders inside versioned out folder (exact names)
    os.makedirs(os.path.join(root_path, f"{shot}_roto_matte_01_v{version:03}"), exist_ok=True)
    os.makedirs(os.path.join(root_path, f"{shot}_roto_matte_02_v{version:03}"), exist_ok=True)
    os.makedirs(os.path.join(root_path, f"{shot}_roto_sfx_v{version:03}"), exist_ok=True)
    os.makedirs(os.path.join(root_path, f"{shot}_roto_nuke_script_v{version:03}"), exist_ok=True)

    return root_path

# -------------------------
# Main Window (Qt)
# -------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 600)
        # central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        # default theme
        self.theme = "dark"  # 'dark' or 'light'
        self._apply_theme()

        # layout: left = form, right = preview
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 6)
        main_layout.setSpacing(12)

        # Left: Form card
        form_card = QtWidgets.QFrame()
        form_card.setObjectName("card")
        form_card.setMinimumWidth(380)
        form_layout = QtWidgets.QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(12)

        title = QtWidgets.QLabel("FStruct")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(title)

        subtitle = QtWidgets.QLabel("Studio folder initializer")
        subtitle.setObjectName("subtitle")
        form_layout.addWidget(subtitle)

        form_layout.addSpacing(6)

        # Base Path row
        self.base_path_edit = QtWidgets.QLineEdit()
        self.base_path_edit.setPlaceholderText("Choose base save path (e.g., D:/VFX_Project)")
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.on_browse)

        base_row = QtWidgets.QHBoxLayout()
        base_row.addWidget(self.base_path_edit)
        base_row.addSpacing(8)
        base_row.addWidget(browse_btn)
        form_layout.addLayout(self._labelled("Base Path", base_row))

        # Show, Shot, Artist, Client Style
        self.show_edit = QtWidgets.QLineEdit()
        self.show_edit.setPlaceholderText("SHOW01")
        self.show_edit.textChanged.connect(self.preview_update_live)

        self.shot_edit = QtWidgets.QLineEdit()
        self.shot_edit.setPlaceholderText("SHOT_010")
        self.shot_edit.textChanged.connect(self.preview_update_live)

        self.artist_edit = QtWidgets.QLineEdit()
        self.artist_edit.setPlaceholderText("ArtistName")
        self.artist_edit.textChanged.connect(self.preview_update_live)

        self.client_combo = QtWidgets.QComboBox()
        self.client_combo.addItems(["default", "clientA", "clientB"])
        self.client_combo.setCurrentIndex(0)

        form_layout.addLayout(self._labelled_row("Show Name", self.show_edit))
        form_layout.addLayout(self._labelled_row("Shot Name", self.shot_edit))
        form_layout.addLayout(self._labelled_row("Artist Name", self.artist_edit))
        form_layout.addLayout(self._labelled_row("Client Style", self.client_combo))

        # theme toggle & create button
        btn_row = QtWidgets.QHBoxLayout()
        self.theme_btn = QtWidgets.QPushButton("Switch Theme")
        self.theme_btn.setFixedWidth(140)
        self.theme_btn.clicked.connect(self.on_toggle_theme)

        self.create_btn = QtWidgets.QPushButton("Create Project")
        self.create_btn.setObjectName("primary")
        self.create_btn.setMinimumHeight(44)
        self.create_btn.clicked.connect(self.on_create)
        btn_row.addWidget(self.theme_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.create_btn)
        form_layout.addStretch()
        form_layout.addLayout(btn_row)

        # Right: Preview card
        preview_card = QtWidgets.QFrame()
        preview_card.setObjectName("card")
        preview_layout = QtWidgets.QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        preview_layout.setSpacing(8)

        preview_title = QtWidgets.QLabel("Preview")
        preview_title.setObjectName("subtitle")
        preview_layout.addWidget(preview_title)

        # Tree view (only names)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        preview_layout.addWidget(self.tree)

        # status area (below preview)
        self.preview_info = QtWidgets.QLabel("Live preview updates as you type")
        self.preview_info.setWordWrap(True)
        preview_layout.addWidget(self.preview_info)

        main_layout.addWidget(form_card, 0)
        main_layout.addWidget(preview_card, 1)

        # footer / status bar
        status = QtWidgets.QStatusBar()
        status.showMessage(FOOTER_TEXT)
        self.setStatusBar(status)

        # initialize preview
        self.preview_update_live()

    # -------------------------
    # UI small helpers
    # -------------------------
    def _labelled(self, label_text, widget_layout):
        wrapper = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(label_text)
        label.setObjectName("fieldlabel")
        wrapper.addWidget(label)
        wrapper.addLayout(widget_layout)
        return wrapper

    def _labelled_row(self, label_text, widget):
        row = QtWidgets.QHBoxLayout()
        row.addWidget(widget)
        return self._labelled(label_text, row)

    # -------------------------
    # Theme / styling
    # -------------------------
    def on_toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()

    def _apply_theme(self):
        # Basic palette + stylesheet
        if self.theme == "dark":
            palette = {
                "bg": "#151515",
                "card": "#1e1e1e",
                "text": "#f3f0e6",
                "muted": "#a9a9a9",
                "accent": "#ffcc00",
                "primary_btn_fg": "#1e1e1e",
                "btn_bg": "#ffcc00",
                "input_bg": "#272727",
            }
        else:
            palette = {
                "bg": "#f7f9fb",
                "card": "#ffffff",
                "text": "#202328",
                "muted": "#5a6b7a",
                "accent": "#0b66d0",
                "primary_btn_fg": "#ffffff",
                "btn_bg": "#0b66d0",
                "input_bg": "#ffffff",
            }

        # Set QSS style - scoped and clean
        qss = f"""
        QMainWindow {{ background: {palette['bg']}; }}
        QFrame#card {{
            background: {palette['card']};
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.04);
        }}
        QLabel#title {{
            color: {palette['accent']};
            font-size: 24px;
            font-weight: 700;
        }}
        QLabel#subtitle {{
            color: {palette['muted']};
            font-size: 12px;
            margin-bottom: 8px;
        }}
        QLabel#fieldlabel {{
            color: {palette['text']};
            font-size: 11px;
            margin-bottom: 4px;
        }}
        QLineEdit {{
            background: {palette['input_bg']};
            color: {palette['text']};
            padding: 8px;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 6px;
        }}
        QComboBox {{
            background: {palette['input_bg']};
            color: {palette['text']};
            padding: 6px;
            border-radius:6px;
        }}
        QPushButton {{
            background: transparent;
            color: {palette['text']};
            padding: 8px 12px;
            border-radius: 6px;
        }}
        QPushButton#primary {{
            background: {palette['btn_bg']};
            color: {palette['primary_btn_fg']};
            font-weight: 700;
            border-radius: 6px;
        }}
        QTreeWidget {{
            background: transparent;
            color: {palette['text']};
            border: none;
        }}
        QStatusBar {{
            background: transparent;
            color: {palette['muted']};
        }}
        """
        self.setStyleSheet(qss)

    # -------------------------
    # Actions
    # -------------------------
    def on_browse(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Base Path", str(Path.home()))
        if folder:
            self.base_path_edit.setText(folder)
            self.preview_update_live()

    def preview_update_live(self):
        """
        Update the tree preview to show only the names (not full paths).
        Uses current show/shot/artist values; shows v001 placeholder for preview.
        """
        show = self.show_edit.text().strip() if hasattr(self, "show_edit") else ""
        shot = self.shot_edit.text().strip() if hasattr(self, "shot_edit") else ""
        artist = self.artist_edit.text().strip() if hasattr(self, "artist_edit") else "Artist"

        self.tree.clear()

        if not show and not shot:
            root = self.tree.invisibleRootItem()
            empty = QtWidgets.QTreeWidgetItem(["Enter Show & Shot to preview"])
            self.tree.addTopLevelItem(empty)
            return

        show_node = QtWidgets.QTreeWidgetItem([show if show else "<SHOW>"])
        self.tree.addTopLevelItem(show_node)
        shot_node = QtWidgets.QTreeWidgetItem([shot if shot else "<SHOT>"])
        show_node.addChild(shot_node)

        # in/
        in_node = QtWidgets.QTreeWidgetItem(["in"])
        shot_node.addChild(in_node)
        in_node.addChild(QtWidgets.QTreeWidgetItem(["feedback"]))
        in_node.addChild(QtWidgets.QTreeWidgetItem(["plate"]))
        in_node.addChild(QtWidgets.QTreeWidgetItem(["ref"]))

        # mid/
        mid_node = QtWidgets.QTreeWidgetItem(["mid"])
        shot_node.addChild(mid_node)
        artist_node = QtWidgets.QTreeWidgetItem([artist if artist else "<ARTIST>"])
        mid_node.addChild(artist_node)
        artist_node.addChild(QtWidgets.QTreeWidgetItem(["sfx"]))
        nuke_node = QtWidgets.QTreeWidgetItem(["nuke"])
        artist_node.addChild(nuke_node)
        nuke_node.addChild(QtWidgets.QTreeWidgetItem(["shapes"]))
        nuke_node.addChild(QtWidgets.QTreeWidgetItem(["scripts"]))
        sil_node = QtWidgets.QTreeWidgetItem(["silhouette"])
        artist_node.addChild(sil_node)
        sil_node.addChild(QtWidgets.QTreeWidgetItem(["shapes"]))
        artist_node.addChild(QtWidgets.QTreeWidgetItem(["pre_render"]))

        # out/ - preview default v001
        out_node = QtWidgets.QTreeWidgetItem(["out"])
        shot_node.addChild(out_node)
        v_node = QtWidgets.QTreeWidgetItem([f"{shot}_roto_v001" if shot else "<SHOT>_roto_v001"])
        out_node.addChild(v_node)
        v_node.addChild(QtWidgets.QTreeWidgetItem([f"{shot}_roto_matte_01_v001" if shot else "<SHOT>_roto_matte_01_v001"]))
        v_node.addChild(QtWidgets.QTreeWidgetItem([f"{shot}_roto_matte_02_v001" if shot else "<SHOT>_roto_matte_02_v001"]))
        v_node.addChild(QtWidgets.QTreeWidgetItem([f"{shot}_roto_sfx_v001" if shot else "<SHOT>_roto_sfx_v001"]))
        v_node.addChild(QtWidgets.QTreeWidgetItem([f"{shot}_roto_nuke_script_v001" if shot else "<SHOT>_roto_nuke_script_v001"]))

        self.tree.expandAll()

    def on_create(self):
        base_path = self.base_path_edit.text().strip()
        show = self.show_edit.text().strip()
        shot = self.shot_edit.text().strip()
        artist = self.artist_edit.text().strip()

        if not base_path or not show or not shot or not artist:
            QtWidgets.QMessageBox.critical(self, "Missing info", "Please fill Base Path, Show, Shot and Artist.")
            return

        try:
            out_path = create_shot_tree(base_path, show, shot, artist)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to create folders:\n{e}")
            return

        QtWidgets.QMessageBox.information(self, "Done", f"Project created:\n{os.path.dirname(out_path)}\n\nOUT: {os.path.basename(out_path)}")
        # update preview to show actual version (scan out folder)
        self.preview_update_live()

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
