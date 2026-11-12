# Review: vote shares and a leader trophy

Reviewed 2026-11-12 by the `code-reviewer` agent in a fresh context, from the files (no
`git diff` was available: shell commands are blocked in this session). Scope: everything the
branch changed relative to `main`, which is the specced "vote shares and leader trophy"
feature plus the earlier, unspecced "show when the poll was created" change.

Verdict: the code is approved, with no Critical findings. Finding 1 needs a decision before
the PR, and finding 2 is a small test gap.

## Findings

| # | Severity | Axis | Where | Finding | Suggested fix | Status |
|---|---|---|---|---|---|---|
| 1 | Important | Architecture, spec alignment | `poll/core.py:13-24`, `app.py:25`, `spec.md` out-of-scope list | The spec says "any change to `poll.json` or the `Poll` data shape" is out of scope, and the plan says `Poll` is unchanged. Relative to `main` the branch does change both, through the unspecced "created at" work (commit `a863c05`). A reader checking the PR against the spec sees a data-shape change that no criterion covers. | In order of preference: (a) move the "created at" commit to its own branch and PR; (b) keep it, add a short "created at" section to the spec and narrow the out-of-scope line; (c) at minimum, call it out in the PR description. | fixed: option (b), "Creation time" section added to `spec.md` and the out-of-scope line narrowed |
| 2 | Important | Correctness (tests) | `tests/test_app.py:35-40` | Spec criterion 9 requires the bar chart to still be present, and nothing asserts it. Deleting `st.bar_chart(results)` would leave the suite green. | Add one wiring assertion that a chart element exists after the vote. The element type name must be checked against the installed Streamlit. | fixed: `assert len(app.get("vega_lite_chart")) == 1` in `test_create_a_poll_then_vote` |
| 3 | Suggestion | Correctness (robustness) | `poll/core.py:78` | `most` is read from `poll["votes"]`, while the lines come from `tally(poll)`, which follows `poll["options"]`. They agree for any poll the app builds. For a hand-edited `poll.json` an empty `votes` raises `ValueError`, and a stray key with the top count leaves nobody with a trophy. | Derive both from one source: `counts = tally(poll)`, then `most = max((votes for _, votes in counts), default=0)`. | fixed |
| 4 | Suggestion | Correctness (robustness) | `poll/core.py:52`, `app.py:44` | `datetime.fromisoformat` raises on a malformed `created_at`. The call runs before the Reset button is drawn, so a bad value crashes the page on every run with no way to reset from the UI. Only a hand-edited file can get there. | Return `None` from `created_label` on `ValueError`/`TypeError`, with a test; or accept the risk. | won't fix: only a hand-edited file gets there; recorded in the spec's edge-case table |
| 5 | Suggestion | Correctness (design) | `app.py:25` | `datetime.now()` is naive local time of the machine running the app, stored without an offset and shown without a zone. A viewer in another time zone reads a wrong time. | Pass `datetime.now().astimezone()`; the label format is unchanged. | won't fix: local time is enough for a single-room poll; recorded in the spec as out of scope |
| 6 | Suggestion | Readability, UX | `app.py:43-47` | The "Created ..." caption sits between "N votes so far" and the results list, splitting two related blocks. | Move the created caption under the subheader, and make the test match it by content rather than by `caption[1]`. | won't fix: a matter of taste, not chosen by the user |
| 7 | Suggestion | Readability | `poll/core.py:87` | `_share` returns a formatted string, not a number, and the name doesn't say so. | Rename to `_share_label` or `_percent`. | fixed: renamed to `_percent` |
| 8 | Suggestion | Process | working tree | Task 3, the gap tests and possibly `spec.md` are not committed yet. A nested clone of the whole repository sits in `exercises/02-sdlc-loop/sdlc-workshop/` and must stay out of every commit. | Commit the pending work by file name. Decide what to do with the nested clone. | open |

## Axes with nothing to raise

- Security: `st.text` renders option names literally, so there is no Markdown injection. The
  caption is built from a parsed datetime, not raw input. No secrets or real data in fixtures.
- Performance: a few linear passes over a handful of options per rerun.

## What the reviewer confirmed

- The half-up rounding `(2000 * votes + total) // (2 * total)` is correct; ten cases were
  worked by hand, including the ones where `round()` would differ.
- The tests would catch the likely regressions: float rounding, a trophy on zero votes, a
  trophy by position.
- The conventions in `CLAUDE.md` hold: the core is pure, `store.py` is untouched, `app.py`
  holds no rules, and the `test_app.py` additions are wiring only.
- A `poll.json` saved on `main` still works.
