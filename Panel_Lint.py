from Utils import *

from Conversion import convert_commands_to_google_format

def _main():
    from main import main
    LintPanel().panel(main)

class LintPanel():
    def panel(self, main_panel_func):
        options = {            
            "l": ["Lint chains", self.linting],
            "d": ["Convert to Google CLI", self.google_cli_convert],

            "": [""], # BLANK SPACE
            "m": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases = {}
        while True:
            selector("&6", "Lint Panel", options=options, aliases=aliases)

    def google_cli_convert(self):
        chains = select_chains("Select chains you want to convert CLI for. (space to select, none for all)")
        for chain in chains:
            convert_commands_to_google_format(chain)            
            print(f"&aConverted {chain}")

    def linting(self):
        chains = select_chains("Select chains to lint")
        for chain in chains: # mp?
            Linting(chain).lint_all()



# === Linting ===
'''
TODO: save output into its own lint dir? .linting/{CHAIN} ? if there is any things to do / fix

Try and make it so we can click on the Txt file to open the folder based on absolute path?
or a way to open all after lint & auto fix + fmt to do so

Custom cosmos linter in the future? Help with proto and things like that
'''
class Linting():  
    def __init__(self, folder_name) -> None:
        self.folder_name = folder_name

    def methods():
        return [func for func in dir(Linting) if callable(getattr(Linting, func)) and not func.startswith("__")]

    def lint_all(self):
        print(f"Linting {self.folder_name}...")            
        self.auto_fix()
        self.gofmt()
        self.govet()
        self.tidy()
        print(f"Lint for {self.folder_name} complete!")

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
    

if __name__ == "__main__":
    _main()