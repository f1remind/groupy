#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
import time, os
import http.client
import requests

def main():
    MAX_WORKERS = None # none means cpu-cores * 5
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

    # Load processed targets into a list
    with open(STATEFILE) as f:
        processed = [l.strip() for l in f.readlines()]

    # Load targets into a list
    print("Checking if links have been resolved before..") # Switch to real db soon
    with open(QUEUE_FILE) as f:
        for l in f.readlines():
            l = l.strip()
            if not l or l in processed:
                continue
            targets.append([BASEURL, l])

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in executor.map(work, targets):
            linebuffer += result[0][0] + '/a/' + result[0][1] + '/forum/'+ ',' + result[1] + '\n'
            processedbuffer += result[0][1] + '\n'
            currentcount = linebuffer.count('\n')
            if currentcount >= BATCH_LINES:
                update(linebuffer, OUTPUT_FILE)
                update(processedbuffer, STATEFILE)
                linecount += currentcount
                print("Wrote {} lines, total {}".format(currentcount, linecount))
                linebuffer = ''
                processedbuffer = ''

    if linebuffer:
        update(linebuffer, OUTPUT_FILE)

    end = time.time()

    print("Finished {} Elements in {:.2f}s".format(len(targets), end-start))

def work(target, use_requests=False):
    if use_requests: # requests is more stable and useful for more applications
        resp = requests.head(target[0] + '/a/{}/forum/'.format(target[1]))
        res = resp.headers['Content-Length']
    else: # simply getting a HEAD response header is faster this way tho, about twice
        conn = http.client.HTTPConnection(target[0])
        conn.request("HEAD", "/a/{}/forum/".format(target[1]))
        res = conn.getresponse()
        res = res.getheader('Content-Length')
        if not res:
            res = '0'
    return target, res

def update(text, filename):
    with open(filename, 'a') as f:
        f.write(text)


if __name__ == '__main__':
    main()
