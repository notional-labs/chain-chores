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
            "u": ["Check updates", self.check_for_updates],
            "": [""],
            "s": ["SDK", self.show_version, "SDK Versions", "sdk"],
            "i": ["IBC", self.show_version, "IBC Versions", "ibc"],
            "w": ["CosmWasm", self.show_version, "CosmWasm Versions", "wasm"],
            "t": ["Tendermint", self.show_version, "Tendermint Versions", "tm"],
            "a": ["IAVL", self.show_version, "IAVL Versions", "iavl"],

            "": [""],
            "v": ["View Latest Versions", self.get_latest_versions],            

            "": [""],
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

    def check_for_updates(self):
        from main import MAJOR_REPOS, GO_MOD_REPLACES
        latest = {}
        # {
        #   'ibc-go': {'3': ['3.3.1', '3.4.0'], '4': ['4.1.1', '4.2.0'], '5': ['5.0.0-rc2', '5.0.1'], '6': ['6.0.0-alpha1', '6.0.0-beta1']}, 
        #   'tm': {'34': ['0.34.21', '0.34.22'], '35': ['0.35.9-rc0', '0.35.9'], '36': ['0.36.0-de'], '37': ['0.37.0-rc1']}
        # }
        limit = 3
        for k, v in GO_MOD_REPLACES.items():    
            repo_link = MAJOR_REPOS.get(k, None)
            tags = Git().get_latest_tags(repo_link, ignore_tags_substrings=[])
            # gets the latest versions for a given group & their major version groups.
            latest[k] = {k2: [i.real for i in sorted(v2, key=lambda x: x.number)[-limit::]] for k2, v2 in tags.items()}   
            # {'ibc-go': {'3': ['3.3.0', '3.3.1', '3.4.0'], '4': ['4.1.0', '4.1.1', '4.2.0'], '5': ['5.0.0-rc1', '5.0.0-rc2', '5.0.1'], '6': ['6.0.0-alpha1', '6.0.0-beta1']}}    
            
            # DEBUGGING
            # latest['iavl'] = {'13': ['0.13.1', '0.13.2', '0.13.3'], '14': ['0.14.1', '0.14.2', '0.14.3'], '15': ['0.15.1', '0.15.2', '0.15.3'], '16': ['0.16.0'], '17': ['0.17.1', '0.17.2', '0.17.3'], '18': ['0.18.0'], '19': ['0.19.2', '0.19.3', '0.19.4']}

            for r in GO_MOD_REPLACES[k]['replace']:
                # plain_version = str(r[1]).split(" ")[-1].replace('v', '')
                plain_version = str(r[1]).split(" ", 1)[-1].replace('v', '')
                if '// indirect' in plain_version:
                    plain_version = plain_version.split(" ", 1)[0]                

                l = len(plain_version.split('.'))
                if l > 3:
                    # print('broken version', plain_version)
                    continue # weird versioning with wasmd

                s, m, e = plain_version.split('.')
                if s == '0': s = m                           

                if s in latest[k]:
                    # print(latest[k][s]) # ['5.0.0-rc1', '5.0.0-rc2', '5.0.1']
                    latest_ver = latest[k][s][-1]            
                    # print('latest_ver', latest_ver)        

                    if plain_version != latest_ver:                        
                        print(f"UPDATE: {k} (v{s}) {plain_version} -> {latest_ver}")

        input("Press enter to continue...")

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