#!/usr/bin/env python3

import sys
import os
import struct

from datetime import datetime 
import time


def get_blockchain_path():
    return os.environ.get('BCHOC_FILE_PATH', 'blockchain.dat')

def create_genesis_block():
    prev_hash = b'\x00' * 32 #32 0 byes
    timestamp = 0.0 # 8 bytes 
    case_id = b'0' * 32 # 32 ascii 0s
    evidence_id = b'0' * 32 # 32 ascii 0s
    state = b'INITIAL\x00\x00\x00\x00\x00' # 12 byes as padding
    creator = b'\x00' * 12 # 12 null bytes
    owner = b'\x00' * 12 # 12 null
    data_length = 14 # 4 bytes 
    data = b'Initial block\x00' #14 bytes

    header = struct.pack(
        "32s d 32s 32s 12s 12s 12s I",
        prev_hash, timestamp, case_id, evidence_id, state, creator, owner, data_length
    )

    return header + data

def handle_init():
    filepath = get_blockchain_path()

    if os.path.exists(filepath):
        print("Blockchain file found with INITIAL block.")
        return 0
    
    try:#file doesnt exist; amke it
        genesis_block = create_genesis_block()
        with open(filepath, 'wb') as f:
            f.write(genesis_block)
        print("Blockchain file not found. Created INITIAL block.")
        return 0
    except Exception as e:
        print(f"Erorr creating blockchain: {e}", file=sys.stderr)
        return 1
    
# new insutrctions here 

def handle_add(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        handle_init()

    case_id = None
    item_ids = []
    creator = None
    password = None

    # pasre arguments for input corectly

    i = 0
    while i < len(args):
        if args[i] == "-c":
            case_id = args[i+1]
            i +=2
        elif args[i] == "-i":
            item_ids.append(args[i+1])
            i+=2
        elif args[i] == "-g":
            creator = args[i+1]
            i+=2
        elif args[i] == "-p":
            password = args[i+1]
            i+=2
        else:
            i+=1
    
    if not case_id or not item_ids:
        print("Error: case_id and item_ids required", file=sys.stderr)
        return 1
    
    #password validation

    if password != "C67C":
        print("Invalid password")
        return 1
    
    #read existing blockingchain

    existing_items = set()

    try:
        with open(filepath, "rb") as f: 
            while True: 
                header = f.read(struct.calcsize("32s d 32s 32s 12s 12s 12s I")) # from outline
                if not header:
                    break

                prev_hash, timestamp, case, evidence, state, creator_f, owner, data_len, = struct.unpack("32s d 32s 32s 12s 12s 12s I", header)

                data = f.read(data_len)
                item = evidence.decode(errors="ignore").strip("\x00")
                existing_items.add(item)
    except Exception as e:
        print(f"Error reading blcokchain: {e}", file=sys.stderr)
        return 1
    
    # dulicate item check

    for item in item_ids: 
        if item in existing_items:
            print(f"Error: Item {item} already exists")
            return 1
        

    # new blocks

    with open(filepath, "ab") as f:
        for item in item_ids:
            prev_hash = b'\x00' * 32
            timestamp = time.time()
            case_bytes = case_id.encode().ljust(32, b'\x00')
            item_bytes = item.encode().ljust(32, b'\x00')
            state = b'CHECKEDIN\x00\x00\x00'
            creator_bytes = creator.encode().ljust(12, b'\x00')
            owner = b'\x00' * 12
            data = b''
            data_length = len(data)
            header = struct.pack("32s d 32s 32s 12s 12s 12s I", prev_hash, timestamp,case_bytes,item_bytes, state, creator_bytes,owner, data_length)

            # append blcok to end

            f.write(header)
            f.write(data)

            #success message
            dt = datetime.utcfromtimestamp(timestamp)
            print(f"Added item: {item}")
            print(f"Status: CHECKEDIN")
            print(f"Time of action: {dt.isoformat()}Z")

    return 0 
    
def main():
    if len(sys.argv) < 2:
        print("Usage: bchoc <command> [options]", file=sys.stderr)
        return 1
    
    command = sys.argv[1]
    
    if command == "init":
        return handle_init()
    #use elif for new commands here 
    elif command == "add":
        return handle_add(sys.argv[2:])
    else: 
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        return 1



if __name__ == "__main__":
    sys.exit(main())