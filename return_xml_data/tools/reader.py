import yaml


# yaml读取
def yaml_reader(file_path):
    try:
        with open(file=file_path, encoding='utf-8') as f:
            temp_data = yaml.safe_load(f)
            def inner(func):
                # 兼容不包含self函数的调用
                if func.__code__.co_varnames[:func.__code__.co_argcount][0] == 'self':
                    def outer_with_self(self, *args, **kwargs):
                        func(self, temp_data, *args, **kwargs)
                    return outer_with_self
                else:
                    def outer(*args, **kwargs):
                        func(temp_data, *args, **kwargs)
                    return outer
            return inner
    except IOError as e:
        print("文件读取出错{}".format(e))


# 数据写入yaml文件
def yaml_writer(file_path, data):
    try:
        with open(file=file_path, mode='a', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
    except IOError as e:
        print("数据写入出错{}".format(e))


def xml_reader():
    pass


def excel_reader():
    pass


if __name__ == '__main__':
    yaml_reader("../files/report_id.yaml")
    # yaml_writer("../files/test.yaml", [{"value":"江苏增值税一般纳税人申报表（新表）[江苏]","key":"3200010001"},{"value":"江苏单位社保费申报表[江苏]","key":"3200010021"},{"value":"江苏地方各项基金费申报表（工会经费）月报[江苏]","key":"3200010019"},{"value":"江苏印花税纳税申报表(选报)[江苏]","key":"3200050001"},{"value":"江苏企业所得税A类申报表2021[江苏]","key":"3200020003"},{"value":"江苏残疾人就业保障金年报[江苏]","key":"3200040011"},{"value":"江苏非税通用申报表——年报[江苏]","key":"3200040033"},{"value":"江苏增值税小规模纳税申报表[江苏]","key":"3200020014"},{"value":"江苏国税财务报表(小企业会计准则)[江苏]","key":"3200020007"},{"value":"江苏新国税消费税（月）[江苏]","key":"3200010022"},{"value":"江苏文化事业建设费[江苏]","key":"3200010018"},{"value":"江苏文化事业建设费[江苏]","key":"3200020018"},{"value":"江苏国税财务报表（企业会计制度）[江苏]","key":"3200020009"},{"value":"江苏印花税纳税申报表[江苏]","key":"3200020013"},{"value":"江苏地方各项基金费申报表（工会经费）季报[江苏]","key":"3200020019"},{"value":"江苏增值税小规模纳税申报表[江苏]","key":"3200010012"},{"value":"江苏国税财务报表(小企业会计准则)[江苏]","key":"3200010007"},{"value":"江苏非税收入通用申报表[江苏]","key":"3200010033"},{"value":"江苏已执行企业会计准则（一般企业）[江苏]","key":"3200020005"},{"value":"江苏地方各项基金费申报表（工会经费）次报[江苏]","key":"3200050030"}])