from Utils import *

from pprint import pprint as pp

from webbrowser import open as open_url

from Panel_Chains import Git

def _main():
    from main import main
    VersionPanel().panel(main)

class VersionPanel():
    def panel(self, main_panel_func):
        options = {            
            "s": ["SDK", self.show_version, "SDK Versions", "sdk"],
            "i": ["IBC", self.show_version, "IBC Versions", "ibc"],
            "w": ["CosmWasm", self.show_version, "CosmWasm Versions", "wasm"],
            "t": ["Tendermint", self.show_version, "Tendermint Versions", "tm"],
            "a": ["IAVL", self.show_version, "IAVL Versions", "iavl"],

            "": [""],
            "v": ["View Latest Versions", self.get_latest_versions],            

            "": [""], # BLANK SPACE
            "m": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases={}
        while True:
            selector("&e", "Versions", options=options, aliases=aliases)

    def get_latest_versions(self, per_group: int = 3):
        from main import MAJOR_REPOS

        repo = pick(list(MAJOR_REPOS.keys()), "Select a repo to view latest versions", multiselect=False)[0]
        repo_link = MAJOR_REPOS[repo]
          
        # ignore_tags = [x[0] for x in pick(["-rc", "beta", "alpha"], "Tags to Ignore:", multiselect=True, min_selection_count=0, indicator='=> ')]
        tags = Git().get_latest_tags(repo_link, ignore_tags_substrings=[])        

        new = {}
        for k, v in tags.items():
            # print(k, sorted(v), '\n')
            new[k] = sorted(v, key=lambda x: x.number)[-per_group::] # latest X number
            new[k] = [i.real for i in new[k]] # show their real value ex: 0.44.5

        pp(new, indent=4)
        cinput("\n&ePress enter to continue...")


    def show_version(self, title, value):        
        print(f"{'='*20} {title} {'='*20}")
        versions = {}

        from main import get_chain_info # TODO: bad, change this in the future

        for chain in get_downloaded_chains():
            info = get_chain_info(chain)
            if info[value] not in versions:
                versions[info[value]] = [chain]
            else:
                versions[info[value]].append(chain)
        
        if '' in versions: del versions['']

        pp(versions, indent=4)
        cinput("\n&ePress enter to continue...")

if __name__ == "__main__":
    _main()