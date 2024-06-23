import DAI

def initialize(): 
    DAI.pushIDF('siren_idf', 0)
    DAI.pushIDF('light_idf', 0)
    global SIREN_SIG
    SIREN_SIG = False