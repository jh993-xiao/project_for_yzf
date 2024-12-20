from cookie_tools.get_cookie import cookie_helper


if __name__ == '__main__':
    # 导入后测试按这种选择要拿的cookie
    big_query = cookie_helper.composed_cookie('big_query')
    sjcx = cookie_helper.composed_cookie('sjcx')
    cgl = cookie_helper.composed_cookie('cgl')
    print(big_query, sjcx, cgl)