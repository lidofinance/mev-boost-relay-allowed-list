"""
Tests for MEV Boost Relays Allowed List ownership management
"""

from ape import reverts
from conftest import (
    assert_single_event,
    ZERO_ADDRESS,
)


def test_owner_can_change_owner(allowed_list, lido_agent, stranger):
    receipt = allowed_list.change_owner(stranger, sender=lido_agent)
    assert_single_event(receipt, allowed_list.OwnerChanged, {"new_owner": stranger})
    assert allowed_list.get_owner() == stranger, "incorrect owner after set_owner call"


def test_stranger_cannot_change_owner(allowed_list, stranger):
    assert allowed_list.get_owner() != stranger
    with reverts("msg.sender not owner"):
        allowed_list.change_owner(stranger, sender=stranger)


def test_manager_cannot_change_owner(allowed_list, lido_agent, stranger):
    manager = stranger
    allowed_list.set_manager(manager, sender=lido_agent)
    assert allowed_list.get_manager() == manager
    assert allowed_list.get_owner() != manager

    with reverts("msg.sender not owner"):
        allowed_list.change_owner(manager, sender=manager)


def test_cannot_set_incorrect_owner(allowed_list, lido_agent):
    with reverts("zero owner address"):
        allowed_list.change_owner(ZERO_ADDRESS, sender=lido_agent)

    with reverts("same owner"):
        allowed_list.change_owner(lido_agent, sender=lido_agent)


def test_stranger_cannot_set_or_dismiss_manager(
    allowed_list, stranger, lido_easy_track_script_executor
):
    with reverts("msg.sender not owner"):
        allowed_list.set_manager(lido_easy_track_script_executor, sender=stranger)

    with reverts("msg.sender not owner"):
        allowed_list.dismiss_manager(sender=stranger)


def test_manager_cannot_update_or_dismiss_manager(
    allowed_list, lido_agent, lido_easy_track_script_executor, stranger
):
    allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)

    with reverts("msg.sender not owner"):
        allowed_list.set_manager(stranger, sender=lido_easy_track_script_executor)

    with reverts("msg.sender not owner"):
        allowed_list.dismiss_manager(sender=lido_easy_track_script_executor)

    allowed_list.dismiss_manager(sender=lido_agent)


def test_set_manager(allowed_list, lido_agent, stranger, lido_easy_track_script_executor):
    receipt = allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)
    assert_single_event(
        receipt, allowed_list.ManagerChanged, {"new_manager": lido_easy_track_script_executor}
    )
    assert (
        allowed_list.get_manager() == lido_easy_track_script_executor
    ), "incorrect manager after set_manager call"

    receipt = allowed_list.set_manager(stranger, sender=lido_agent)
    assert_single_event(receipt, allowed_list.ManagerChanged, {"new_manager": stranger})
    assert (
        allowed_list.get_manager() == stranger
    ), "incorrect manager after the second set_manager call"


def test_set_same_manager(allowed_list, lido_agent, lido_easy_track_script_executor):
    receipt = allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)
    assert_single_event(
        receipt, allowed_list.ManagerChanged, {"new_manager": lido_easy_track_script_executor}
    )
    assert (
        allowed_list.get_manager() == lido_easy_track_script_executor
    ), "incorrect manager after set_manager call"

    with reverts("same manager"):
        receipt = allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)


def test_set_zero_manager(allowed_list, lido_agent):
    with reverts("zero manager address"):
        allowed_list.set_manager(ZERO_ADDRESS, sender=lido_agent)


def test_dismiss_manager(allowed_list, lido_agent, lido_easy_track_script_executor):
    receipt = allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)
    assert_single_event(
        receipt, allowed_list.ManagerChanged, {"new_manager": lido_easy_track_script_executor}
    )
    assert (
        allowed_list.get_manager() == lido_easy_track_script_executor
    ), "incorrect manager after set_manager call"

    receipt = allowed_list.dismiss_manager(sender=lido_agent)
    assert_single_event(receipt, allowed_list.ManagerChanged, {"new_manager": ZERO_ADDRESS})
    assert allowed_list.get_manager() == ZERO_ADDRESS, "non-zero manager after dismiss"


def test_dismiss_manager_when_no_manager_set(allowed_list, lido_agent):
    assert allowed_list.get_manager() == ZERO_ADDRESS
    with reverts("no manager set"):
        allowed_list.dismiss_manager(sender=lido_agent)
