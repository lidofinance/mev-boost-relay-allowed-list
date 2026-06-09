# MEV-Boost relay allowed list

MEV-Boost relay allowed list is a simple contract storing a list of relays that have been approved by DAO for use in [MEV-Boost](https://github.com/flashbots/mev-boost). The data from the contract are used to generate a configuration file that contains a list of relays that should be connected to.

MEVBoostRelaysWhitelist contract documentation is in [docs/MEVBoostRelayAllowedList.md](./docs/MEVBoostRelayAllowedList.md).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) >= 0.5
- [foundry](https://getfoundry.sh/) (anvil is used as the fork provider)

## Setup

```shell
uv sync
export RPC_URL=<your mainnet rpc url>
```

Prefix `ape` commands with `uv run` (e.g. `uv run ape test ...`), or activate the environment with `source .venv/bin/activate`.

## Configuration

The project uses configuration files in format `config_<network-name>.json`. Configuration for the required network
is read automatically upon network variable `NETWORK` is set. Currently, `NETWORK` can be one of `mainnet`, `goerli`, `holesky`, `hoodi`.

## Run tests

```shell
NETWORK=mainnet uv run ape test -s --network :mainnet-fork:foundry
```

The networks supported are `mainnet-fork` and `goerli-fork` for which network-specific
configurations `config_*.py` are specified.

## Deployment

Get sure your account is imported to Ape (see `ape accounts list`).

### Test deployment

Let's assume the deploy account alias is `lido_deployer`. To deploy on mainnet fork run:

```shell
DEPLOYER=lido_deployer NETWORK=mainnet uv run ape run deploy --network :mainnet-fork:foundry
```

### Custom RPC deployment

Let's assume the deploy account alias is `lido_deployer`. To deploy on network `holesky` via custom RPC run:

```shell
DEPLOYER=lido_deployer NETWORK=holesky uv run ape run deploy --network <RPC-URI>
```

Deployment addresses are available in files `deployed_{network-name}.txt` where `{network-name}` is name of the network.

## Code style

Please, use the shared pre-commit hooks to maintain code style:

```bash
uv run pre-commit install
```
