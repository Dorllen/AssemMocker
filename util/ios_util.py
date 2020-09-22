

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


if __name__ == '__main__':
    # image list Aweme
    # command script import /Users/admin/PycharmProjects/pythonProject/Nt_LLDB/dump_lldb.py
    adsl = 0x0000000100a6c000
    print(iOSUtil.compute_real_address(adsl,
                                       0x100369284,
                                       0x10036964C,
                                       0x1003697D8
                                       ))
    pass