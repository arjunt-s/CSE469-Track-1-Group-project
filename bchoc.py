#!/usr/bin/env python3

import sys
import os
import struct


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

def main():
    if len(sys.argv) < 2:
        print("Usage: bchoc <command> [options]", file=sys.stderr)
        return 1
    
    command = sys.argv[1]
    
    if command == "init":
        return handle_init()
    #use elif for new commands here 
    else: 
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())