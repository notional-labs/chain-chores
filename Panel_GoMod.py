


from Utils import *

import multiprocessing as mp
from datetime import date

from Panel_Chains import Git

from subprocess import Popen, PIPE

def _main():
    from main import main
    GoModPanel().panel(main)

class GoModPanel():
    def panel(self, main_panel_func):
        options = {            
            "1": ["Update GoMod for a chain", self.edit_single_gomod],    
            "2": ["Update GoMod for many chains", self.edit_mass_gomod], 
            "3": ["Apply all updates", self.apply_all], 

            "": [""],
            "m": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases = {}
        while True:
            selector("&e", "Go Mod", options=options, aliases=aliases)

    # TODO:
    def edit_single_gomod(self, chain=None, simulate=False, pause=False):
        from main import get_chain_info, GO_MOD_REPLACES

        # select chains we have downloaded
        if chain == None:
            chain = pick(get_downloaded_chains(), "Select chain to edit go.mod", multiselect=False, min_selection_count=1)[0]

        info = get_chain_info(chain)        
        replaces = [r[0] for r in pick(list(GO_MOD_REPLACES.keys()), f"{chain} select replace values (Spaces to select)\n\tCurrent: {info}", multiselect=True, min_selection_count=1, indicator="=> ")]
        
        # combine all replaces into a single list        
        replace_values = []
        for r in replaces:
            replace_values.extend(GO_MOD_REPLACES[r]['replace'])

        commit_and_push = cinput("Commit and push? (y/n): ").lower().startswith("y")
        make_pr = commit_and_push and cinput("Create pull request on web? (y/n): ").lower().startswith("y")

        GoMod(chain).go_mod_update(replace_values, simulate=simulate, pause=pause, branch_name=branch_name(), vscode_prompt=True, commit_and_push=commit_and_push, make_pr=make_pr)


    def edit_mass_gomod(self):
        from main import get_chain_info, SIMULATION

        chains = get_downloaded_chains()

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

        # print(options)
        # exit(1)

        # sorts keys based off of the version of the value we want (ex: largest sdk version to smallest)
        options = [options[k] for k in sorted(options.keys(), reverse=True)]
        final = []
        for opt in options:            
            final.extend(opt)

        selected_chains = [chain[0].split(" ")[0] for chain in pick(final, "Select chains to edit go.mod (sdk, ibc, wasm)", multiselect=True, min_selection_count=1, indicator="=> ")]
        print(f"selected_chains={selected_chains}")

        for chain in selected_chains:
            self.edit_single_gomod(chain=chain, simulate=SIMULATION, pause=True)
            

    def apply_all(self, simulate=False, pause=False):
        from main import get_chain_info, SIMULATION, GO_MOD_REPLACES, VALIDATING_CHAINS
        chains = get_downloaded_chains()

        simulate = input("Simulate? (y/n): ").lower().startswith("y")

        replaces = [r[0] for r in pick(list(GO_MOD_REPLACES.keys()), f"Select replace values (Spaces to select)\n\tCurrent", multiselect=True, min_selection_count=1, indicator="=> ")]
        # combine all replaces into a single list        
        replace_values = []
        for r in replaces:
            replace_values.extend(GO_MOD_REPLACES[r]['replace'])        

        bname = branch_name()

        commit_and_push = cinput("Commit and push? (y/n): ").lower().startswith("y")
        pull_request = cinput("Create pull request on web? (y/n): ").lower().startswith("y")

        success_chains = []
        for chain in chains:
            res = GoMod(chain).go_mod_update(
                replace_values, simulate=simulate, pause=pause, branch_name=bname, 
                vscode_prompt=False, skip_write_validation=True, 
                commit_and_push=commit_and_push, make_pr=pull_request
            )
            if res == True:
                success_chains.append(chain)

        print(f"Success: {success_chains}")

        if len(success_chains) > 0:
            open_in_vscode_prompt(success_chains)

        cinput("Press enter to continue...")

def open_in_vscode_prompt(chains: str | list):
    if input(f"Open all in VSCode? (y/n)").lower().startswith('y'):
        if type(chains) == str: chains = [chains]
        for chain in chains:                
            os.system(f"code {os.path.join(current_dir, chain)}")

def branch_name() -> str:
    # t = date.today()
    default_name = f'cchores_gomod'
    branch_name = cinput(f"&eBranch name: &7{default_name} : ") or default_name
    return branch_name

class GoMod():
    def __init__(self, chain):
        self.chain = chain        

    def go_mod_update(
        self, 
        replace_values: list[list[str]] = [], simulate: bool = False, 
        pause: bool = False, branch_name: str = "", vscode_prompt=False, 
        skip_write_validation=False, commit_and_push=False,
        make_pr=False
    ) -> bool:

        from main import VALIDATING_CHAINS
        SUCCESS = False

        os.chdir(os.path.join(current_dir, self.chain))           
        
        if "go.mod" not in os.listdir():
            print(f"{self.chain} does not have a go.mod file, skipping...")
            return

        # read go.mod data
        with open("go.mod", "r") as f:
            data = f.read()
            
        successful_replacements = []
        for replacements in replace_values:
            old = replacements[0]
            new = replacements[1]


            # Example: old: cosmos/cosmos-sdk v0.46.*. new: cosmos/cosmos-sdk v0.46.4    
            matches = re.search(old, data)            
            
            # isIndirect = '// indirect' in old

            skip = False
            # manually ignore things, can likely remove this in the future.
            if 'ignore_updates' in VALIDATING_CHAINS[self.chain].keys():
                for repl in replacements:
                    for ignore in VALIDATING_CHAINS[self.chain]['ignore_updates']:
                        if ignore.lower() in repl.lower():
                            skip = True
            
            # Skip custom forks of a replacement
            base = new.split(" ")[0] # ex: cosmos/cosmos-sdk            
            if f"{base} =>" in data:
                cprint(f"&e[{self.chain}] Custom fork: {base}. Skipping.")
                skip = True

            if skip: 
                continue            

            if matches: # allow for us to use regex
                if matches.group(0) == new:
                    # ensure the matches are not exactly the new value
                    # print(f"Skipping {old} as it is already {new}")
                    continue

                if simulate:   
                    # get the matches in string form from matches                         
                    print(f"{self.chain:<10} Would replace '{matches.group(0)}'\t-> {new}")    
                else:                
                    old = matches.group(0)
                    if '// indirect' in old:
                        new.rstrip()
                        new += ' // indirect'

                    if old != new:
                        data = re.sub(old, new, data)
                        successful_replacements.append([old, new])

        if simulate == False:
            # prettyprint successful_replacements
            if len(successful_replacements) > 0:
                cprint(f"&aSuccessfully replaced &f{len(successful_replacements)} &avalues in &f{self.chain}")
                SUCCESS = True
                for r in successful_replacements:
                    cprint(f"\t&c{r[0]} &f-> &a{r[1]}")
                if not skip_write_validation: cinput("&6Press enter to continue and write to gomod...")

            with open("go.mod", "w") as f:
                print(f"Writing go.mod for {self.chain}")
                f.write(data)
                            
            stdout, stderr = run_cmd("go mod tidy")
            for line in stderr.split('\n'):
                if 'go mod tidy -compat=' in line:                    
                    stdout, stderr = run_cmd(line.strip())
                    print('stderr', stderr)
                    break
            
            if len(branch_name) > 0:            
                cprint(f"Creating new branch {branch_name}")
                Git().create_branch(self.chain, branch_name, cd_dir=False)
                if commit_and_push:
                    cprint(f"Committing changes for {branch_name}")
                    # Git().commit(self.chain, cd_dir=False, vscode_prompt=vscode_prompt)
                    Git().commit(self.chain, "chore(deps): Dependency Bumps [chain-chores]")
                    Git().push(self.chain, branch_name=branch_name, repo_name="origin") # our fork
                    if make_pr:
                        changes = ""
                        for r in successful_replacements:                            
                            changes += f"- {r[0]} -> {r[1]}\n"
                        Git().pull_request(self.chain, cd_dir=False, changes=changes)

            if vscode_prompt:
                open_in_vscode_prompt([self.chain])       

        if pause:
            input("\nPaused, Press enter to continue...")

        os.chdir(current_dir)
        return SUCCESS

def run_cmd(cmd):
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    proc.wait()
    err = proc.stderr.read().decode()
    out = proc.stdout.read().decode()
    return out, err

if __name__ == "__main__":
    _main()