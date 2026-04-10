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


def find_latest_block_for_item(blocks, item_id):
    latest = None

    for block in blocks:
        if block["item_id"] == item_id:
            latest = block

    return latest

    
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
            creator_bytes = (creator or '').encode().ljust(12, b'\x00')
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

# some helper functions needed to run code -arjun
def read_all_blocks(filepath):
    blocks = []
    header_format = "32s d 32s 32s 12s 12s 12s I"
    header_size = struct.calcsize(header_format)

    try:
        with open(filepath, "rb") as f:
            while True:
                header = f.read(header_size)
                if not header:
                    break

                if len(header) != header_size:
                    print("Error: Corrupted block header", file=sys.stderr)
                    return None

                prev_hash, timestamp, case_id, evidence_id, state, creator, owner, data_len = struct.unpack(header_format, header)
                data = f.read(data_len)

                if len(data) != data_len:
                    print("Error: Corrupted block data", file=sys.stderr)
                    return None

                # decode the stored byte fields so they are easier to work with
                block = {
                    "prev_hash": prev_hash,
                    "timestamp": timestamp,
                    "case_id": case_id.decode(errors="ignore").strip("\x00"),
                    "item_id": evidence_id.decode(errors="ignore").strip("\x00"),
                    "state": state.decode(errors="ignore").strip("\x00"),
                    "creator": creator.decode(errors="ignore").strip("\x00"),
                    "owner": owner.decode(errors="ignore").strip("\x00"),
                    "data_len": data_len,
                    "data": data
                }

                blocks.append(block)

    except Exception as e:
        print(f"Error reading blockchain: {e}", file=sys.stderr)
        return None

    return blocks


# show items -arjun
def handle_show_items(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1

    case_id = None

    # parse command line args
    i = 0
    while i < len(args):
        if args[i] == "-c":
            case_id = args[i+1]
            i += 2
        else:
            i += 1

    if not case_id:
        print("Error: case_id required", file=sys.stderr)
        return 1

    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1

    found_items = []
    seen = set()

    for block in blocks:
        # skip genesis block
        if block["state"] == "INITIAL":
            continue

        if block["case_id"] == case_id:
            if block["item_id"] not in seen:
                seen.add(block["item_id"])
                found_items.append(block["item_id"])

    for item in found_items:
        print(item)

    return 0


# show history -arjun
def handle_show_history(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1

    case_id = None
    item_id = None
    num_entries = None
    reverse = False

    # parse options for filtering history
    i = 0
    while i < len(args):
        if args[i] == "-c":
            case_id = args[i+1]
            i += 2
        elif args[i] == "-i":
            item_id = args[i+1]
            i += 2
        elif args[i] == "-n":
            num_entries = int(args[i+1])
            i += 2
        elif args[i] == "-r":
            reverse = True
            i += 1
        else:
            i += 1

    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1

    filtered_blocks = []

    for block in blocks:
        if block["state"] == "INITIAL":
            continue

        if case_id and block["case_id"] != case_id:
            continue

        if item_id and block["item_id"] != item_id:
            continue

        filtered_blocks.append(block)

    # oldest first unless reverse was requested
    filtered_blocks.sort(key=lambda x: x["timestamp"])

    if reverse:
        filtered_blocks.reverse()

    if num_entries is not None:
        filtered_blocks = filtered_blocks[:num_entries]

    for index, block in enumerate(filtered_blocks):
        dt = datetime.utcfromtimestamp(block["timestamp"])

        print(f"Case: {block['case_id']}")
        print(f"Item: {block['item_id']}")
        print(f"Action: {block['state']}")
        print(f"Time: {dt.isoformat()}Z")

        if index != len(filtered_blocks) - 1:
            print()

    return 0


# remove -arjun
def handle_remove(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1

    item_id = None
    reason = None
    password = None
    owner_info = ""

    i = 0
    while i < len(args):
        if args[i] == "-i":
            item_id = args[i+1]
            i += 2
        elif args[i] == "-y":
            reason = args[i+1]
            i += 2
        elif args[i] == "-p":
            password = args[i+1]
            i += 2
        elif args[i] == "-o":
            owner_info = args[i+1]
            i += 2
        else:
            i += 1

    if not item_id or not reason:
        print("Error: item_id and reason required", file=sys.stderr)
        return 1

    if password != "C67C":
        print("Invalid password")
        return 1

    if reason not in ["DISPOSED", "DESTROYED", "RELEASED"]:
        print("Error: Invalid removal reason", file=sys.stderr)
        return 1

    if reason == "RELEASED" and owner_info == "":
        print("Error: owner info required when reason is RELEASED", file=sys.stderr)
        return 1

    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1

    latest_block = find_latest_block_for_item(blocks, item_id)

    if latest_block is None:
        print("Error: Item not found", file=sys.stderr)
        return 1

    if latest_block["state"] != "CHECKEDIN":
        print("Error: Item must be CHECKEDIN before removal", file=sys.stderr)
        return 1

    # build the new remove block
    with open(filepath, "ab") as f:
        prev_hash = b'\x00' * 32
        timestamp = time.time()
        case_bytes = latest_block["case_id"].encode().ljust(32, b'\x00')
        item_bytes = item_id.encode().ljust(32, b'\x00')
        state_bytes = reason.encode().ljust(12, b'\x00')
        creator_bytes = latest_block["creator"].encode().ljust(12, b'\x00')
        owner_bytes = b'\x00' * 12
        data = owner_info.encode() if reason == "RELEASED" else b''
        data_length = len(data)

        header = struct.pack(
            "32s d 32s 32s 12s 12s 12s I",
            prev_hash,
            timestamp,
            case_bytes,
            item_bytes,
            state_bytes,
            creator_bytes,
            owner_bytes,
            data_length
        )

        f.write(header)
        f.write(data)

        dt = datetime.utcfromtimestamp(timestamp)
        print(f"Case: {latest_block['case_id']}")
        print(f"Removed item: {item_id}")
        print(f"Status: {reason}")
        print(f"Time of action: {dt.isoformat()}Z")

    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: bchoc <command> [options]", file=sys.stderr)
        return 1
    
    command = sys.argv[1]
    
    if command == "init":
        if len(sys.argv) > 2:
            print("Error: init does not accept additional arguments", file=sys.stderr)
            return 1
        return handle_init()
    elif command == "add":
        return handle_add(sys.argv[2:])
    elif command == "remove":
        return handle_remove(sys.argv[2:])
    elif command == "show":
        if len(sys.argv) < 3:
            print("Error: show requires a subcommand", file=sys.stderr)
            return 1

        show_command = sys.argv[2]

        if show_command == "items":
            return handle_show_items(sys.argv[3:])
        elif show_command == "history":
            return handle_show_history(sys.argv[3:])
        else:
            print(f"Error: Unknown show command '{show_command}'", file=sys.stderr)
            return 1
    else: 
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
