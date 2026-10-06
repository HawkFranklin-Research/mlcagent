from typing import Any

from mlca.ui_text import text

from .brief import FormScreen


class ProjectScreen(FormScreen):
    def __init__(self, path: Any, initialise: Any = False) -> None:
        fields = [("path", text("project"), str(path))]
        if initialise:
            fields.extend(
                [
                    ("data", text("data"), ""),
                    ("template", text("template"), "tabular_classification"),
                    ("aim", text("brief"), ""),
                    ("target", text("target"), ""),
                    ("unit", text("unit"), ""),
                    ("event_column", text("event_column"), ""),
                ]
            )
        super().__init__(text("init") if initialise else text("open"), fields)
