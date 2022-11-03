


from Utils import *

import multiprocessing as mp

def _main():
    from main import main
    GoModPanel().panel(main)

class GoModPanel():
    def panel(self, main_panel_func):
        options = {            
            "g": ["Update GoMod for a chain", self.edit_single_gomod],    
            "m": ["Update GoMod for many chains\n", self.edit_mass_gomod], 

            "main": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases = {}
        while True:
            selector("&e", "Git", options=options, aliases=aliases)

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
            replace_values.extend(GO_MOD_REPLACES[r])
        cinput(replace_values)

        GoMod(chain).go_mod_update(replace_values, simulate=simulate, pause=pause)

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

if __name__ == "__main__":
    _main()