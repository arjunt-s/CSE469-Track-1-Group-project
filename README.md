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

