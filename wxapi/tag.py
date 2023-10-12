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

import token

ACCESS_TOKEN = token.get()

action_method_d = {
    "create": "POST",      #u"创建标签"
    "update": "POST",      #u"更新标签名"
    "delete": "GET",       #u"删除标签"
    "get": "GET",          #u"获取标签成员"
    "addtagusers": "POST", #u"增加标签成员"
    "deltagusers": "POST", #u"删除标签成员"
    "list": "GET"          #u"获取标签列表"
}

def tagurl(action):
    url = "https://qyapi.weixin.qq.com/cgi-bin/tag/{1}?access_token={0}".format(ACCESS_TOKEN, str(action))
    return url

def responsedict(url, method='GET', data=None):
    if str(method) == 'GET':
        if data and isinstance(data, dict):
            sub = ""
            for k in data:
                sub += "&{0}={1}".format(k,data[k])
            url += sub
        s = requests.get(url, verify=False)
        message = s.text
        response_r=json.loads(message)
        return response_r
    elif str(method) == 'POST':
        s = requests.post(url, data=json.dumps(data), verify=False)
        message = s.text
        response_r=json.loads(message)
        return response_r
    else:
        return {}

def result(action, data=None):
    if str(action) not in action_method_d:
        return {}
    url = tagurl(str(action))
    return responsedict(url, method=action_method_d[str(action)], data=data)


if __name__ == '__main__':
    #pass
    #data = {"tagname": "OPS"}
    #print result('create', data)
    data = {"tagid": 1}
    print result('get',data)
    #data = {"tagid": 1, 'userlist':[] }
    #user_l = user_str.strip().split('|')
    #data = {"tagid": 1, "userlist": user_l}
    #data = {"tagname": "OPS"}
    #data = {"tagid": 1}
    #print result('get',data=data)

