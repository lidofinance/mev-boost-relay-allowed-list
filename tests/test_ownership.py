"""
Tests for MEV Boost Relays Whitelist ownership management
"""

from ape import reverts
from conftest import (
    assert_single_event,
    ZERO_ADDRESS,
)


def test_stranger_cannot_set_or_dismiss_manager(
    whitelist, stranger, lido_easy_track_script_executor
):
    with reverts("msg.sender not lido agent"):
        whitelist.set_manager(lido_easy_track_script_executor, sender=stranger)


def test_manager_cannot_update_or_dismiss_manager(
    whitelist, lido_agent, lido_easy_track_script_executor, stranger
):
    whitelist.set_manager(lido_easy_track_script_executor, sender=lido_agent)

    with reverts("msg.sender not lido agent"):
        whitelist.set_manager(stranger, sender=lido_easy_track_script_executor)

    with reverts("msg.sender not lido agent"):
        whitelist.dismiss_manager(sender=lido_easy_track_script_executor)

    whitelist.dismiss_manager(sender=lido_agent)


def test_set_manager(whitelist, lido_agent, stranger, lido_easy_track_script_executor):
    receipt = whitelist.set_manager(lido_easy_track_script_executor, sender=lido_agent)
    assert_single_event(
        receipt, whitelist.ManagerChanged, {"new_manager": lido_easy_track_script_executor}
    )
    assert (
        whitelist.get_manager() == lido_easy_track_script_executor
    ), "incorrect manager after set_manager call"

    receipt = whitelist.set_manager(stranger, sender=lido_agent)
    assert_single_event(receipt, whitelist.ManagerChanged, {"new_manager": stranger})
    assert (
        whitelist.get_manager() == stranger
    ), "incorrect manager after the second set_manager call"


def test_set_same_manager(whitelist, lido_agent, lido_easy_track_script_executor):
    receipt = whitelist.set_manager(lido_easy_track_script_executor, sender=lido_agent)
    assert_single_event(
        receipt, whitelist.ManagerChanged, {"new_manager": lido_easy_track_script_executor}
    )
    assert (
        whitelist.get_manager() == lido_easy_track_script_executor
    ), "incorrect manager after set_manager call"

    with reverts("same manager"):
        receipt = whitelist.set_manager(lido_easy_track_script_executor, sender=lido_agent)


def test_set_zero_manager(whitelist, lido_agent):
    with reverts("zero manager address"):
        whitelist.set_manager(ZERO_ADDRESS, sender=lido_agent)


def test_dismiss_manager(whitelist, lido_agent, lido_easy_track_script_executor):
    receipt = whitelist.set_manager(lido_easy_track_script_executor, sender=lido_agent)
    assert_single_event(
        receipt, whitelist.ManagerChanged, {"new_manager": lido_easy_track_script_executor}
    )
    assert (
        whitelist.get_manager() == lido_easy_track_script_executor
    ), "incorrect manager after set_manager call"

    receipt = whitelist.dismiss_manager(sender=lido_agent)
    assert_single_event(receipt, whitelist.ManagerChanged, {"new_manager": ZERO_ADDRESS})
    assert whitelist.get_manager() == ZERO_ADDRESS, "non-zero manager after dismiss"


def test_dismiss_manager_when_no_manager_set(whitelist, lido_agent):
    assert whitelist.get_manager() == ZERO_ADDRESS
    with reverts("no manager set"):
        whitelist.dismiss_manager(sender=lido_agent)
