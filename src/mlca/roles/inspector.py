from typing import Any

from mlca.log.schema import StrictModel

from .base import Role, prompt


class FigureNote(StrictModel):
    description: str
    concerns: list[str]


class Inspector(Role):
    name = "inspector"

    def describe_figure(self, path: Any, caption: Any, step_id: Any) -> Any:
        response = self.session.client.complete(
            self.name,
            [{"role": "user", "content": prompt("inspector_figure.md", caption=caption)}],
            images=[path],
            context=self.context("figure", step_id=step_id),
            categories=["facts", "figure_image"],
        )
        return response.text
