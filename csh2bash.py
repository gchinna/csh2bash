import sys
import os
import logging
import re

_DEBUG = False

log = logging.getLogger(__name__);

if _DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


if len(sys.argv) != 2:
    print("invalid number of argumnets: {}".format(len(sys.argv) -1))
    print("usage: python3 csh2sh.py <input_csh_file>")
    sys.exit()

cshfile = sys.argv[1]
if not os.path.isfile(cshfile):
    print("input file {} does not exist! exiting ...".format(cshfile))
    sys.exit()

bashfile = cshfile.replace(".csh", ".sh")
log.info("input file: {}, output file: {}".format(cshfile, bashfile))

if os.path.isfile(bashfile):
    log.warning("output file {} exists! overwriting ...".format(bashfile))

comRegex  = re.compile(r'^#(.+)')   # comment regex
cshRegex  = re.compile(r'^#(\s*!\s*/bin/csh\s+-f)')  # csh header regex
envRegex  = re.compile(r'(setenv)\s+(\S+)\s(\S+)')  # setenv regex
pathRegex = re.compile(r'(set\s+path)\s*=\s*(.+)')  # set path regex
blnkRegex = re.compile(r'^$')  # blank line regex
echoRegex = re.compile(r'(echo)\s+(.+)')  # echo regex


with open(cshfile, 'r') as infp, open(bashfile, 'w') as outfp:
    for cnt, rdline in enumerate(infp):
        ##log.info("Line {}: {}".format(cnt, rdline.strip()))
        rdline = rdline.strip()

        comMatch = comRegex.search(rdline)
        ## add # prefix to wrline if commented line and continue processing rdline
        if comMatch:
            wrline = "#"
        else:
            wrline = ""

        match = cshRegex.search(rdline)
        if match:
            log.debug("{}, !/bin/csh found: {}".format(cnt, match.group()))
            wrline = wrline + "!/bin/bash -f\n"  ## wrline already got # prefix
            outfp.write(wrline)
            continue

        match = envRegex.search(rdline)
        if match:
            log.debug("{}, setenv found: {}".format(cnt, match.group()))
            wrline = wrline + "export {}={}\n".format(match.group(2), match.group(3))
            outfp.write(wrline)
            continue

        match = pathRegex.search(rdline)
        if match:
            log.debug("{}, path found: {}".format(cnt, match.group()))
            ##log.info("path found: {}".format(match.group(2)))
            outpath = re.sub("[()]", "", match.group(2))  # strip leading/trailing ( )
            outpath = re.sub("\s+", ":", outpath.strip())  # strip leading/trailing spaces (if any) and replace spaces with :
            wrline = wrline + "export PATH={}\n".format(outpath)
            outfp.write(wrline)
            continue

        blnkMatch = blnkRegex.search(rdline)
        echoMatch = echoRegex.search(rdline)
        if blnkMatch or comMatch or echoMatch:
            log.debug("{}, blank/comment/echo found: {}".format(cnt, rdline))
        else: ## unknown construct - issue warning and write to output file as is.
            log.warning("{}, unknown/unsupported csh cmd found: {}".format(cnt, rdline))
        wrline = wrline + rdline + "\n"
        outfp.writelines(wrline)
