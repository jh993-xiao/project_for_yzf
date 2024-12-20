import requests
import json
from return_xml_data.tools.reader import yaml_reader
from return_xml_data.enums import AreaEnum, TaskResultEnum
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from return_xml_data.get_cookie import cookie_helper
import itertools


class Main:
    def __init__(self, begin_date, end_date, page_size, carrier):
        self.beginDate = begin_date
        self.endDate = end_date
        self.pageSize = page_size
        self.carrier = carrier
        cookie = cookie_helper.composed_cookie('sjcx')  # sjcx--->数据查询
        self.headers = {
            "Cookie": cookie,
            "Content-type": "application/json"
        }

        self.param_list = []  # 参数列表
        self.success_search = []  # 成功查询的列表，列表中拼接数据存往数舟
        self.error_search = []  # 失败查询的列表
        self.report_id_list = []  # 地区税表id
        self.need_nsrzgdm = [(1, 1), (1, 2), (1, 3)]  # 特殊要求，需要查询纳税人资格代码的任务（task_type, son_type）

    # @yaml_reader('files/task_dict.yaml')
    # def fixed_lost_data(self, task_types):
    #     area_list = [item.value for item in AreaEnum]
    #     type_list = [item for item in task_types]
    #     result_list = [item.value for item in TaskResultEnum]
    #     for area_index, area in enumerate(area_list):
    #         for result_index, result in enumerate(result_list):
    #             self.param_list.append({
    #                 "areas": [area],
    #                 "taskTypes": ["20"],
    #                 "subType": "2",
    #                 "codeCategory": [str(result)],
    #                 "carrier": self.carrier,
    #                 "beginDate": self.beginDate,
    #                 "endDate": self.endDate,
    #                 "pageIndex": 1,
    #                 "pageSize": self.pageSize
    #             })
    # 补缺少的数据

    # 请求体body拼接
    @yaml_reader('files/task_dict.yaml')
    def data_joint(self, task_types):
        area_list = [item.value for item in AreaEnum]
        type_list = [item for item in task_types]
        result_list = [item.value for item in TaskResultEnum]
        for area_index, area in enumerate(area_list):
            self.report_id_list = []  # 清除上一个地区report_id
            self.processing_report_id(area)
            for type_index, types in enumerate(type_list):
                for son_index, son in enumerate(task_types[types]):
                    for combination in itertools.product(self.report_id_list, result_list):  # 无特殊要求的参数，用生成器降低复杂度
                        self.param_list.append({
                            "areas": [area],
                            "taskTypes": [str(types)],
                            "subType": str(son),
                            "codeCategory": [str(combination[1])],
                            "carrier": self.carrier,
                            "beginDate": self.beginDate,
                            "endDate": self.endDate,
                            "pageIndex": 1,
                            "pageSize": self.pageSize,
                            "qiYongId": combination[0]
                        })
                        # break
                    # break
                # break
            # break
            # 通过break控制生成的数据种类和数据量

    # 读取report_id.yaml文件,处理report_id列表
    @yaml_reader('files/report_id.yaml')
    def processing_report_id(self, report_name_id, area_code):
        self.report_id_list.append("-1")  # 防止有的任务没有report_id而捞不到，例如采集
        for item in report_name_id:
            if area_code in item['key']:
                self.report_id_list.append(item['key'])

    # 主流程函数
    def main_work(self):
        for index, data in enumerate(self.param_list):
            resp = self.data_search(data=data)
            if resp['totalElements'] == 0:
                self.error_search.append((data['areas'], data['taskTypes'], data['subType'], data['qiYongId'], data['codeCategory']))
            else:
                if resp['content'] == []:
                    print("{}地区，{}任务类型，{}子任务类型，{}税表id，{}任务结果执行完成,未查询到数据".format(data['areas'], data['taskTypes'], data['subType'], data['qiYongId'], data['codeCategory']))
                for _, temp in enumerate(resp['content']):
                    status, nsrzgdm, file_url, result_code, result_desc, task_group_id, report_name, report_id = self.xml_search(xzqhid=temp['xzqhid'], taskId=temp['taskId'], qymc=temp['qyName'], task_type=temp['rwlx'], son_type=temp['subType'])
                    if status:
                        is_default = 1 if data['codeCategory'] == ['0'] else 0
                        self.data_update_table((data['areas'], data['taskTypes'], data['subType'], file_url, result_code, result_desc, is_default, nsrzgdm, task_group_id, report_name, report_id))
                        print("{}地区，{}任务类型，{}子任务类型，{}税表id，{}任务结果执行完成".format(data['areas'], data['taskTypes'], data['subType'], data['qiYongId'], data['codeCategory']))
                        print(file_url)
                        # print(report_name, report_id)
                        break  # break控制获取url的数量

    # 报税支撑数据查询
    def data_search(self, data):
        resp = requests.post(url="https://taxsupport.yunzhangfang.com/tax/esTaskLog", data=json.dumps(data),
                             headers=self.headers)
        return resp.json()['data']['pageResult']

    # xml获取函数
    def xml_search(self, xzqhid, taskId, qymc, task_type, son_type):
        data = {
            "xzqhid": xzqhid,
            "taskId": taskId,
            "qymc": qymc
        }
        resp = requests.get(url="https://taxsupport.yunzhangfang.com/tax/remoteTaskMessageList", params=data, headers=self.headers)
        for index, item in enumerate(resp.json()['data']):
            if item['interfaceName'] == "tasksReturn" and item['inFilePath'] is not None:
                status, nsrzgdm, result_code, result_desc, task_group_id, report_name, report_id = self.xml_filtation(url=item['inFilePath'], task_type=task_type, son_type=son_type)
                if status:
                    return status, nsrzgdm, item['inFilePath'], result_code, result_desc, task_group_id, report_name, report_id
        return False, "-1", "", "", "", "", "", ""

    # xml内容分析，过滤符合条件的xml，True和False表示符不符合预期xml
    def xml_filtation(self, url, task_type, son_type):
        res = urlopen(url)
        et = ET.fromstring(res.read())
        for index, item in enumerate(et.findall('.//TaskGroup')):
            try:
                if item.attrib['taskType'] == str(task_type) and item.attrib['sonType'] == str(son_type):
                    if (task_type, son_type) in self.need_nsrzgdm:
                        temp_et = et.find('.//nsrzgdm') if et.find('.//nsrzgdm') is not None else et.find('.//nsrzg')
                        return True, temp_et.text, item.find('GroupResult').find('ResultCode').text, item.find('GroupResult').find('ResultDesc').text, item.attrib['id'], item.attrib.get('name', ''), item.attrib['taskReportId']
                    else:
                        return True, "-1", item.find('GroupResult').find('ResultCode').text, item.find('GroupResult').find('ResultDesc').text, item.attrib['id'], item.attrib.get('name', ''), item.attrib['taskReportId']
            except KeyError as e:
                print("未找到关键字" + str(e))
            else:
                return False, "-1", -1, -1, "", "", ""

    # 往数舟中插入数据
    def data_update_table(self, data):
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "baggage": "sentry-environment=production,sentry-public_key=9ab9c91f11b920c441a27b97b6f1c187,sentry-trace_id=f6bafe30b98e420bad13f48fe78443d9,sentry-sample_rate=0.15,sentry-sampled=false",
            "content-type": "application/json",
            "cookie": "sourceType=host; sourceType=host; tenant_id=master; tenant_code=master; dd_access_token=eyJhbGciOiJIUzI1NiJ9.eyJwaG9uZSI6IiIsImdzSWQiOiIwSFRSNkcxQUJLRFdHIiwiaXNzIjoiYXV0aDAiLCJ1c2VyTmFtZSI6Iue6quixqiIsImV4cCI6MTczNDUyMDMyMiwidXNlcklkIjoiMEhUUjZHMUFCS0RXRyJ9.8m81Mdb1-issDhbIisQDfW5OU8DsrtNFIhladzzaQb0; dd_refresh_token=3d3479f4221340fcaddd44c654d4a8d3; _pk_id.2.63a8=a2f1fdb1b6f354ab.1734518523.; _pk_ses.2.63a8=1",
            "origin": "https://fastapp-beta.yunzhangfang.com",
            "priority": "u=1, i",
            "referer": "https://fastapp-beta.yunzhangfang.com/jh_app/blank/jh_app_return_config_list",
            "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sentry-trace": "f6bafe30b98e420bad13f48fe78443d9-a419c098062366fb-0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        }
        data = {
            "values": {
                "name": None,
                "area_code": int(data[0][0]),
                "task_type": data[1][0],
                "son_type": data[2],
                "execute_time": "30",
                "return_file": data[3],
                "result_code": data[4],
                "result_desc": data[5],
                "is_default": data[6],
                "is_general": 1,
                "nsrzg": data[7],
                "id": None,
                "create_time": None,
                "update_time": None,
                "task_group_id": data[8],
                "report_name": data[9],
                "report_id": data[10]
            }
        }
        try:
            result = requests.post(url='https://fastapp-beta.yunzhangfang.com/fast_app/fa/api/v1/livelydata/auto_test_tools/0HWNZYPS9Q7YE/create', headers=headers, data=json.dumps(data))
            print(result.text)
        except Exception as e:
            print(e)


if __name__ == '__main__':

    data = Main("2024-01-01 00:00:00", "2024-11-14 11:13:26", page_size=10, carrier=3)
    data.data_joint()
    # data.fixed_lost_data()   #  补充遗失的数据
    data.main_work()