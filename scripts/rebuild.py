from collections import defaultdict
import glob
import toml
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader

def build_graph(validators):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[validator['address'] for validator in validators],
        y=[validator['voting_power'] for validator in validators],
        name='validators',
        marker_color='indianred',
    ))

    fig.update_layout(xaxis={'categoryorder':'total descending'})
    fig.update_xaxes(tickangle=75)

    fig.write_image("images/validators.png")


def build_readme(validators):
    environment = Environment(loader=FileSystemLoader("scripts/artifacts"))
    template = environment.get_template("README.jinja")

    content = template.render({"validators": validators})

    with open("genesis/README.md", mode="w", encoding="utf-8") as message:
        message.write(content)


def read_unsafe_toml(file_path):
    try:
        return toml.load(open(file_path, "r"))
    except Exception as e:
        return None


def parse_validators():
    validator_files = glob.glob("transactions/*-validator.toml")
    bond_files = glob.glob("transactions/*-bond.toml")

    bonds = []
    target_vp = defaultdict(int)
    for file in bond_files:
        bonds_toml = read_unsafe_toml(file)
        if bonds_toml is None:
            continue
        
        for bond in bonds_toml['bond']:
            bonds.append({
                'source': bond['source'],
                'validator': bond['validator'],
                'amount': bond['amount'],
            })
            target_vp[bond['validator']] += float(bond['amount'])

    validators = []
    for file in validator_files:
        validators_toml = read_unsafe_toml(file)
        if validators_toml is None:
            continue

        for validator in validators_toml['validator_account']:
            validators.append({
                'address': validator['address'],
                'commission_rate': float(validator['commission_rate']) * 100,
                'max_commission_rate_change': float(validator['max_commission_rate_change']) * 100,
                'email': validator['metadata']['email'],
                'alias': validator['metadata']['alias'] if 'alias' in validator['metadata'] else None,
                'website': validator['metadata']['website'] if 'website' in validator['metadata'] else None,
                'voting_power': target_vp[validator['address']] if validator['address'] in target_vp else 0
            })

    return sorted(validators, key=lambda d: d['voting_power'])

def main():
    validators = parse_validators()
    build_graph(validators)
    build_readme(validators)

if __name__ == "__main__":
    main()