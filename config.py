import os

from ape import accounts


DEPLOYER_ENV_VAR = "DEPLOYER"
NETWORK_ENV_VAR = "NETWORK"
MAINNET = "mainnet"
GOERLI = "goerli"
HOLESKY = "holesky"
SUPPORTED_NETWORKS = [MAINNET, GOERLI, HOLESKY]


def get_network_name() -> str:
    network_name = os.environ.get(NETWORK_ENV_VAR, None)
    if network_name not in SUPPORTED_NETWORKS:
        raise RuntimeError(f"Must specify env variable {NETWORK_ENV_VAR} be one of {','.join(SUPPORTED_NETWORKS)}")

    return network_name


network_name = get_network_name()
if network_name == GOERLI:
    print(f"Using config_goerli.py addresses")
    from config_goerli import *
elif network_name == MAINNET:
    print(f"Using config_mainnet.py addresses")
    from config_mainnet import *
elif network_name == HOLESKY:
    print(f"Using config_holesky.py addresses")
    from config_holesky import *
else:
    assert False, f"Unknown network {network_name}"


def get_deployer_account():
    if DEPLOYER_ENV_VAR not in os.environ:
        raise EnvironmentError(f"Please set {DEPLOYER_ENV_VAR} env variable to the deployer Ape account name")

    return accounts.load(os.environ[DEPLOYER_ENV_VAR])
