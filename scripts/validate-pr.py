import subprocess
import re
from typing import Dict, List
import toml

FILE_NAME_PATTER = "transactions/(.*)-(validator|bond|account).toml"

def check_no_deleted_files():
    res = subprocess.run(["git", "diff", "--name-only", "--diff-filter=D", "origin/main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode > 0:
        exit(1)
    
    deleted_files = list(map(lambda file_path: file_path.decode(), res.stdout.splitlines()))
    if deleted_files:
        exit(1)

def get_all_modified_or_created_files():
    res = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", "origin/main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode > 0:
        exit(1)
    
    return list(map(lambda file_path: file_path.decode(), res.stdout.splitlines()))


def read_unsafe_toml(file_path):
    try:
        return toml.load(open(file_path, "r"))
    except Exception as e:
        print(e)
        return None
    

def check_if_account_is_valid(accounts_toml: List[Dict], balances_toml: Dict[str, Dict]):
    for account in accounts_toml['established_account']:
        vp = account['vp']
        threshold = account['threshold']
        public_keys = account['public_keys']

        if vp != "vp_user":
            exit(1)
        
        if len(public_keys) < threshold:
            exit(1)

        if threshold <= 0:
            exit(1)

        # TODO: check for bech32m public keys

def check_if_validator_is_valid(validators_toml: List[Dict], balances_toml: Dict[str, Dict]):
    check_if_account_is_valid(validators_toml, balances_toml)


def check_if_bond_is_valid(validators_toml: List[Dict], balances_toml: Dict[str, Dict]):
    return True


def validate_toml(file):
    balances = toml.load(open("genesis/balances.toml", "r"))
    nam_balances = balances['token']['NAM']

    if '-account.toml' in file:
        accounts_toml = read_unsafe_toml(file)
        check_if_account_is_valid(accounts_toml, nam_balances)
    elif '-validator.toml' in file:
        validators_toml = read_unsafe_toml(file)
        check_if_validator_is_valid(validators_toml, balances)
    elif '-bond.toml':
        bonds_toml = read_unsafe_toml(file)
        check_if_bond_is_valid(bonds_toml, balances)

    print("{} is valid.".format(file))

def main():
    check_no_deleted_files()
    changed_files = get_all_modified_or_created_files()

    print("Found {} file changed/added.".format(len(changed_files)))
    
    # only files changes in transactions with a specific format are allowed
    for file in changed_files:
        res = re.search(FILE_NAME_PATTER, file)
        if res is None:
            print("{} doesn't match pattern {}".format(file, FILE_NAME_PATTER))

        print("{} is allowed, checking if its valid...".format(file))

        if 'scripts' in file:
            continue

        validate_toml(file)



if __name__ == "__main__":
    main()