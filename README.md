# MEV-Boost relay allowed list

MEV-Boost relay allowed list is a simple contract storing a list of relays that have been approved by DAO for use in [MEV-Boost](https://github.com/flashbots/mev-boost). The data from the contract are used to generate a configuration file that contains a list of relays that should be connected to.

MEVBoostRelaysWhitelist contract documentation is in [docs/MEVBoostRelayAllowedList.md](./docs/MEVBoostRelayAllowedList.md).

**NB**. CI tests flow is disabled due to the tooling being outdated. The repo is not in an active mode thus it is not worth to maintain the flow currently.
If you'd like to restore it, please start from [the old flow file](.github/workflows/tests.yml.disabled).

## Prerequisites

- python >= 3.9
- node >= 16.0
- poetry >= 1.1.14

## Setup

```shell
poetry install
npm install
export WEB3_INFURA_PROJECT_ID=<your infura project id>
```

and run

```shell
poetry shell
```

to initialize shell for `ape` command usage.

As long as the environment shell prompt name is cumbersome you might want to call
`export PS1="allowed-list-env $ "` to make it shorter.

## Configuration

The project uses configuration files in format `config_<network-name>.json`. Configuration for the required network
is read automatically upon network variable `NETWORK` is set. Currently, `NETWORK` can be one of `mainnet`, `goerli`, `holesky`, `hoodi`.

## Run tests

```shell
NETWORK=mainnet ape test -s --network :mainnet-fork:hardhat
```

The networks supported are `mainnet-fork` and `goerli-fork` for which network-specific
configurations `config_*.py` are specified.

## Deployment

Get sure your account is imported to Ape (see `ape accounts list`).

### Test deployment

Let's assume the deploy account alias is `lido_deployer`. To deploy on mainnet fork run:

```shell
DEPLOYER=lido_deployer NETWORK=mainnet ape run deploy --network :mainnet-fork:hardhat
```

### Custom RPC deployment

Let's assume the deploy account alias is `lido_deployer`. To deploy on network `holesky` via custom RPC run:

```shell
DEPLOYER=lido_deployer NETWORK=holesky ape run deploy --network <RPC-URI>
```

Deployment addresses are available in files `deployed_{network-name}.txt` where `{network-name}` is name of the network.

## Code style

Please, use the shared pre-commit hooks to maintain code style:

```bash
poetry run pre-commit install
```
