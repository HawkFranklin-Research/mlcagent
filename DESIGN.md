# MLCA terminal interface

## Purpose and visual ownership

MLCA is a terminal tool for guided, auditable machine-learning studies. The
existing Textual theme, banner, and panel CSS remain the runtime design owners;
this document records their use, rather than defining a second token system.
The terminal controls its font and colour rendering. English UI labels follow
existing `ui_text` vocabulary; no new locale or market-specific styling is added.

## Layout and controls

Keep the event strip, numbered option cards, sub-goals, facts, journey and status
panels. Reuse `Progress` for active work and the decision countdown, without a
new overlay or changing panel dimensions. The footer exposes `h: Halt`; Space is
an equivalent shortcut. Existing form/modal keyboard handling takes priority.

## Autonomous decision behaviour

`a: Run study` starts human-authorized driver automation. Each decision shows its
title and remaining seconds. `h` halts the decision without executing it. The
existing cards, question form, confirm and scoped-custom controls then apply;
`a` resumes automation. Human choices retain human attribution. Halt does not
terminate an already-running sandbox process; it pauses before the next action.

A window expiry selects the recorded recommendation; it does not bypass gates,
change package permissions, or grant an MCP agent human privileges. Failures
remain visible in the journey/log and ordinary recovery controls. Use Textual
pilot tests for countdown, keyboard Halt, state recovery and existing workflows.
