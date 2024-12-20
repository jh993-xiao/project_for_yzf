from enum import Enum


# 地区枚举类
class AreaEnum(Enum):

    # code_beijing = '11'
    # code_tianjin = '12'
    # code_hebei = '13'
    #
    # code_shanxi = '14'
    # code_neimenggu = '15'
    # code_liaoning = '21'
    #
    # code_dalian = '2102'
    # code_jilin = '22'
    # code_heilongjiang = '23'
    #
    # code_shanghai = '31'
    # code_jiangsu = '32'
    # code_zhejiang = '33'
    #
    # code_ningbo = '3302'
    # code_anhui = '34'
    # code_fujian = '35'
    #
    # code_xiamen = '3502'
    # code_jiangxi = '36'
    # code_shandong = '37'
    #
    # code_qindao = '3702'
    # code_henan = '41'
    # code_hubei = '42'
    #
    # code_hunan = '43'
    # code_guangdong = '44'
    # code_shenzhen = '4403'
    #
    # code_guangxi = '45'
    # code_hainan = '46'
    # code_chongqing = '50'

    code_sichuan = '51'
    # code_guizhou = '52'
    # code_yunnan = '53'
    #
    # code_xizang = '54'
    # code_shaanxi = '61'
    # code_gansu = '62'
    #
    # code_qinghai = '63'
    # code_ningxia = '64'
    # code_xinjiang = '65'


# 任务结果枚举类
class TaskResultEnum(Enum):
    code_success = 0
    code_system_error = 1