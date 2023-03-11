import sys
sys.dont_write_bytecode = True
from cytolk import tolk
tolk.load()
def speak(text):
    tolk.speak(text)
