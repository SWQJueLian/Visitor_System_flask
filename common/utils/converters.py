# 自定义转换器
# 1、继承werkzeug.routing的BaseConverter，并编写regex
# 2、注册自定义转换器
#   app.url_map.converters["mobile"] = MobileConverter

from werkzeug.routing import BaseConverter


class MobileConverter(BaseConverter):
    # 编写正则表达式
    # 注意：不能写^来匹配开头，但是可以用$匹配结尾。这点和django的转换器也是一样的
    regex = r"1[3-9]\d{9}$"

    def __init__(self, map, *args, **kwargs):
        # 重写init方法可以做一些更多的功能，比如int转化器，可以这样用<int(max=199):age>
        # 这种方式就是再init中初始化的，具体直接看NumberConverter
        super().__init__(map, *args, **kwargs)

    # 这里可以根据需要决定是否重写to_python方法
    # 然后可以实现更多的功能，具体也可以参考NumberConverter
    #         if self.fixed_digits and len(value) != self.fixed_digits:
    #             raise ValidationError()
    #         value = self.num_convert(value)
    #         if (self.min is not None and value < self.min) or (
    #             self.max is not None and value > self.max
    #         ):
    #             raise ValidationError()
    #         return value
    def to_python(self, value: str):
        return super().to_python(value)


def register_converters(app):
    # 注册自定义转换器
    app.url_map.converters["MOBILE"] = MobileConverter
