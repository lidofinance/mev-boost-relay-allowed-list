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


def test_recover_erc20_dai(whitelist, stranger, dai_token, helpers):
    agent_dai_before = dai_token.balanceOf(lido_dao_agent_address)
    dai_amount = 1 * 10**18

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
    ), "Agent DAI balance hasn't increased properly"


def test_recover_erc20_usdt(whitelist, stranger, usdt_token, helpers):
    """USDT transfer() implementation lack return value, thus checking the safe transfer"""
    agent_usdt_before = usdt_token.balanceOf(lido_dao_agent_address)
    usdt_amount = 300 * 10**6

    helpers.fund_with_usdt(whitelist, usdt_amount)
    receipt = whitelist.recover_erc20(usdt_token.address, usdt_amount, sender=stranger)
    assert_single_event(
        receipt,
        whitelist.ERC20Recovered,
        {"requested_by": stranger, "token": usdt_token.address, "amount": usdt_amount},
    )

    assert usdt_token.balanceOf(whitelist.address) == 0, "some USDT left on the contract"
    assert (
        usdt_token.balanceOf(lido_dao_agent_address) == agent_usdt_before + usdt_amount
    ), "Agent USDT balance hasn't increased properly"


def test_recover_erc20_failure_due_amount(whitelist, stranger, dai_token, helpers):
    dai_amount = 10**18

    helpers.fund_with_dai(whitelist, dai_amount)
    with reverts("Dai/insufficient-balance"):
        whitelist.recover_erc20(dai_token.address, dai_amount + 1, sender=stranger)


def test_recover_erc20_failure_due_zero_token_address(whitelist, stranger, dai_token, helpers):
    dai_amount = 10**18

    helpers.fund_with_dai(whitelist, dai_amount)

    with reverts("zero token address"):
        whitelist.recover_erc20(ZERO_ADDRESS, dai_amount, sender=stranger)
