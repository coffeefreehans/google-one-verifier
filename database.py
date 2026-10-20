"""数据库工厂入口

支持 MySQL 与 SQLite 自动切换
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def Database():
    """获取数据库实例（优先按配置，默认支持 MySQL 失败时自动回退 SQLite）"""
    db_type = os.getenv("DB_TYPE", "").lower()
    if db_type == "sqlite":
        from database_sqlite import SQLiteDatabase
        return SQLiteDatabase()

    try:
        from database_mysql import MySQLDatabase
        return MySQLDatabase()
    except Exception as e:
        logger.warning(
            f"⚠️ 无法连接到 MySQL 数据库 ({e})，已自动切换为本地 SQLite 数据库 (tgbot.db)。"
        )
        from database_sqlite import SQLiteDatabase
        return SQLiteDatabase()
