import pyfiglet
import re
import os

from pick import pick

current_dir = os.path.dirname(os.path.realpath(__file__))

# === Chain Utils ===
def get_chains():
    from CHAINS import VALIDATING_CHAINS
    for chain, locations in VALIDATING_CHAINS.items():
        yield chain, locations   

def select_chains(title, min_selection_count=0) -> list[str]:
    chains = [c[0] for c in pick(get_downloaded_chains(), title, multiselect=True, min_selection_count=min_selection_count, indicator="=> ")]
    if len(chains) == 0: chains = get_downloaded_chains()
    return chains

def get_downloaded_chains(show=False):        
    valid_chains = [chain[0] for chain in get_chains()]
    v = [folder for folder in os.listdir(current_dir) if os.path.isdir(folder) and folder in valid_chains]        
    v.sort(key=str.lower)

    if show: cinput(f"\n&a{'='*20} Downloaded Chains {'='*20}\n&f{', '.join(v)}\n\n(( Enter to continue... ))")
    return v



# === Chain Info & Versions ===
def get_chain_info(folder_name):
    sdk_version, ibc_version, wasm_version, wasmvm, iavl = "", "", "", "", ""

    with open(os.path.join(current_dir, folder_name, "go.mod"), "r") as f:
        data = f.read()
    
    for line in data.split("\n"):
        if re.search(r"(.*)\sv\d+\.\d+\.\d+", line):
            version = line.split(" ")[1] # -1 or 2 = // indirect in some cases
            if not re.search(r"\d", version):
                # if version does not contain any numbers, then continue
                continue

            if "=>" in line: continue

            if "github.com/CosmWasm/wasmd" in line:
                wasm_version = line.split(" ")[1] or ""
            elif "github.com/CosmWasm/wasmvm" in line:
                wasmvm = line.split(" ")[1] or ""
            elif "github.com/cosmos/ibc-go" in line:
                ibc_version = line.split(" ")[1] or ""
            elif "github.com/cosmos/cosmos-sdk" in line:
                sdk_version = line.split(" ")[1] or ""
            elif "github.com/tendermint/tendermint" in line:
                tm_version = line.split(" ")[1] or ""
            elif "github.com/cosmos/iavl" in line:
                iavl = line.split(" ")[1] or ""
    return {
        "sdk": sdk_version,
        "ibc": ibc_version,
        "wasm": wasm_version,
        "wasmvm": wasmvm,
        "tm": tm_version,
        "iavl": iavl,
    }

def get_chain_versions():
    sdk_chain_version, ibc_version, wasm_ver, tm_ver, iavl_ver = {}, {}, {}, {}, {}

    for chain, _ in get_chains():
        info = get_chain_info(chain)
        sdk_version = info["sdk"]
        ibc = info["ibc"]
        wasm = info["wasm"]
        tm = info["tm"]
        iavl = info["iavl"]
        
        sdk_chain_version.get(sdk_version, []).append(chain)        
        ibc_version.get(ibc, []).append(chain)
        wasm_ver.get(wasm, []).append(chain)
        tm_ver.get(tm, []).append(chain)
        iavl_ver.get(iavl, []).append(chain)
    return {
        "sdk": sdk_chain_version,
        "ibc": ibc_version,
        "wasm": wasm_ver,
        "tm": tm_ver,
        "iavl": iavl_ver,
    }



# === Panel selector ===
def selector(color, title, options, aliases):
    cfiglet(color, title, True)
    for k, v in options.items():
        if k == "": print("")
        else: print(f"[{k:^3}] {v[0]}")            
    res = cinput("\n&fSelect an option: ").lower()
    if res in aliases: res = aliases[res]
    if res in options and res != "":                
        func = options[res][1]
        if len(options[res]) >= 3:
            func(*options[res][2:])
        else:
            func()
    else:
        cprint("&aInvalid option")




# ====== Colors ======
# https://github.com/Reecepbcups/minecraft-panel/blob/main/src/utils/cosmetics.py    
def getColorDict() -> dict:
    return { 
    '&1': '\u001b[38;5;4m', '&2': '\u001b[38;5;2m', '&3': '\u001b[38;5;6m', '&4': '\u001b[38;5;1m', '&5': '\u001b[38;5;5m', 
    '&6': '\u001b[38;5;3m', '&7': '\u001b[38;5;7m', '&8': '\u001b[38;5;8m', '&0': '\u001b[38;5;0m', '&a': '\u001b[38;5;10m', 
    '&b': '\u001b[38;5;14m', '&c': '\u001b[38;5;9m', '&d': '\u001b[38;5;13m', '&e': '\u001b[38;5;11m', '&f': '\u001b[38;5;15m', 
    '&r': '\u001b[0m',
}


def splitColors(myStr) -> list:
    # "&at&bt&ct" -> ['', '&a', 't', '&b', 't', '&c', 't']
    # _str = "&at&bt&ct"; splitColors(_str)
    return re.split("(&[a-zA-Z0-9])", myStr)


def cfiglet(clr, text, clearScreen=False): # prints fancy text
    if clearScreen:
        os.system('clear')
    # standard, small, computer, bulbhead, cybersmall, cybermedium, digital,  doom, madrid, maxfour, mini, rounded
    print(color(clr+pyfiglet.figlet_format(text, font="small")))


def color(text):
    '''
    Translates the color codes in text to the color codes in colors
    '''
    colors = getColorDict()
    text = text.replace("§", "&")
    formatted = ""
    i = 0
    while i in range(0, len(text)):
        
        if text[i:i+2] in colors:
            formatted += colors[text[i:i+2]]
            i += 1
        else:
            formatted += text[i]
        i += 1
    return formatted + colors['&r']

def cprint(text):  
    print(color(str(text)))  

def cinput(text=""):
    msg = color(str(text))
    try:
        user_input = input(msg)
        if user_input == "\x18": # ctrl + c
            exit(0)
        return user_input
    except KeyboardInterrupt:
        cprint("\n&cKeyboard Interrupt, Exiting...\n")
        exit(0)
    except ValueError:
        cprint("\n&cExit on input, Exiting...\n")
        exit(0)