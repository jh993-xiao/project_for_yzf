import requests
from return_xml_data.tools.reader import yaml_reader
from enum import Enum
from bs4 import BeautifulSoup


# 可获得cookie的枚举类cgl-->成功率，big_query-->大数据查询，sjcx-->数据查询
class PageCookieEnum(Enum):
    cgl = {'dingding_login_by_pwd': ['33ea3b9c8d374d20a81450c44a0c2f81', 'dd_access_token', 'dd_refresh_token', 'userInfo']}
    sjcx = {'dingding_login_by_pwd': ['dd_access_token', 'dd_refresh_token', 'userInfo', '33ea3b9c8d374d20a81450c44a0c2f81']}
    big_query = {'bigquery_login_by_pwd': ['csrftoken', 'sessionid']}


class GetCookie:

    @yaml_reader("files/login_message.yaml")
    def __init__(self, login_temp_data):
        self.login_temp_data = login_temp_data

    # 钉钉登录
    def dingding_login_by_pwd(self):
        resp = requests.post(url=self.login_temp_data['DingDing']['URL']['login_url'], data=self.login_temp_data['DingDing']['Message'])
        try:
            redirect_uri = resp.json()['data']
            if redirect_uri:
                resp1 = requests.get(url=redirect_uri, allow_redirects=True)
                result = [one_info.cookies for one_info in resp1.history]
                self.login_temp_data['Cookie']['dd_access_token'] = result[1]['dd_access_token']
                self.login_temp_data['Cookie']['dd_refresh_token'] = result[1]['dd_refresh_token']
        except Exception as e:
            print("cookie获取失败" + str(e))

    # 大数据登录Cookie获取
    def bigquery_login_by_pwd(self):
        try:
            resp = requests.get(url=self.login_temp_data['BigQuery']['URL'][0])

            # 获取登陆前临时csrftoken和sessionid
            temp_resp = resp.headers['Set-Cookie'].split(",")
            temp_csrftoken = temp_resp[0].split(";")[0]
            temp_sessionid = temp_resp[2].split(";")[0]

            # 获取csrfmiddlewaretoken
            bs = BeautifulSoup(resp.content, 'html.parser')  # html解析
            self.login_temp_data['BigQuery']['Message']['csrfmiddlewaretoken'] = bs.find(name="input").attrs['value']

            # 登录大数据页面，获取真实csrftoken和sessionid
            login_result = requests.post(url=self.login_temp_data['BigQuery']['URL'][1], headers={"Cookie": temp_csrftoken+";"+temp_sessionid}, allow_redirects=True, data=self.login_temp_data['BigQuery']['Message'])
            temp_login_result = login_result.headers['Set-Cookie'].split(",")
            csrftoken = temp_login_result[0].split(";")[0]
            sessionid = temp_login_result[2].split(";")[0]
            self.login_temp_data['Cookie']['csrftoken'] = csrftoken.split("=")[1]
            self.login_temp_data['Cookie']['sessionid'] = sessionid.split("=")[1]
        except Exception as e:
            print("大数据登录失败" + str(e))

    # cookie组装
    def composed_cookie(self, page):
        cookie = ""
        # 调用对应的函数
        func_name = getattr(self, list(PageCookieEnum[page].value.keys())[0])
        func_name()
        try:
            for index, item in enumerate(list(PageCookieEnum[page].value.values())[0]):
                cookie += item + "=" + str(self.login_temp_data['Cookie'][item]) + ";"
            print(cookie)
        except Exception as e:
            print("cookie组装失败" + str(e))
        return cookie[:-1]


cookie_helper = GetCookie()


if __name__ == '__main__':
    cookie_helper.composed_cookie('sjcx')
    # print(get_cookie.__dir__())
