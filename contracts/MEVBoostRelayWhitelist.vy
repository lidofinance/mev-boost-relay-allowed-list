# @version 0.3.6
# @title MEV Boost Relay Whitelist
# @notice Storage of the whitelisted MEB-Boost relays.
# @license GPL-3.0
# @author Lido <info@lido.fi>
# @dev Relay data modification is supposed to be done by remove and add,
#      to reduce the number of lines of code of the contract.

from vyper.interfaces import ERC20

# The relay was added
event RelayAdded:
    uri_hash: indexed(String[MAX_STRING_LENGTH])
    relay: Relay

# The relay was removed
event RelayRemoved:
    uri_hash: indexed(String[MAX_STRING_LENGTH])
    uri: String[MAX_STRING_LENGTH]


# The ERC20 token was transferred from the contract's address to the Lido treasury address
event ERC20Recovered:
    # the address calling `recover_erc20` function
    requested_by: indexed(address)
    # the token address
    token: indexed(address)
    # the token amount
    amount: uint256


struct Relay:
    uri: String[MAX_STRING_LENGTH]
    operator: String[MAX_STRING_LENGTH]
    is_mandatory: bool
    description: String[MAX_STRING_LENGTH]


# Just some sane number
MAX_STRING_LENGTH: constant(uint256) = 1024

# Just some sane number
MAX_NUM_RELAYS: constant(uint256) = 40


LIDO_DAO_AGENT: immutable(address)

relays: public(DynArray[Relay, MAX_NUM_RELAYS])


@external
def __init__(lido_agent: address):
    assert lido_agent != empty(address), "zero lido agent address"
    LIDO_DAO_AGENT = lido_agent


@view
@external
def get_lido_dao_agent() -> address:
    """Return the address of Lido DAO Agent contract"""
    return LIDO_DAO_AGENT


@view
@external
def get_relays_amount() -> uint256:
    """
    @notice Return number of the whitelisted relays
    @return The number of the whitelisted relays
    """
    return len(self.relays)


@view
@external
def get_relays() -> DynArray[Relay, MAX_NUM_RELAYS]:
    """Return list of the whitelisted relays"""
    return self.relays


@external
def add_relay(
    uri: String[MAX_STRING_LENGTH],
    operator: String[MAX_STRING_LENGTH],
    is_mandatory: bool,
    description: String[MAX_STRING_LENGTH]
):
    """
    @notice Add relay to the whitelist. Can be executed only by the Lido Agent.
            Reverts if relay with the URI is already whitelisted.
    @param uri URI of the relay. Must be non-empty
    @param operator Name of the relay operator
    @param is_mandatory If the relay is mandatory for usage for Lido Node Operator
    @param description Description of the relay in free format
    """
    self._check_sender_is_lido_agent()
    assert uri != empty(String[MAX_STRING_LENGTH]), "relay URI must not be empty"

    index: uint256 = self._find_relay(uri)
    assert index == max_value(uint256), "relay with the URI already exists"

    relay: Relay = Relay({
        uri: uri,
        operator: operator,
        is_mandatory: is_mandatory,
        description: description,
    })
    self.relays.append(relay)

    log RelayAdded(uri, relay)


@external
def remove_relay(uri: String[MAX_STRING_LENGTH]):
    """
    @notice Add relay to the whitelist. Can be executed only by the Lido Agent.
            Reverts if there is no such relay. Order of the relays might get changed.
    @param uri URI of the relay. Must be non-empty
    """
    self._check_sender_is_lido_agent()
    assert uri != empty(String[MAX_STRING_LENGTH]), "relay URI must not be empty"

    num_relays: uint256 = len(self.relays)
    index: uint256 = self._find_relay(uri)
    assert index < num_relays, "no relay with the URI"

    if index != (num_relays - 1):
        self.relays[index] = self.relays[num_relays - 1]

    self.relays.pop()

    log RelayRemoved(uri, uri)


@external
def recover_erc20(_token: address, _amount: uint256):
    """
    @notice Transfers ERC20 tokens from the contract's balance to the DAO treasury.
    """
    ERC20(_token).transfer(LIDO_DAO_AGENT, _amount)
    log ERC20Recovered(msg.sender, _token, _amount)


@external
def __default__():
    """Prevents receiving ether"""
    raise


@view
@internal
def _find_relay(uri: String[MAX_STRING_LENGTH]) -> uint256:
    index: uint256 = max_value(uint256)
    i: uint256 = 0
    for r in self.relays:
        if r.uri == uri:
            index = i
            break
        i = i + 1
    return index


@internal
def _check_sender_is_lido_agent():
    assert msg.sender == LIDO_DAO_AGENT, "not lido agent"
