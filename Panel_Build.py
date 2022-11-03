from Utils import *
from subprocess import PIPE, Popen
import multiprocessing as mp

import datetime
import os

current_dir = os.path.dirname(os.path.realpath(__file__))

def _main():
    from main import main
    BuildPanel().panel(main)

class BuildPanel():
    def panel(self, main_panel_func):
        options = {            
            "b": ["Build chains", self.build],
            "t": ["Test chains", self.test],

            "": [""],
            "m": ["Main Panel", main_panel_func],
            "e": ["Exit", exit],
        }
        aliases = {}
        while True:
            selector("&f", "Test / Build", options=options, aliases=aliases)

    def test(self):
        chains = select_chains("Select chains you want to test. (space to select, none for all)")
        to_run = []        
        
        # clear old test since we are running new ones
        from main import test_output # TODO: bad.
        with open(os.path.join(test_output, "testing.txt"), "w") as f:
            f.write("")
        with open(os.path.join(test_output, "errors.txt"), "w") as f:
            f.write("")

        for chain in chains:                   
            to_run.append(Testing(chain))

        with mp.Pool(mp.cpu_count()) as p:
            p.map(Testing.run_tests, to_run)
        
        cinput(f"\n&f{len(to_run)} tests finished!\n&eEnter to continue...")

    def build(self):
        chains = select_chains("Select chains you want to build. (space to select, none for all)")
        to_run = []        
        for chain in chains:            
            to_run.append(Testing(chain))            
        with mp.Pool(mp.cpu_count()) as p:
            p.map(Testing.build_binary, to_run)
        cinput("&fEnter to continue...")


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
        from main import test_output # TODO: bad.

        with open(os.path.join(test_output, "testing.txt"), "a") as f:
            f.write(f"="*40)
            f.write(f"\n{self.chain} {current_time}\n{output}\n\n")

        if len(err) > 0:
            with open(os.path.join(test_output, "errors.txt"), "a") as f:
                f.write(f"="*40)               
                f.write(f"\n{self.chain} {current_time}\n{err}\n\n")
        
        cprint(f"&a[+] Test finished for {self.chain}")
        os.chdir(os.path.join(current_dir))

if __name__ == "__main__":
    _main()