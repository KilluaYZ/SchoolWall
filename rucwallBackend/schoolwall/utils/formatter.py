from typing import List


def convert_to_str(data: dict, key: str) -> dict:
    """
    将字典中指定键对应的值转换为字符串格式。

    :param data: 包含数据信息的字典对象。
    :param key: 需要转换为字符串的键值名称。
    :return: 更新后的字典对象。
    """
    try:
        # 尝试将键值对应的值转换为字符串，并更新到字典中
        data.update({key: str(data[key])})
    except KeyError:
        # 如果指定的键不存在，则忽略异常
        pass
    finally:
        return data


def process_comment_time(comment_dict: dict) -> dict:
    """
    将评论字典中的 createTime 转换为字符串格式。

    :param comment_dict: 包含评论信息的字典对象。
    :return: 更新后的评论字典对象。
    """
    return convert_to_str(comment_dict, 'createTime')


def process_comment_list_time(comments: List[dict]) -> List[dict]:
    """
    将评论字典列表中的所有 createTime 键对应的值转换为字符串格式并更新到原始字典中。

    :param comments: 包含评论信息的字典列表。
    :return: 更新后的评论字典列表。
    """
    comments = [process_comment_time(comment) for comment in comments]
    # comments = [comment.update({'createTime': str(comment['createTime'])}) or comment for comment in comments]
    return comments
