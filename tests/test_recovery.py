"""
Tests for MEV Boost Relays Whitelist
"""

from ape import reverts
from ape.managers.converters import HexConverter
from conftest import (
    assert_single_event,
    suppress_3rd_party_deprecation_warnings,
    Relay,
    ZERO_ADDRESS,
)
from config import lido_dao_agent_address


def test_recover_erc20(whitelist, stranger, dai_token, helpers):
    agent_dai_before = dai_token.balanceOf(lido_dao_agent_address)
    dai_amount = 10**18

    helpers.fund_with_dai(whitelist, dai_amount)
    receipt = whitelist.recover_erc20(dai_token.address, dai_amount, sender=stranger)
    assert_single_event(
        receipt,
        whitelist.ERC20Recovered,
        {"requested_by": stranger, "token": dai_token.address, "amount": dai_amount},
    )

    assert dai_token.balanceOf(whitelist.address) == 0, "some Dai left on the contract"
    assert (
        dai_token.balanceOf(lido_dao_agent_address) == agent_dai_before + dai_amount
    ), "some Dai left on the contract"


def test_recover_erc20_failure_due_amount(whitelist, stranger, dai_token, helpers):
    agent_dai_before = dai_token.balanceOf(lido_dao_agent_address)
    dai_amount = 10**18

    helpers.fund_with_dai(whitelist, dai_amount)
    with reverts("Dai/insufficient-balance"):
        whitelist.recover_erc20(dai_token.address, dai_amount + 1, sender=stranger)


def test_recover_erc20_failure_due_zero_token_address(whitelist, stranger, dai_token, helpers):
    agent_dai_before = dai_token.balanceOf(lido_dao_agent_address)
    dai_amount = 10**18

    helpers.fund_with_dai(whitelist, dai_amount)

    with reverts():
        whitelist.recover_erc20(ZERO_ADDRESS, dai_amount, sender=stranger)
