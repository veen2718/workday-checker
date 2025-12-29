import asyncio
import sys

from browser import *
from notify import sendNotification
from tableParse import log,last


if __name__ == "__main__":
    doHead=True
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "head":
            doHead = False
        elif command == "last":
            last()
            quit()
        if doHead:
            quit()
    nfMsg = asyncio.run(
        checkWorkday(doHead)
        )
    if nfMsg:
        sendNotification(*nfMsg)
        log(nfMsg)
    else:
        log("no new changes")
        

