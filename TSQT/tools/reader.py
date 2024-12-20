import yaml
import os


def yaml_reader(file_path):
    try:
        with open(file=file_path, encoding='utf-8') as f:
            temp_data = yaml.safe_load(f)

            def inner(func):
                def outer(self, *args, **kwargs):
                    func(self, temp_data, *args, **kwargs)

                return outer
            return inner
    except Exception as e:
        # error("文件读取出错{}".format(e))
        print("文件读取出错{}".format(e))


def xml_reader():
    pass


def excel_reader():
    pass


if __name__ == '__main__':
    if not os.path.exists("../files/login_message.yaml"):
        raise FileNotFoundError("文件不存在")
    if not os.path.exists("../files/login_message.yaml"):
        print("文件存在")