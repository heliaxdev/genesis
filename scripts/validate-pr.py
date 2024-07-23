import subprocess
import re
import os
from typing import Dict, List
import toml

FILE_NAME_PATTER = r"transactions/(.*)-(validator|bond|account).toml"
EMAIL_PATTERN = r"^\S+@\S+\.\S+$"

def check_no_deleted_or_modified_files():
    res = subprocess.run(["git", "diff", "--name-only", "--diff-filter=DM", "origin/main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode > 0:
        exit(1)
    
    deleted_files = list(map(lambda file_path: file_path.decode(), res.stdout.splitlines()))
    if deleted_files:
        exit(1)

def get_all_created_files():
    res = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "origin/main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode > 0:
        exit(1)
    
    return list(map(lambda file_path: file_path.decode(), res.stdout.splitlines()))


def read_unsafe_toml(file_path):
    try:
        return toml.load(open(file_path, "r"))
    except Exception as e:
        return None
    

def get_alias():
    alias = os.environ.get("ALIAS")
    if alias is None:
        exit(1)
    return alias


def check_if_account_is_valid(accounts_toml: List[Dict]):
    for account in accounts_toml['established_account']:
        for field in ['vp', 'threshold', 'public_keys']:
            if field not in account:
                return False

        vp = account['vp']
        threshold = account['threshold']
        public_keys = account['public_keys']

        if vp != "vp_user":
            return False
        
        if len(public_keys) < threshold:
            return False

        if threshold <= 0:
            return False

        # TODO: check for bech32m public keys
    return True

def check_if_validator_is_valid(validators_toml: List[Dict]):
    is_valid = check_if_account_is_valid(validators_toml)
    if not is_valid:
        return False
    
    for validator in validators_toml['validator_account']:
        for field in ['consensus_key', 'protocol_key', 'tendermint_node_key', 'eth_hot_key', 'eth_cold_key', 'metadata', 'signatures', 'address', 'vp', 'commission_rate', 'max_commission_rate_change']:
            if field not in validator:
                return False
            
        for field in ['consensus_key', 'protocol_key', 'tendermint_node_key', 'eth_hot_key', 'eth_cold_key']:
            for sub_field in ['pk', 'authorization']:
                if sub_field not in validator[field]:
                    return False
                
        for field in ['metadata']:
            for sub_field in ['email']:
                if sub_field not in validator[field]:
                    return False
                
        if len(validator['signatures']) <= 0:
            return False
    
        vp = validator['vp']
        commission_rate = float(validator['commission_rate'])
        max_commission_rate_change = float(validator['max_commission_rate_change'])
        address = validator['address']
        email = validator['metadata']['email']

        if vp != "vp_user":
            return False
        
        # TODO: check address bech32m

        if not 0 <= commission_rate <= 1:
            return False
        
        if not 0 <= max_commission_rate_change <= 1:
            return False
        
        if not re.search(EMAIL_PATTERN, email):
            return False

    return True


def check_if_bond_is_valid(bonds_toml: List[Dict], balances: Dict[str, Dict]):
    for bond in bonds_toml['bond']:
        for field in ['source', 'validator', 'amount', 'signatures']:
            if field not in bond:
                return False
            
        if len(bond['signatures']) <= 0:
            return False
        
        source = bond['source']
        validator = bond['validator']
        amount = float(bond['amount'])
        
        balance = float(balances[source]) if source in balances else 0

        if balance == 0 or not balance >= amount:
            return False
        
        # TODO: check source and validator bech32

    return True


def validate_toml(file):
    balances = toml.load(open("genesis/balances.toml", "r"))
    nam_balances = balances['token']['NAM']

    if '-account.toml' in file:
        accounts_toml = read_unsafe_toml(file)
        if accounts_toml is None:
            print("{} is NOT valid.".format(file))
        is_valid = check_if_account_is_valid(accounts_toml)
        if not is_valid:
            print("{} is NOT valid.".format(file))
    elif '-validator.toml' in file:
        validators_toml = read_unsafe_toml(file)
        if validators_toml is None:
            print("{} is NOT valid.".format(file))
        is_valid = check_if_validator_is_valid(validators_toml)
        if not is_valid:
            print("{} is NOT valid.".format(file))
    elif '-bond.toml' in file:
        bonds_toml = read_unsafe_toml(file)
        if not bonds_toml:
            print("{} is NOT valid.".format(file))
        is_valid = check_if_bond_is_valid(bonds_toml, nam_balances)
        if not is_valid:
            print("{} is NOT valid.".format(file))
    else:
        return False

    print("{} is valid.".format(file))

def main():
    check_no_deleted_or_modified_files()
    changed_files = get_all_created_files()
    alias = get_alias()

    print("Found {} file changed/added.".format(len(changed_files)))
    
    # only files changes in transactions with a specific format are allowed
    for file in changed_files:
        res = re.search(FILE_NAME_PATTER, file)
        if res is None:
            print("{} doesn't match pattern {}".format(file, FILE_NAME_PATTER))
            exit(1)

        file_alias = file.split('/')[1].split('.')[0]
        if not alias.lower() in file_alias.lower():
            exit(1)

        print("{} is allowed, checking if its valid...".format(file))

        if 'scripts' in file or 'yml' in file:
            continue

        validate_toml(file)


if __name__ == "__main__":
    main()