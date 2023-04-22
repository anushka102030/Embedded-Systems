import time
#Functions imported from website_control
from website_control import block_write, unblock_write

websites = []

#Read websites from sites.txt
with open("sites.txt", "r+") as f:
    websites = f.read().splitlines()

ITERATIONS = 40

# Similar to GUI loop but finite iterations
for i in range(0,ITERATIONS):

    #Block 20 iterations
    if i <= 30:
        if i == 0:
            print("BLOCKING all URLs listed in sites.txt")
        block_write(websites)

    if i == 21:
        print("UNBLOCKING all URLs except first two")
        unblock_sites = websites[2:]
        websites = websites[:2]
        unblock_write(unblock_sites)


    if i == 31:
        print("UNBLOCKING first two URLs")
        unblock_write(websites)

    time.sleep(5)
