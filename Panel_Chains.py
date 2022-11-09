from Utils import *

from dataclasses import dataclass

import multiprocessing as mp
import shutil
import requests
import re

@dataclass
class Version:
    def __init__(self, real: str, number: int = 0):
        self.real = real        
        self.number = number

    # create a sort / compare function
    def __lt__(self, other):        
        return self.number < other.number and self.sub_version < other.sub_version

    def __gt__(self, other):
        return self.number > other.number and self.sub_version > other.sub_version

    def __eq__(self, other):
        return self.number == other.number and self.sub_version == other.sub_version        

    real: str
     # ex: 0.44.5 = 445. Useful for sorting
    number: int 
    # ex: -alpha1, -beta1, -rc1 (sort first character then sub number. a=0, ...)
    # so -alpha2 = 02. -beta2 = 22, -rc2 = 272 (r = 27)
    sub_version: int 

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
        cprint(f"&fDownloading {len(select_chains)} chains...")
        sync_forks = cinput("&eSync forks as well when you download? (y/n): ").lower() == "y"
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

    def get_latest_tags(self, repo_link:str = "", ignore_tags_substrings:list = []) -> dict[str, list]:        
        if 'git@github.com:' in repo_link:
            repo_link = repo_link.replace('git@github.com:', '').replace('.git', '')
        
        API = f"https://api.github.com/repos/{repo_link}/tags"        
        v = requests.get(API).json()
        versions = []
        for doc in v:            
            if isinstance(v, str):                
                if 'api rate limit' in v.lower():
                    cprint("&cYou have reached the github api rate limit. Try again later.")
                    exit(1)
                else:
                    cprint(f"&c{v}")
                    exit(1)

            if "tag_name" in doc.keys():
                tag_name = doc.get("tag_name")
            else:
                tag_name = doc.get("name")
            ignore = False
            if len(ignore_tags_substrings) > 0:
                for sub in ignore_tags_substrings:
                    if sub in tag_name:
                        ignore = True
                    
            if not ignore:
                versions.append(tag_name)

        versions = sorted(versions)        
        return self._sort_groups(versions)

    def _sort_groups(self, versions: list) -> dict:
        # now we loop through these and return a dict of teh X latest values
        groups = {}
        for ver in versions:      
            ver = str(ver.replace('v', ''))

            # print(ver.split('.'))
            if len(ver.split('.')) > 3:
                continue # wasmd 0.27.0-junity.0 ?

            start, middle, end = ver.split('.')    
            
            if start == '0': start = middle            
            if start not in groups: groups[start] = []    

            subversion = "00" # 00 by default
            s, m, e = ver.split('.') # since we update start -> middle

            subv2 = e
            if '-' in e:
                # if it has a sub tag, we get the first char + version number to sort these
                e, subv = e.split('-')        
                subv1 = ord(subv[0])-97 if subv else 0        
                # subv2 = int(subv[-1]) if subv else 0
                subv2 = re.findall(r'\d+', subv) if subv else 0        
                subv2 = sum([int(i) for i in subv2]) if subv2 else 0        
                subversion = f"{subv1}{subv2}"    

            n = Version(ver, int(s + m + e) + float(f"0.{subv2}"))
            n.sub_version = int(subversion)
            groups[start].append(n)
        return groups

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

    def create_branch(self, folder_name, branch_name, cd_dir=False):
        if cd_dir: os.chdir(os.path.join(current_dir, folder_name))

        branches = []        
        for b in os.popen("git branch").read().split('\n'):
            if len(b) == 0: continue
            if b.startswith('*'): b = b[1:]
            b = b.strip()
            branches.append(b)

        # print('branches', branches)
        if branch_name in branches:
            os.system(f"git checkout {branch_name}")
        else: # create
            os.system(f"git checkout -b {branch_name}")            
        if cd_dir: os.chdir(current_dir)

    def commit(self, folder_name, commit_msg, cd_dir=False):
        if cd_dir: os.chdir(os.path.join(current_dir, folder_name))
        os.system(f"git add .")
        os.system(f"git commit -m '{commit_msg}'")
        if cd_dir: os.chdir(current_dir)

    def push(self, folder_name, branch_name, repo_name="origin", cd_dir=False):
        if cd_dir: os.chdir(os.path.join(current_dir, folder_name))
        os.system(f"git push {repo_name} {branch_name}")
        if cd_dir: os.chdir(current_dir)

if __name__ == "__main__":
    _main()