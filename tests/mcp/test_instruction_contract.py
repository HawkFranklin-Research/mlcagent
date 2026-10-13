from pathlib import Path

from mlca.mcp.server import INSTRUCTIONS


def test_server_and_skill_describe_guided_human_routes():
    assert len(INSTRUCTIONS.strip().splitlines()) <= 15
    for word in ["actor", "human", "study_fields", "journey", "messages_data", "choose yourself"]:
        assert word in INSTRUCTIONS
    skill = (Path(__file__).parents[2] / "skills/mlca/SKILL.md").read_text()
    assert "Guided style (default)" in skill
    for word in ["how", "study_fields", "--edit", "journey", "autonomous"]:
        assert word in skill
