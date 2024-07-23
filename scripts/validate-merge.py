import glob
import os

def get_all_merged_transactions():
    return glob.glob("transactions/*-*.toml")

def get_alias():
    alias = os.environ.get("ALIAS")
    if alias is None:
        exit(1)
    return alias

def main():
    transactions = get_all_merged_transactions()
    genesis_transactions = open("genesis/transactions.toml", "w")

    print("Adding {} transactions...".format(len(transactions)))

    for file in transactions:
        print("Adding {}...".format(file))
        new_transaction = open(file, "r")
        genesis_transactions.write("{}\n".format(new_transaction.read()))

    print("Done.")


if __name__ == "__main__":
    main()