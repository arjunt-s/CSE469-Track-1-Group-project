import os
import subprocess

# set test blockchain file so it's not messing up the real file
TEST_FILE = "test_blockchain.dat"
os.environ["BCHOC_FILE_PATH"] = TEST_FILE


def run_command(cmd):
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("ERROR:", result.stderr)


def clean():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


def test_all():
    clean()

    # init
    run_command("./bchoc init")

    # add items
    run_command("./bchoc add -c case123 -i 1 -g arjun -p C67C")
    run_command("./bchoc add -c case123 -i 2 -g arjun -p C67C")

    # show items
    run_command("./bchoc show items -c case123")

    # show history
    run_command("./bchoc show history")

    # remove item
    run_command("./bchoc remove -i 1 -y DISPOSED -p C67C")

    # show history again
    run_command("./bchoc show history -i 1")

    # edge case: remove again (this should fail)
    run_command("./bchoc remove -i 1 -y DISPOSED -p C67C")


if __name__ == "__main__":
    test_all()
