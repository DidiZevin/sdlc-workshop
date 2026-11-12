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

Nothing is stored: `Poll` and `poll.json` are unchanged, and `poll/store.py` is not touched.

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
- [ ] /sdlc:build
- [ ] /sdlc:test
- [ ] /sdlc:review
- [ ] /sdlc:code-simplify

## Test evidence

