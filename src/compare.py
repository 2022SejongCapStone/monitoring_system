import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src import AdditiveElgamal as ae
import json
import pickle
from Crypto.Util.number import getRandomRange, long_to_bytes, bytes_to_long
from os import urandom
from sys import getsizeof


def int_to_binlist(x): #max bit num == 64
    if x>=2**64:
        raise ValueError('argument bigger than 2**64')
    return [x >> i & 1 for i in range(0,64)]

def binlist_to_int(lst):
    if len(lst)!=64:
        raise ValueError('argument list length must be 64')
    x = 0
    for i in range(len(lst)):
        x += 2**i * lst[i]
    return x

def encrypt_simhash(pubkey, x): # x: 64bit simhash
    if not isinstance(pubkey,ae.AdditiveElgamalKey):
        raise ValueError('Argument pubkey must be ae.AdditiveElgamalKey instance')
    if x>=2**64:
        raise ValueError('argument x bigger than 2**64')

    lst = int_to_binlist(x)
    enc_lst = []
    for i in range(64):
        K = getRandomRange(0, pubkey.p-1, urandom)
        enc_lst.append(pubkey._encrypt(lst[i],K))
    return enc_lst

def get_enc_HD(pubkey, simhash, enc_server_simhash):
    if not isinstance(pubkey,ae.AdditiveElgamalKey):
        raise ValueError('Argument pubkey must be ae.AdditiveElgamalKey instance')
    
    simhash_binlist = int_to_binlist(simhash)
    enc_HD = [1,1]
    for i in range(64):
        if simhash_binlist[i]==0:
            enc_HD = [ x*y for x,y in zip(enc_HD,enc_server_simhash[i])]
        else:
            K = getRandomRange(0, pubkey.p-1, urandom)
            enc_1 = pubkey._encrypt(1,K)
            inverse = [pow(x,-1,int(pubkey.p)) for x in enc_server_simhash[i]]            #NEEDS TO BE PYTHON3.8+
            enc_HD = [ x*y*z for x,y,z in zip(enc_HD,enc_1,inverse)]
        enc_HD = [ x%int(pubkey.p) for x in enc_HD]

    return enc_HD

def get_HD(simhash1,simhash2): 
    s1 = int_to_binlist(simhash1)
    s2 = int_to_binlist(simhash2)
    xor = [ x^y for x,y in zip(s1,s2) ]
    return xor.count(1)

if __name__ == "__main__":
    '''
    privkey = ae.construct_additive((key_json['p'], key_json['g'], key_json['y'],key_json['x']))
    pubkey = ae.construct_additive((key_json['p'], key_json['g'], key_json['y']))
    server_simhash = getRandomRange(0, 2**64-1, urandom)
    enc_server_simhash = encrypt_simhash(pubkey,server_simhash)

    cli_simhash = getRandomRange(0, 2**64-1, urandom)

    HD = get_HD(int_to_binlist(server_simhash),int_to_binlist(cli_simhash))
    enc_HD = get_enc_HD(pubkey, cli_simhash, enc_server_simhash)
    print(HD)
    print(enc_HD)
    print(privkey._decrypt(enc_HD))

    '''

    ##### GET PUB KEY from server, .JSON from analyze.py
    with open('key.json','r') as f:  ## TO DO : get from server and store in pickle
        key_json = json.load(f)

    with open('../../system/test.p','rb') as f:
        obj = pickle.load(f)

    pubkey = ae.construct_additive((key_json['p'], key_json['g'], key_json['y']))


    #GET ENCRYPTED SIMHASH AND INDEX FROM SERVER // in pickle!
    server_idx = 2
    server_simhash = getRandomRange(0, 2**64-1, urandom)
    enc_server_simhash = encrypt_simhash(pubkey,server_simhash)



    #Start Comparing process
    enc_HD_dict = {} # k,v = reprisentative_id , enc_HD
    for idx, val in obj.items(): 
        if not (idx == server_idx):                                                 # JSON in STR , LATER USE PICKLE instead
            continue
        for reprisentative_cfid, cloneclass in val.items():
            for cfid, code_fragment in cloneclass.items():
                if not ( cfid == reprisentative_cfid):
                    continue
                simhash = code_fragment[3]
                enc_HD_dict[reprisentative_cfid] = get_enc_HD(pubkey,simhash,enc_server_simhash)
                print('real HD :',get_HD(simhash,server_simhash))
                print('enc HD added')
        break

    ##### TEST
    print(enc_HD_dict)

    privkey = ae.construct_additive((key_json['p'], key_json['g'], key_json['y'],key_json['x']))

    for _,enc_HD in enc_HD_dict.items():
        print(privkey._decrypt(enc_HD))


    ##### TO DO : socket pickle : send enc_HD_dict to server
