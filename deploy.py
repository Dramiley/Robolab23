"""
call deploy_once.py with the same arguments but in while loop with press any key to continue

"""

while True:
    exec(open("deploy_once.py").read())
    input("Press any key to continue...")
