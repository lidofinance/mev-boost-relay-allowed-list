from typing import NamedTuple
import pytest
from ape import accounts, project
from ape.contracts.base import ContractEvent
from ape.types import ContractLog, AddressType
from ape.api.transactions import ReceiptAPI

from config import dai_token_address


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


@pytest.fixture()
def whitelist(deployer):
    return project.MEVBoostRelayWhitelist.deploy(sender=deployer)


@pytest.fixture(scope="module")
def dai_token():
    return project.Dai.at(dai_token_address)


def assert_single_event(receipt: ReceiptAPI, event: ContractEvent, args: dict):
    logs: list[ContractLog] = list(event.from_receipt(receipt))
    assert len(logs) == 1, f"event '{event.name}' must exist and be single"
    assert logs[0].event_arguments == args, f"incorrect event '{event.name}' arguments"


class Helpers:
    dai_token = None

    @staticmethod
    def fund_with_dai(addr, amount):
        dai_holder = accounts["0x075e72a5edf65f0a5f44699c7654c1a76941ddc8"]
        Helpers.dai_token.transfer(addr, amount, sender=dai_holder)


@pytest.fixture(scope="module")
def helpers(dai_token):
    Helpers.dai_token = dai_token
    return Helpers
