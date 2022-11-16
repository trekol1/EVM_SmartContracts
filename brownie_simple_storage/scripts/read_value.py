from brownie import SimpleStorage, accounts, config


def read_cotract():
    simple_storage = SimpleStorage[-1]
    # go take the deployment index that is one less than the length
    # ABI
    # Address
    print(simple_storage.retrieve())


def main():
    read_cotract()
