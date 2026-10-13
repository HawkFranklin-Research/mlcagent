import asyncio

from mcp import Client
from mcp.types import Implementation

from mlca.api import Session
from mlca.engine.questions import ask
from mlca.mcp.server import create_server
from tests.helpers import advance_to
from tests.mcp.test_protocol import data


def test_questions_and_engine_human_boundary(project_factory):
    root = project_factory()
    with Session(root) as s:
        advance_to(s, "data")
        s.review_data()
        sensitive = ask(
            s,
            {
                "header": "Source feature",
                "question": "Exclude x1?",
                "explicit": True,
                "human_only": True,
                "options": [
                    {
                        "label": "Exclude",
                        "description": "Exclude this prediction feature",
                        "effect": {"kind": "exclude_column", "column": "x1"},
                    }
                ],
            },
            key="leakage:x1",
        )
        ordinary = ask(
            s,
            {
                "header": "Retain",
                "question": "Keep the other columns?",
                "options": [
                    {
                        "label": "Keep",
                        "description": "Retain the recorded features",
                        "effect": {"kind": "keep"},
                    }
                ],
            },
        )

    async def check():
        server = create_server(root, "brain")
        async with Client(server, client_info=Implementation(name="question-client", version="1")) as client:
            qs = data(await client.call_tool("mlca_questions", {}))["questions_data"]
            assert {q["question_id"] for q in qs} == {sensitive, ordinary}
            refused = await client.call_tool("mlca_answer", {"question_id": sensitive, "answer": 0})
            assert refused.is_error
            data(await client.call_tool("mlca_answer", {"question_id": ordinary, "answer": 0}))
            with Session(root) as human:
                human.answer_question(sensitive, 0)
            assert data(await client.call_tool("mlca_questions", {}))["questions_data"] == []
            records = server.controller.session.branches.records()
            answer = next(
                r
                for r in records
                if r.type.value == "QuestionAnswered" and r.payload["question_id"] == ordinary
            )
            assert answer.actor == "agent:question-client/1"
            assert server.controller.session.client.disabled

    asyncio.run(check())
