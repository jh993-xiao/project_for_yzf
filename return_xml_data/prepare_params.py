from return_xml_data.tools.reader import yaml_writer, yaml_reader
from return_xml_data.get_cookie import cookie_helper
import requests


@yaml_reader('files/area_mapping.yaml')
def get_report_id(temp_data):
    keyswords = list(temp_data.keys())
    cookie = cookie_helper.composed_cookie('sjcx')
    headers = {
        'cookie': cookie
    }
    for index, keyword in enumerate(keyswords):
        print(index)
        try:
            resp = requests.get(url='https://taxsupport.yunzhangfang.com/tax/reportSearch', headers=headers, params={'keyword': keyword})
            yaml_writer(file_path='files/report_id.yaml', data=resp.json()['data'])
        except requests.exceptions.HTTPError as e:
            print("获取税表id失败" + str(e))


if __name__ == '__main__':
    get_report_id()
