from brownie import network, accounts, config, Contract

from web3 import Web3
import eth_utils

FORKED_LOCAL_ENRIVONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "mainnet-fork-dev",
    "development",
    "ganache-local",
]  # this is a list of local networks so that we know when to deploy mocks


def get_account(index=None, id=None):
    # index will choose one of the addresses inside accounts array
    # id will use one of the accounts saved inside brownie -> $ brownie accounts list
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENRIVONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return initializer.encode_input(*args)


def upgrade(
    _account,
    _proxy,
    _new_implementation_contract,
    _new_implementation_contract_name,
    _proxy_admin_contract=None,
    _initializer=None,
    *_args,
):
    # Deploy New Implementation
    print("Deploying New Implementation of Contract")
    new_implementation = _new_implementation_contract.deploy(
        {"from": _account}, publish_source=True
    )

    # Based on The Type selec if Proxy_admin and if initializer
    if _proxy_admin_contract:
        if _initializer:
            encoded_function_call = encode_function_data(_initializer, *_args)
            _proxy_admin_contract.upgradeAndCall(
                _proxy.address,
                new_implementation.address,
                encoded_function_call,
                {"from": _account},
            ).wait(1)
        else:
            _proxy_admin_contract.upgrade(
                _proxy.address, new_implementation.address, {"from": _account}
            ).wait(1)
    else:
        if _initializer:
            encoded_function_call = encode_function_data(_initializer, *_args)
            _proxy.upgradeToAndCall(
                new_implementation.address,
                encoded_function_call,
                {"from": _account},
            ).wait(1)
        else:
            _proxy.upgradeTo(new_implementation.address, {"from": _account}).wait(1)

    print("Proxy Upgraded")

    # Return the Updated Proxy_Contract
    return Contract.from_abi(
        _new_implementation_contract_name,
        _proxy.address,
        _new_implementation_contract.abi,
    )
