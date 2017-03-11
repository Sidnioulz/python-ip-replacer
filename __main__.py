#!/usr/bin/env python3

from utils import registerTimePrint, tprnt
from collections import deque
import getopt
import sys
import os
import re
import random
import shutil


USAGE_STRING = 'Usage: __main__.py [--help] --input=<DIR> --output=<DIR>'

ipRe = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
ipMap = dict()
nameMap = dict()

ipMap["0.0.0.0"] = "0.0.0.0"
ipMap["1.1.1.1"] = "1.1.1.1"
ipMap["127.0.0.1"] = "127.0.0.1"
ipMap["255.255.255.255"] = "255.255.255.255"


def mapIp(ip: str):
    ip = ip.group()
    if ip not in ipMap:
        ipMap[ip] = ".".join(str(random.randint(1, 254)) for _ in range(4))

    return ipMap[ip]


def mapIpInName(name: str):
    res = ipRe.findall(name)
    nameMap[name] = ipRe.sub(mapIp, name) if res else name
    return len(res)


def mapIpInFile(name: str):
    count = 0
    try:
        with open(name, "rb") as f:
            content = f.readlines()
            for binary in content:
                try:
                    readable = binary.decode("utf-8")
                    res = ipRe.findall(readable)
                    if res:
                        newContent = ipRe.sub(mapIp, readable)
                        count += len(res)
                except(UnicodeDecodeError) as e:
                    continue
    except(IOError) as e:
        tnprnt("Error when opening file '%s': %s" % (name, e), file=sys.stderr)
    
    return count
    
def rewriteFile(inFile: str, outFile: str):
    count = 0
    try:
        with open(inFile, "rb") as f:
            try:
                with open(outFile, "ab") as o:
                    content = f.readlines()
                    for binary in content:
                        try:
                            readable = binary.decode("utf-8")
                            res = ipRe.findall(readable)
                            if res:
                                newContent = ipRe.sub(mapIp, readable)
                                o.write(bytearray(newContent, "utf-8"))
                            else:
                                o.write(binary)
                        except(UnicodeDecodeError) as e:
                            o.write(binary)
            except(IOError) as e:
                tnprnt("Error when opening file '%s': %s" % (outFile, e),
                       file=sys.stderr)
    except(IOError) as e:
        tnprnt("Error when opening file '%s': %s" % (inFile, e),
               file=sys.stderr)
    

def main(argv):
    registerTimePrint()

    __opt_input = None
    __opt_output = None

    # Parse command-line parameters
    try:
        (opts, args) = getopt.getopt(argv, "hi:o:",
                                     ["input=",
                                      "output=",
                                      "help="])
    except(getopt.GetoptError):
        print(USAGE_STRING, file=sys.stderr)
        sys.exit(2)
    else:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print(USAGE_STRING + "\n\n\n\n")

                print("--input:\n\tDirectory containing files to convert.\n")
                print("--help:\n\tPrints this help information and exits.\n")
                print("--output:\n\tOutput directory for converted files.\n")
                sys.exit()
            elif opt in ('-i', '--input'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __opt_input = (arg[1:] if arg[0] == '=' else arg)
            elif opt in ('-o', '--output'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __opt_output = (arg[1:] if arg[0] == '=' else arg)

    if not __opt_input:
        tprnt("Error: missing input directory.", file=sys.stderr)
        print(USAGE_STRING, file=sys.stderr)
        sys.exit(2)

    if not __opt_output:
        tprnt("Error: missing output directory.", file=sys.stderr)
        print(USAGE_STRING, file=sys.stderr)
        sys.exit(2)
        
    nameMap[__opt_input] = __opt_output

    # TODO: browse all folder
    # TODO: for each file, collect IP in name, and in content
    # TODO: make an IP map
    # TODO: make a filename in->out map
    # TODO: re.sub each file and write to out

    # Browse input directory to map all IPs and file names.
    walkables = deque([__opt_input])
    for root, subdirs, files in os.walk(__opt_input):
        editCount = 0
        
        # Map IPs in subdir names, and add subdirs to list to browse.
        for subdir in subdirs:
            editCount += mapIpInName(subdir)
            walkables.append(os.path.join(root, subdir))
  
        # Map IPs in file names and content.
        for f in files:
            editCount += mapIpInName(f)
            editCount += mapIpInFile(os.path.join(root, f))
       
        if editCount:
            tprnt("Walking %s:\t%d directories and %d files found, "
                  "%d IPs found." % (
                   root, len(subdirs), len(files), editCount))
       
    # Print number of IPs translated.
    tprnt("Number of unique IPs translated: %d" % len(ipMap))

    # Build the output dir.
    if os.path.exists(__opt_output):
        backup = __opt_output.rstrip("/") + ".backup"
        if os.path.exists(backup):
            shutil.rmtree(backup)
        os.replace(__opt_output, backup)
    os.makedirs(__opt_output, exist_ok=False)


    # Browse again, compose output names and translate file contents.
    walkables = deque([__opt_input])
    for root, subdirs, files in os.walk(__opt_input):
        translated = nameMap[root]
        
        # Map IPs in subdir names, and add subdirs to list to browse.
        for subdir in subdirs:
            fullSubdir = os.path.join(root, subdir)
            fullTranslated = os.path.join(translated, nameMap[subdir])
            nameMap[fullSubdir] = fullTranslated
            os.makedirs(fullTranslated, exist_ok=False)
            walkables.append(fullSubdir)
  
        # Map IPs in file names and content.
        for f in files:
            fullF = os.path.join(root, f)
            fullTranslated = os.path.join(translated, nameMap[f])
            rewriteFile(fullF, fullTranslated)

    tprnt("Done.")


if __name__ == "__main__":
    main(sys.argv[1:])
