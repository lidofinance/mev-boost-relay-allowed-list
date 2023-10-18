"""
Tests for MEV Boost Relays Allowed List
"""

from ape import reverts, project, accounts
from ape.managers.converters import HexConverter
from conftest import (
    assert_single_event,
    suppress_3rd_party_deprecation_warnings,
    Relay,
    ZERO_ADDRESS,
)


MAX_RELAYS_NUM = 40  # supposed to correspond to the limit in the contract


TEST_RELAY0 = Relay(
    uri="https://0xb124d80a00b80815397b4e7f1f05377ccc83aeeceb6be87963ba3649f1e6efa32ca870a88845917ec3f26a8e2aa25c77@one.mev-boost-relays.test",
    operator="Relay Operator #1",
    is_mandatory=False,
    description="",
)
TEST_RELAY0_URI_HASH = HexConverter().convert(
    "1e269efbae2680fe1299c248b3dd211bc8a56ced30cd68d88812772c346e463b"  # keccak256
)

TEST_RELAY1 = Relay(
    uri="https://0xafa4c6985aa049fb79dd37010438cfebeb0f2bd42b115b89dd678dab0670c1de38da0c4e9138c9290a398ecd9a0b3110@two.mev-boost-relays.test",
    operator="Relay Operator #2",
    is_mandatory=True,
    description="The relay which is optional",
)
TEST_RELAY1_URI_HASH = HexConverter().convert(
    "133b5f68e62a8abe60fb79a49a87e726af05aacf61b295f04ed20851e8975790"  # keccak256
)


def test_zero_lido_agent(deployer):
    with reverts("zero owner address"):
        project.MEVBoostRelayAllowedList.deploy(ZERO_ADDRESS, sender=deployer)


def test_initial_state(allowed_list, lido_agent):
    assert allowed_list.get_relays_amount() == 0
    assert allowed_list.get_allowed_list_version() == 0
    assert allowed_list.get_relays() is None, "must have 0 relays initially"
    assert allowed_list.get_owner() == lido_agent
    assert allowed_list.get_manager() == ZERO_ADDRESS


def test_add_relay(allowed_list, lido_agent):
    receipt = allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    assert_single_event(receipt, allowed_list.RelayAdded, {"relay": TEST_RELAY0, "uri_hash": TEST_RELAY0_URI_HASH})
    assert_single_event(receipt, allowed_list.AllowedListUpdated, {"allowed_list_version": 1})
    relays = allowed_list.get_relays()
    assert relays == list(TEST_RELAY0)
    assert allowed_list.get_allowed_list_version() == 1

    assert allowed_list.get_relay_by_uri(TEST_RELAY0.uri) == TEST_RELAY0
    with reverts("no relay with the URI"):
        allowed_list.get_relay_by_uri(TEST_RELAY1.uri)
    with reverts("no relay with the URI"):
        allowed_list.get_relay_by_uri("")


def test_manager_can_add_relay(allowed_list, lido_agent, lido_easy_track_script_executor):
    with reverts("msg.sender not owner or manager"):
        allowed_list.add_relay(*TEST_RELAY0, sender=lido_easy_track_script_executor)
    allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)

    allowed_list.add_relay(*TEST_RELAY0, sender=lido_easy_track_script_executor)
    assert allowed_list.get_relays() == list(TEST_RELAY0)

    allowed_list.dismiss_manager(sender=lido_agent)
    assert allowed_list.get_manager() == ZERO_ADDRESS

    with reverts("msg.sender not owner or manager"):
        allowed_list.add_relay(*TEST_RELAY0, sender=lido_easy_track_script_executor)


def test_manager_can_remove_relay(allowed_list, lido_agent, lido_easy_track_script_executor):
    receipt = allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    assert_single_event(receipt, allowed_list.AllowedListUpdated, {"allowed_list_version": 1})

    with reverts("msg.sender not owner or manager"):
        allowed_list.remove_relay(TEST_RELAY0.uri, sender=lido_easy_track_script_executor)
    allowed_list.set_manager(lido_easy_track_script_executor, sender=lido_agent)

    receipt = allowed_list.remove_relay(TEST_RELAY0.uri, sender=lido_easy_track_script_executor)
    assert allowed_list.get_relays() == None
    assert_single_event(receipt, allowed_list.AllowedListUpdated, {"allowed_list_version": 2})
    receipt = allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    assert_single_event(receipt, allowed_list.AllowedListUpdated, {"allowed_list_version": 3})

    allowed_list.dismiss_manager(sender=lido_agent)
    assert allowed_list.get_manager() == ZERO_ADDRESS

    with reverts("msg.sender not owner or manager"):
        allowed_list.remove_relay(TEST_RELAY0.uri, sender=lido_easy_track_script_executor)


def test_zero_msg_sender_as_manager(allowed_list):
    assert allowed_list.get_manager() == ZERO_ADDRESS

    with reverts("msg.sender not owner or manager"):
        allowed_list.add_relay(*TEST_RELAY0, sender=accounts[ZERO_ADDRESS])


@suppress_3rd_party_deprecation_warnings
def test_add_relay_with_same_uri(allowed_list, lido_agent):
    allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    with reverts("relay with the URI already exists"):
        allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    assert allowed_list.get_allowed_list_version() == 1


@suppress_3rd_party_deprecation_warnings
def test_add_too_many_relays(allowed_list, lido_agent):
    test_relays = [list(Relay(f"uri #{i}", "", bool(i % 2), "")) for i in range(MAX_RELAYS_NUM)]

    for relay in test_relays:
        allowed_list.add_relay(*relay, sender=lido_agent)

    for actual, expected in zip(allowed_list.get_relays(), test_relays):
        assert list(actual) == expected

    assert allowed_list.get_allowed_list_version() == MAX_RELAYS_NUM

    with reverts():
        allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)


@suppress_3rd_party_deprecation_warnings
def test_add_relay_with_empty_uri(allowed_list, lido_agent):
    with reverts("relay URI must not be empty"):
        allowed_list.add_relay(*Relay("", "", False, ""), sender=lido_agent)


@suppress_3rd_party_deprecation_warnings
def test_remove_relay_with_empty_uri(allowed_list, lido_agent):
    with reverts("relay URI must not be empty"):
        allowed_list.remove_relay("", sender=lido_agent)


@suppress_3rd_party_deprecation_warnings
def test_remove_relay_when_no_such_relays(allowed_list, lido_agent):
    allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    allowed_list.add_relay(*TEST_RELAY1, sender=lido_agent)
    assert allowed_list.get_relay_by_uri(TEST_RELAY0.uri) == TEST_RELAY0
    assert allowed_list.get_relay_by_uri(TEST_RELAY1.uri) == TEST_RELAY1
    with reverts("no relay with the URI"):
        allowed_list.remove_relay("non-presenting uri", sender=lido_agent)


@suppress_3rd_party_deprecation_warnings
def test_remove_relay_when_no_relays(allowed_list, lido_agent):
    with reverts("no relay with the URI"):
        allowed_list.remove_relay(TEST_RELAY0.uri, sender=lido_agent)


def test_remove_single_existing_relay(allowed_list, lido_agent):
    allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    receipt = allowed_list.remove_relay(TEST_RELAY0.uri, sender=lido_agent)
    assert_single_event(
        receipt,
        allowed_list.RelayRemoved,
        {"uri": TEST_RELAY0.uri, "uri_hash": TEST_RELAY0_URI_HASH},
    )
    assert allowed_list.get_allowed_list_version() == 2


def test_remove_first_relay(allowed_list, lido_agent):
    allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    allowed_list.add_relay(*TEST_RELAY1, sender=lido_agent)
    receipt = allowed_list.remove_relay(TEST_RELAY0.uri, sender=lido_agent)
    assert_single_event(
        receipt,
        allowed_list.RelayRemoved,
        {"uri": TEST_RELAY0.uri, "uri_hash": TEST_RELAY0_URI_HASH},
    )
    assert allowed_list.get_relays() == list(TEST_RELAY1)
    assert allowed_list.get_allowed_list_version() == 3


def test_remove_last_relay(allowed_list, lido_agent):
    allowed_list.add_relay(*TEST_RELAY0, sender=lido_agent)
    allowed_list.add_relay(*TEST_RELAY1, sender=lido_agent)
    receipt = allowed_list.remove_relay(TEST_RELAY1.uri, sender=lido_agent)
    assert_single_event(
        receipt,
        allowed_list.RelayRemoved,
        {"uri": TEST_RELAY1.uri, "uri_hash": TEST_RELAY1_URI_HASH},
    )
    assert allowed_list.get_relays() == list(TEST_RELAY0)
    assert allowed_list.get_allowed_list_version() == 3


def test_remove_middle_relay(allowed_list, lido_agent):
    test_relays = [list(Relay(f"uri #{i}", "", bool(i % 2), "")) for i in range(MAX_RELAYS_NUM)]

    for relay in test_relays:
        allowed_list.add_relay(*relay, sender=lido_agent)

    allowed_list.remove_relay("uri #7", sender=lido_agent)
    test_relays[7] = test_relays.pop()

    assert allowed_list.get_relay_by_uri("uri #6") == Relay("uri #6", "", False, "")

    with reverts("no relay with the URI"):
        assert allowed_list.get_relay_by_uri("uri #7")

    assert allowed_list.get_relay_by_uri("uri #8") == Relay("uri #8", "", False, "")

    for actual, expected in zip(allowed_list.get_relays(), test_relays):
        assert list(actual) == expected
    assert allowed_list.get_allowed_list_version() == MAX_RELAYS_NUM + 1


@suppress_3rd_party_deprecation_warnings
def test_stranger_cannot_add_relay(allowed_list, stranger):
    assert allowed_list.get_owner() != stranger

    with reverts("msg.sender not owner or manager"):
        allowed_list.add_relay(*TEST_RELAY0, sender=stranger)


@suppress_3rd_party_deprecation_warnings
def test_stranger_cannot_remove_relay(allowed_list, stranger):
    assert allowed_list.get_owner() != stranger

    with reverts("msg.sender not owner or manager"):
        allowed_list.remove_relay("arbitrary uri", sender=stranger)
