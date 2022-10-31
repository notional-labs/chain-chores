import pyfiglet
import re
import os


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