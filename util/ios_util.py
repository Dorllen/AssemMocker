

class iOSUtil(object):

    ARM64_IDA_BASE_OFFSET_ADDRESS = 0x10000_0000

    @staticmethod
    def compute_real_address(adsl, *args, IDA_offset_address=None):
        result = []
        if IDA_offset_address is None:
            IDA_offset_address = iOSUtil.ARM64_IDA_BASE_OFFSET_ADDRESS
        for arg in args:
            result.append(hex(adsl + (arg - IDA_offset_address)))
        return result

    @staticmethod
    def reverse_real_address(adsl, *args, IDA_offset_address=None):
        result = []
        if IDA_offset_address is None:
            IDA_offset_address = iOSUtil.ARM64_IDA_BASE_OFFSET_ADDRESS
        for arg in args:
            result.append(hex(IDA_offset_address + arg - adsl))
        return result


def aweme_test():
    # image list Aweme
    # command script import /Users/admin/PycharmProjects/pythonProject/Nt_LLDB/dump_lldb.py
    adsl = 0x00000001020ec000
    print(iOSUtil.compute_real_address(adsl,
                                       0x100369284, # 函数进入
                                       0x10036964C, # 循环结束
                                       0x1003697D8
                                       ))
    print(iOSUtil.reverse_real_address(adsl, 0x102455c34))

def news_article_test():
    # image list News
    adsl = 0x0000000100e78000
    print(iOSUtil.compute_real_address(adsl,
                                       0x102778178, # location/locate/ dwinfo 发送时method
                                       0x102778394, # dwinfo 请求时
                                       0x102761084, # location/submit/ 提交坐标到服务器method
                                       0x102761138, #
                                       0x102765244, # location/geocode/
                                       0x10276533C,
                                       0x1027654B8, # location/geocode/ callback
                                       0x1027723E8, # 访问base64处理方法
                                       0x102772424,
                                       0x102772468,
                                       0x102772570, # b64 解密tojson
                                       ))
    print(iOSUtil.reverse_real_address(adsl, 0x1036153e0))

if __name__ == '__main__':
    # aweme_test()
    news_article_test()
    pass
