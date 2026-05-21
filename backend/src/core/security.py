"""
安全相关工具函数

提供密码哈希与验证功能（使用 bcrypt）。
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    使用 bcrypt 哈希密码

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码字符串
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        bool: 密码是否匹配
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
