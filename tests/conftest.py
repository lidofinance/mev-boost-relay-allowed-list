import sys
import os
from typing import NamedTuple
import pytest
from ape import accounts, project
from ape.contracts.base import ContractEvent
from ape.types import ContractLog, AddressType
from ape.api.transactions import ReceiptAPI

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    lido_dao_agent_address,
    lido_easy_track_script_executor_address,
    dai_token_address,
    dai_token_holder_address,
    usdt_token_address,
    usdt_token_holder_address,
)


suppress_3rd_party_deprecation_warnings = pytest.mark.filterwarnings(
    "ignore:abi.decode_single().+is.+deprecated"
)

ZERO_ADDRESS: AddressType = "0x0000000000000000000000000000000000000000"


class Relay(NamedTuple):
    uri: str
    operator: str
    is_mandatory: bool
    description: str


@pytest.fixture(scope="module")
def deployer():
    return accounts.test_accounts[0]


@pytest.fixture(scope="module")
def stranger():
    return accounts.test_accounts[9]


@pytest.fixture(scope="module")
def lido_agent():
    return accounts[lido_dao_agent_address]


@pytest.fixture(scope="module")
def lido_easy_track_script_executor():
    return accounts[lido_easy_track_script_executor_address]


@pytest.fixture()
def allowed_list(deployer):
    return project.MEVBoostRelayAllowedList.deploy(lido_dao_agent_address, sender=deployer)


@pytest.fixture(scope="module")
def dai_token():
    return project.Dai.at(dai_token_address)


@pytest.fixture(scope="module")
def usdt_token():
    return project.Usdt.at(usdt_token_address)


def assert_single_event(receipt: ReceiptAPI, event: ContractEvent, args: dict):
    logs: list[ContractLog] = list(event.from_receipt(receipt))
    assert len(logs) == 1, f"event '{event.name}' must exist and be single"
    assert logs[0].event_arguments == args, f"incorrect event '{event.name}' arguments"


class Helpers:
    dai_token = None
    usdt_token = None

    @staticmethod
    def fund_with_dai(address, amount):
        dai_holder = accounts[dai_token_holder_address]
        assert Helpers.dai_token.balanceOf(dai_holder) >= amount
        Helpers.dai_token.transfer(address, amount, sender=dai_holder)

    @staticmethod
    def fund_with_usdt(address, amount):
        usdt_holder = accounts[usdt_token_holder_address]
        assert Helpers.usdt_token.balanceOf(usdt_holder) >= amount
        Helpers.usdt_token.transfer(address, amount, sender=usdt_holder)


@pytest.fixture(scope="module")
def helpers(dai_token, usdt_token):
    Helpers.dai_token = dai_token
    Helpers.usdt_token = usdt_token
    return Helpers
