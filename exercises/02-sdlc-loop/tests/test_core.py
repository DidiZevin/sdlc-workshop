from copy import deepcopy
from datetime import datetime

import pytest

from poll.core import create_poll, created_label, result_lines, tally, total_votes, vote


def make_poll():
    return create_poll("Lunch?", ["Pizza", "Sushi", "Salad"])


def poll_with_votes(**votes):
    """A poll whose options are the keyword names, each voted for the given number of times."""
    poll = create_poll("Lunch?", list(votes))
    for option, count in votes.items():
        for _ in range(count):
            poll = vote(poll, option)
    return poll


def test_create_poll_starts_with_zero_votes():
    poll = make_poll()

    assert poll["question"] == "Lunch?"
    assert poll["options"] == ["Pizza", "Sushi", "Salad"]
    assert poll["votes"] == {"Pizza": 0, "Sushi": 0, "Salad": 0}


def test_create_poll_trims_whitespace_and_drops_blank_options():
    poll = create_poll("  Lunch?  ", [" Pizza ", "", "   ", "Sushi"])

    assert poll["question"] == "Lunch?"
    assert poll["options"] == ["Pizza", "Sushi"]


def test_create_poll_needs_a_question():
    with pytest.raises(ValueError, match="question"):
        create_poll("   ", ["Pizza", "Sushi"])


def test_create_poll_needs_two_options():
    with pytest.raises(ValueError, match="two options"):
        create_poll("Lunch?", ["Pizza", ""])


def test_create_poll_rejects_duplicate_options():
    with pytest.raises(ValueError, match="unique"):
        create_poll("Lunch?", ["Pizza", "Pizza"])


def test_create_poll_records_when_it_was_created():
    poll = create_poll("Lunch?", ["Pizza", "Sushi"], created_at=datetime(2026, 11, 12, 14, 30, 5))

    assert poll["created_at"] == "2026-11-12T14:30:05"


def test_create_poll_without_a_time_has_no_created_at():
    assert "created_at" not in make_poll()


def test_vote_keeps_the_creation_time():
    poll = create_poll("Lunch?", ["Pizza", "Sushi"], created_at=datetime(2026, 11, 12, 14, 30))

    assert vote(poll, "Pizza")["created_at"] == poll["created_at"]


def test_created_label_shows_date_and_time_to_the_minute():
    poll = create_poll("Lunch?", ["Pizza", "Sushi"], created_at=datetime(2026, 11, 12, 14, 30, 5))

    assert created_label(poll) == "Created 2026-11-12 14:30"


def test_created_label_is_none_for_a_poll_saved_before_the_feature():
    assert created_label(make_poll()) is None


def test_vote_adds_one_vote_to_the_option():
    poll = vote(make_poll(), "Sushi")

    assert poll["votes"]["Sushi"] == 1
    assert poll["votes"]["Pizza"] == 0


def test_vote_leaves_the_original_poll_unchanged():
    original = make_poll()

    vote(original, "Pizza")

    assert original["votes"]["Pizza"] == 0


def test_vote_for_an_unknown_option_raises():
    with pytest.raises(ValueError, match="Unknown option"):
        vote(make_poll(), "Burgers")


def test_tally_keeps_the_order_options_were_created_in():
    poll = vote(vote(make_poll(), "Salad"), "Salad")

    assert tally(poll) == [("Pizza", 0), ("Sushi", 0), ("Salad", 2)]


def test_total_votes_counts_every_vote():
    poll = vote(vote(vote(make_poll(), "Pizza"), "Sushi"), "Pizza")

    assert total_votes(poll) == 3


def test_total_votes_is_zero_for_a_new_poll():
    assert total_votes(make_poll()) == 0


def test_result_lines_show_share_and_count_in_creation_order():
    poll = poll_with_votes(Pizza=2, Sushi=1, Salad=0)

    assert result_lines(poll) == [
        "Pizza — 66.7% (2 votes) 🏆",
        "Sushi — 33.3% (1 vote)",
        "Salad — 0.0% (0 votes)",
    ]


def test_result_lines_show_zero_percent_when_nobody_voted():
    assert result_lines(make_poll()) == [
        "Pizza — 0.0% (0 votes)",
        "Sushi — 0.0% (0 votes)",
        "Salad — 0.0% (0 votes)",
    ]


def test_result_lines_always_show_one_decimal():
    assert result_lines(poll_with_votes(Pizza=1, Sushi=1))[0].startswith("Pizza — 50.0% ")
    assert result_lines(poll_with_votes(Pizza=3, Sushi=0))[0].startswith("Pizza — 100.0% ")


def test_result_lines_say_vote_in_the_singular():
    lines = result_lines(poll_with_votes(Pizza=1, Sushi=2, Salad=3))

    assert lines[0].endswith("(1 vote)")
    assert lines[1].endswith("(2 votes)")


def test_result_lines_round_an_exact_half_up():
    lines = result_lines(poll_with_votes(Pizza=1, Sushi=15))

    assert lines[0].startswith("Pizza — 6.3% ")
    assert lines[1].startswith("Sushi — 93.8% ")


def test_result_lines_mark_the_single_leader_with_a_trophy():
    lines = result_lines(poll_with_votes(Pizza=1, Sushi=3, Salad=2))

    assert lines[1].endswith(" 🏆")
    assert "🏆" not in lines[0]
    assert "🏆" not in lines[2]


def test_result_lines_give_every_tied_leader_a_trophy():
    assert result_lines(poll_with_votes(Pizza=2, Sushi=1, Salad=2)) == [
        "Pizza — 40.0% (2 votes) 🏆",
        "Sushi — 20.0% (1 vote)",
        "Salad — 40.0% (2 votes) 🏆",
    ]
    assert result_lines(poll_with_votes(Pizza=1, Sushi=1, Salad=1)) == [
        "Pizza — 33.3% (1 vote) 🏆",
        "Sushi — 33.3% (1 vote) 🏆",
        "Salad — 33.3% (1 vote) 🏆",
    ]


def test_result_lines_have_no_trophy_when_nobody_voted():
    assert all("🏆" not in line for line in result_lines(make_poll()))


def test_result_lines_leave_the_poll_unchanged():
    poll = poll_with_votes(Pizza=2, Sushi=1)
    before = deepcopy(poll)

    result_lines(poll)

    assert poll == before
