#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from socket import gaierror, gethostbyname
import yaml, json, time, os, http.client


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

def get_groups(host):
    # Not too sure about these headers, but they work
    headers = {
        'Host': 'groups.google.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'text/x-gwt-rpc; charset=utf-8',
        'X-Groups-Time-Zone': '4402827_48_52_123900_48_436380',
        'X-GWT-Permutation': '5D5151DBCAFD1C0ED54B504BC5CC86D2',
        'X-GWT-Module-Base': 'https://groups.google.com/forum/',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    # Setup connection to groups.google.com
    conn = http.client.HTTPSConnection('groups.google.com')

    # Get the xsrf from the base site
    xsrfurl = 'https://groups.google.com/a/{}/forum/#!forumsearch/'.format(host)
    conn.request('GET', xsrfurl)
    response = conn.getresponse().read().decode('UTF-8')
    xsrf = response.split('xsrf-token":"')[1].split('"')[0]

    # Add the xsrf into the data
    # no idea what any of these fields mean, except the xsrf, but it works
    data='7|3|10|https://groups.google.com/forum/|D2FD55322ACD18E1E5E0D2074EB623A5|5m|{}|_|getMatchingForums|5t|4l|I|59|1|2|3|4|5|6|6|7|8|8|7|9|9|0|10|0|-2|0|0|20|'.format(
        xsrf
    )

    # Request the yaml-encoded data and decode it
    conn.request('POST', 'https://groups.google.com/a/{}/forum/fsearch?appversion=1&hl=en&authuser=0'.format(host), body=data, headers=headers)
    response = conn.getresponse().read().decode('utf-8')[4:]
    response = yaml.safe_load(response)

    # Again, no idea what the other fields except for the third-last one mean
    return response, response[-3]

if __name__ == '__main__':
    main()
