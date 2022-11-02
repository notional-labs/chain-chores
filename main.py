# https://www.notion.so/List-Of-Chains-2497cbaae9c6447b8bdb049e7acd806b
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
- when we update code, we need to create a new git branch for us to PR off of (do not build off of main) [probably fine with the vscode option]
- Multiple panels ex: repo management (download, pull/fetch, and sync branches)
'''

import multiprocessing as mp
import datetime
import shutil
import os
import re

from subprocess import PIPE, Popen
from pprint import pprint as pp

from pick import pick
from webbrowser import open as open_url

from CHAINS import VALIDATING_CHAINS
from Utils import cfiglet, cinput, cprint
from Linting import Linting

# === SETTINGS ===
SYNC_FORKS = False
SIMULATION = True

GO_MOD_REPLACES = { # ensure the right hand side is the latest non state beraking version
    "ibc3->ibc331": [
        ["github.com/cosmos/ibc-go/v3 v3.*.*", "github.com/cosmos/ibc-go/v3 v3.3.1"],
    ],
    "test": [
        ["github.com/gogo/protobuf v*", "github.com/gogo/protobuf v6.9.0"],
    ],
}

# === FILE PATHS ===
GIT_PATHS = ["parent", "fork"]
current_dir = os.path.dirname(os.path.realpath(__file__))
yml_files = os.path.join(current_dir, ".yml_files")
test_output = os.path.join(current_dir, ".test_output")
WORKFLOWS = os.path.join(yml_files, "workflows")
ISSUE_TEMPLATE = os.path.join(yml_files, "TEMPLATES")
for paths in [test_output, yml_files, WORKFLOWS, ISSUE_TEMPLATE]:    
    os.makedirs(paths, exist_ok=True)
os.chdir(current_dir)

# === Main Function ===
def main():    
    Chains().panel()

# === CLASSES ===
class Chains():
    def __init__(self) -> None:
        self.selected_chains = self.get_downloaded_chains()
        if len(self.selected_chains) == 0:
            self.download_chains()

    def _select_chains(self, title, min_selection_count=0) -> list[str]:
        chains = [c[0] for c in pick(self.get_downloaded_chains(), title, multiselect=True, min_selection_count=min_selection_count, indicator="=> ")]
        if len(chains) == 0: chains = self.get_downloaded_chains()
        return chains

    def panel(self):
        options = {            
            "d": ["Download Chains", self.download_chains],
            "p": ["Pull Latest Down", self.pull_latest_down],
            "chains": ["Get Downloaded", self.get_downloaded_chains, True],

            "t": ["Test chains", self.test],
            "b": ["Build chains", self.build],
            # "lint": ["Test chains", self.linting],

            "sdkv": ["Show SDK Versions", self.show_version, "SDK Versions", "sdk"],
            "ibcv": ["Show IBC Versions", self.show_version, "IBC Versions", "ibc"],

            "code": ["VSCode edit a chain", self.vscode_edit],            
            "gomod": ["Update GoMod for a chain", self.edit_single_gomod],    
            "mass-gomod": ["Update gomod for many chains", self.edit_mass_gomod], 

            "flows": ["Workflows", self.workflows],   
            "dbot": ["Adds dependabot if not already", self.dependabot],   


            "web": ["Open chains github pages", self.website],   

            "e": ["Exit", exit],
        }
        while True:            
            cfiglet("&a", "Chain Chores", True)
            for k, v in options.items():
                print(f"[{k:^10}] {v[0]}")            
            res = cinput("\n&fSelect an option: ").lower()
            if res in options:
                func = options[res][1]
                if len(options[res]) >= 3:
                    func(*options[res][2:])
                else:
                    func()
            else:
                cprint("&aInvalid option")    

    def pull_latest_down(self):
        '''
        Pulls syncs, and fetches the latest changes for already downloaded chains                        
        '''
        chains = self._select_chains("Select chains you want to pull. (space to select, none for all)")        
        Git().download_chains_locally(chains)

    def test(self):
        chains = self._select_chains("Select chains you want to test. (space to select, none for all)")
        to_run = []        
        for chain in chains:                   
            to_run.append(Testing(chain))

        with mp.Pool(mp.cpu_count()) as p:
            p.map(Testing.run_tests, to_run)   

    def build(self):
        chains = self._select_chains("Select chains you want to build. (space to select, none for all)")
        to_run = []        
        for chain in chains:            
            to_run.append(Testing(chain))            
        with mp.Pool(mp.cpu_count()) as p:
            p.map(Testing.build_binary, to_run)


    def website(self):        
        chains = self._select_chains("Select a chain(s) to open the website for (space to select)")
        location = pick(GIT_PATHS, "Open the 'parent' repo or 'fork' version? (select 1)")[0]
        cprint(f"Opening Website for: {','.join(chains)}...")
        for chain in chains:
            info = VALIDATING_CHAINS.get(chain, None)
            if info == None: continue
            url_path = info[location].replace(".git", "").split(":")[1]            
            open_url(f"https://github.com/{url_path}")                

    def workflows(self):
        # select a chain, and add workflows to it
        chain = pick(self.selected_chains, "Select a chain to add workflows to")[0]
        # os.chdir(os.path.join(current_dir, chain))
        cprint(f"&aAdding workflows to {chain}")
        Workflow(chain).add_workflows()

    def dependabot(self): # combine with workflows?
        chain = pick(self.selected_chains, "Select a chain to add dependabot to")[0]
        cprint(f"&aAdding dependabot to {chain} if it is not already there")
        Workflow(chain).add_dependabot()

    def vscode_edit(self):
        chains = self._select_chains("Select chains to edit in VSCode", min_selection_count=1)
        for c in chains:
            os.system(f"code {os.path.join(current_dir, c)}")        

    def download_chains(self, title="Select chains to do download (space to select) [leave empty for all]"):
        chain_options = sorted([chain for chain, _ in get_chains() if chain not in self.get_downloaded_chains()], key=str.lower, reverse=False)
        if len(chain_options) == 0:
            cinput("&eAll chains are downloaded already...\n&fEnter to continue")
            return

        pick_chains = [chain[0] for chain in pick(chain_options, title, multiselect=True, min_selection_count=0, indicator="=> ")]

        if len(pick_chains) == 0:
            res = input("No chains selected, [d]ownload all or [c] continue? (d/c): ").lower()
            if res == "d":
                self.selected_chains = chain_options
                Git().download_chains_locally(self.selected_chains)
        else:       
            Git().download_chains_locally(pick_chains)

        self.selected_chains = self.get_downloaded_chains()
    
    def get_downloaded_chains(self, show=False):        
        valid_chains = [chain[0] for chain in get_chains()]
        v = [folder for folder in os.listdir(current_dir) if os.path.isdir(folder) and folder in valid_chains]        
        v.sort(key=str.lower)

        if show: 
            cinput(f"\n&a{'='*20} Downloaded Chains {'='*20}\n&f{', '.join(v)}\n\n(( Enter to continue... ))")
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
        cinput("\n&ePress enter to continue...")

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
        cinput(replace_values)

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
            self.edit_single_gomod(chain=chain, simulate=SIMULATION, pause=True)  

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

class Git():
    def __init__(self) -> None:
        pass

    def download_chains_locally(self, select_chains: list = []):
        to_run = []
        sync_forks = input("Sync forks as well when you download? (y/n): ").lower() == "y"
        for chain, loc in get_chains():
            if len(select_chains) > 0 and chain not in select_chains:
                continue
            # to_run.append((chain, SYNC_FORKS))
            to_run.append((chain, sync_forks))

        # run all to_run in parallel with mp
        with mp.Pool(mp.cpu_count()) as pool:
            pool.starmap(self.pull_latest, to_run)

    def sync_forks(self, repo_link:str = "", enabled:bool = SYNC_FORKS):
        '''
        NOTE: You must already be in the repo dir to run this.
        '''
        if shutil.which("gh") != None: # check if user has gh installed
            print(f"Syncing fork to latest of parent main/master branch (overwriting any main/master changes)")    
            os.system(f"gh repo sync {repo_link.replace('git@github.com:', '').replace('.git', '')} --force")        
        else:
            print("You need to install github cli (gh) to sync forks. See https://cli.github.com/")
            return

    def pull_latest(self, folder_name, repo_sync=False):
        # git clone if it is not there already, if it is, cd into dir and git pull    
        os.chdir(current_dir)

        # parent_link = VALIDATING_CHAINS[folder_name]["parent"]    
        repo_link = VALIDATING_CHAINS[folder_name]["fork"]    
        
        if not os.path.isdir(os.path.join(current_dir, folder_name)):        
            print(f"Cloning {folder_name} from {repo_link}")
            os.system(f"git clone {repo_link} {folder_name}")
            os.chdir(os.path.join(current_dir, folder_name))
            os.system(f"git remote add upstream {repo_link}") # may want to do this after cloning

        os.chdir(os.path.join(current_dir, folder_name))
        if repo_sync:    
            self.sync_forks(repo_link=repo_link, enabled=repo_sync)
        # pull after we sync to the new files in the notional repo which we will build off of
        os.system("git pull origin")  
        # os.system("git pull upstream")
        os.chdir(current_dir)   

# === Logic === (move these into Chains class)
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
    sdk_chain_version, ibc_version, wasm_ver = {}, {}, {}

    for chain, _ in get_chains():
        info = get_chain_info(chain)
        sdk_version = info["sdk"]
        ibc = info["ibc"]
        wasm = info["wasm"]
        
        sdk_chain_version.get(sdk_version, []).append(chain)        
        ibc_version.get(ibc, []).append(chain)
        wasm_ver.get(wasm, []).append(chain)        
    
    return {
        "sdk": sdk_chain_version,
        "ibc": ibc_version,
        "wasm": wasm_ver,
    }


class Testing():
    def __init__(self, chain) -> None:
        self.chain = chain

    def build_binary(self):
        '''
        Build binary (appd) from makefile if it is there, if not, go install ./...
        '''
        os.chdir(os.path.join(current_dir, self.chain))        
        if not os.path.isfile("Makefile"):
            cprint(f"&6[!] No Makefile, {self.chain} (go install ./...)")
            os.system("go install ./...")
            return
        
        with open("Makefile", "r") as f:
            data = f.read()
            if "install:" not in data:
                cprint(f"&6[!] No 'install' in makefile, {self.chain} (go install ./...)")
                os.system("go install ./...")
                return
        
        cprint(f"&a[+] Building {self.chain} from Makefile install")
        os.system("make install")
        os.chdir(os.path.join(current_dir))

    def run_tests(self, hideNoTestFound=False):
        '''
        go test ./... and saves output to a single file appending more on each run
        '''
        os.chdir(os.path.join(current_dir, self.chain))
        cprint(f"&e[+] Running tests for {self.chain}")
        
        # run go test ./... and save output to a file including stderr and stdout
        p = Popen(["go", "test", "./..."], stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()

        output = output.decode("utf-8")
        err = err.decode("utf-8")

        updated_err = "" # fix go downloading writing to stderr since we don' care
        for line in err.split("\n"):
            if "go: downloading" not in line:                
                updated_err += line + "\n"

        if hideNoTestFound: 
            # optionally hide the files which have no test files in given packages (frees up clutter)
            new_output = ""
            for line in output.split("\n"):
                if "no test files" not in line:
                    new_output += line + "\n"
            output = new_output

        # # save to a file as current_dir/testing.txt
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(test_output, "testing.txt"), "a") as f:
            f.write(f"="*40)
            f.write(f"\n{self.chain} {current_time}\n{output}\n\n")

        if len(err) > 0:
            with open(os.path.join(test_output, "errors.txt"), "a") as f:
                f.write(f"="*40)               
                f.write(f"\n{self.chain} {current_time}\n{err}\n\n")
        
        cprint(f"&a[+] Test finished for {self.chain}")
        os.chdir(os.path.join(current_dir))
            
        



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
