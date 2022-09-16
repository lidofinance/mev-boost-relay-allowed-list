# MEV-Boost relay allowed list

MEV-Boost relay allowed list is a simple contract storing a list of relays that have been approved by DAO for use in [MEV-Boost](https://github.com/flashbots/mev-boost). The data from the contract are used to generate a configuration file that contains a list of relays that should be connected to.

MEVBoostRelaysWhitelist contract documentation is in [docs/MEVBoostRelayAllowedList.md](./docs/MEVBoostRelayAllowedList.md).

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

## Run tests

```shell
ape test -s --network :mainnet-fork:hardhat
```

The networks supported are `mainnet-fork` and `goerli-fork` for which network-specific
configurations `config_*.py` are specified.

## Deployment

Get sure your account is imported to Ape (see `ape accounts list`).

Let's assume the deploy account alias is `lido_deployer`. To deploy on mainnet fork:

```shell
DEPLOYER=lido_deployer ape run deploy --network :mainnet-fork:hardhat
```

Deployment addresses are available in files `deployed_mainnet.txt` and `deployed_goerli.txt`.
