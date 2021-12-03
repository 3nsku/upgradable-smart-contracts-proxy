from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to Network: {network.show_active()}")
    box = Box.deploy(
        {"from": account}, publish_source=True
    )  # THIS IS THE IMPLEMENTATION CONTRACT

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    # initialize the variables
    box_encoded_initializer_data = encode_function_data(box.store, 1)

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_data,
        {
            "from": account,
            "gas_limit": 1000000,
        },
        publish_source=True,  # proxies can sometimes have a hard times figuring out the gas limit, so it can be helpful to pass set it.
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to V2")

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    print("RETRIEVE", proxy_box.retrieve())

    proxy_box = upgrade(account, proxy, BoxV2, "BoxV2", proxy_admin)

    proxy_box.increment({"from": account})
    print("Incremented Value:", proxy_box.retrieve())
