#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from socket import gaierror, gethostbyname
import time, os, http.client

def main():
    MAX_WORKERS = 250 # none means cpu-cores * 5
    QUEUE_FILE = 'queue.txt'
    OUTPUT_FILE = 'output.txt'
    STATEFILE = 'processed.txt'
    BATCH_LINES = 200
    BASEURL = 'groups.google.com'

    start = time.time()
    linebuffer = ''
    processedbuffer = ''
    linecount = 0
    targets = []
    processed = []

    if not os.path.exists(STATEFILE):
        open(STATEFILE, 'w').close()

    if not os.path.exists(OUTPUT_FILE):
        open(OUTPUT_FILE, 'w').close()


    # Load targets into a list
    print(time.ctime(), "Checking if links have been resolved before..") # Switch to real db soon
    with open(QUEUE_FILE) as f:
        for l in f.readlines():
            l = l.strip()
            if l:
                targets.append(l)

    # Load processed targets into a list
    with open(STATEFILE) as f:
        for line in f.readlines():
            line = line.strip()
            while line in targets:
                targets.remove(line)


    print(time.ctime(), "Done, starting scraper")

    targetsize = sum([sum([len(e) for e in entry]) for entry in targets])
    print(time.ctime(), "Targets consume {:.2f}MB of space".format(targetsize / 2**20))

    workstart = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in executor.map(work, [[BASEURL, target] for target in targets]):
            linebuffer += result[0][0] + '/a/' + result[0][1] + '/forum/'+ ',' + result[1] + '\n'
            processedbuffer += result[0][1] + '\n'
            currentcount = linebuffer.count('\n')
            if currentcount >= BATCH_LINES:
                update(linebuffer, OUTPUT_FILE)
                update(processedbuffer, STATEFILE)
                linecount += currentcount
                print(time.ctime(), "Wrote {} lines, total {} ({:.2f}/s)".format(
                    currentcount, linecount, linecount/(time.time()-workstart)))
                linebuffer = ''
                processedbuffer = ''

    if linebuffer:
        update(linebuffer, OUTPUT_FILE)

    end = time.time()

    print(time.ctime(), "Finished {} Elements in {:.2f}s".format(len(targets), end-start))

def work(target, use_requests=False):
    res = None
    while res is None:
        try:
            conn = http.client.HTTPConnection(target[0])
            conn.request("HEAD", "/a/{}/forum/".format(target[1]))
            res = conn.getresponse()
            res = res.getheader('Content-Length')
            if not res:
                res = '0'
        except gaierror:
            print("Retrying", target[0] + ' with /a/' + target[1] + '/forum/')
    return target, res

def update(text, filename):
    with open(filename, 'a') as f:
        f.write(text)


if __name__ == '__main__':
    main()
