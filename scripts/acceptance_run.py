"""Offline TUI autopilot acceptance. Data stay outside Git; failures are retained.

This is a no-AI reference comparison check, not an agent measurement or paper result.
"""

import argparse
import asyncio
import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from textual.widgets import Input, Select

from mlca.api import Session
from mlca.evaluation.metrics import generate
from mlca.llm.usage import read
from mlca.paths import sha256
from mlca.project.init import initialise
from mlca.tui.app import MlcaApp
from mlca.tui.screens.main import MainScreen
from mlca.tui.widgets.questions import Questions

# Task-card metadata from benchmark_datasets/README.md, never engine rules.
CARDS = {
    "breast_cancer_diagnostic_uci.csv": ("tabular_classification", "Diagnosis", None),
    "heart_disease_cleveland_uci.csv": ("tabular_classification", "heart_disease_binary", None),
    "adult_census_uci.csv": ("tabular_classification", "income", None),
    "dry_bean_uci.csv": ("tabular_classification", "Class", None),
    "lung_cancer_survival.csv": ("survival", "time", "event"),
    "gbsg2_breast_cancer_survival.csv": ("survival", "time", "cens"),
}


async def pilot_run(root, principal):
    app = MlcaApp(root)
    stops = []
    async with app.run_test(size=(140, 55)) as pilot:

        async def settle():
            await pilot.pause()
            await app.workers.wait_for_complete()
            await pilot.pause()

        await settle()
        if not isinstance(app.screen, MainScreen):
            raise RuntimeError("Study did not open in the TUI")
        # The offline pilot is policy-driven, never counted as a human intervention.
        app.session.close()
        app.session = Session(root, client="tui-acceptance", principal=principal, policy=True)
        app.session.progress_callback = lambda p: app.call_from_thread(app.update_progress, p)
        await pilot.press("a")
        await settle()
        for _ in range(100):
            state = app.session.state
            if state.current_event == "report" and state.event_statuses.get("report") == "done":
                app.session.store.verify()
                metrics = generate(app.session)
                if read(root):
                    raise RuntimeError("Offline reference acceptance unexpectedly called a model")
                return stops, metrics
            failures = [s for s in state.steps if s["status"] == "failed"]
            if failures:
                raise RuntimeError(failures[-1]["last_error"])
            qs = app.session.questions()
            if qs:
                q = qs[0]
                stops.append(
                    {
                        "kind": "question",
                        "event": state.current_event,
                        "id": q["question_id"],
                        "answer": q["recommended"],
                        "explicit": q.get("explicit", False),
                    }
                )
                widget = app.screen.query_one(Questions)
                widget.tab = 0
                widget.show_questions(qs)
                widget.query_one(Select).value = q["recommended"]
                widget.submit()
                await settle()
                continue
            turn = app.session.guided_view()
            human = next((c for c in turn if c["id"].startswith("human:")), None)
            if human:
                stops.append({"kind": "approval", "event": state.current_event, "id": human["id"]})
                app.select_option(human["id"])
                await pilot.pause()
                if human["id"] == "human:unlock":
                    app.screen.query_one("#phrase", Input).value = "UNLOCK TEST"
                    app.screen.query_one(
                        "#reason", Input
                    ).value = "Prespecified offline acceptance task-card policy"
                elif human["id"].startswith("human:confirm:"):
                    app.screen.query_one(
                        "#note", Input
                    ).value = "Prespecified offline acceptance task-card policy"
                else:
                    raise RuntimeError("Task card left study fields unresolved")
                app.screen.query_one("#submit").scroll_visible(animate=False)
                await pilot.pause()
                await pilot.click("#submit")
                await settle()
                continue
            if not app.busy:
                await pilot.press("a")
                await settle()
        raise RuntimeError("Acceptance pilot stop limit reached")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--select", action="append")
    args = parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        parser.error("Choose a fresh output directory; prior failures must be preserved")
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ["UV_OFFLINE"] = "1"
    os.environ["XDG_CONFIG_HOME"] = str(args.out / "user-config")
    os.environ["XDG_DATA_HOME"] = str(args.out / "user-data")
    summary = []
    for name, (template, target, event) in CARDS.items():
        if args.select and name not in args.select:
            continue
        started = time.monotonic()
        data = args.data / name
        brief = {
            "aim": "Predict the recorded outcome using the available covariates",
            "target": target,
            "unit": "One subject",
            "repeated_subjects": "no",
        }
        if event:
            brief.update(duration=target, event_column=event)
        card = {
            "template": template,
            "data_sha256": sha256(data),
            "brief": brief,
            "measurement_arm": "reference",
            "seed": 42,
            "bootstrap_resamples": 1000,
            "answers": "recommended, explicitly selected",
            "approvals": "brief, validation choice, one test exposure",
            "option_policy": "primary then alternative",
            "feature_policy": "retain all unless source columns exceed training rows",
        }
        digest = hashlib.sha256(json.dumps(card, sort_keys=True).encode()).hexdigest()
        principal = "user:policy/" + digest[:12]
        root = args.out / name.removesuffix(".csv")
        (args.out / (name + ".task.json")).write_text(json.dumps(card, indent=2))
        row = {
            "dataset": name,
            "measurement_arm": "reference",
            "status": "failed",
            "model_calls": 0,
            "task_card_sha256": digest,
            "data_sha256": card["data_sha256"],
            "project": str(root),
        }
        try:
            initialise(root, [data], template, brief, {"measurement_arm": "reference"}, principal=principal)
            stops, metrics = asyncio.run(pilot_run(root, principal))
            (args.out / (name + ".stops.json")).write_text(json.dumps(stops, indent=2))
            row.update(
                status="completed",
                stops=len(stops),
                questions=sum(s["kind"] == "question" for s in stops),
                approvals=sum(s["kind"] == "approval" for s in stops),
                metric=metrics["results"]["test"]["name"],
                value=metrics["results"]["test"]["value"]["value"],
            )
        except Exception as exc:
            row["error"] = str(exc)[:1000]
        row["seconds"] = round(time.monotonic() - started, 3)
        summary.append(row)
        fields = list(dict.fromkeys(k for r in summary for k in r))
        with (args.out / "summary.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fields)
            writer.writeheader()
            writer.writerows(summary)
        print(json.dumps(row), flush=True)
    print("Completed at " + datetime.now(timezone.utc).isoformat(), flush=True)
    if any(r["status"] != "completed" for r in summary):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
