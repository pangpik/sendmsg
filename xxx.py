# 受理人
handlers = ["huangzhen", "liweidong", "zhangziting"]

# dxl header
dxl_headers = {
    "Content-Type": "application/json; charset=utf-8",
    'x-token': "c2FreWFfZGI6OTJkYWQyOTFjMWVmNGVmZWI0YTFjNzhkZmY5ZGU0ZTE=",
}

# query header
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Token": "c2FreWFfZGI6OTJkYWQyOTFjMWVmNGVmZWI0YTFjNzhkZmY5ZGU0ZTE="
}


def dxl_authorization(data):
    for c in range(0, 3):
        try:
            res = requests.post("http://sakya.lzffffkk.com/db/openapi/grant-dxl-auth/",
                                data=json.dumps(data),
                                headers=dxl_headers)
        except:
            # send_app_msg(users=handlers, content=f"{res.status_code}, {res.text}")
            time.sleep(1)
        else:
            return res.status_code, res.text
    else:
        return 600, "【DDL/DML数据源权限】自动开通接口异常"


def query_authorization(data):
    for c in range(0, 3):
        try:
            res = requests.post("http://sakya.lzffffkk.com/db/openapi/auto-setup/dql-auth/",
                                data=json.dumps(data),
                                headers=headers)
        except:
            # send_app_msg(users=handlers, content=f"{res.status_code}, {res.text}")
            time.sleep(1)
        else:
            return res.status_code, res.text
    else:
        return 600, "【数据查询】自动开通接口异常"
      
def check_domain_db_port(domain, dbname, port):
    for c in range(0, 3):
        try:
            res = requests.get(f"http://sakya.lzffffkk.com/db/mysql/domains/?f_domain={domain}",
                                headers=headers)
            if res.status_code == 200:
                result = res.json()
                if result["data"]["count"] == 0:
                    return False, "数据库不存在"
                else:
                    data = result["data"]["data"][0]
                    cluster = data["cluster"]
                    if cluster["hidden"]:
                        return False, "请切换区域申请"
                    else:
                        if cluster["port"] != int(port):
                            return False, "端口错误"
                        if data["database"]["name"] != dbname:
                            return False, "数据库名错误"
                return True, ""
        except:
            time.sleep(1)
    else:
        return False, "查询异常"


class Sakya:
    def __init__(self):
        self.base_url = "http://sakya.lllll.ffffkk"
        self.headers = {
            "accept": "application/json",
            "X-Token": "5p2D6ZmQ5bmz5Y+wOmZjMzIxOWY4MTJmYmFkMWYzZGJkNmM2ZjAzMzM5MjI4"
        }

    def get_user_info(self, name):
        url = "%s/uc/org/user/?name=%s" % (self.base_url, name)
        r = requests.get(url, headers=self.headers)
        response = json.loads(r.content)
        return response


def split_db_info(database_info):
    ret = []
    database_info = str(database_info).strip()
    for di in database_info.replace(';', ' ').replace(',', ' ').split():
        di = di.strip()
        if (":" not in di) or ("/" not in di) or (" " in di):
            raise Exception(f"数据库信息异常: {di}，需要 域名:端口/库名 格式(不能带空格)")
        domain = di.split(":")[0]
        temp = di.split(":")[1]
        port = temp.split("/")[0]
        db = temp.split("/")[1]
        ret.append((domain, port, db))
    return ret


def trigger_start(ticket, params, **kw):
    """ 新建工单申请时触发 """
    order = params["ticket_custom_attributes"]
    database_info = order["database_info"].strip()
    db_infos = split_db_info(database_info)
    for db_info in db_infos:
        domain = db_info[0]
        port = db_info[1]
        db = db_info[2]

        if domain.startswith('r_') or domain.startswith("br"):
            raise Exception(f"域名: {domain} 为从库域名，请提交主库域名")
        if not domain.endswith(".com"):
            raise Exception(f"域名: {domain} 不符合规范")
        rst = check_domain_db_port(domain, db, port)
        if not rst[0]:
            raise Exception(f"域名: {domain} 校验失败，{rst[1]}")
    user = params['user']
    sakya = Sakya()
    user_info = sakya.get_user_info(user)
    if user['leader_name'] == 'luozhixin':
        approval_user("submit_direct_leader", "fengteng")


def trigger_approval_complete(ticket, params, **kw):
    """点击受理触发"""
    order = params["ticket_custom_attributes"]
    read_name = params['user']['readname']
    email = params['user']['email']
    user_id = int(params['user']['id'])
    username = email.split('@')[0]
    apply_id = ticket.model.id

    expire_days = 7
    export_limit = 10000
    comment = order["comment"].strip()
    database_info = order["database_info"].strip()
    ticket_msg = f"""工单类型: {ticket.model.ticket_tmpl.name}
工单号: {ticket.model.id}
提单人: {read_name}"""

    db_infos = split_db_info(database_info)
    for db_info in db_infos:
        domain = db_info[0]
        port = db_info[1]
        db_name = db_info[2]

        domain_port = ':'.join([domain, port])

        # 自动查询开通
        data = {
            "apply_id": apply_id,
            "domain_port": domain_port,
            "db_name": db_name,
            "expire_time": expire_days,
            "down_limit": export_limit
        }
        res = query_authorization(data)
        status_code = res[0]
        resp_msg = res[1]
        if status_code == 200:
            proposer_msg = f"""{ticket_msg}
    内  容: 查询申请自动授权
    信  息: {domain_port}/{db_name} 授权成功。
    链  接: https://atpplus.lllll.ffffkk/#/db/mysql/user/dml"""
            # 发送给提单人
            send_app_msg(users=[username], content=proposer_msg)
            data = json.loads(resp_msg)
            handler_msg = f"""{ticket_msg}
    内  容: 查询申请自动授权
    申请信息: 
         {domain_port}/{db_name}
    授权信息:
         Domain  : {data["real_domain"]}
         IPPort  : {data["ip_port"]}
         NodeAttr: {data["node_attr"]}
    链  接: https://atpplus.lllll.ffffkk/#/db/mysql/user/dml"""

            # 发送给受理人
            send_app_msg(users=handlers, content=handler_msg)
        elif status_code == 600:
            error_msg = f"""{ticket_msg}
    异  常: {resp_msg}
    """
            send_app_msg(users=handlers, content=error_msg)
        else:
            resp_msg = json.loads(resp_msg)
            error_msg = f"""{ticket_msg}
    内  容: 查询申请自动授权
    信  息: 库地址:端口 {domain_port} | 库名称 {db_name} ｜ 过期时间 {expire_days} ｜ 导出条数限制 {export_limit}
    异  常: {resp_msg}
    信息校验不通过，请重新提交申请。
    """
            send_app_msg(users=[username] + handlers, content=error_msg)

        # dxl权限开通
        dxl_data = {
            "username": username,
            "user_id": user_id,
            "read_name": read_name,
            "domain": domain,
            "database": db_name,
            "port": port,
            "expire_days": expire_days,
            "comment": comment
        }
        res = dxl_authorization(dxl_data)
        status_code = res[0]
        resp_msg = res[1]
        if status_code == 200:
            if domain.startswith('r_') or domain.startswith("br"):
                resp_msg = json.loads(resp_msg)
                error_msg = f"""{ticket_msg}
            内  容: DDL/DML数据源权限自动开通
            信  息: 库地址:端口 {domain_port} | 库名称 {db_name} ｜ 过期时间 {expire_days} ｜ 备注 {comment}
            异  常: 只读域名: {domain} 无法执行DDL/DML，请填写主实例域名地址并重新申请
            信息校验不通过，请重新提交申请。
            """
                send_app_msg(users=[username] + handlers, content=error_msg)
            else:
                proposer_msg = f"""{ticket_msg}
        内  容: DDL/DML数据源权限自动开通
        信  息: {domain_port}/{db_name} 授权成功。
        链  接: http://atpplus.lllll.ffffkk/#/db/mysql/dxl/ddl/order-push"""
            # 发送给提单人
                send_app_msg(users=[username], content=proposer_msg)

                handler_msg = f"""{ticket_msg}
        内  容: DDL/DML数据源权限自动开通
        申请信息: 
             {domain_port}/{db_name}
        授权信息:
             数据源信息 : {domain_port}/{db_name}
             授权结果: {json.loads(resp_msg)["code"]}
        链  接: http://atpplus.lllll.ffffkk/#/db/mysql/dxl/ddl/order-push """
            # 发送给受理人
                send_app_msg(users=handlers, content=handler_msg)


        elif status_code == 600:
            error_msg = f"""{ticket_msg}
    异  常: {json.loads(resp_msg)["message"]}
    """
            send_app_msg(users=handlers, content=error_msg)
        else:
            resp_msg = json.loads(resp_msg)
            error_msg = f"""{ticket_msg}
    内  容: DDL/DML数据源权限自动开通
    信  息: 库地址:端口 {domain_port} | 库名称 {db_name} ｜ 过期时间 {expire_days} ｜ 备注 {comment}
    异  常: {resp_msg["message"]}
    信息校验不通过，请重新提交申请。
    """
            send_app_msg(users=[username] + handlers, content=error_msg)