from Utils import *

from webbrowser import open as open_url

def _main():
    from main import main
    GithubPanel().panel(main)

class GithubPanel():

    def __init__(self) -> None:
        from main import VALIDATING_CHAINS
        self.VALIDATING_CHAINS = VALIDATING_CHAINS        

    def panel(self, main_panel_func):
        options = {            
            "f": ["Workflows", self.workflows],   
            "d": ["Adds dependabot if not already", self.dependabot],   
            "w": ["Open chain in browser\n", self.website],       

            "m": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases = {}
        while True:
            selector("&f", "Github", options=options, aliases=aliases)

    def website(self):
        chains = select_chains("Select a chain(s) to open the website for (space to select)")
        location = pick(["parent", "fork"], "Open the 'parent' repo or 'fork' version? (select 1)")[0]
        cprint(f"Opening Website for: {','.join(chains)}...")
        for chain in chains:
            info = self.VALIDATING_CHAINS.get(chain, None)
            if info == None: continue
            url_path = info[location].replace(".git", "").split(":")[1]            
            open_url(f"https://github.com/{url_path}")     

    def workflows(self):
        # select a chain, and add workflows to it
        chain = pick(get_downloaded_chains(), "Select a chain to add workflows to")[0]
        # os.chdir(os.path.join(current_dir, chain))
        cprint(f"&aAdding workflows to {chain}")        
        Workflow(chain).add_workflows()

    def dependabot(self): # combine with workflows?
        chain = pick(get_downloaded_chains(), "Select a chain to add dependabot to")[0]
        cprint(f"&aAdding dependabot to {chain} if it is not already there")
        Workflow(chain).add_dependabot()


class Workflow():
    def __init__(self, folder_name) -> None:
        self.folder_name = folder_name
        self.chain_dir = os.path.join(current_dir, self.folder_name)
        from main import WORKFLOWS, VALIDATING_CHAINS, yml_files
        self.WORKFLOWS = WORKFLOWS
        self.VALIDATING_CHAINS = VALIDATING_CHAINS
        self.yml_files = yml_files

    def available_workflows(self):        
        return os.listdir(self.WORKFLOWS)

    def upgrade_actions(self):
        # check if there is a github folder
        if not os.path.isdir(os.path.join(self.chain_dir, ".github")):
            return     
        # Turn all actions/checkout@v3 -> actions/checkout@v3.1.0


    def _write_workflow(self, workflow_name):
        if workflow_name not in self.available_workflows():
            print(f"Workflow {workflow_name} not found in {self.WORKFLOWS}")
            return

        main_branch_name = self.VALIDATING_CHAINS[self.folder_name]["branch"]
        
        os.chdir(os.path.join(current_dir, self.folder_name))
        print(f"Writing {workflow_name} to .github/workflows/{workflow_name} for {self.folder_name}")
        with open(os.path.join(self.yml_files, "workflows", workflow_name), "r") as f2:
            with open(f".github/workflows/{workflow_name}", "w") as f:
                f.write(f2.read().replace("_MAIN_BRANCH_", main_branch_name))
        os.chdir(current_dir)

    def add_workflows(self):
        os.chdir(self.chain_dir)
        if not os.path.exists(".github/workflows"):
            os.makedirs(".github/workflows", exist_ok=True) 

        workflow_options = [x for x in os.listdir(self.WORKFLOWS) if x not in os.listdir(".github/workflows")]

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
        main_branch = self.VALIDATING_CHAINS[self.folder_name]["branch"] # main, master, etc

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
                    with open(os.path.join(self.yml_files, "dependabot.yml"), "r") as f2:
                        f.write(f2.read().replace("_MAIN_BRANCH_", main_branch))
            os.chdir(current_dir)

if __name__ == "__main__":
    _main()