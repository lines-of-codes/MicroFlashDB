from numba import njit
from string import ascii_letters, digits

characters = ascii_letters + digits + "~!@#$%^&*()_+`-={}[]|\\:;\"'><?/"
charlen = len(characters)

@njit(fastmath=True)
def encrypt(uinput, shiftedup):
    newstr = ""
    for i in uinput:
        index = characters.find(i)
        if ((index + shiftedup) > charlen):
            if index == charlen:
                newstr += characters[0 + (shiftedup - 1)]
            else:
                j = index + shiftedup
                nindex = 0
                while j > charlen:
                    j -= 1
                    nindex += 1
                newstr += characters[nindex]
        newstr += characters[index + shiftedup]
    return newstr

@njit(fastmath=True)
def decrypt(uinput, shiftedup):
    newstr = ""
    for i in uinput:
        index = characters.find(i)
        if ((index + shiftedup) > charlen):
            if index == charlen:
                newstr += characters[0 + (shiftedup - 1)]
            else:
                j = index + shiftedup
                nindex = 0
                while j > charlen:
                    j -= 1
                    nindex += 1
                newstr += characters[nindex]
        newstr += characters[index - shiftedup]
    return newstr