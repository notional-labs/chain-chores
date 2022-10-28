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

# ToDO: if we do not have a repo, we should auto fork it for notional?
VALIDATING_CHAINS = {
    # "Osmosis": { # currently protected main
    #     "branch": "main",
    #     "root": "git@github.com:osmosis-labs/osmosis.git",
    #     "notional": "git@github.com:notional-labs/osmosis.git"
    # },
    # "Gaia": {
    #     "branch": "main",
    #     "root": "git@github.com:cosmos/gaia.git",
    #     "notional": "git@github.com:notional-labs/gaia.git"
    # },    
    # "Juno": { 
    #     "branch": "main",
    #     "root": "git@github.com:CosmosContracts/juno.git",
    #     "notional": "git@github.com:notional-labs/juno.git"
    # },
    # "Sifchain": { 
    #     "branch": "master",
    #     "root": "git@github.com:Sifchain/sifnode.git",
    #     "notional": "git@github.com:notional-labs/sifnode.git"
    # },    
    # "Omniflix": {
    #     "branch": "main",
    #     "root": "git@github.com:OmniFlix/omniflixhub.git",
    #     "notional": "git@github.com:notional-labs/omniflixhub.git"
    # },
    # "Secret": {
    #     "branch": "master",
    #     "root": "git@github.com:scrtlabs/SecretNetwork.git",
    #     "notional": "git@github.com:notional-labs/SecretNetwork.git"
    # },
    "Starname-IOV": {
        "branch": "master",
        "root": "git@github.com:iov-one/starnamed.git",
        "notional": "git@github.com:notional-labs/starnamed.git"
    },
    "Regen": {
        "branch": "master",
        "root": "git@github.com:regen-network/regen-ledger.git",
        "notional": "git@github.com:notional-labs/regen-ledger.git"
    },
    "Akash": {
        "branch": "master",
        "root": "git@github.com:ovrclk/akash.git",
        "notional": "git@github.com:notional-labs/akash.git"
    },
    "Sentinel": {
        "branch": "master",
        "root": "git@github.com:sentinel-official/sentinel.git",
        "notional": "git@github.com:notional-labs/sentinel.git"
    },
    "Emoney": {
        "branch": "develop",
        "root": "git@github.com:e-money/em-ledger.git",
        "notional": "git@github.com:notional-labs/em-ledger.git"
    },
    "Emoney": {
        "branch": "main",
        "root": "git@github.com:ixofoundation/ixo-blockchain.git",
        "notional": "git@github.com:notional-labs/ixo-blockchain.git"
    },
    "LikeCoin": {
        "branch": "master",
        "root": "git@github.com:likecoin/likecoin-chain.git",
        "notional": "git@github.com:notional-labs/likecoin-chain.git"
    },
    # "Cyber": {
    #     "branch": "main",
    #     "root": "git@github.com:cybercongress/go-cyber.git",
    #     "notional": "git@github.com:notional-labs/go-cyber.git"
    # },
    "Cheqd": {
        "branch": "main",
        "root": "git@github.com:cheqd/cheqd-node.git",
        "notional": "git@github.com:notional-labs/cheqd-node.git"
    },
    "Stargaze": {
        "branch": "main",
        "root": "git@github.com:public-awesome/stargaze.git",
        "notional": "git@github.com:notional-labs/stargaze.git"
    },
    "BandChain": {
        "branch": "master",
        "root": "git@github.com:bandprotocol/chain.git",
        "notional": "git@github.com:notional-labs/chain.git"
    },
    "Chihuahua": {
        "branch": "main",
        "root": "git@github.com:ChihuahuaChain/chihuahua.git",
        "notional": "git@github.com:notional-labs/chihuahua.git"
    },
    "Kava": {
        "branch": "master",
        "root": "git@github.com:Kava-Labs/kava.git",
        "notional": "git@github.com:notional-labs/kava.git"
    },
    "BitCanna": {
        "branch": "main",
        "root": "git@github.com:BitCannaGlobal/bcna.git",
        "notional": "git@github.com:notional-labs/bcna.git"
    },
    "Evmos": {
        "branch": "main",
        "root": "git@github.com:evmos/evmos.git",
        "notional": "git@github.com:notional-labs/evmos.git"
    },
    "Provenance": {
        "branch": "main",
        "root": "git@github.com:provenance-io/provenance.git",
        "notional": "git@github.com:notional-labs/provenance.git"
    },
    "Vidulum": {
        "branch": "main",
        "root": "git@github.com:vidulum/mainnet.git",
        "notional": "git@github.com:notional-labs/vidulum.git"
    },
    "Bitsong": {
        "branch": "main",
        "root": "git@github.com:bitsongofficial/go-bitsong.git",
        "notional": "git@github.com:notional-labs/go-bitsong.git"
    },
    "FetchAI": {
        "branch": "master",
        "root": "git@github.com:fetchai/fetchd.git",
        "notional": "git@github.com:notional-labs/fetchd.git"
    },
    "Uume": {
        "branch": "main",
        "root": "git@github.com:umee-network/umee.git",
        "notional": "git@github.com:notional-labs/umee.git"
    },
    "Passage3D": {
        "branch": "main",
        "root": "git@github.com:envadiv/Passage3D.git",
        "notional": "git@github.com:notional-labs/Passage3D.git"
    },
    "Stride": {
        "branch": "main",
        "root": "git@github.com:Stride-Labs/stride.git",
        "notional": "git@github.com:notional-labs/stride.git"
    },
    "QuickSilver": {
        "branch": "main",
        "root": "git@github.com:ingenuity-build/quicksilver.git",
        "notional": "git@github.com:notional-labs/quicksilver.git"
    },
    "Jackal": {
        "branch": "master",
        "root": "git@github.com:JackalLabs/canine-chain.git",
        "notional": "git@github.com:notional-labs/canine-chain.git"
    },
    # # "Injective": "",    
    # # "Ki": "", # ??  
    # # "Konstellation": "",
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

    parent_link = VALIDATING_CHAINS[folder_name]["root"]    
    repo_link = VALIDATING_CHAINS[folder_name]["notional"]    

    # check if folder_name exists
    if os.path.isdir(os.path.join(current_dir, folder_name)):        
        print(f"pulling latest {folder_name}")
        os.chdir(folder_name)
        os.system("git pull origin")
        # os.chdir("..")
    else:
        # run a system command to get git clone
        print(f"Cloning {folder_name} from {repo_link}")
        os.system(f"git clone {repo_link} {folder_name}")    

    # print(f"Syncing fork to latest of parent main/master branch (overwriting any main/master changes)")    
    os.system(f"git remote add upstream {repo_link}") # if not already
    os.system(f"gh repo sync {repo_link.replace('git@github.com:', '').replace('.git', '')} --force")

    # pull after we sync to the new files in the notional repo which we will build off of
    os.system("git pull")

    os.chdir(current_dir)


def lint(folder_name):
    print(f"Linting {folder_name}...")
    os.chdir(os.path.join(current_dir, folder_name))
    os.system("golangci-lint run --fix")
    os.system("gofmt -s -w .")
    os.system("go vet ./...")
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




def go_mod_update(folder_name, values: list[str] = []):
    os.chdir(os.path.join(current_dir, folder_name))
    
    # read go.mod data
    with open("go.mod", "r") as f:
        data = f.read()
        
    for replacements in values:
        # print(f"Replacing {replacements[0]} with {replacements[1]}")
        data = data.replace(replacements[0], replacements[1])
    # print(data)

    with open("go.mod", "w") as f:
        print(f"Writing go.mod for {folder_name}")
        f.write(data)

    os.system("go mod tidy")
    os.chdir(current_dir)



PATCH_BRANCH_NAME = "reece-ibc331" # this is made on notionals fork
def oct_28_2022_patches():
    for chain, loc in get_chains():
        print(f"Chain: {chain}")
        pull_latest(chain)
        # dependabot(chain)
        # workflows(chain)

        # go_mod_update(chain, [
        #     # allow regex matching here? so we could do v3.*.* -> v3.3.1
        #     ["github.com/cosmos/ibc-go/v3 v3.3.0", "github.com/cosmos/ibc-go/v3 v3.3.1"]
        # ])

        # lint(chain)




oct_28_2022_patches()