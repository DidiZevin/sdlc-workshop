# Plan: vote shares and a leader trophy

Spec: [spec.md](spec.md)

## Approach

The whole rule set lives in `poll/core.py`, in one new pure function:

```python
def result_lines(poll: Poll) -> list[str]:
    """One display line per option, in creation order, e.g. "Pizza — 66.7% (2 votes) 🏆"."""
```

It builds on the existing `tally` (order and counts) and `total_votes`. Formatting the line
is a business rule here (rounding, singular/plural, who gets a trophy), so it belongs in the
core, the same way `created_label` does. `app.py` only loops over the lines and renders them.

Two implementation decisions:

- **Rounding with integers, not floats.** The share in tenths of a percent is
  `(2000 * votes + total) // (2 * total)`, which rounds an exact half up (spec criterion 7)
  with no float error. Python's `round()` and `f"{x:.1f}"` both round 6.25 to 6.2, so they
  are not used. The line is then formatted as `f"{tenths // 10}.{tenths % 10}%"`.
- **Render with `st.text`, one call per line, under the "votes so far" caption.** `st.text`
  shows the string literally, so an option named `*bold*` or `# title` is not interpreted as
  Markdown. Placing the list after the existing captions keeps `caption[0]` and `caption[1]`
  in `tests/test_app.py` pointing at what they point at today.

This feature stores nothing: it leaves `Poll` and `poll.json` as it found them, and
`poll/store.py` is not touched. (The branch as a whole does add an optional `created_at` key,
from the earlier "created at" change; see the "Creation time" section of the spec.)

## Tasks

### Task 1: Share lines in the core

`result_lines(poll)` returns one line per option, `<option> — <share>% (<n> votes)`, without
any trophy yet.

- Acceptance criteria:
  - Lines come in creation order, with share and count: Pizza 2, Sushi 1, Salad 0 gives
    `66.7%`, `33.3%`, `0.0%` (spec #1, without the trophy).
  - A poll with no votes shows `0.0%` for every option, and doesn't divide by zero (spec #2,
    share part). Always one decimal, including `50.0%` and `100.0%` (spec #5). Three options
    with one vote each show `33.3%` each (spec #4, share part).
  - `(1 vote)` for exactly one vote, `(<n> votes)` otherwise (spec #6). 1 vote of 16 shows
    `6.3%` (spec #7). The poll passed in is not modified (spec #8).
- Test that proves it, in `tests/test_core.py`, written first:
  `test_result_lines_show_share_and_count_in_creation_order`,
  `test_result_lines_show_zero_percent_when_nobody_voted`,
  `test_result_lines_always_show_one_decimal`,
  `test_result_lines_say_vote_in_the_singular`,
  `test_result_lines_round_an_exact_half_up`,
  `test_result_lines_leave_the_poll_unchanged`.
- Files: `poll/core.py`, `tests/test_core.py`

### Task 2: Leader trophy in the core

`result_lines` appends ` 🏆` to the line of every option that has the most votes, when that
maximum is at least one vote.

- Acceptance criteria:
  - A single leader's line ends with ` 🏆`, and no other line does (spec #1 in full).
  - Every option tied for first gets the trophy; three options with one vote each all get
    one (spec #3, #4).
  - A poll with no votes has no trophy on any line (spec #2).
- Test that proves it, in `tests/test_core.py`, written first:
  `test_result_lines_mark_the_single_leader_with_a_trophy`,
  `test_result_lines_give_every_tied_leader_a_trophy`,
  `test_result_lines_have_no_trophy_when_nobody_voted`.
  The exact-string assertions from Task 1 that involve a leader are updated to include the
  trophy.
- Files: `poll/core.py`, `tests/test_core.py`

### Task 3: Show the list in the app

`app.py` renders each line from `result_lines(poll)` with `st.text`, after the existing
captions.

- Acceptance criteria:
  - After creating a poll and voting for Sushi, the page shows `Sushi — 100.0% (1 vote) 🏆`
    and `Pizza — 0.0% (0 votes)` (spec #9).
  - The bar chart, the "votes so far" caption and the "Created" caption are still there, and
    the existing assertions in `tests/test_app.py` pass unchanged (spec #9).
  - `uv run python -m pytest -q` and `uv run python -m ruff check .` both pass (spec #10).
- Test that proves it: `test_create_a_poll_then_vote` in `tests/test_app.py` gains one
  wiring assertion on `app.text`. No logic is tested there.
- Files: `app.py`, `tests/test_app.py`

## Risks

- **The baseline has never been run.** The "created at" changes on this branch (`app.py`,
  `poll/core.py`, both test files) were written without running pytest or ruff. `/sdlc:build`
  must start with a full run; a failure there belongs to that earlier work, not to this plan.
- **The agent cannot run commands in this session.** A strict sandbox blocks every shell
  command, so RED and GREEN runs have to be executed by the user in their own terminal and
  the output pasted back. Test evidence is only recorded from pasted output, never assumed.
- **Two features on one branch.** This plan sits in `sdlc/feature/poll-created-at/` beside the
  "created at" feature, which has no spec. Gate G5 (nothing outside the spec's scope
  changed) will flag that work at `/sdlc:pr`, unless the feature moves to its own branch or
  the gap is called out in the PR.
- **Float rounding.** Using `round()` or `:.1f` by habit would pass most tests and fail the
  exact-half case. We'd notice through `test_result_lines_round_an_exact_half_up`.
- **Look of `st.text`.** It renders in a monospace font. If that looks out of place next to
  the captions, switching to another element is a one-line change in `app.py` and in the
  wiring assertion; it doesn't touch the core.

## SDLC command coverage

- [x] /sdlc:spec: approved 2026-11-12 after 4 questions
- [x] /sdlc:plan: 3 tasks
- [x] /sdlc:build: 3 of 3 tasks done
- [x] /sdlc:test: 10 criteria and 12 edge cases mapped, 4 gaps closed, no bug found; open: no assertion that the bar chart is still rendered (criterion 9)
- [x] /sdlc:review: 8 findings: 4 fixed, 3 won't fix, 1 open (process: pending commits and a nested clone of the repo in the exercise folder)
- [ ] /sdlc:code-simplify

## Test evidence

- 2026-11-12 · baseline before task 1 (run by the user) · `uv run python -m pytest -q` → 22 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · task 1 RED (run by the user) · `uv run python -m pytest tests/test_core.py -q` → 1 error during collection: `ImportError: cannot import name 'result_lines' from 'poll.core'` (expected)
- 2026-11-12 · task 1 GREEN (run by the user) · `uv run python -m pytest -q` → 28 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · task 2 RED (run by the user) · `uv run python -m pytest tests/test_core.py -q` → 3 failed, 22 passed: the three trophy tests fail on the missing 🏆 (expected)
- 2026-11-12 · task 2 GREEN (run by the user) · `uv run python -m pytest -q` → 31 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 11:57 · task 3 RED (run by the user) · `uv run python -m pytest tests/test_app.py -q` → 1 failed, 1 passed: `test_create_a_poll_then_vote` fails with `assert [] == ['Pizza — 0.0...% (1 vote) 🏆']` (expected)
- 2026-11-12 · task 3 GREEN (run by the user) · `uv run python -m pytest -q` → 31 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · /sdlc:test gap pass, 4 regression tests added (run by the user) · `uv run python -m pytest -q` → 35 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · after review fixes 2, 3 and 7 (run by the user) · `uv run python -m pytest -q` → 35 passed · `uv run python -m ruff check .` → All checks passed!
