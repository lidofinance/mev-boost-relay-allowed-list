"""
Ownership tests for the MEV Boost Relays Whitelist contract
"""

from ape import reverts
from conftest import suppress_3rd_party_deprecation_warnings, ZERO_ADDRESS, assert_single_event


def test_initial_owner(whitelist, deployer):
    assert whitelist.owner() == deployer


@suppress_3rd_party_deprecation_warnings
def test_stranger_cant_change_owner(whitelist, deployer, stranger):
    assert whitelist.owner() == deployer
    with reverts("not owner"):
        whitelist.change_owner(stranger, sender=stranger)


def test_owner_can_change_owner(whitelist, deployer, stranger):
    assert whitelist.owner() == deployer
    receipt = whitelist.change_owner(stranger, sender=deployer)
    assert whitelist.owner() == stranger

    assert_single_event(
        receipt,
        whitelist.OwnerChanged,
        {
            "previous_owner": deployer,
            "new_owner": stranger,
        },
    )


@suppress_3rd_party_deprecation_warnings
def test_cant_set_same_owner(whitelist, deployer):
    assert whitelist.owner() == deployer
    with reverts("same owner"):
        whitelist.change_owner(deployer, sender=deployer)


@suppress_3rd_party_deprecation_warnings
def test_zero_address_cant_be_owner(whitelist, deployer):
    with reverts("zero owner"):
        whitelist.change_owner(ZERO_ADDRESS, sender=deployer)


# TODO: test other function owners
