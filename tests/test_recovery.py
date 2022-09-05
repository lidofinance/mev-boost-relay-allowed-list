"""
Tests for MEV Boost Relays Whitelist
"""

from ape import reverts
from conftest import (
    assert_single_event,
    ZERO_ADDRESS,
)
from config import lido_dao_agent_address


def test_stranger_cannot_recover(whitelist, stranger, dai_token, helpers):
    dai_amount = 10**18
    helpers.fund_with_dai(whitelist, dai_amount)

    with reverts("msg.sender not owner"):
        whitelist.recover_erc20(dai_token, dai_amount, stranger, sender=stranger)


def test_manager_cannot_recover(whitelist, stranger, lido_agent, dai_token, helpers):
    manager = stranger
    whitelist.set_manager(manager, sender=lido_agent)
    assert whitelist.get_manager() == manager, "incorrect manager after set_manager call"

    dai_amount = 10**18
    helpers.fund_with_dai(whitelist, dai_amount)
    with reverts("msg.sender not owner"):
        whitelist.recover_erc20(dai_token, dai_amount, manager, sender=manager)


def test_zero_erc20_recovery_recipient(whitelist, dai_token, lido_agent):
    dai_amount = 10**18
    with reverts("zero recipient address"):
        whitelist.recover_erc20(dai_token, dai_amount, ZERO_ADDRESS, sender=lido_agent)


def test_recover_erc20_dai(whitelist, dai_token, helpers, lido_agent):
    agent_dai_before = dai_token.balanceOf(lido_dao_agent_address)
    dai_amount = 1 * 10**18

    helpers.fund_with_dai(whitelist, dai_amount)
    receipt = whitelist.recover_erc20(
        dai_token.address, dai_amount, lido_dao_agent_address, sender=lido_agent
    )
    assert_single_event(
        receipt,
        whitelist.ERC20Recovered,
        {
            "requested_by": lido_agent,
            "token": dai_token,
            "amount": dai_amount,
            "recipient": lido_dao_agent_address,
        },
    )

    assert dai_token.balanceOf(whitelist.address) == 0, "some Dai left on the contract"
    assert (
        dai_token.balanceOf(lido_dao_agent_address) == agent_dai_before + dai_amount
    ), "Agent DAI balance hasn't increased properly"


def test_recover_erc20_usdt(whitelist, usdt_token, helpers, lido_agent):
    """USDT transfer() implementation lack return value, thus checking the safe transfer"""
    agent_usdt_before = usdt_token.balanceOf(lido_dao_agent_address)
    usdt_amount = 300 * 10**6

    helpers.fund_with_usdt(whitelist, usdt_amount)
    receipt = whitelist.recover_erc20(
        usdt_token.address, usdt_amount, lido_dao_agent_address, sender=lido_agent
    )
    assert_single_event(
        receipt,
        whitelist.ERC20Recovered,
        {
            "requested_by": lido_agent,
            "token": usdt_token,
            "amount": usdt_amount,
            "recipient": lido_dao_agent_address,
        },
    )

    assert usdt_token.balanceOf(whitelist.address) == 0, "some USDT left on the contract"
    assert (
        usdt_token.balanceOf(lido_dao_agent_address) == agent_usdt_before + usdt_amount
    ), "Agent USDT balance hasn't increased properly"


def test_recover_erc20_failure_due_amount(whitelist, stranger, dai_token, helpers, lido_agent):
    dai_amount = 10**18

    helpers.fund_with_dai(whitelist, dai_amount)
    with reverts("Dai/insufficient-balance"):
        whitelist.recover_erc20(dai_token.address, dai_amount + 1, stranger, sender=lido_agent)


def test_recover_erc20_failure_due_zero_token_address(whitelist, stranger, helpers, lido_agent):
    dai_amount = 10**18
    helpers.fund_with_dai(whitelist, dai_amount)

    with reverts("zero token address"):
        whitelist.recover_erc20(ZERO_ADDRESS, dai_amount, stranger, sender=lido_agent)
