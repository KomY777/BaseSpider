import re
import time


def is_right_time_str(dateStr):
    """
    判断时间字符串是否有效
    :param dateStr: 时间字符串
    :return:
    """
    dateStr = changeAllConn(dateStr)
    try:
        if ":" in dateStr:
            if dateStr.count(":") == 2:
                time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
            else:
                time.strptime(dateStr, "%Y-%m-%d %H:%M")
        else:
            if dateStr.count("-") == 2:
                time.strptime(dateStr, "%Y-%m-%d")
            else:
                time.strptime(dateStr, "%Y-%m")
        return True
    except:
        return False


def changeAllConn(string: str):
    """
    修改时间字符串的连接符 %Y-%m-%d %H:%M:%S
    :param string:
    :return:
    """
    number_list = re.findall(r'\d+', string)
    for i in range(len(number_list), 6):
        number_list.append('00')
    return number_list[0] + '-' + number_list[1] + '-' + number_list[2] + ' ' + number_list[3] + ':' + number_list[
        4] + ':' + number_list[5]


def get_re_time():
    """
    获得时间的正则表达式
    :return:
    """
    return r'(((((\d{4}[-/年.]\d{1,2})([-/月.]\d{1,2})?)([ 日T.]+\d{1,2})?)([:：时.]\d{1,2})?)([:：分.]\d{1,2})?)'


def get_time_from_str(string: str):
    """
    获得有效时间字符串
    :param string:
    :return:
    """
    if not string:
        return []
    time_list = []
    try:
        time_sor_list = re.findall(get_re_time(), string.strip())
        for time in time_sor_list:
            for timeStr in time:
                if len(re.findall(r'\d+', timeStr)) >= 2:
                    times = changeAllConn(timeStr)
                    if is_right_time_str(times):
                        time_list.append(times)
                        break
    except:
        pass
    finally:
        return time_list


def get_one_time_from_str(string) -> str:
    """
     从字符串中获得一个有效时间字符串
    :param string:
    :return:
    """
    time_list = get_time_from_str(string)
    return time_list[0] if time_list else ''

def stamp2time(time_stamp) -> str:
    if isinstance(time_stamp,  str):
        time_stamp = int(time_stamp)

    if len(str(time_stamp)) == 13:
        time_stamp = time_stamp // 1000

    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_stamp))
