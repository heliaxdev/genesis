import subprocess

def get_all_created_files():
    res = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "origin/main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode > 0:
        exit(1)
    
    return list(map(lambda file_path: file_path.decode(), res.stdout.splitlines()))

def get_alias(changes_files):
    alias = changes_files[0].split('/')[1].split('-')[0]
    for file in changes_files:
        if not alias == file.split('/')[1].split('-')[0]:
            return None
    
    return alias

def main():
    changed_files = get_all_created_files()
    alias = get_alias(changed_files)
    genesis_transactions = open("genesis/transactions.toml", "a")

    print("Will add {} transactions for alias {}...".format(len(changed_files), alias))

    genesis_transactions.write("\n\n# adding transactions for {}\n\n".format(alias))

    for file in changed_files:
        print("Adding {}...".format(file))
        new_transaction = open(file, "r")
        genesis_transactions.write("{}\n".format(new_transaction.read()))

    print("Done.")


if __name__ == "__main__":
    main()