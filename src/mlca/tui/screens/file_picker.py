from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Static


class FilePicker(ModalScreen[str | None]):
    """Explicit file or folder selection, including remote-terminal typed paths."""

    CSS = """FilePicker { align: center middle; }
    #browser { width: 90%; height: 90%; border: round $accent; padding: 1; }
    DirectoryTree { height: 1fr; } #picker-buttons { height: 3; }"""

    def __init__(self, start, folders_only=False):
        super().__init__()
        from pathlib import Path

        self.start = Path(start or "~").expanduser()
        if not self.start.is_dir():
            self.start = self.start.parent
        if not self.start.is_dir():
            self.start = Path.home()
        self.folders_only = folders_only

    def compose(self) -> ComposeResult:
        with Vertical(id="browser"):
            yield Static("Choose a folder" if self.folders_only else "Choose a file or folder")
            yield Input(str(self.start), id="picked-path")
            yield DirectoryTree(self.start, id="directory-tree")
            with Horizontal(id="picker-buttons"):
                yield Button("Go", id="go")
                yield Button("Select", id="select", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_directory_tree_file_selected(self, event):
        self.query_one("#picked-path", Input).value = str(event.path)

    def on_directory_tree_directory_selected(self, event):
        self.query_one("#picked-path", Input).value = str(event.path)

    def on_button_pressed(self, event):
        from pathlib import Path

        identifier = event.button.id
        if identifier == "cancel":
            self.dismiss(None)
            return
        path = Path(self.query_one("#picked-path", Input).value).expanduser()
        if identifier == "go":
            if path.is_dir():
                self.query_one(DirectoryTree).path = path
            else:
                self.notify("Enter an existing folder to browse", severity="error")
        elif identifier == "select":
            if self.folders_only and path.is_file():
                self.notify("Select a folder", severity="error")
            elif path.exists() or (self.folders_only and path.parent.is_dir()):
                self.dismiss(str(path))
            else:
                self.notify(
                    "Path does not exist (new project folders need an existing parent)", severity="error"
                )
