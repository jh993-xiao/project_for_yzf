import yaml
import os


# yaml读取
def yaml_reader(file_path):

    try:
        with open(file=file_path, encoding='utf-8') as f:
            temp_data = yaml.safe_load(f)
            def inner(func):
                def outer(self, *args, **kwargs):
                    func(self, temp_data, *args, **kwargs)
                return outer
            return inner
    except IOError as e:
        print("文件读取出错{}".format(e))


def xml_reader():
    pass


def excel_reader():
    pass


if __name__ == '__main__':
    yaml_reader("../files/login_message.yaml")