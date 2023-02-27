from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import base64
import hashlib
import json
import time
import six
import sys
import os

def issue(argv):
    rpc_port = 18884
    rpc_user = 'nestor'
    rpc_password = 'nestor'

    NAME = str(argv[1])
    TICKER = str(argv[2])
    DOMAIN = str(argv[3])

    ASSET_AMOUNT = float(argv[4])
    TOKEN_AMOUNT = float(argv[5])

    PRECISION = int(argv[6])
    VERSION = 0

    FEERATE = 0.00001000

    IPLD_MHASH = 'QmQqNpuRGrdB1EBV2qj4Di6DKzRyukwwPCXXCtfyRwkVxW'



    try:
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(rpc_user, rpc_password, rpc_port))
        NEWADDR = rpc_connection.getnewaddress("WRAPPEDtoken", "legacy")
        VALIDATEADDR = rpc_connection.getaddressinfo(NEWADDR)
        PUBKEY = VALIDATEADDR["pubkey"]
        ASSET_ADDR = NEWADDR
        NEWADDR = rpc_connection.getnewaddress("WRAPPEDtoken", "legacy")
        TOKEN_ADDR = NEWADDR

    except JSONRPCException as json_exception:
        print("A JSON RPX exception occured: " + str(json_exception))
    except Exception as general_exception:
        print("An exception occured: " + str(general_exception))

    print(VALIDATEADDR)
    print(PUBKEY)
    print(ASSET_ADDR)
    print(TOKEN_ADDR)


    # CONTRACT = f"{{\"entity\":{{\"domain\":\"{DOMAIN}\"}}, \"issuer_pubkey\":\"{PUBKEY}\", \"name\":\"{NAME}\", \"precision\":{PRECISION}, \"ticker\":\"{TICKER}\", \"version\":{VERSION}}}"
    CONTRACT = f"{{\"entity\":{{\"domain\":\"{DOMAIN}\"}}, \"issuer_pubkey\":\"{PUBKEY}\", \"name\":\"{NAME}\", \"nft\":\"{IPLD_MHASH}\", \"precision\":{PRECISION}, \"ticker\":\"{TICKER}\", \"version\":{VERSION}}}"
    print(CONTRACT)

    CONTRACT_SORTED=json.dumps(json.loads(CONTRACT), sort_keys=True, separators=(",",":"))
    CONTRACT_HASH=hashlib.sha256(six.ensure_binary(CONTRACT_SORTED)).hexdigest()
    print(CONTRACT_HASH)

    CONTRACT_HASH_REV="".join(reversed([CONTRACT_HASH[i:i+2] for i in range(0, len(CONTRACT_HASH), 2)]))
    print(CONTRACT_HASH_REV)


    RAWTX = rpc_connection.createrawtransaction([], [{"data":"00"}])
    print(RAWTX)


    FRT = rpc_connection.fundrawtransaction(RAWTX, {"feeRate":FEERATE})
    print(FRT)

    HEXFRT = FRT["hex"]
    print(HEXFRT)

    RIA = rpc_connection.rawissueasset(HEXFRT, [{"asset_amount":ASSET_AMOUNT,
                                            "asset_address":ASSET_ADDR,
                                            "token_amount":TOKEN_AMOUNT,
                                            "token_address":TOKEN_ADDR,
                                            "blind":False,
                                            "contract_hash":CONTRACT_HASH_REV,}])
    print(RIA)

    HEXRIA = RIA[0]["hex"]
    ASSET = RIA[0]["asset"]
    ENTROPY = RIA[0]["entropy"]
    TOKEN = RIA[0]["token"]

    BRT = rpc_connection.blindrawtransaction(HEXRIA, True, [], False)
    SRT = rpc_connection.signrawtransactionwithwallet(BRT)
    HEXSRT = SRT["hex"]

    ##  TEST = rpc_connection.testmempoolaccept(['"' + HEXSRT + '"'])
    TEST = rpc_connection.testmempoolaccept([HEXSRT])
    ALLOWED = TEST[0]["allowed"]
    print(ALLOWED)

    ISSUETX = rpc_connection.sendrawtransaction(HEXSRT)

    #print("\n\n")
    #print(F"ASSET_ID: {ASSET}")
    #print(F"CONTRACT: {CONTRACT}")

    return ( [ ASSET, CONTRACT])

def show(argv):
    n0 = str(argv[1])
    n1 = str(argv[2])
    n2 = str(argv[3])


    n3 = int(argv[4])
    n4 = int(argv[5])

    n5 = int(argv[6])

    return ( [ n0, n1, n2, n3, n4, n5])


if __name__ == '__main__':
    print ( issue(sys.argv))


"""

ddf8c4c47b19b4cc99f421d4ac826a41a3f8de153f78ae43a6bd1e26df0d6f94

'/home/nestor/elements-elements-0.21.0.2/bin/elements-qt' -datadir='/home/nestor/elements-elements-0.21.0.2/Liquid/liquid_network_1' >/dev/null 2>&1

python3.10 '/home/nestor/libwally-core/src/test/live_issue2liquid_testnet.py' 'Transport Token' 'L-TRNS' 'lab.r3c.network' 21000000 1 0

python3.10 '/home/nestor/libwally-core/src/test/live_issue2liquid_testnet.py' 'Transport Token' 'L-TRNS' 'lab.r3c.network' 0.00000001 0.00000001 8

https://blockstream.info/testnet/

"""