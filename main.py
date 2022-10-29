# https://www.notion.so/List-Of-Chains-2497cbaae9c6447b8bdb049e7acd806b
import os
from pick import pick
from CHAINS import VALIDATING_CHAINS
import re
import multiprocessing as mp
from pprint import pprint as pp

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

SYNC_FORKS = False

# global file locations relative to current filepath
current_dir = os.path.dirname(os.path.realpath(__file__))
yml_files = os.path.join(current_dir, ".yml_files")
WORKFLOWS = os.path.join(yml_files, "workflows")
ISSUE_TEMPLATE = os.path.join(yml_files, "TEMPLATES")
os.chdir(current_dir)

GO_MOD_REPLACES = { # ensure the right hand side is the latest non state beraking version
    "ibc3->ibc331": [
        ["github.com/cosmos/ibc-go/v3 v3.*.*", "github.com/cosmos/ibc-go/v3 v3.3.1"],
    ],
    "test": [
        ["github.com/gogo/protobuf v*", "github.com/gogo/protobuf v6.9.0"],
    ],
}

class GoMod():
    def __init__(self, chain):
        self.chain = chain        

    def go_mod_update(self, replace_values: list[list[str]] = [], simulate: bool = False, pause: bool = False):
        os.chdir(os.path.join(current_dir, self.chain))
        
        if "go.mod" not in os.listdir():
            print(f"{self.chain} does not have a go.mod file, skipping...")
            return

        # read go.mod data
        with open("go.mod", "r") as f:
            data = f.read()
            
        for replacements in replace_values:
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
                    print(f"{self.chain:<10} Would replace '{matches.group(0)}'\t-> {new}")    
                else:                
                    print(f"Replacing {old} with {new}")                
                    data = re.sub(old, new, data)

        if simulate == False:
            with open("go.mod", "w") as f:
                print(f"Writing go.mod for {self.chain}")
                f.write(data)

            os.system("go mod tidy")

        if pause:
            input("\nPaused, Press enter to continue...")
        os.chdir(current_dir)


class Chains():
    def __init__(self) -> None:
        self.selected_chains = self.get_downloaded_chains()
        if len(self.selected_chains) == 0:
            self.download_chains()

    def panel(self):
        options = {            
            "d": ["Download Chains", self.download_chains],
            "chains": ["Get Downloaded", self.get_downloaded_chains, True],

            "sdkv": ["Show SDK Versions", self.show_version, "SDK Versions", "sdk"],
            "ibcv": ["Show IBC Versions", self.show_version, "IBC Versions", "ibc"],

            "code": ["VSCode edit a chain", self.vscode_edit],            
            "gomod": ["Update GoMod for a chain", self.edit_single_gomod], # also need a mass edit gomod        
            "mass-gomod": ["Update gomod for many chains", self.edit_mass_gomod], # also need a mass edit gomod        

            "e": ["Exit", exit],
        }
        while True:
            print(f"\n{'='*20} CHAIN PANEL {'='*20}")
            for k, v in options.items():
                print(f"[{k:^10}] {v[0]}")
            res = input("\nSelect an option: ")
            if res in options:
                func = options[res][1]
                if len(options[res]) >= 3:
                    func(*options[res][2:])
                else:
                    func()
            else:
                print("Invalid option")    

    def vscode_edit(self):
        chain = pick(self.get_downloaded_chains(), "Select a chain to edit in VSCode")[0]
        os.system(f"code {os.path.join(current_dir, chain)}")        

    def download_chains(self, title="Select chains to do download (space to select)"):
        chain_options = sorted([chain for chain, _ in get_chains() if chain not in self.get_downloaded_chains()], key=str.lower, reverse=False)
        pick_chains = [chain[0] for chain in pick(chain_options, title, multiselect=True, min_selection_count=0, indicator="=> ")]

        if len(pick_chains) == 0:
            res = input("No chains selected, [d]ownload all or [c] continue? (d/c)").lower()
            if res == "d":
                self.selected_chains = chain_options
                download_chains(self.selected_chains)
        else:       
            download_chains(pick_chains)

        self.selected_chains = self.get_downloaded_chains()
    
    def get_downloaded_chains(self, show=False):        
        valid_chains = [chain[0] for chain in get_chains()]
        v = [folder for folder in os.listdir(current_dir) if os.path.isdir(folder) and folder in valid_chains]
        if show: 
            input(f"\n{'='*20} Downloaded Chains {'='*20}\n{', '.join(v)}\n\n(( Enter to continue... ))")
        return v
   
    def show_version(self, title, value):        
        print(f"{'='*20} {title} {'='*20}")
        versions = {}
        for chain in self.selected_chains:            
            info = get_chain_info(chain)            
            if info[value] not in versions:
                versions[info[value]] = [chain]
            else:
                versions[info[value]].append(chain)

        pp(versions, indent=4)
        input("\nPress enter to continue...")        

    # TODO:
    def edit_single_gomod(self, chain=None, simulate=False, pause=False):
        # select chains we have downloaded
        if chain == None:
            chain = pick(self.get_downloaded_chains(), "Select chain to edit go.mod", multiselect=False, min_selection_count=1)[0]

        info = get_chain_info(chain)        
        replaces = [r[0] for r in pick(list(GO_MOD_REPLACES.keys()), f"{chain} select replace values (Spaces to select)\n\tCurrent: {info}", multiselect=True, min_selection_count=1, indicator="=> ")]
        
        # combine all replaces into a single list        
        replace_values = []
        for r in replaces:
            replace_values.extend(GO_MOD_REPLACES[r])
        input(replace_values)

        GoMod(chain).go_mod_update(replace_values, simulate=simulate, pause=pause)

    def edit_mass_gomod(self):
        chains = self.get_downloaded_chains()

        sort_by = pick(['sdk', 'ibc', "wasm"], "Sort by version:")[0]

        options = {}
        for c in chains:
            info = get_chain_info(c)
            sdkv, ibc, wasm = info['sdk'], info['ibc'], info['wasm']

            new_c = f"{c} ({sdkv}, {ibc}"
            if len(wasm) > 0:
                new_c += f", {wasm}"
            new_c += ")"

            if sort_by not in options:
                options[info[sort_by]] = [new_c]
            else:
                options[info[sort_by]].append(new_c)

        # ssorts keys based off of the version of the value we want (ex: largest sdk version to smallest)
        options = [options[k] for k in sorted(options.keys(), key=lambda x: [int(i) for i in x.replace("v", "").split(".") if len(x) > 0], reverse=True)]
        options = [item for sublist in options for item in sublist]                

        selected_chains = [chain[0].split(" ")[0] for chain in pick(options, "Select chains to edit go.mod (sdk, ibc, wasm)", multiselect=True, min_selection_count=1, indicator="=> ")]
        print(f"selected_chains={selected_chains}")

        for chain in selected_chains:
            self.edit_single_gomod(chain=chain, simulate=True, pause=True)  
        


    def add_workflows(self):
        pass

def main():
    # vers = get_chain_versions()
    # pp(vers['ibc'])
    
    chains = Chains()

    chains.panel()

    # workflows
    # for chain in chains.selected_chains:        
    #     Workflow(chain).add_workflows()


    # for chain, _ in get_chains():
    #     Workflow(chain).add_dependabot(simulate=True)        
        # workflows(chain)

        # go_mod_update(chain, [
        #     ["github.com/cosmos/ibc-go/v3 v3.3.0", "github.com/cosmos/ibc-go/v3 v3.3.1"],
        # ], simulate=False)
        # # TODO: when we do update, we need to create a new git branch for us to PR off of (do not build off of main)

        # open_in_vscode(chain)
        # # lint(chain)
        # pass

# === Logic ===
def get_chains():
    for chain, locations in VALIDATING_CHAINS.items():
        yield chain, locations    

def get_chain_info(folder_name):
    sdk_version, ibc_version, wasm_version, wasmvm = "", "", "", ""

    with open(os.path.join(current_dir, folder_name, "go.mod"), "r") as f:
        data = f.read()
    
    for line in data.split("\n"):
        if re.search(r"(.*)\sv\d+\.\d+\.\d+", line):
            version = line.split(" ")[1] # -1 or 2 = // indirect in some cases
            if not re.search(r"\d", version):
                # if version does not contain any numbers, then continue
                continue

            if "=>" in line:
                continue

            if "github.com/CosmWasm/wasmd" in line:
                wasm_version = line.split(" ")[1] or ""
            elif "github.com/CosmWasm/wasmvm" in line:
                wasmvm = line.split(" ")[1] or ""
            elif "github.com/cosmos/ibc-go" in line:
                ibc_version = line.split(" ")[1] or ""
            elif "github.com/cosmos/cosmos-sdk" in line:
                sdk_version = line.split(" ")[1] or ""

    return {
        "sdk": sdk_version,
        "ibc": ibc_version,
        "wasm": wasm_version,
        "wasmvm": wasmvm,
    }

def get_chain_versions():
    sdk_chain_version, ibc_version, wasm_ver, wasmvm_ver = {}, {}, {}, {}

    for chain, _ in get_chains():
        info = get_chain_info(chain)
        sdk_version = info["sdk"]
        ibc = info["ibc"]
        wasm = info["wasm"]
        wasmvm = info["wasmvm"]

        if sdk_version not in sdk_chain_version:
            sdk_chain_version[sdk_version] = []
        sdk_chain_version[sdk_version].append(chain)

        if ibc not in ibc_version:
            ibc_version[ibc] = []
        ibc_version[ibc].append(chain)

        if wasm not in ibc_version:
            wasm_ver[wasm] = []
        wasm_ver[wasm].append(chain)

        if wasmvm not in ibc_version:
            wasmvm_ver[wasmvm] = []
        wasmvm_ver[wasmvm].append(chain)
    
    return {
        "sdk": sdk_chain_version,
        "ibc": ibc_version,
        "wasm": wasm_ver,
        "wasmvm": wasmvm_ver,
    }

def download_chains(select_chains: list = []):
    to_run = []
    for chain, loc in get_chains():
        if len(select_chains) > 0 and chain not in select_chains:
            continue
        to_run.append((chain, SYNC_FORKS))

    # run all to_run in parallel with mp
    with mp.Pool(mp.cpu_count()) as pool:
        pool.starmap(pull_latest, to_run)

def pull_latest(folder_name, repo_sync=False):
    # git clone if it is not there already, if it is, cd into dir and git pull    
    os.chdir(current_dir)

    parent_link = VALIDATING_CHAINS[folder_name]["root"]    
    repo_link = VALIDATING_CHAINS[folder_name]["notional"]    

    # check if folder_name exists
    if not os.path.isdir(os.path.join(current_dir, folder_name)):        
        print(f"Cloning {folder_name} from {repo_link}")
        os.system(f"git clone {repo_link} {folder_name}")
        os.chdir(os.path.join(current_dir, folder_name))
        os.system(f"git remote add upstream {repo_link}") # may want to do this after cloning

    os.chdir(os.path.join(current_dir, folder_name))
    if repo_sync:
        print(f"Syncing fork to latest of parent main/master branch (overwriting any main/master changes)")    
        os.system(f"gh repo sync {repo_link.replace('git@github.com:', '').replace('.git', '')} --force")

    # pull after we sync to the new files in the notional repo which we will build off of
    os.system("git pull origin")  
    # os.system("git pull upstream")

    os.chdir(current_dir)

# === Linting ===
class Lint():
    def __init__(self, folder_name) -> None:
        self.folder_name = folder_name        

    def auto_fix(self):
        self._cmd("golangci-lint run --fix")

    def gofmt(self):
        self._cmd("gofmt -s -w .")
    
    def govet(self):
        self._cmd("go vet ./...")

    def tidy(self):
        self._cmd("go mod tidy")

    def _cmd(self, cmd):
        os.chdir(os.path.join(current_dir, self.folder_name))
        os.system(cmd)
        os.chdir(current_dir)

def lint_all(folder_name):
    print(f"Linting {folder_name}...")    
    l = Lint(folder_name)
    l.auto_fix()
    l.gofmt()
    l.govet()
    l.tidy()
    

# === Workflows ===
class Workflow():
    def __init__(self, folder_name) -> None:
        self.folder_name = folder_name
        self.chain_dir = os.path.join(current_dir, self.folder_name)

    def available_workflows(self):          
        return os.listdir(WORKFLOWS)

    def _write_workflow(self, workflow_name):
        if workflow_name not in self.available_workflows():
            print(f"Workflow {workflow_name} not found in {WORKFLOWS}")
            return

        main_branch_name = VALIDATING_CHAINS[self.folder_name]["branch"]
        
        os.chdir(os.path.join(current_dir, self.folder_name))
        print(f"Writing {workflow_name} to .github/workflows/{workflow_name} for {self.folder_name}")
        with open(os.path.join(yml_files, "workflows", workflow_name), "r") as f2:
            with open(f".github/workflows/{workflow_name}", "w") as f:
                f.write(f2.read().replace("_MAIN_BRANCH_", main_branch_name))
        os.chdir(current_dir)

    def add_workflows(self):
        os.chdir(self.chain_dir)
        if not os.path.exists(".github/workflows"):
            os.makedirs(".github/workflows", exist_ok=True) 

        workflow_options = [x for x in os.listdir(WORKFLOWS) if x not in os.listdir(".github/workflows")]

        title = "Workflow options to install (space, then enter) [ignores already installed]"
        selected = [s[0] for s in pick(workflow_options, title, multiselect=True, min_selection_count=0, indicator="=> ")]

        for file in selected:
            self._write_workflow(file)
        os.chdir(current_dir)

    def add_dependabot(self, simulate=False):
        # check if self.folder_name/.github exists, if so see if any files have "dependabot" in them        
        p = os.path.join(self.chain_dir, ".github")
        if not os.path.isdir(p):
            os.mkdir(p)
        
        containsDependABot = False
        for root, dirs, files in os.walk(p, topdown=True):
            for name in files:                
                if "dependabot" in name:
                    containsDependABot = True
                    break

        if containsDependABot:
            if simulate == False:
                print(f"{self.folder_name} already has dependabot")
            return

        # https://github.com/eve-network/eve, put in .yml_files folder
        # check if folder chains .github/dependabot.yml dir        
        main_branch = VALIDATING_CHAINS[self.folder_name]["branch"] # main, master, etc

        if simulate:
            print(f"SIMULATE: Would add dependabot to {self.folder_name}")
            return
        else:
            print(f"Adding dependabot to {self.folder_name}...")
            os.chdir(self.chain_dir)
            if not os.path.exists(".github/dependabot.yml"):
                os.makedirs(".github", exist_ok=True)        
                # write yml_files/dependabot.yml to .github/dependabot.yml
                print(f"Writing dependabot.yml to .github/dependabot.yml for {self.folder_name} as it did not have it...")
                with open(f".github/dependabot.yml", "w") as f:
                    with open(os.path.join(yml_files, "dependabot.yml"), "r") as f2:
                        f.write(f2.read().replace("_MAIN_BRANCH_", main_branch))
            os.chdir(current_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:        
        print("\nExited via keyboard quit...")