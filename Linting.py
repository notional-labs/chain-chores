import os

'''
TODO: save output into its own lint dir? .linting/{CHAIN} ? if there is any things to do / fix

Try and make it so we can click on the Txt file to open the folder based on absolute path?
or a way to open all after lint & auto fix + fmt to do so

Custom cosmos linter in the future? Help with proto and things like that
'''

current_dir = os.path.dirname(os.path.realpath(__file__))

# === Linting ===
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
    