from Utils import *

import multiprocessing as mp
import shutil
import requests

def _main():
    from main import main
    ChainsPanel().panel(main)

class ChainsPanel():
    def panel(self, main_panel_func):
        options = {            
            "d": ["Download Chains", self.download_chains],
            "p": ["Pull Latest Down", self.pull_latest_down],            
            "c": ["Get Local Chains\n", get_downloaded_chains, True],

            "m": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases = {}
        while True:
            selector("&f", "Chains / Git", options=options, aliases=aliases)

    def download_chains(self, title="Select chains to do download (space to select) [leave empty for all]"):
        chain_options = sorted([chain for chain, _ in get_chains() if chain not in get_downloaded_chains()], key=str.lower, reverse=False)
        if len(chain_options) == 0:
            cinput("&eAll chains are downloaded already...\n&fEnter to continue")
            return

        pick_chains = [chain[0] for chain in pick(chain_options, title, multiselect=True, min_selection_count=0, indicator="=> ")]        

        if len(pick_chains) == 0:
            res = input("No chains selected, [d]ownload all or [c] continue? (d/c): ").lower()
            if res == "d":                
                Git().download_chains_locally(chain_options)
        else:       
            Git().download_chains_locally(pick_chains)

    def pull_latest_down(self):
        '''
        Pulls syncs, and fetches the latest changes for already downloaded chains                        
        '''
        chains = select_chains("Select chains you want to pull. (space to select, none for all)")

        from main import Git # TODO: BAD PRACTICE, CHANGE THIS IN THE FUTURE
        Git().download_chains_locally(chains)


class Git():
    def __init__(self):
        from main import VALIDATING_CHAINS
        self.VALIDATING_CHAINS = VALIDATING_CHAINS


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

    def sync_forks(self, repo_link:str = "", enabled:bool = False):
        '''
        NOTE: You must already be in the repo dir to run this.
        '''
        if shutil.which("gh") != None: # check if user has gh installed
            print(f"Syncing fork to latest of parent main/master branch (overwriting any main/master changes)")    
            os.system(f"gh repo sync {repo_link.replace('git@github.com:', '').replace('.git', '')} --force")        
        else:
            print("You need to install github cli (gh) to sync forks. See https://cli.github.com/")
            return

    def get_latest_tags(self, repo_link:str = "", ignore_tags_substrings:list = []):
        if 'git@github.com:' in repo_link:
            repo_link = repo_link.replace('git@github.com:', '').replace('.git', '')
        
        API = f"https://api.github.com/repos/{repo_link}/releases" # /releases or /tags?
        v = requests.get(API).json()
        versions = []
        for doc in v:
            tag_name = doc["tag_name"]
            ignore = False
            if len(ignore_tags_substrings) > 0:
                for sub in ignore_tags_substrings:
                    if sub in tag_name:
                        ignore = True
                    
            if not ignore:
                versions.append(tag_name)

        return sorted(versions)

    def pull_latest(self, folder_name, repo_sync=False):
        # git clone if it is not there already, if it is, cd into dir and git pull    
        os.chdir(current_dir)

        # parent_link = VALIDATING_CHAINS[folder_name]["parent"]    
        repo_link = self.VALIDATING_CHAINS[folder_name]["fork"]    
        
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

if __name__ == "__main__":
    _main()