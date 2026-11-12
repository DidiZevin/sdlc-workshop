"""Poll logic as plain functions over plain data.

Nothing here touches files or Streamlit. That's what makes it easy to test: every
function takes a poll and returns a value or a new poll.
"""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict


class _RequiredPoll(TypedDict):
    question: str
    options: list[str]
    votes: dict[str, int]


class Poll(_RequiredPoll, total=False):
    # ISO 8601, to the second. Missing on polls saved before creation time was recorded.
    created_at: str


def create_poll(question: str, options: list[str], created_at: datetime | None = None) -> Poll:
    """Return a new poll with zero votes. Surrounding whitespace and blank options are dropped.

    The caller supplies `created_at`, so this module never reads the clock.
    """
    question = question.strip()
    cleaned = [option.strip() for option in options if option.strip()]
    if not question:
        raise ValueError("A poll needs a question.")
    if len(cleaned) < 2:
        raise ValueError("A poll needs at least two options.")
    if len(set(cleaned)) != len(cleaned):
        raise ValueError("Options must be unique.")
    poll: Poll = {
        "question": question,
        "options": cleaned,
        "votes": {option: 0 for option in cleaned},
    }
    if created_at is not None:
        poll["created_at"] = created_at.isoformat(timespec="seconds")
    return poll


def created_label(poll: Poll) -> str | None:
    """A line such as "Created 2026-11-12 14:30", or None when the poll has no creation time."""
    created_at = poll.get("created_at")
    if created_at is None:
        return None
    return f"Created {datetime.fromisoformat(created_at):%Y-%m-%d %H:%M}"


def vote(poll: Poll, option: str) -> Poll:
    """Return a copy of the poll with one more vote for `option`."""
    if option not in poll["votes"]:
        raise ValueError(f"Unknown option: {option!r}")
    votes = {**poll["votes"], option: poll["votes"][option] + 1}
    return {**poll, "votes": votes}


def tally(poll: Poll) -> list[tuple[str, int]]:
    """Vote counts per option, in the order the options were created."""
    return [(option, poll["votes"][option]) for option in poll["options"]]


def total_votes(poll: Poll) -> int:
    return sum(poll["votes"].values())


def result_lines(poll: Poll) -> list[str]:
    """One display line per option, in creation order, such as "Pizza — 66.7% (2 votes) 🏆".

    Every option tied for the most votes gets the trophy. Nobody leads a poll with no votes.
    """
    counts = tally(poll)
    total = total_votes(poll)
    most = max((votes for _, votes in counts), default=0)
    lines = []
    for option, votes in counts:
        noun = "vote" if votes == 1 else "votes"
        trophy = " 🏆" if votes and votes == most else ""
        lines.append(f"{option} — {_percent(votes, total)} ({votes} {noun}){trophy}")
    return lines


def _percent(votes: int, total: int) -> str:
    """`votes` out of `total` as a percentage with one decimal, such as "33.3%".

    Integer arithmetic, so that an exact half rounds up (6.25 → 6.3). `round()` and float
    formatting would round it down to 6.2.
    """
    tenths = (2000 * votes + total) // (2 * total) if total else 0
    return f"{tenths // 10}.{tenths % 10}%"
