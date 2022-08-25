# MEV-Boost relay whitelist

MEV-Boost relay whitelist is a simple contract storing a list of relays that have been approved by DAO for use in [MEV-Boost](https://github.com/flashbots/mev-boost). The data from the contract are used to generate a configuration file that contains a list of relays that should be connected to.

## Setup

```shell
poetry install
npm install
export WEB3_INFURA_PROJECT_ID=<your infura project id>
```

## Run tests

```shell
ape test -s --network :mainnet-fork:hardhat
```


## Deployment

> **NB:** The deployment is done via Ape console because this contract deployment is trivial and because Ape doesn't provide the capability to specify deployer account in a script.

Get sure your account is imported to Ape: `ape accounts list`.

Start Ape console for the target network and provider, e. g.
```bash
ape console --network :mainnet:infura
```

Deploy from the console:

```python
from ape import accounts, project
account = accounts.load("my_account_alias")
lido_dao_agent_address = "PUT THE ADDRESS FOR THE TARGET NETWORK HERE"
project.MEVBoostRelayWhitelist.deploy(sender=account)
```

**TODO**: Load the Lido DAO Agent address from config
