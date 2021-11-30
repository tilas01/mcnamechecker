def main():
    from requests import get
    from time import sleep
    from datetime import datetime
    import configparser
    import os
    import sys
    badconfig = 0
    print("Disclaimer:")
    print("This program spams Mojangs api with requests.")
    print("I recommend using a vpn while in use although this will slow down the program depending on your connection.\n")
    '''
    checks settings directory/files exists
    if they dont they will be created
    '''
    if os.path.isdir("settings"):
        print("settings directory found!")
    else:
        print("settings directory does not exist.")
        os.mkdir("settings")
        print("settings directory created...")
    if os.path.isfile("settings/config.txt"):
        print("config.txt found!")
        try:
            config = configparser.ConfigParser() #testing config.txt
            config.read(os.path.expanduser('settings/config.txt'))
            config.get('config','break')
            config.get('config','time')
            config.get('config','mtime')
        except:
            badconfig = 1 #if cant access any config setting will mark it as a badconfig
    else:
        print("config.txt does not exist.")
        print("Generating config.txt...")
        f = open("settings/config.txt", 'w') #regenerate a default config
        f.write("[config]\n\n#take a break per this amount of requests\nbreak = 200\n#how long to take breaks for (seconds)\ntime = 60\n#how long to take breaks for when mojang blocks you from sending requests (seconds)\nmtime = 60")
        f.close()
    if os.path.isfile("settings/logs.txt"):
        print("logs.txt found!")
    else:
        print("logs.txt does not exist.")
        f = open("settings/logs.txt", 'w')
        f.close()
        print("logs.txt created...")
    if os.path.isfile("settings/list.txt"):
        print("list.txt found!")
    else:
        print("list.txt does not exist.")
        f = open("settings/list.txt", 'w')
        f.close()
        print("\nA list.txt file has been created for you but you must put usernames in it manually.")
        print("Add names to list.txt and relaunch this application.\n")
        a = input("Press enter to exit...")
        sys.exit()
    print("Grabbing config...\n")
    '''
    grabs config
    if marked as a bad config display extra text and use fallback values
    '''
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('settings/config.txt'))
    per = config.get('config','break', fallback='200') #fallback values
    delay = config.get('config','time', fallback='200')
    mdelay = config.get('config','mtime', fallback='60')
    if badconfig == 1:
        print("Failed to grab config...")
        print("Default settings will be used\n")
    print("Application config:\n")
    print (f"Break: {per}")
    print(f"Break Time: {delay}")
    print(f"Mojang Break Time: {mdelay}")
    if badconfig == 1: #if marked as a bad configuration display these messages
        print("Repair your config.txt file to edit these values.")
        print("Deleting your config.txt file will regenerate it in this directory.\n")
    else:
        print("Visit your config.txt file to understand these settings or modify them.\n")
    while True:
        a = input("Begin [y/n]? ")
        if a == "y":
            break
        elif a == "n":
            print("Exiting...")
            sleep(1)
            sys.exit()
        else:
            print("Invalid Response.")
    #setup for the rest of the program
    acc = []
    fails = 0
    attempt = 0
    s = 0
    f = open("settings/list.txt", 'r') #saves number of lines in list.txt to a variable for later
    checks = sum(1 for line in f)
    f.close()
    with open('settings/list.txt') as x:
        for line in x: #loop for each line in list.txt run a check
            attempt = attempt + 1
            line = line.strip()
            r = get(f"https://api.mojang.com/users/profiles/minecraft/{line}")
            if attempt == int(per): #if attempts = number of requests required for a break (setting defined in config.txt)
                '''
                these checks dont matter
                just in there to check the one name before the break begins
                should be the exact same as the main checks
                '''
                if r.status_code == 204:
                    acc.append(line)
                    now = datetime.now()
                    currenttime = now.strftime("%d/%m/%Y %H:%M:%S")
                    l = open("settings/logs.txt", 'a')
                    l.write(f"Success: Username {line} is not taken! [{currenttime}]\n")
                    l.close()
                    print(f"Success: Username {line} is not taken! [{attempt}] [{checks - attempt}/{checks}]")
                    s = s + 1
                elif r.status_code == 200:
                    uuid = r.json()["id"]
                    print(f'Fail: Username {line} is already taken ({uuid}) [{attempt}] [{checks - attempt}/{checks}]')
                    fails = fails + 1
                elif r.status_code == 400:
                    print(f"Fail: Bad request on username {line}! [{attempt}] [{checks - attempt}/{checks}]")
                    fails = fails + 1
                elif r.status_code == 429:
                    print("Mojang has temporarily blocked your requests")
                    print(f"Sleeping for {mdelay} seconds...")
                    sleep(int(mdelay))
                else:
                    print(f"Fail: Unknown error occured on username {line}")
                    fails = fails + 1
                '''
                end of the almost useless checks
                '''
                print(f"You have submitted {per} requests.")
                print(f"The program will now sleep for {delay} seconds to avoid being blocked from sending requests.")
                sleep(int(delay)) #sleep for amount set in config
            elif r.status_code == 204: #if successful response code
                acc.append(line)
                now = datetime.now()
                currenttime = now.strftime("%d/%m/%Y %H:%M:%S") #calculate time into currenttime
                l = open("settings/logs.txt", 'a') #log successful attempt to logs.txt
                l.write(f"Success: Username {line} is not taken! [{currenttime}]\n")
                l.close()
                print(f"Success: Username {line} is not taken! [{attempt}] [{checks - attempt}/{checks}]")
                s = s + 1
            elif r.status_code == 400: #bad request
                print(f"Fail: Bad request on username {line}! [{attempt}] [{checks - attempt}/{checks}]")
                fails = fails + 1
            elif r.status_code == 200: #if username is taken
                uuid = r.json()["id"]
                print(f'Fail: Username {line} is already taken ({uuid}) [{attempt}] [{checks - attempt}/{checks}]')
                fails = fails + 1
            elif r.status_code == 429: #if mojang has temporarily blocked your requests
                print("Mojang has temporarily blocked your requests")
                print(f"Sleeping for {mdelay} seconds...")
                sleep(int(mdelay)) #sleep for amoutn set in config file for a mojang block
            else: #any other response code reply with unknown error
                print(f"Fail: Unknown error occured on username {line}")
                fails = fails + 1
    #summary
    x.close()
    print("\nSummary:")
    print(f"Total checks: {attempt}")
    print(f"Failed checks: {fails}")
    print(f"Successful checks: {s}\n")
    print("Available usernames:")
    print(*acc, sep = "\n")
    print("\nAll successful checks have been saved to logs.txt...")
    a=input("Press enter to exit...")


if __name__ == '__main__':
    main()