#       _                 _                       _       _           _ 
#   ___(_)_ __ ___  _ __ | |_   _ _   _ _ __   __| | __ _| |_ ___  __| |
#  / __| | '_ ` _ \| '_ \| | | | | | | | '_ \ / _` |/ _` | __/ _ \/ _` |
#  \__ \ | | | | | | |_) | | |_| | |_| | |_) | (_| | (_| | ||  __/ (_| |
#  |___/_|_| |_| |_| .__/|_|\__, |\__,_| .__/ \__,_|\__,_|\__\___|\__,_|
#                  |_|      |___/      |_|                              
#
#   by februu 2024
#
# +-----------+--------------------------------------------+
# | Exit Code |                  Message                   |
# +-----------+--------------------------------------------+
# |         0 | Update finished correctly.                 |
# |        -1 | No update needed.                          |
# |         1 | Cannot connect to the Internet.            |
# |         2 | Bad configuration(.autoupdate file or pb   |
# |         3 | Error while unzipping the file.            |
# |         4 | Other error has occured.                   |
# +-----------+--------------------------------------------+
#
# +------------+---------------------+
# |   Flags    |       Meaning       |
# +------------+---------------------+
# | (no flags) | check for updates   |
# | f          | force (re-)download |
# +------------+---------------------+
#

from requests import get, RequestException
from configparser import ConfigParser, Error as ConfigError
from zipfile import ZipFile, error as ZipError
from sys import exit, argv

localConfig = ConfigParser()
onlineConfig = ConfigParser()

def downloadAndApplyUpdate(source : str, version : str):
    try:
        req = get(source)
        req.raise_for_status()
        
        filename = source.split('/')[-1]
        with open(filename, 'wb') as output_file:
            output_file.write(req.content)
        
        with ZipFile(filename) as zFile:
            zFile.extractall()
        
        localConfig.set("local_version", "current_version", version)
        with open('.autoupdate', 'w') as file:
            localConfig.write(file)
        
        exit(0)
    except RequestException:
        exit(1)
    except ZipError:
        exit(3)
    except Exception as e:
        print(f"Error while updating: {e}")
        exit(4)

def checkForUpdates(*, forced=False):
    try:
        localConfig.read('.autoupdate')
        localVersion = localConfig.get("local_version", "current_version")
        pbLink = f'https://pastebin.com/raw/{localConfig["local_version"]["update_token"]}'

        req = get(pbLink)
        req.raise_for_status()

        onlineConfig.read_string(req.text.strip())
        currentVersion = str(onlineConfig["version"]["current_version"])

        if not forced and currentVersion == localVersion:
            exit(-1)
        else:
            downloadAndApplyUpdate(onlineConfig["version"]["source"], currentVersion)
    except RequestException:
        exit(1)
    except ConfigError:
        exit(2)
    except Exception:
        exit(4)


def main():
    if '-f' in argv:
        checkForUpdates(forced=True)
    else:
        checkForUpdates()


if __name__ == "__main__":
    main()
