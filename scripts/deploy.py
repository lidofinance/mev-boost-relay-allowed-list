from ape import accounts, project
from config import LIDO_DAO_AGENT_ADDRESS, get_deployer_account, get_network_name


def main():
    print(f"\n!!! Current network is {get_network_name()} !!!\n")

    deployer = get_deployer_account()

    allowed_list = project.MEVBoostRelayAllowedList.deploy(LIDO_DAO_AGENT_ADDRESS, sender=deployer, max_fee="300 gwei")
