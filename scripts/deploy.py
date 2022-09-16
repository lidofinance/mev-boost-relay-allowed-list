from ape import accounts, project
from config import lido_dao_agent_address, get_deployer_account, get_network_name


def main():
    print(f"\n!!! Current network is {get_network_name()} !!!\n")

    deployer = get_deployer_account()

    allowed_list = project.MEVBoostRelayAllowedList.deploy(
        lido_dao_agent_address, sender=deployer, max_fee="300 gwei"
    )
