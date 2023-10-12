#encoding:utf-8
import requests
import json
import sys
import time
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
reload(sys)
sys.setdefaultencoding('utf8')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



#LZ
ID = "XXXXX"
SECRECT="XXXX"
url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(ID, SECRECT)

indir=os.path.split(os.path.realpath(__file__))[0]
token_file = os.path.join(indir,'.token.key')
used_file = os.path.join(indir,'.request.count')

def init():
    if not os.path.exists(token_file):
        os.mknod(token_file)

def refresh():
    init()
    while True:
        s = requests.get(url, verify=False)
        try:
            message = s.text
            h_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            with open(used_file, 'a+') as ufw:
                ufw.write("{0} {1}\n".format(h_time, str(message)))
            response_r=json.loads(message)
            expired_time = int(response_r["expires_in"]) + int(time.time())
            with open(token_file,'w') as fw:
                fw.write('{0} {1}\n'.format(int(expired_time),str(response_r["access_token"])))
            break
        except:
            continue

def get():
    init()
    while True:
        try:
            with open(token_file,'r') as fr:
                line = fr.readline()
                token_l = line.strip().split()
                expired_time = int(token_l[0])
                token_str = str(token_l[1])
                if int(time.time()) < expired_time - 200:
                    return token_str
                else:
                    with open(token_file,'w') as fw:
                        fw.write("\n")
                    continue
        except:
            refresh()

if __name__ == '__main__':
    print get()