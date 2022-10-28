# https://www.notion.so/List-Of-Chains-2497cbaae9c6447b8bdb049e7acd806b
from pick import pick

'''
Reece Williams | Notional - Started Oct 28th 2022

Requirements:
- must have ssh keys on github
- Have installed: git, gh, gofmt, golangci-lint

Goal:
- Auto git pull/clone latest repos we validate
- golang-cli lint / gofmt the files.\
    - let the user know this file needs work. Is there a way to auto gofmt/lint fix?
- Check files, see if it has dependabot. If not, add it in. [make this its own option, use pick]
- Add options for many different chains
- Get latest values in go.mod, toggle for state breaking or just minor version patches <- useful for security patches. Bump them

VERSION BUMPING:
- Get current version from go.mod (ex: ibc-go v3.3.0)
- Bump to v3.3.1
'''

# chains real repos (put notional repos here in the future so we have write access)
'''
{
    "Osmosis": "git@github.com:osmosis-labs/osmosis.git",
    "Cosmoshub": "git@github.com:cosmos/gaia.git",
    "Juno": "git@github.com:CosmosContracts/juno.git",
    "Sifchain": "git@github.com:Sifchain/sifnode.git",
    "Omniflix": "git@github.com:OmniFlix/omniflixhub.git",
    "Secret-Network": "git@github.com:scrtlabs/SecretNetwork.git",
    "Starname": "",
    "Regen": "git@github.com:regen-network/regen-ledger.git",
    "Akash": "git@github.com:ovrclk/akash.git",
    "Sentinel": "git@github.com:sentinel-official/sentinel.git",
    "E-Money": "git@github.com:e-money/em-ledger.git",
    "Ixo": "git@github.com:ixofoundation/ixo-blockchain.git",
    # "Likecoin": "",
    # "Ki": "",
    "Cyber": "git@github.com:cybercongress/go-cyber.git",
    "Cheqd": "git@github.com:cheqd/cheqd-node.git",
    "Stargaze": "",
    "Band": "git@github.com:bandprotocol/chain.git",
    # "Chihuahua": "",
    # "Kava": "",
    # "BitCanna": "",
    # "Konstellation": "",
    # "Evmos": "",
    # "Provenance": "",
    # "Vidulum": "",
    # "Bitsong": "",
    # "Fetch.AI": "",
    # "Umee": "",
    # "Injective": "",
    # "Passage3D": "",
    "Stride": "git@github.com:Stride-Labs/stride.git",
    # "QuickSilver": "",
    # "Jackal": "",
}
'''

VALIDATING_CHAINS = {
    # "Osmosis": {
    #     "root": "git@github.com:osmosis-labs/osmosis.git",
    #     "notional": "git@github.com:notional-labs/osmosis.git"
    # },
    # "Cosmoshub": {
    #     "root": "git@github.com:cosmos/gaia.git",
    #     "notional": "git@github.com:notional-labs/gaia.git"
    # },
    # "Juno": "git@github.com:CosmosContracts/juno.git",
    # "Sifchain": "git@github.com:Sifchain/sifnode.git",
    # "Omniflix": {
    #     "root": "git@github.com:OmniFlix/omniflixhub.git",
    #     "notional": "git@github.com:notional-labs/mainnet-1.git"
    # },
    "Cyber": {
        "branch": "main",

        "root": "git@github.com:cybercongress/go-cyber.git",
        "notional": "git@github.com:notional-labs/go-cyber.git"
    },
    # "Secret-Network": "git@github.com:scrtlabs/SecretNetwork.git",
    # "Regen": "git@github.com:regen-network/regen-ledger.git",
    # "Akash": "git@github.com:ovrclk/akash.git",
    # "Sentinel": "git@github.com:sentinel-official/sentinel.git",
    # "E-Money": "git@github.com:e-money/em-ledger.git",
    # "Ixo": "git@github.com:ixofoundation/ixo-blockchain.git",    
    # "Cheqd": "git@github.com:cheqd/cheqd-node.git",
    # "Band": "git@github.com:bandprotocol/chain.git",

}

import os

# current dir of the file
current_dir = os.path.dirname(os.path.realpath(__file__))
yml_files = os.path.join(current_dir, ".yml_files")
os.chdir(current_dir)

def get_chains():
    for chain, locations in VALIDATING_CHAINS.items():
        yield chain, locations


def pull_latest(folder_name):
    # git clone if it is not there already, if it is, cd into dir and git pull    
    os.chdir(current_dir)

    repo_link = VALIDATING_CHAINS[folder_name]["notional"]    

    # check if folder_name exists
    if os.path.isdir(os.path.join(current_dir, folder_name)):        
        print(f"pulling latest {folder_name}")
        os.chdir(folder_name)
        os.system("git pull")
        # os.chdir("..")
    else:
        # run a system command to get git clone
        print(f"Cloning {folder_name} from {repo_link}")
        os.system(f"git clone {repo_link} {folder_name}")


    # Ex: gh repo sync notional-labs/go-cyber (gets latest synced branchs up to date)
    # force pulls an overwrite on main/master branch
    print(f"Syncing fork to latest of parent main/master branch (overwriting any main/master changes)")
    # ✓ Synced the "notional-labs:main" branch from "osmosis-labs:main"
    os.system(f"gh repo sync {repo_link.replace('git@github.com:', '').replace('.git', '')} --force")

    os.chdir(current_dir)


def lint(folder_name):
    print(f"Linting {folder_name}...")
    os.chdir(os.path.join(current_dir, folder_name))
    # os.system("gofmt")
    # os.system("golangci-lint run")
    os.system("go mod tidy")
    os.chdir(current_dir)


def dependabot(folder_name):
    # https://github.com/eve-network/eve, put in .yml_files folder
    # check if folder chains .github/dependabot.yml dir

    repo = os.path.join(current_dir, folder_name)
    main_branch = VALIDATING_CHAINS[folder_name]["branch"] # main, master, etc

    os.chdir(repo)
    if not os.path.exists(".github/dependabot.yml"):
        os.makedirs(".github", exist_ok=True)        
        # write yml_files/dependabot.yml to .github/dependabot.yml
        print(f"Writing dependabot.yml to .github/dependabot.yml for {folder_name} as it did not have it...")
        with open(f".github/dependabot.yml", "w") as f:
            with open(os.path.join(yml_files, "dependabot.yml"), "r") as f2:
                f.write(f2.read().replace("_MAIN_BRANCH_", main_branch))
    os.chdir(current_dir)


def _write_workflow(folder_name, workflow_name, main_branch_name):
    # we are already in the folder_name here    
    print(f"Writing {workflow_name} to .github/workflows/{workflow_name} for {folder_name}")
    with open(os.path.join(yml_files, "workflows", workflow_name), "r") as f2:
        with open(f".github/workflows/{workflow_name}", "w") as f:
            f.write(f2.read().replace("_MAIN_BRANCH_", main_branch_name))


def workflows(folder_name):
    # https://github.com/eve-network/eve, put in .yml_files folder
    # check if folder chains .github/dependabot.yml dir
    repo = os.path.join(current_dir, folder_name)   
    main_branch = VALIDATING_CHAINS[folder_name]["branch"] # main, master, etc 

    os.chdir(repo)
    if not os.path.exists(".github/workflows"):
        os.makedirs(".github/workflows", exist_ok=True)        
        
    # TODO: multiselect pick here

    all_workflow_options = os.listdir(os.path.join(yml_files, "workflows"))    
    workflow_options = [x for x in all_workflow_options if x not in os.listdir(".github/workflows")]

    title = "Workflow options to install (space, then enter)"
    selected = pick(workflow_options, title, multiselect=True, min_selection_count=0, indicator="=> ")
    # print(selected)

    for file, idx in selected:
        _write_workflow(folder_name, file, main_branch)

    os.chdir(current_dir)


    


def oct_28_2022_patches():
    '''
    Loop through all chains we validate,
    '''
    for chain, loc in get_chains():
        print(f"Chain: {chain}. Location: {loc}")
        # pull_latest(chain)
        # dependabot(chain)
        workflows(chain)


oct_28_2022_patches()

# pull_latest("Cyber")