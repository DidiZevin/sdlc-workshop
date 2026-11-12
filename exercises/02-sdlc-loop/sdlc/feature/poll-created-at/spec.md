# Spec: vote shares and a leader trophy

Status: Approved (2026-11-12)

## Objective

Someone watching a live poll should see at a glance what share of the vote each option has
and which option is leading, without doing the arithmetic from raw counts. Below the bar
chart, the app lists every option with its percentage, its vote count, and a 🏆 at the end
of the line of the leading option.

## Scope

In scope:
- A results list under the bar chart, one line per option, in the order the options were
  created: `<option> — <share>% (<n> votes)`, with ` 🏆` appended to a leader's line.
- The share and leader logic in `poll/core.py`, as pure functions, tested in
  `tests/test_core.py`.
- Wiring the list into `app.py`, with one wiring check in `tests/test_app.py`.
- Also on this branch, built before this spec was written: the poll records when it was
  created and shows it. See "Creation time" below. Added to the spec after review
  finding 1, so that the spec matches what the branch changes.

Out of scope:
- The bar chart: it keeps showing raw vote counts, unchanged.
- The existing "N votes so far" caption, including its "1 votes" wording.
- Sorting results by votes. Lines never move when the lead changes.
- Any change to `poll.json` or the `Poll` data shape by the shares and trophy feature.
  Shares are computed, never stored. The only data-shape change on the branch is the
  optional `created_at` key described under "Creation time".
- Time zones for the creation time: it is the local time of the machine running the app,
  stored without an offset.
- Declaring a final winner, closing a poll, or any other poll state.
- Forcing the trophy to the right-hand side of the screen. It is the last character of the
  line; in a line that starts with right-to-left text the browser may render that end on
  the left.

## Success criteria

1. Given a poll with votes Pizza 2, Sushi 1, Salad 0, when the results are listed, then the
   lines are, in this order: `Pizza — 66.7% (2 votes) 🏆`, `Sushi — 33.3% (1 vote)`,
   `Salad — 0.0% (0 votes)`.
2. Given a poll with no votes, when the results are listed, then every option shows `0.0%`
   and no line has a 🏆.
3. Given two or more options tied for the most votes (with at least one vote), when the
   results are listed, then every tied option's line ends with 🏆 and no other line does.
4. Given three options with one vote each, when the results are listed, then each shows
   `33.3%` (the shares add up to 99.9%, and that is accepted) and all three have a 🏆.
5. Given any poll, when the results are listed, then every share has exactly one digit
   after the decimal point, including `0.0%`, `50.0%` and `100.0%`.
6. Given an option with exactly one vote, then its line says `(1 vote)`; any other count
   says `(<n> votes)`.
7. Given a share that falls exactly halfway between two tenths (1 vote of 16 is 6.25%),
   then it rounds up (`6.3%`).
8. Given a poll, when the results are listed, then the poll passed in is not modified.
9. Given the running app, when a poll is created and a vote is cast, then the page shows
   the results list with the voted option's line ending in 🏆, and the bar chart and the
   "votes so far" caption are still present.
10. `uv run python -m pytest -q` and `uv run python -m ruff check .` both pass.

### Creation time

11. Given a poll created through the app, then `poll.json` holds a `created_at` key with
    the creation time in ISO 8601 format to the second, such as `2026-11-12T14:30:05`.
12. Given a poll with a `created_at`, when the page is shown, then a caption reads
    `Created 2026-11-12 14:30` (date and time to the minute).
13. Given a poll saved before this change, with no `created_at`, then the page works and
    shows no "Created" caption.
14. Given a poll with a `created_at`, when a vote is cast, then the creation time is
    unchanged.
15. `poll/core.py` never reads the clock: the caller passes the creation time in.

## Edge cases and decisions

| Case | Decision | Why |
|---|---|---|
| Tie for first place | Every tied option gets a 🏆 | A tie is a real state in a live poll; picking one by creation order would show a winner that doesn't exist. |
| Zero votes | Every option shows `0.0%`, and nobody gets a 🏆 | Under the tie rule all options would "lead" on zero; a trophy for zero votes is meaningless. There is no leader until the first vote. |
| Rounding | One decimal place, each option rounded on its own | The user asked for one decimal (`33.3%`) rather than whole numbers. |
| Shares not adding up to 100% | Accepted (99.9% or 100.1% can happen) | The user doesn't need an exact 100%. Correcting the sum would show different shares for options with equal votes. |
| Number format | Always one decimal, also for whole values (`50.0%`) | Consistent width and no special cases. |
| Exact half (e.g. 6.25%) | Rounds up, to `6.3%` | What a reader expects from school arithmetic. Python's built-in `round` would give `6.2%` here, so this has to be deliberate. |
| Trophy position | End of the line, after the vote count | The user asked for the trophy at the end rather than the start. |
| Order of lines | The order the options were created in | Matches the existing `tally` order, and lines stay put as votes come in. |
| One vote | `(1 vote)`, singular | Correct English in the new list. The existing "1 votes so far" caption is out of scope. |
| Where it's shown | A separate list under the chart, not in the chart's labels | Chart labels that change with every vote can reorder the bars; a list is stable and easy to test. |
| Poll saved before this feature | Works unchanged | Nothing new is stored, so an existing `poll.json` needs no migration. |
| Single option holding every vote | `100.0%` and a 🏆 | Follows from the rules above. |
| Poll with no creation time | No "Created" caption, and no error | Polls saved before the change must keep working without a migration. |
| Malformed `created_at` in a hand-edited `poll.json` | Not handled: the page raises an error | Review finding 4, won't fix. The app always writes a valid value. |
| Time zone of the creation time | Local time of the machine running the app, no offset | Review finding 5, won't fix. Good enough for a single-room workshop poll. |

## Open questions

- None.

## Decisions

- No ADR. None of the decisions above has a trade-off that outlives this feature.
