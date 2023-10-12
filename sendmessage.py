#!/usr/local/zabbix3.0.4/share/zabbix/alertscripts/zbx_env/bin/python
#encoding:utf-8
import requests
import json
import sys
import os
import time
import wxapi.token as wxtoken
from requests.packages.urllib3.exceptions import InsecureRequestWarning
reload(sys)
sys.setdefaultencoding('utf8')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#if len(sys.argv) < 3:
#    print u"参数不够"
#    sys.exit(1)

ACCESS_TOKEN = wxtoken.get()
url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(ACCESS_TOKEN)
dir='/usr/local/zabbix/share/zabbix/alertscripts'
logfile=os.path.join(dir, 'wxlog')

to_email = sys.argv[1]
subject = sys.argv[2]
message = sys.argv[3]

#content = "{1}\n{2}\n[ ZABBIX  {0} ]".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(subject), str(message))
content = "{0}\n{1}".format(str(subject), str(message))
with open(logfile, 'w') as fa:
    fa.write(content+"\n")

data = {
    #"totag" : "1",
    "touser": "qy018023bbe240f0009b2b09838e",
    "msgtype" : "text",
    "agentid" : 1000015,
    "text": {
        "content": content
    },
    "safe": 0
}

ac_data = {
    "chatid": "14224337948888052816",
    "msgtype": "text",
    "text": {
        "content": content
     },
     "safe": 0
}

count = 0
while count < 10:
    appchat_url = "https://qyapi.weixin.qq.com/cgi-bin/appchat/send?access_token={0}".format(ACCESS_TOKEN)
    ac_s = requests.post(appchat_url,data=json.dumps(ac_data), verify=False)
    response_dict = json.loads(ac_s.text)
    print response_dict
    count +=1
    if response_dict.get("errcode",629) != 0:
        wxtoken.refresh()
        ACCESS_TOKEN = wxtoken.get()
        print ACCESS_TOKEN
        continue
    else:
        try:
            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(ACCESS_TOKEN)
            #s = requests.post(url,data=json.dumps(data), verify=False)
        except:
            pass
        break
