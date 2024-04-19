# 计算爬取合格率
def content_count(content, count_list):
    count = 0
    for i in range(len(count_list)):
        if content.get(count_list[i]) is not None and content[count_list[i]] != '':
            count += 1
    return count/len(count_list)
