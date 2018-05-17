#!/usr/bin/env python3
import http.client
from bs4 import BeautifulSoup as bs
import yaml, json

def get_groups(host):

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


    conn = http.client.HTTPSConnection('groups.google.com')
    url = 'https://groups.google.com/a/{}/forum/#!forumsearch/'.format(host)
    conn.request('GET', url)
    response = conn.getresponse().read().decode('ISO-8859-1')
    xsrf = response.split('xsrf-token":"')[1].split('"')[0]

    index = 0
    length = 15+1
    while length > 15:
        step = 20
        data = '7|3|10|https://groups.google.com/forum/|D2FD55322ACD18E1E5E0D2074EB623A5|5m|{}|_|getMatchingForums|5t|4l|I|59|1|2|3|4|5|6|6|7|8|8|7|9|9|0|10|0|-2|0|{}|{}|'.format(
            xsrf,
            index,
            step
        )
        conn.request('POST', 'https://groups.google.com/a/{}/forum/fsearch?appversion=1&hl=en&authuser=0'.format(host), body=data, headers=headers)
        response = conn.getresponse().read().decode('utf8', 'replace')[4:]
        response = yaml.safe_load(response)

        relevant = response[-3]
        print("Host:", host)
        for e in range(len(relevant)): #DEBUG SHIT
            print(str(e) + '\t' + relevant[e])


        if len(relevant) == 3:
            break
            
        offset = 0
        if relevant[5] == '5f':
            offset += 1

        firstdescription = relevant[7+offset]
        mystery1 = relevant[9+offset]
        privacytype = relevant[11+offset] # can be 'other', 'public' or 'domainpub' afaik

        if mystery1 == '2v':
            offset -= 2

        firsttitle = relevant[18+offset]


        if len(firstdescription):
            offset += 0#1



        # DEBUG SHIT
        print('firstdescription:', firstdescription)
        print('firsttitle:', firsttitle)
        print(relevant[offset+8:16])
        print(relevant[15+offset:19+offset])
        print('#'*80)
        break
        '''print('{:150}\t{}'.format(str(response[-3][:10]), host))

        if len(response) > 15:
            print(response[-3][:11])
            print('11:', response[-3][11])
            relevant = response[17:]

        print(response)
        print('#'*80)
        print(host)
        print("Length:", len(response))
        print("Length of content_entry", response[7])
        print("Current Index", response[8])
        print("Index:", index)
        print('Guess1:', response[-9])
        #print('Guess2:', response[85])
        print('#'*80)'''
        index += step
        length = len(response)
    return response[-3], response

def get_messages(host):

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


    conn = http.client.HTTPSConnection('groups.google.com')
    url = 'https://groups.google.com/a/{}/forum/#!search/*'.format(host)
    conn.request('GET', url)
    response = conn.getresponse().read().decode('UTF-8')
    xsrf = response.split('xsrf-token":"')[1].split('"')[0]

    index = 0
    length = 26+1
    while length > 26:
        step = 20
        data = '7|3|12|https://groups.google.com/forum/|D2FD55322ACD18E1E5E0D2074EB623A5|5m|{}|_|getMatchingMessages|5t|i|I|1u|5n|*|1|2|3|4|5|6|6|7|8|9|9|10|11|12|0|{}|{}|0|0|'.format(
            xsrf,
            index,
            step
        )
        conn.request('POST', 'https://groups.google.com/a/{}/forum/fsearch?appversion=1&hl=en&authuser=0'.format(host), body=data, headers=headers)
        response = conn.getresponse().read().decode('utf-8')[4:]
        response = yaml.safe_load(response)
        length = len(response)
        print(host)
        for e in response[-3]:
            print('\t' + e)
        print('#'*80)
        print("Length:", len(response))
        print("Index:", index)
        print('#'*80)
        index += step
    return response[-3]#, response

if __name__ == '__main__':
    with open('filtered.txt') as f:
        #get_messages('myposter.de')
        for line in f.readlines():
            #host = 'myposter.de'
            #host = 'blastingnews.com'
            data = {
                'url':line.strip(),
                'response':get_groups(line.strip())
            }
            #print(json.dumps(data))
