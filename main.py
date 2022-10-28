# https://www.notion.so/List-Of-Chains-2497cbaae9c6447b8bdb049e7acd806b
import os
from pick import pick
from CHAINS import VALIDATING_CHAINS
import re

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

TODO:
- Use mp to run all of these in parallel
'''

# current dir of the file
current_dir = os.path.dirname(os.path.realpath(__file__))
yml_files = os.path.join(current_dir, ".yml_files")
os.chdir(current_dir)

def get_chains():
    for chain, locations in VALIDATING_CHAINS.items():
        yield chain, locations


def pull_latest(folder_name, repo_sync=False):
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
    if repo_sync:
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




def go_mod_update(folder_name, values: list[str] = [], simulate: bool = False):
    os.chdir(os.path.join(current_dir, folder_name))
    
    if "go.mod" not in os.listdir():
        print(f"{folder_name} does not have a go.mod file, skipping...")
        return

    # read go.mod data
    with open("go.mod", "r") as f:
        data = f.read()
        
    for replacements in values:
        old = replacements[0]
        new = replacements[1]        
        matches = re.search(old, data)

        if matches: # allow for us to use regex
            if matches.group(0) == new:
                # ensure the matches are not exactly the new value
                # print(f"Skipping {old} as it is already {new}")
                continue

            if simulate:   
                # get the matches in string form from matches                         
                print(f"{folder_name:<10} Would replace '{matches.group(0)}'\t-> {new}")    
            else:                
                print(f"Replacing {old} with {new}")                
                data = re.sub(old, new, data)

    if simulate == False:
        with open("go.mod", "w") as f:
            print(f"Writing go.mod for {folder_name}")
            f.write(data)

        os.system("go mod tidy")
    os.chdir(current_dir)


def open_in_vscode(folder_name):
    # This way we can commit and push changes we have made
    os.system(f"code {os.path.join(current_dir, folder_name)}")    

PATCH_BRANCH_NAME = "reece-ibc331" # this is made on notionals fork
def oct_28_2022_patches():
    
    select_chains = ["Kava"]
    for chain, loc in get_chains():
        if len(select_chains) > 0 and chain not in select_chains:
            continue

        # print(f"Chain: {chain}")
        pull_latest(chain, repo_sync=False)
        # dependabot(chain)
        # workflows(chain)

        go_mod_update(chain, [
            ["github.com/cosmos/ibc-go/v3 v3.3.0", "github.com/cosmos/ibc-go/v3 v3.3.1"],
        ], simulate=False)
        # TODO: when we do update, we need to create a new git branch for us to PR off of (do not build off of main)

        open_in_vscode(chain)

        # lint(chain)



try:
    oct_28_2022_patches()
except Exception as e:
    print(e)
    print("Something went wrong, please check the logs above")