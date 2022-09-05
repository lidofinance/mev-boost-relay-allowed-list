# @version 0.3.6
# @title MEV Boost Relay Whitelist
# @notice Storage of the whitelisted MEB-Boost relays.
# @license MIT
# @author Lido <info@lido.fi>
# @dev Relay data modification is supposed to be done by remove and add,
#      to reduce the number of lines of code of the contract.


# The relay was added
event RelayAdded:
    uri_hash: indexed(String[MAX_STRING_LENGTH])
    relay: Relay

# The relay was removed
event RelayRemoved:
    uri_hash: indexed(String[MAX_STRING_LENGTH])
    uri: String[MAX_STRING_LENGTH]

# Emitted every time the whitelist is changed
event RelaysUpdated:
    whitelist_version: indexed(uint256)

# Emitted when contract manager is set or dismissed
# When dismissed the address is zero
event ManagerChanged:
    new_manager: indexed(address)


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


# Just some sane limit
MAX_STRING_LENGTH: constant(uint256) = 1024

# Just some sane limit
MAX_NUM_RELAYS: constant(uint256) = 40

# Can change the relays and change the manager
LIDO_DAO_AGENT: immutable(address)

# Manager can change the whitelist as well as Lido DAO Agent
# Can be assigned and dismissed by Lido DAO Agent
# Zero manager means manager is not assigned
manager: address

# List of the relays. Order might be arbitrary
relays: DynArray[Relay, MAX_NUM_RELAYS]

# Incremented each time the list of relays is modified.
# Introduced to facilitate easy versioning of whitelist
whitelist_version: uint256


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
def get_manager() -> address:
    """Return the address of manager of the contract"""
    return self.manager


@view
@external
def get_relays() -> DynArray[Relay, MAX_NUM_RELAYS]:
    """Return list of the whitelisted relays"""
    return self.relays


@view
@external
def get_relay_by_uri(relay_uri: String[MAX_STRING_LENGTH]) -> Relay:
    """Find whitelisted relay by URI. Revert if no relay found"""
    index: uint256 = self._find_relay(relay_uri)
    assert index != max_value(uint256), "no relay with the URI"
    return self.relays[index]


@view
@external
def get_whitelist_version() -> uint256:
    """
    @notice Return version of the whitelist
    @dev The version is incremented on every relays list update
    """
    return self.whitelist_version


@external
def add_relay(
    uri: String[MAX_STRING_LENGTH],
    operator: String[MAX_STRING_LENGTH],
    is_mandatory: bool,
    description: String[MAX_STRING_LENGTH]
):
    """
    @notice Add relay to the whitelist. Can be executed only by Lido DAO Agent or
            manager. Reverts if relay with the URI is already whitelisted.
    @param uri URI of the relay. Must be non-empty
    @param operator Name of the relay operator
    @param is_mandatory If the relay is mandatory for usage for Lido Node Operator
    @param description Description of the relay in free format
    """
    self._check_sender_is_lido_agent_or_manager()
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
    self._bump_version()

    log RelayAdded(uri, relay)


@external
def remove_relay(uri: String[MAX_STRING_LENGTH]):
    """
    @notice Add relay to the whitelist. Can be executed only by the Lido DAO Agent or
            manager. Reverts if there is no such relay.
            Order of the relays might get changed.
    @param uri URI of the relay. Must be non-empty
    """
    self._check_sender_is_lido_agent_or_manager()
    assert uri != empty(String[MAX_STRING_LENGTH]), "relay URI must not be empty"

    num_relays: uint256 = len(self.relays)
    index: uint256 = self._find_relay(uri)
    assert index < num_relays, "no relay with the URI"

    if index != (num_relays - 1):
        self.relays[index] = self.relays[num_relays - 1]

    self.relays.pop()
    self._bump_version()

    log RelayRemoved(uri, uri)


@external
def set_manager(manager: address):
    """
    @notice Set contract manager. Zero address is not allowed.
            Can update manager if it is already set.
            Can be called only by Lido DAO Agent.
    @param manager Address of the new manager
    """
    self._check_sender_is_lido_agent()
    assert manager != empty(address), "zero manager address"
    assert manager != self.manager, "same manager"

    self.manager = manager
    log ManagerChanged(manager)


@external
def dismiss_manager():
    """
    @notice Dismiss the manager. Reverts if no manager set.
            Can be called only by Lido DAO Agent.
    """
    self._check_sender_is_lido_agent()
    assert self.manager != empty(address), "no manager set"

    self.manager = empty(address)
    log ManagerChanged(empty(address))


@external
def recover_erc20(token: address, amount: uint256):
    """
    @notice Transfer ERC20 tokens from the contract's balance to the DAO treasury.
    """
    assert token != empty(address), "zero token address"
    if amount > 0:
        self._safe_erc20_transfer(token, LIDO_DAO_AGENT, amount)
        log ERC20Recovered(msg.sender, token, amount)


@external
def __default__():
    """Prevent receiving ether"""
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
def _check_sender_is_lido_agent_or_manager():
    assert (
        msg.sender == LIDO_DAO_AGENT
        or
        (msg.sender == self.manager and msg.sender != empty(address))
    ), "msg.sender not lido agent or manager"


@internal
def _check_sender_is_lido_agent():
    assert msg.sender == LIDO_DAO_AGENT, "msg.sender not lido agent"


@internal
def _bump_version():
   new_version: uint256 = self.whitelist_version + 1
   self.whitelist_version = new_version
   log RelaysUpdated(new_version)


@internal
def _safe_erc20_transfer(token: address, to: address, amount: uint256):
    response: Bytes[32] = raw_call(
        token,
        concat(
            method_id("transfer(address,uint256)"),
            convert(to, bytes32),
            convert(amount, bytes32)
        ),
        max_outsize=32
    )
    if len(response) > 0:
        assert convert(response, bool), "erc20 transfer failed"
