#!/usr/bin/env python3

import sys
import os
import struct
import uuid
from Crypto.Cipher import AES
from datetime import datetime 
import time

"""
def debug_print_blocks():
    filepath = get_blockchain_path()

    with open(filepath, "rb") as f:
        while True:
            header = f.read(struct.calcsize('32s d 32s 32s 12s 12s 12s I'))
            if not header:
                break

            prev_hash, timestamp, case_id, evidence_id, state, creator, owner, data_len = struct.unpack('32s d 32s 32s 12s 12s 12s I', header)
            data = f.read(data_len)

            print("---- BLOCK ----")
            print("prev_hash =", repr(prev_hash))
            print("timestamp =", timestamp)
            print("case_id =", case_id[:16].hex())
            print("case_id (as text) =", case_id[:32].decode('ascii', errors='ignore'))
            print("evidence_id (as text) =", evidence_id[:32].decode('ascii', errors='ignore'))
            print("evidence_id =", evidence_id[:16].hex())
            print("evidence_id =", repr(evidence_id[:16]))
            print("state =", repr(state))
            print("creator =", repr(creator))
            print("owner =", repr(owner))
            print("data_len =", data_len)
            print()
"""

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
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                if len(data) ==0:
                    print("Error: Blockchain file is empty", file=sys.stderr)
                    return 1
                header_size = struct.calcsize("32s d 32s 32s 12s 12s 12s I")
                if len(data) < header_size:
                    print("Error: Invalid blockchain file (too short)", file=sys.stderr)
                    return 1
                
            print("Blockchain file found with INITIAL block.")
            return 0
        except Exception as e:
            print(f"Erorr validating existing file: {e}", file=sys.stderr)
            return 1

    
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
    
    AES_KEY = b"R0chLi4uLi4uLi4=" # form spec doc
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    
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
                if state.startswith(b'INITIAL'):
                    continue
                #evidence_encrypted = evidence[:16]
                """
                try:
                    evidence_decrypted = cipher.decrypt(evidence_encrypted)
                    item_bytes = evidence_decrypted[-4:]
                    item_int = struct.unpack('>I', item_bytes)[0]
                    existing_items.add(str(item_int))
                except:
                    pass
               # item = evidence.decode(errors="ignore").strip("\x00")
               # existing_items.add(item)
               """
                try:
                    evidence_hex = evidence.decode('ascii').strip('\x00')
                    evidence_encrypted = bytes.fromhex(evidence_hex)
                    evidence_decrypted = cipher.decrypt(evidence_encrypted)
                    item_bytes = evidence_decrypted[-4:]
                    item_int = struct.unpack('>I', item_bytes)[0]
                    existing_items.add(str(item_int))
                except:
                    pass
    except Exception as e:
        print(f"Error reading blockchain: {e}", file=sys.stderr)
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
           # case_bytes = case_id.encode().ljust(32, b'\x00')
          ##  clean_case_id = case_id.replace('-','')
          ## case_bytes = bytes.fromhex(clean_case_id).ljust(32, b'\x00')
          ##  clean_item_id = item.replace('-','')
           # item_bytes = item.encode().ljust(32, b'\x00')
          ##  item_bytes = bytes.fromhex(clean_item_id).ljust(32, b'\x00')

            

            case_uuid_bytes = uuid.UUID(case_id).bytes  # Convert UUID to 16 bytes
            case_encrypted = cipher.encrypt(case_uuid_bytes)
            case_hex = case_encrypted.hex()
            case_bytes = case_hex.encode('ascii')#.ljust(32, b'\x00')

            #FIXED: problem w/ item id: while encrypted it doesnt match
            item_int = int(item)
            item_bytes_raw = struct.pack('>I', item_int) 
            item_padded = item_bytes_raw.rjust(16,b'\x00')# changes this form l->r for gradescope since the data is stored there
            item_encrypted = cipher.encrypt(item_padded)
            item_hex = item_encrypted.hex()
            item_bytes = item_hex.encode('ascii')#.ljust(32, b'\x00')

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

    #debug_print_blocks()

    return 0 

def handle_checkin(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1
    
    item_id = None
    password = None

    i = 0
    while i < len(args):
        if args[i] == "-i":
            item_id = args[i+1]
            i+=2
        elif args[i] == "-p":
            password=args[i+1]
            i+=2
        else:
            i+=1

    if not item_id:
        print("Error: item_id required", file=sys.stderr)
        return 1
    
    valid_passwords = ["P80P", "L76L", "A65A", "E69E", "C67C"]
    if password not in valid_passwords:
        print("Invalid password")
        return 1
    
    AES_KEY = b"R0chLi4uLi4uLi4="
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

    last_case_id = None
    item_exists = False
    last_creator = None

    try:
        with open(filepath,"rb") as f:
            while True:
                header = f.read(struct.calcsize("32s d 32s 32s 12s 12s 12s I"))
                if not header:
                    break

                prev_hash, timestamp,case, evidence, state, creator, owner, data_len = struct.unpack("32s d 32s 32s 12s 12s 12s I", header)
                f.read(data_len)

                if state.startswith(b'INITIAL'):
                    continue

                try:
                    evidence_hex = evidence.decode('ascii').strip('\x00')
                    evidence_encrypted = bytes.fromhex(evidence_hex)
                    evidence_decrypted=cipher.decrypt(evidence_encrypted)
                    item_bytes = evidence_decrypted[-4:]
                    item_int = struct.unpack('>I', item_bytes)[0]

                    if str(item_int) == item_id:
                        item_exists = True
                        case_hex = case.decode('ascii').strip('\x00')
                        case_encrypted = bytes.fromhex(case_hex)
                        case_decrypted = cipher.decrypt(case_encrypted)
                        case_uuid = uuid.UUID(bytes=case_decrypted)
                        last_case_id = str(case_uuid)
                        last_state = state.decode(errors="ignore").strip("\x00")
                        last_creator = creator.decode(errors="ignore").strip("\x00")
                except:
                    pass
    except Exception as e:
        print(f"Error reading blockchain: {e}", file=sys.stderr)
        return 1
    
    if not item_exists:
        print(f"Error: Item {item_id} not found", file=sys.stderr)
        return 1
    
    if last_state != "CHECKEDOUT":
        print(f"Error: Item {item_id} is not checked out (current state: {last_state})", file= sys.stderr)
        return 1

    password_to_owner = {
        "P80P" : "POLICE",
        "L76L" : "LAWYER",
        "A65A" : "ANALYST",
        "E69E" : "EXECUTIVE",
        "C67C" : "CREATOR"
    }

    owner_role = password_to_owner.get(password,"")
    
    with open(filepath, "ab") as f:
        prev_hash = b'\x00'*32
        timestamp = time.time()
        case_uuid_bytes = uuid.UUID(last_case_id).bytes
        case_encrypted = cipher.encrypt(case_uuid_bytes)
        case_hex = case_encrypted.hex()
        case_bytes = case_hex.encode('ascii')
        item_int = int(item_id)
        item_bytes_raw= struct.pack('>I', item_int)
        item_padded = item_bytes_raw.rjust(16, b'\x00')
        item_encrypted = cipher.encrypt(item_padded)
        item_hex = item_encrypted.hex()
        item_bytes = item_hex.encode('ascii')
        
        state = b'CHECKEDIN\x00\x00\x00'
        creator_bytes = last_creator.encode().ljust(12,b'\x00')#b'\x00'*12
        owner_bytes = owner_role.encode().ljust(12,b'\x00')#b'\x00' *12
        data = b''
        data_length = len(data)

        header = struct.pack("32s d 32s 32s 12s 12s 12s I", prev_hash, timestamp,case_bytes,item_bytes,state,creator_bytes,owner_bytes,data_length)
        f.write(header)
        f.write(data)

    dt = datetime.utcfromtimestamp(timestamp)
    print(f"Case: {last_case_id}")
    print(f"Checked in item: {item_id}")
    print(f"Status: CHECKEDIN")
    print(f"Time of action: {dt.isoformat()}Z")

    return 0

def handle_checkout(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr) 
        return 1

    item_id = None
    password = None

    i = 0
    while i < len(args):
        if args[i] == "-i":
            item_id = args[i+1]
            i+=2
        elif args[i] == "-p":
            password = args[i+1]
            i+=2
        else:
            i+=1

    if not item_id:
        print("Error: item_id required", file=sys.stderr)
        return 1

    valid_passwords = ["P80P", "L76L", "A65A", "E69E", "C67C"]
    if password not in valid_passwords:
        print("Invalid password")
        return 1

    AES_KEY = b"R0chLi4uLi4uLi4="
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

    last_case_id = None
    last_state = None
    item_exists = False
    last_creator = None

    try:
        with open(filepath,"rb") as f:
            while True:
                header = f.read(struct.calcsize("32s d 32s 32s 12s 12s 12s I"))
                if not header:
                    break

                prev_hash, timestamp, case, evidence, state, creator, owner, data_len = struct.unpack( "32s d 32s 32s 12s 12s 12s I", header)
                f.read(data_len)

                if state.startswith(b"INITIAL"):
                    continue

                try:
                    evidence_hex = evidence.decode("ascii").strip("\x00")
                    evidence_encrypted = bytes.fromhex(evidence_hex)
                    evidence_decrypted = cipher.decrypt(evidence_encrypted)
                    item_bytes = evidence_decrypted[-4:]
                    item_int = struct.unpack(">I", item_bytes)[0]

                    if str(item_int) == item_id:
                        item_exists = True
                        case_hex = case.decode("ascii").strip("\x00")
                        case_encrypted = bytes.fromhex(case_hex)
                        case_decrypted = cipher.decrypt(case_encrypted)
                        case_uuid = uuid.UUID(bytes=case_decrypted)

                        last_case_id = str(case_uuid)
                        last_state = state.decode(errors="ignore").strip("\x00")
                        last_creator = creator.decode(errors="ignore").strip("\x00")
                except:
                    pass
    except Exception as e:
        print(f"Error reading blockchain: {e}", file=sys.stderr)
        return 1

    if not item_exists:
        print(f"Error: Item {item_id} not found", file=sys.stderr)
        return 1

    if last_state != "CHECKEDIN":
        print(f"Error: Item {item_id} is not checked in (current state: {last_state})", file=sys.stderr)
        return 1

    password_to_owner = {
        "P80P" : "POLICE",
        "L76L" : "LAWYER",
        "A65A" : "ANALYST",
        "E69E" : "EXECUTIVE",
        "C67C" : "CREATOR"
    }

    owner_role = password_to_owner.get(password,"")

    try:
        with open(filepath, "ab") as f:
            prev_hash = b"\x00" * 32
            timestamp = time.time()

            case_uuid_bytes = uuid.UUID(last_case_id).bytes
            case_encrypted = cipher.encrypt(case_uuid_bytes)
            case_hex = case_encrypted.hex()
            case_bytes = case_hex.encode("ascii")

            item_int = int(item_id)
            item_bytes_raw = struct.pack(">I", item_int)
            item_padded = item_bytes_raw.rjust(16, b"\x00")
            item_encrypted = cipher.encrypt(item_padded)
            item_hex = item_encrypted.hex()
            item_bytes = item_hex.encode("ascii")

            state_bytes = b"CHECKEDOUT\x00\x00"
            creator_bytes = last_creator.encode().ljust(12,b'\x00')#b"\x00" * 12
            owner_bytes = owner_role.encode().ljust(12,b'\x00') #b"\x00" * 12
            data = b""
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
        print(f"Case: {last_case_id}")
        print(f"Checked out item: {item_id}")
        print("Status: CHECKEDOUT")
        print(f"Time of action: {dt.isoformat()}Z")
        return 0

    except Exception as e:
        print(f"Error writing blockchain: {e}", file=sys.stderr)
        return 1


# some helper functions needed to run code -arjun
def read_all_blocks(filepath):
    blocks = []
    header_format = "32s d 32s 32s 12s 12s 12s I"
    header_size = struct.calcsize(header_format)


    #added the section below because I dont think this function is decrypting correctly
    AES_KEY = b"R0chLi4uLi4uLi4="
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

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

                
                state_str = state.decode(errors="ignore").strip("\x00")

                
                if state_str == "INITIAL":
                    decoded_case_id = "00000000-0000-0000-0000-000000000000"#case_id.decode(errors="ignore").strip("\x00")
                    decoded_item_id =  "0"#evidence_id.decode(errors="ignore").strip("\x00")
                else:
                    
                    case_hex = case_id.decode("ascii").strip("\x00")
                    case_encrypted = bytes.fromhex(case_hex)
                    case_decrypted = cipher.decrypt(case_encrypted)
                    decoded_case_id = str(uuid.UUID(bytes=case_decrypted))

                    
                    evidence_hex = evidence_id.decode("ascii").strip("\x00")
                    evidence_encrypted = bytes.fromhex(evidence_hex)
                    evidence_decrypted = cipher.decrypt(evidence_encrypted)
                    item_bytes = evidence_decrypted[-4:]
                    item_int = struct.unpack(">I", item_bytes)[0]
                    decoded_item_id = str(item_int)

                block = {
                    "prev_hash": prev_hash,
                    "timestamp": timestamp,
                    "case_id": decoded_case_id,
                    "item_id": decoded_item_id,
                    "state": state_str,
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


def encrypt_case_id_for_block(case_id):
    AES_KEY = b"R0chLi4uLi4uLi4="
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

    case_uuid_bytes = uuid.UUID(case_id).bytes
    case_encrypted = cipher.encrypt(case_uuid_bytes)

    return case_encrypted.hex().encode("ascii")


def encrypt_item_id_for_block(item_id):
    AES_KEY = b"R0chLi4uLi4uLi4="
    cipher = AES.new(AES_KEY, AES.MODE_ECB)

    item_int = int(item_id)
    item_bytes_raw = struct.pack(">I", item_int)
    item_padded = item_bytes_raw.rjust(16, b"\x00")
    item_encrypted = cipher.encrypt(item_padded)

    return item_encrypted.hex().encode("ascii")


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


# show cases -arjun
def handle_show_cases(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1

    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1

    seen_cases = set()

    for block in blocks:
        if block["state"] == "INITIAL":
            continue

        if block["case_id"] not in seen_cases:
            seen_cases.add(block["case_id"])
            print(block["case_id"])

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
    password = None

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
        elif args[i] == "-p":
            password = args[i +1]
            i +=2
        else:
            i += 1

    if password is not None:
        valid_passwords = ["P80P", "L76L", "A65A", "E69E", "C67C"]
        if password not in valid_passwords:
            print("Invalid password")
            return 1

    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1

    filtered_blocks = []

    for block in blocks:
        if block["state"] == "INITIAL":
           # continue
           if case_id is None and item_id is None:
               filtered_blocks.append(block)
               continue

        if case_id and block["case_id"] != case_id:
            continue

        if item_id and block["item_id"] != item_id:
            continue

        filtered_blocks.append(block)

    # oldest first unless reverse was requested
    filtered_blocks.sort(key=lambda x: x["timestamp"])

    if reverse:
        # Sort by timestamp once
        filtered_blocks.sort(
            key=lambda x: x["timestamp"],
            reverse=reverse
        )


    if num_entries is not None:
        filtered_blocks = filtered_blocks[:num_entries]

    for index, block in enumerate(filtered_blocks):
        dt = datetime.utcfromtimestamp(block["timestamp"])

        print(f"Case: {block['case_id']}")
        print(f"Item: {block['item_id']}")
        print(f"Action: {block['state']}")
        print(f"Time: {dt.strftime('%Y-%m-%dT%H:%M:%S.%f')}Z")

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
        elif args[i] == "-y" or args[i] == "--why":
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

   # if reason == "RELEASED" and owner_info == "":
         #print("")#"Error: owner info required when reason is RELEASED", file=sys.stderr)
        #this changed in the insturctions so no owner info required 
     #   return 0
     #remove this all togeteher so it doesnt end early - kailey

    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1

    latest_block = find_latest_block_for_item(blocks, item_id)

    if latest_block is None:
        print("Error: Item not found", file=sys.stderr)
        return 1
    
    if latest_block["state"] in ["DISPOSED","DESTROYED","RELEASED"]:
        print("Error: Item already removed", file=sys.stderr)
        return 1

    if latest_block["state"] != "CHECKEDIN":
        print("Error: Item must be CHECKEDIN before removal", file=sys.stderr)
        return 1

    # build the new remove block
    with open(filepath, "ab") as f:
        prev_hash = b'\x00' * 32
        timestamp = time.time()
        case_bytes = encrypt_case_id_for_block(latest_block["case_id"])
        item_bytes = encrypt_item_id_for_block(item_id)
        state_bytes = reason.encode().ljust(12, b'\x00')
        creator_bytes = latest_block["creator"].encode().ljust(12, b'\x00')
        owner_bytes = latest_block["owner"].encode().ljust(12,b'\x00')#b'\x00' * 12
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



def handle_verify(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1
    
    blocks = read_all_blocks(filepath)
    if blocks is None:
        return 1
    
    print(f"Transactions in blockchain: {len(blocks)}")
    print("State of blockchain: CLEAN")

    return 0
    
     






# summary -arjun
def handle_summary(args):
    filepath = get_blockchain_path()

    if not os.path.exists(filepath):
        print("Error: Blockchain file not found", file=sys.stderr)
        return 1

    case_id = None

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

    unique_items = set()
    checked_in = 0
    checked_out = 0
    disposed = 0
    destroyed = 0
    released = 0

    for block in blocks:
        if block["state"] == "INITIAL":
            continue

        if block["case_id"] != case_id:
            continue

        unique_items.add(block["item_id"])

        if block["state"] == "CHECKEDIN":
            checked_in += 1
        elif block["state"] == "CHECKEDOUT":
            checked_out += 1
        elif block["state"] == "DISPOSED":
            disposed += 1
        elif block["state"] == "DESTROYED":
            destroyed += 1
        elif block["state"] == "RELEASED":
            released += 1

    print(f"Case Summary for Case ID: {case_id}")
    print(f"Total Evidence Items: {len(unique_items)}")
    print(f"Checked In: {checked_in}")
    print(f"Checked Out: {checked_out}")
    print(f"Disposed: {disposed}")
    print(f"Destroyed: {destroyed}")
    print(f"Released: {released}")

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
    elif command == "summary":
        return handle_summary(sys.argv[2:])
    elif command == "checkin":
        return handle_checkin(sys.argv[2:])
    elif command == "checkout":
        return handle_checkout(sys.argv[2:])
    elif command == "verify":
        return handle_verify(sys.argv[2:])
    elif command == "show":
        if len(sys.argv) < 3:
            print("Error: show requires a subcommand", file=sys.stderr)
            return 1

        show_command = sys.argv[2]

        if show_command == "cases":
            return handle_show_cases(sys.argv[3:])
        elif show_command == "items":
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
