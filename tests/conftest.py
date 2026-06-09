import sys
import os

from evm_trace.geth import TraceFrame

# anvil (foundry >= 1.0) omits gasCost in debug_traceTransaction struct logs,
# while evm-trace of the ape 0.6 era requires it; default it to keep revert
# message extraction working
TraceFrame.model_fields["gas_cost"].default = 0
TraceFrame.model_rebuild(force=True)

from ape.utils.abi import LogInputABICollection

# ape 0.6 zips event arg values (decoded topics-first) with ABI types in
# declaration order, mis-typing events whose indexed args are not a prefix
# (e.g. ERC20Recovered); return args in ABI order to realign the zip
_original_decode = LogInputABICollection.decode

def _decode_in_abi_order(self, topics, data, use_hex_on_fail=False):
    decoded = _original_decode(self, topics, data, use_hex_on_fail=use_hex_on_fail)
    order = [i.name for i in self.abi.inputs]
    return {name: decoded[name] for name in order if name in decoded}

LogInputABICollection.decode = _decode_in_abi_order


from typing import NamedTuple
import pytest
from ape import accounts, project
from ape.contracts.base import ContractEvent
from ape.types import ContractLog, AddressType
from ape.api.transactions import ReceiptAPI

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import (
    LIDO_DAO_AGENT_ADDRESS,
    LIDO_EASY_TRACK_SCRIPT_EXECUTOR_ADDRESS,
    DAI_TOKEN_ADDRESS,
    DAI_TOKEN_HOLDER_ADDRESS,
    USDT_TOKEN_ADDRESS,
    USDT_TOKEN_HOLDER_ADDRESS,
)


suppress_3rd_party_deprecation_warnings = pytest.mark.filterwarnings("ignore:abi.decode_single().+is.+deprecated")

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
    return accounts[LIDO_DAO_AGENT_ADDRESS]


@pytest.fixture(scope="module")
def lido_easy_track_script_executor():
    return accounts[LIDO_EASY_TRACK_SCRIPT_EXECUTOR_ADDRESS]


@pytest.fixture()
def allowed_list(deployer):
    return project.MEVBoostRelayAllowedList.deploy(LIDO_DAO_AGENT_ADDRESS, sender=deployer)


@pytest.fixture(scope="module")
def dai_token():
    return project.Dai.at(DAI_TOKEN_ADDRESS)


@pytest.fixture(scope="module")
def usdt_token():
    return project.Usdt.at(USDT_TOKEN_ADDRESS)


def assert_single_event(receipt: ReceiptAPI, event: ContractEvent, args: dict):
    logs: list[ContractLog] = list(event.from_receipt(receipt))
    assert len(logs) == 1, f"event '{event.name}' must exist and be single"
    expected = {k: list(v) if isinstance(v, tuple) else v for k, v in args.items()}
    assert logs[0].event_arguments == expected, f"incorrect event '{event.name}' arguments"


class Helpers:
    dai_token = None
    usdt_token = None

    @staticmethod
    def fund_with_dai(address, amount):
        dai_holder = accounts[DAI_TOKEN_HOLDER_ADDRESS]
        assert Helpers.dai_token.balanceOf(dai_holder) >= amount
        Helpers.dai_token.transfer(address, amount, sender=dai_holder)

    @staticmethod
    def fund_with_usdt(address, amount):
        usdt_holder = accounts[USDT_TOKEN_HOLDER_ADDRESS]
        assert Helpers.usdt_token.balanceOf(usdt_holder) >= amount
        Helpers.usdt_token.transfer(address, amount, sender=usdt_holder)


@pytest.fixture(scope="module")
def helpers(dai_token, usdt_token):
    Helpers.dai_token = dai_token
    Helpers.usdt_token = usdt_token
    return Helpers
