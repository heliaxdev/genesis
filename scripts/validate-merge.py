import glob
import os
import subprocess

def get_all_merged_transactions():
    return glob.glob("transactions/*-*.toml")


def get_alias():
    alias = os.environ.get("ALIAS")
    if alias is None:
        exit(1)
    return alias


def is_valid_template():
    namada_binaries_path = os.environ.get("NAMADA_PATH", 'namada')
    res = subprocess.run([namada_binaries_path, "client", "utils", "validate-genesis-templates", "--path", "genesis"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode > 0:
        print(res.stderr)
        print(res.stdout)
        exit(1)


def main():
    transactions = get_all_merged_transactions()
    genesis_transactions = open("genesis/transactions.toml", "w")

    print("Adding {} transactions...".format(len(transactions)))

    for file in transactions:
        print("Adding {}...".format(file))
        new_transaction = open(file, "r")
        genesis_transactions.write("{}\n".format(new_transaction.read()))

    is_valid_template()

    print("Done.")


if __name__ == "__main__":
    main()