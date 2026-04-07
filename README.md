# CSE469-Track-1-Group-project
This is going a repo that will house all source code relating to Track 1
- Use any general purpose programming language (preferably Python) to develop a program, that is
executable on Ubuntu 18.04 64-bit or later versions
- Submission on Gradescope
- Grading will done via gradescope (Autograding)

  Deliverables -
 - Progress report(Bi-weekly)
 - Checkpoint Report(Google form)
 - Source code
 - README
 - Demo video(Youtube Unlisted)
 - Project Repor

* Run 'make' first to get the correct file names. 

# INIT Insutrction Use Case:
On first run of this command it will create the INITIAL block.
```./bchoc init```
On second run of the command, it will say file found with INITIAL block.

# ADD Instruction Use Case:
The command should look like this
```./bchoc add -c case_id -i item_id -p password```
If we take this command 
```./bchoc add -c c84e339e-5c0f-4f4d-84c5-bb79a3c1d2a2 -i 1004820154 -g 1Ze4XNk8PuUp -p C67C``` 
as given in the outline document we will get output: 

```
Added item: 1004820154
Status: CHECKEDIN
Time of action: 2026-03-07T19:00:43.762459Z
```

which is as expected as well. 

Additionally, having multiple '-i' item_ids can be added at once as long as all other information is correct.



# Added Functions 4/7/2026 by Arjun:

# SHOW ITEMS
Command:
./bchoc show items -c <case_id>

Description:
This function reads through the blockchain file and prints all unique item IDs associated
with the given case ID. It skips the initial genesis block and avoids printing duplicates.

# SHOW HISTORY
Command:
./bchoc show history [-c case_id] [-i item_id] [-n num_entries] [-r]

Description:
This function displays the history of blockchain entries. It can filter by case ID,
item ID, limit the number of entries shown, and reverse the order so the newest entries
appear first.

Supported options:
-c  filter by case ID
-i  filter by item ID
-n  show only a certain number of entries
-r  reverse the order of the displayed entries

# REMOVE FUNCTION
Command:
./bchoc remove -i <item_id> -y <reason> -p <password> [-o owner_info]

Description:
This function removes an item from further use in the blockchain by creating a new block
with a removal state. The item must already exist and must currently be in CHECKEDIN state.

Valid removal reasons:
DISPOSED
DESTROYED
RELEASED

If RELEASED is used, owner information must also be provided with -o.

Helper Functions-

read_all_blocks(filepath)
Reads all blocks from the blockchain file and stores them in a list of dictionaries
so the other functions can work with them more easily.

find_latest_block_for_item(blocks, item_id)
Finds the most recent block associated with a specific item ID.

How these additions work-

These functions were added onto the existing implementation without changing the original
program structure too much. The new code follows the same style as the rest of the file,
using manual argument parsing and the same block reading format already used in the project.

Build / Run

Run:
make

This creates the executable:
./bchoc
