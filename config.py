import os

from ape import accounts


NETWORK_ENV_VAR = "NETWORK"
ALLOWED_NETWORKS = ["mainnet", "goerli", "holesky"]


def get_network_name() -> str:
    network_name = os.environ.get(NETWORK_ENV_VAR, None)
    if network_name not in ALLOWED_NETWORKS:
        raise RuntimeError(f"Must specify env variable {NETWORK_ENV_VAR} be one of {','.join(ALLOWED_NETWORKS)}")

    return network_name


if get_network_name() == "goerli":
    print(f"Using config_goerli.py addresses")
    from config_goerli import *
elif get_network_name() == "mainnet":
    print(f"Using config_mainnet.py addresses")
    from config_mainnet import *
elif get_network_name() == "holesky":
    print(f"Using config_holesky.py addresses")
    from config_holesky import *
else:
    assert False, f"Unknown network {get_network_name()}"


def get_deployer_account():
    if "DEPLOYER" not in os.environ:
        raise EnvironmentError("Please set DEPLOYER env variable to the deployer Ape account name")

    return accounts.load(os.environ["DEPLOYER"])
