# PR: feat(poll): show vote shares, a leader trophy and creation time

- Title: `feat(poll): show vote shares, a leader trophy and creation time`
- Head branch: `feature/poll-created-at`
- Base branch: `main`
- Status: ready (all gates pass on the recorded evidence; see the note under Gates)

Why this is a file and not a pull request: the agent session that prepared it could not run
shell commands (a strict sandbox blocks `git push` and `gh`), and `origin` in this clone
points at `haco29/sdlc-workshop`, the workshop's source repository, not at a fork the author
can push to. Push the branch to your own fork and paste the body below into the pull
request form.

---

## Why

Someone watching a live poll should see at a glance what share of the vote each option has
and which option is leading, without doing the arithmetic from raw counts. Below the bar
chart, the app now lists every option with its percentage, its vote count, and a 🏆 at the
end of the line of the leading option.

The branch also records when a poll was created and shows it. That change was built before
the spec was written and was added to the spec after review.

Spec: [spec.md](exercises/02-sdlc-loop/sdlc/feature/poll-created-at/spec.md)

## What changed

- Task 1, share lines in the core: `result_lines(poll)` in `poll/core.py` returns one line
  per option in creation order, such as `Pizza — 66.7% (2 votes)`. Shares have one decimal
  and an exact half rounds up, computed with integer arithmetic.
- Task 2, leader trophy in the core: every option tied for the most votes gets ` 🏆` at the
  end of its line. A poll with no votes has no trophy.
- Task 3, show the list in the app: `app.py` renders each line with `st.text` under the
  existing captions. The bar chart and the "votes so far" caption are unchanged.
- Creation time (built before the spec): `create_poll` accepts a `created_at` passed in by
  the caller, stored in `poll.json` as an optional ISO 8601 string, and shown as
  `Created 2026-11-12 14:30`. Polls saved before the change have no such key and keep
  working.

## How it was tested

From the Test evidence log in `plan.md`, verbatim. The agent could not run commands, so every
run was executed by the author and pasted back.

- 2026-11-12 · baseline before task 1 (run by the user) · `uv run python -m pytest -q` → 22 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · task 1 RED (run by the user) · `uv run python -m pytest tests/test_core.py -q` → 1 error during collection: `ImportError: cannot import name 'result_lines' from 'poll.core'` (expected)
- 2026-11-12 · task 1 GREEN (run by the user) · `uv run python -m pytest -q` → 28 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · task 2 RED (run by the user) · `uv run python -m pytest tests/test_core.py -q` → 3 failed, 22 passed: the three trophy tests fail on the missing 🏆 (expected)
- 2026-11-12 · task 2 GREEN (run by the user) · `uv run python -m pytest -q` → 31 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 11:57 · task 3 RED (run by the user) · `uv run python -m pytest tests/test_app.py -q` → 1 failed, 1 passed: `test_create_a_poll_then_vote` fails with `assert [] == ['Pizza — 0.0...% (1 vote) 🏆']` (expected)
- 2026-11-12 · task 3 GREEN (run by the user) · `uv run python -m pytest -q` → 31 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · /sdlc:test gap pass, 4 regression tests added (run by the user) · `uv run python -m pytest -q` → 35 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · after review fixes 2, 3 and 7 (run by the user) · `uv run python -m pytest -q` → 35 passed · `uv run python -m ruff check .` → All checks passed!
- 2026-11-12 · /sdlc:code-simplify · no code changed, so no new run; the run above is the latest and covers the current code

## Gates

| Gate | Result | Evidence |
|---|---|---|
| G1 Spec | Pass | `spec.md` is `Status: Approved (2026-11-12)` and specific to this feature. The "Creation time" section was added after approval, following review finding 1. |
| G2 Plan | Pass | `plan.md` has 3 tasks with acceptance criteria mapped to spec criteria, plus the coverage and evidence sections. |
| G3 Tasks | Pass | All 3 boxes in `todo.md` are ticked. |
| G4 Evidence | Pass | `uv run python -m pytest -q` → 35 passed and `uv run python -m ruff check .` → All checks passed!, run by the author after the last code change and logged. Not re-run by the agent, which cannot run commands. |
| G5 Alignment | Pass | Criteria 1 to 9 and 11 to 14 each map to code and a test. Criterion 10 is this gate's own check. Criterion 15 (the core never reads the clock) holds by construction and has no test. The data-shape change is now inside the spec's scope. |
| G6 Coverage | Pass | All six lines in "SDLC command coverage" are ticked. |

Not verified: that the working tree is clean. `git status` could not be run by the agent.

## Review

Reviewed by the `code-reviewer` agent in a fresh context: 8 findings, none Critical. Full
table in [review.md](exercises/02-sdlc-loop/sdlc/feature/poll-created-at/review.md).

Fixed:
- 1 (Important): the branch changed the `Poll` shape while the spec said it would not. The
  spec now has a "Creation time" section and a narrower out-of-scope line.
- 2 (Important): nothing asserted that the bar chart is still rendered. Added a wiring
  assertion.
- 3 (Suggestion): the trophy threshold and the lines came from different parts of the poll.
  Both now come from `tally`.
- 7 (Suggestion): `_share` renamed to `_percent`.

Won't fix:
- 4: a malformed `created_at` in a hand-edited `poll.json` raises an error. The app always
  writes a valid value.
- 5: the creation time is naive local time with no offset. Enough for a single-room poll.
- 6: the "Created" caption sits between the vote count and the results list. A matter of
  taste.

Open:
- 8 (process): an untracked nested clone of the repository sits in
  `exercises/02-sdlc-loop/sdlc-workshop/`. It is not part of this branch and must stay out
  of it.

## Out of scope

- The bar chart keeps showing raw vote counts.
- The existing "N votes so far" caption, including its "1 votes" wording.
- Sorting results by votes: lines never move when the lead changes.
- Declaring a final winner, closing a poll, or any other poll state.
- Forcing the trophy to the right-hand side of the screen: it is the last character of the
  line, so in a line that starts with right-to-left text the browser may render it on the
  left.
- Time zones for the creation time.

Follow-ups:
- The results list renders in a monospace font (`st.text`). Changing the element is a
  one-line change in `app.py` and in the wiring assertion.
- Two features share this branch and one PR. A project rule "one feature per branch, no
  code without an approved spec" was proposed in review and is not yet decided.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
