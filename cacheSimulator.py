## Antoine Chiny
## n° de matricule : 000409802
## INFO-F102 Fonctionnement des ordinateurs
## Projet d'année - Cache Simulator
## Command: python3 cacheSimulator.py <instruction file>

import sys

SIZE_OF_CACHE = 8
SIZE_OF_MAIN  = 32
INSTRUCT      = 0
MAIN  = 0
DATA  = 1
ADDR  = 2
DIRT  = 3
WRITE = "W"
READ  = "R"

def init_memory():
    """ Initialise la mémoire """
    M      = [0 for i in range(SIZE_OF_MAIN)]
    L1Data = [0 for i in range(SIZE_OF_CACHE)]
    L1Addr = [0 for i in range(SIZE_OF_CACHE)]
    L1Dirt = [False for i in range(SIZE_OF_CACHE)]
    return M, L1Data, L1Addr, L1Dirt

def get_victim(LastUse):
    """ Fonction qui retourne l'index de la plus petite valeur
    de la liste LastUse """
    index = 0
    for i in range(SIZE_OF_CACHE):
        if LastUse[index] > LastUse[i]:
            index = i
    return index

def print_dash(nb, end="\n"):
    """ Affiche un nombre nb de tiret """
    for i in range(nb):
        print("-", end="")
    print(end=end)
        
def display_memory(Mem, LastUse):
    """" Affiche la mémoire """
    M, L1Data, L1Addr, L1Dirt = Mem[MAIN], Mem[DATA], Mem[ADDR], Mem[DIRT]
    shift = SIZE_OF_MAIN//2
    print_dash(29, end="\t")
    print_dash(37)
    print("|\t MAIN MEMORY        |", end="\t")
    print("|\t    CACHE MEMORY\t    |")
    print_dash(29, end="\t")
    print_dash(37)
    print(" ADDR", "VALUE", " ADDR", "VALUE", sep="\t", end="\t")
    print("INDEX", " ADDR", " DATA", " DIRT", " USE", sep="\t")
    for i in range(SIZE_OF_MAIN//2):
        print("|%3d|\t|%3d|\t|%3d|\t|%3d|"%\
            (i, M[i], i+shift, M[i+shift]), end="\t")
        if i < SIZE_OF_CACHE:
            print("|%3d|\t|%3d|\t|%3d|\t|%3d|\t|%3d|" %\
                (i, L1Addr[i], L1Data[i], L1Dirt[i], LastUse[i]))
        else:
            if i == SIZE_OF_CACHE:
                print_dash(37, end="")
            print()
    print_dash(29)

def write_instruct(Instructs, Mem, LastUse, instructNbr):
    """ Ecris une valeur en mémoire """
    M, L1Data, L1Addr, L1Dirt = Mem[MAIN], Mem[DATA], Mem[ADDR], Mem[DIRT]
    value   = int(Instructs[DATA])
    adress  = int(Instructs[ADDR])
    print("WR", Instructs[DATA], "to", Instructs[ADDR], end="\t\t")
    # Si l'adresse est dans le cache
    if adress in L1Addr:
        # On écrit la valeur dans le cache
        caseHit          = L1Addr.index(adress)
        L1Data[caseHit]  = value
        # La valeur deviens dirty
        L1Dirt[caseHit]  = True
        LastUse[caseHit] = instructNbr
        print("hit: case %d (LU %d)\t\tdirty!" % (caseHit, instructNbr), end="")
    # Si l'adresse n'est pas dans le cache
    else:
        dirty = False
        M[adress] = value
        # On cherche une victime
        k = get_victim(LastUse)
        # Si la victime est dirty
        if L1Dirt[k]:
            # On écrit la valeur dans la mémoire principale
            vData        = L1Data[k]
            vAddr        = L1Addr[k]
            M[L1Addr[k]] = L1Data[k]
            L1Dirt[k]    = False
            dirty        = True
        # On écrit la valeur dans le cache
        L1Data[k]  = value
        L1Addr[k]  = adress
        LastUse[k] = instructNbr
        print("miss: victim %d (LU %d)" % (k, instructNbr), end="")
        if dirty:
            print("\t\tdirty WR %d to %d" % (vData, vAddr), end="")
    print()

def read_instruct(Instructs, Mem, LastUse, instructNbr):
    """ Lis une valeur en mémoire """
    M, L1Data, L1Addr, L1Dirt = Mem[MAIN], Mem[DATA], Mem[ADDR], Mem[DIRT]
    addr = int(Instructs[DATA])
    # On écrit l'instruction exécuter
    print("RD %d to %d" % (M[addr], addr), end="\t\t")
    # Si l'adresse est dans le cache
    if addr in L1Addr:
        # On récupére l'index de l'adresse dans le cache
        index          = L1Addr.index(addr)
        # On ajuste la valeur de last use
        LastUse[index] = instructNbr
        # On affiche qu'il y a eut un cache hit
        print("hit: %d (LU %d)" % (index, instructNbr))
    # Si l'adresse n'est pas dans le cache
    else:
        dirty = False
        # On cheche une victime
        k     = get_victim(LastUse)
        # Si la victime est dirty
        if L1Dirt[k]:
            # On écrit la valeur dans la mémoire principale
            # On sauvegarde les valeurs pour l'affichage
            vData        = L1Data[k]
            vAddr        = L1Addr[k]
            M[L1Addr[k]] = L1Data[k]
            L1Dirt[k]    = False
        # On écrit la valeur dans le cache
        L1Addr[k]  = addr
        L1Data[k]  = L1Data[L1Addr.index(addr)]
        LastUse[k] = instructNbr
        print("miss: victim %d (LU %d)" % (k, instructNbr), end="")
        if dirty:
            print("\t\tdirty WR %d to %d" % (vData, vAddr), end="")
        print()

if __name__ == "__main__":
    fd          = open(sys.argv[1])
    Instructs   = []
    instructNbr = 1
    instruction = fd.readline().strip()
    Mem         = init_memory()
    LastUse     = [0 for i in range(SIZE_OF_CACHE)]

    # Tant qu'on ne lis pas une chaine vide sur le fichier
    while instruction:
        # On split la ligne lu
        Instructs = instruction.split(" ")
        # Si le premiére bloc vaut "W" on exécute write
        if Instructs[INSTRUCT] == WRITE:
            write_instruct(Instructs, Mem, LastUse, instructNbr)
        # Si elle vaut "R" on exécute read
        if Instructs[INSTRUCT] == READ:
            read_instruct(Instructs, Mem, LastUse, instructNbr)
        # On nettoie la ligne
        instruction = fd.readline().strip()
        instructNbr += 1
    # On affiche la mémoire à la fin du programme
    display_memory(Mem, LastUse)
