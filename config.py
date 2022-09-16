import os
import sys
from typing import Optional

from ape import networks, accounts


def get_network_name() -> Optional[str]:
    # It is None at moment of config.py network initialization
    if networks.active_provider is None:
        network_index = sys.argv.index("--network")
        if network_index + 1 < len(sys.argv):
            network_arg = sys.argv[network_index + 1]
            _, name, provider = network_arg.split(":")
            return name
        return None

    return networks.active_provider.network.name


if get_network_name() in ("goerli", "goerli-fork"):
    print(f"Using config_goerli.py addresses")
    from config_goerli import *
else:
    print(f"Using config_mainnet.py addresses")
    from config_mainnet import *


def get_deployer_account():
    if "DEPLOYER" not in os.environ:
        raise EnvironmentError("Please set DEPLOYER env variable to the deployer Ape account name")

    return accounts.load(os.environ["DEPLOYER"])
