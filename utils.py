from datetime import datetime
import sys
import os
# from urllib.parse import urlparse, unquote
import re
import mimetypes
import random
import string


def genRandStr(count: int=10, chars=string.ascii_uppercase + string.digits):
    """Generate a random string."""
    return ''.join(random.choice(chars) for _ in range(count))


def time2Str(timestamp):
    """Transform a Zeitgeist timestamp into a human-readable string."""
    (timestamp, remainder) = divmod(timestamp, 1000)
    string = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    string += (".%d" % remainder)
    return string


# def urlToUnixPath(url):
#     """Convert a file:// URL to a Unix path string."""
#     p = urlparse(url)
#     return unquote(os.path.abspath(os.path.join(p.netloc, p.path)))


# def uq(s):
#     """Unquote a string."""
#     return unquote(s)


def hasIntersection(s1, s2):
    """Return True if two sets share at least one item, False otherwise."""
    for i in s1:
        for j in s2:
            if i == j:
                return True

    return False


def intersection(l1, l2):
    """Return the intersection of two lists. Naive implementation."""
    ret = []
    for i in l1:
        if i in l2:
            ret.append(i)

    return ret


# Get the last line of a file
BLOCKSIZE = 4096
def tail(f):
    # Save old position.
    oldPos = f.tell()

    # Seek to end of file to get file length.
    f.seek(0, 2)
    bytesInFile = f.tell()

    # Parse file to get tail.
    linesFound = 0
    totalBytesScanned = 0

    # Find any position (efficiently-ish) such that it's before 2+ lines.
    while (linesFound < 2 and bytesInFile > totalBytesScanned):
        byteBlock = min(BLOCKSIZE, bytesInFile - totalBytesScanned)
        f.seek( -(byteBlock + totalBytesScanned), 2)
        totalBytesScanned += byteBlock

        buff = f.read(BLOCKSIZE)
        try:
            countableBuff = buff.decode('utf-8')
        except(UnicodeDecodeError) as e:
            return None
        else:
            linesFound += countableBuff.count('\n')

    # Seek to that position where there are 2+ lines, and then read lines.
    f.seek(-totalBytesScanned, 2)
    lineList = list(f.readlines())

    # Reset position;
    f.seek(oldPos, 0)

    # Return the last line.
    try:
        readableLine = lineList[-1].decode('utf-8')
    except(UnicodeDecodeError) as e:
        return None
    else:
        return readableLine


# Copied from StackExchange, timed prints.
import atexit
from time import time
from datetime import timedelta

__timed_print_start = time()

def __secondsToStr(t):
    global __timed_print_start
    return str(timedelta(seconds=t - __timed_print_start))

def tprnt(msg: str, file=sys.stdout):
    stripped = msg.lstrip("\n")
    leadingCount = len(msg) - len(stripped)
    print("%s%s: %s" % ("\n" * leadingCount, __secondsToStr(time()), stripped),
          file=file)

def __finalTimedPrint():
    tprnt("Exiting.")

def registerTimePrint():
    atexit.register(__finalTimedPrint)
