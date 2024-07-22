import glob

def get_all_merged_transactions():
    return glob.glob("transactions/*-*.toml")

def get_alias(file):
    return "{}".format(file.split('/')[1].split('.')[0])

def main():
    transactions = get_all_merged_transactions()
    genesis_transactions = open("genesis/transactions.toml", "w")

    print("Adding {} transactions...".format(len(transactions)))

    for index, file in enumerate(transactions):
        print("Adding {}...".format(file))
        alias = get_alias(file)
        if index == 0:
            genesis_transactions.write("# adding transaction for {}\n\n".format(alias))
        else:
            genesis_transactions.write("\n\n# adding transaction for {}\n\n".format(alias))
        new_transaction = open(file, "r")
        genesis_transactions.write("{}\n".format(new_transaction.read()))

    print("Done.")


if __name__ == "__main__":
    main()