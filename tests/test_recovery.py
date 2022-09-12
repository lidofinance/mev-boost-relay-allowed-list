"""
Tests for MEV Boost Relays Allowed List
"""

from ape import reverts
from conftest import (
    assert_single_event,
    ZERO_ADDRESS,
)


def test_stranger_cannot_recover(allowed_list, stranger, dai_token, helpers):
    dai_amount = 10**18
    helpers.fund_with_dai(allowed_list, dai_amount)

    with reverts("msg.sender not owner"):
        allowed_list.recover_erc20(dai_token, dai_amount, stranger, sender=stranger)


def test_manager_cannot_recover(allowed_list, stranger, lido_agent, dai_token, helpers):
    manager = stranger
    allowed_list.set_manager(manager, sender=lido_agent)
    assert allowed_list.get_manager() == manager, "incorrect manager after set_manager call"

    dai_amount = 10**18
    helpers.fund_with_dai(allowed_list, dai_amount)
    with reverts("msg.sender not owner"):
        allowed_list.recover_erc20(dai_token, dai_amount, manager, sender=manager)


def test_zero_erc20_recovery_recipient(allowed_list, dai_token, lido_agent):
    dai_amount = 10**18
    with reverts("zero recipient address"):
        allowed_list.recover_erc20(dai_token, dai_amount, ZERO_ADDRESS, sender=lido_agent)


def test_recover_erc20_dai(allowed_list, dai_token, helpers, lido_agent):
    agent_dai_before = dai_token.balanceOf(lido_agent)
    dai_amount = 1 * 10**18

    helpers.fund_with_dai(allowed_list, dai_amount)
    receipt = allowed_list.recover_erc20(dai_token, dai_amount, lido_agent, sender=lido_agent)
    assert_single_event(
        receipt,
        allowed_list.ERC20Recovered,
        {
            "token": dai_token,
            "amount": dai_amount,
            "recipient": lido_agent,
        },
    )

    assert dai_token.balanceOf(allowed_list) == 0, "some Dai left on the contract"
    assert (
        dai_token.balanceOf(lido_agent) == agent_dai_before + dai_amount
    ), "Agent DAI balance hasn't increased properly"


def test_recover_erc20_usdt(allowed_list, usdt_token, helpers, lido_agent):
    """USDT transfer() implementation lack return value, thus checking the safe transfer"""
    agent_usdt_before = usdt_token.balanceOf(lido_agent)
    usdt_amount = 300 * 10**6

    helpers.fund_with_usdt(allowed_list, usdt_amount)
    receipt = allowed_list.recover_erc20(usdt_token, usdt_amount, lido_agent, sender=lido_agent)
    assert_single_event(
        receipt,
        allowed_list.ERC20Recovered,
        {
            "token": usdt_token,
            "amount": usdt_amount,
            "recipient": lido_agent,
        },
    )

    assert usdt_token.balanceOf(allowed_list) == 0, "some USDT left on the contract"
    assert (
        usdt_token.balanceOf(lido_agent) == agent_usdt_before + usdt_amount
    ), "Agent USDT balance hasn't increased properly"


def test_recover_erc20_failure_due_amount(allowed_list, stranger, dai_token, helpers, lido_agent):
    dai_amount = 10**18

    helpers.fund_with_dai(allowed_list, dai_amount)
    with reverts("Dai/insufficient-balance"):
        allowed_list.recover_erc20(dai_token, dai_amount + 1, stranger, sender=lido_agent)


def test_recover_erc20_failure_due_zero_token_address(allowed_list, stranger, helpers, lido_agent):
    dai_amount = 10**18
    helpers.fund_with_dai(allowed_list, dai_amount)

    with reverts("zero token address"):
        allowed_list.recover_erc20(ZERO_ADDRESS, dai_amount, stranger, sender=lido_agent)


def test_recover_erc20_with_incorrect_eoa_token_address(allowed_list, stranger, lido_agent):
    eoa = stranger
    with reverts("eoa token address"):
        allowed_list.recover_erc20(eoa, 10**18, stranger, sender=lido_agent)


def test_recover_erc20_with_incorrect_non_token_token_address(allowed_list, stranger, lido_agent):
    non_token_contract = allowed_list.address

    with reverts():
        allowed_list.recover_erc20(non_token_contract, 10**18, stranger, sender=lido_agent)
