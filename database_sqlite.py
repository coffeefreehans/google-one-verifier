"""SQLite 数据库实现

支持无 MySQL 环境下的本地开箱即用运行
"""
import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tgbot.db")


class SQLiteDatabase:
    """SQLite 数据库管理类"""

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        logger.info(f"SQLite 数据库初始化: {self.db_path}")
        self.init_database()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance INTEGER DEFAULT 1,
                    is_blocked INTEGER DEFAULT 0,
                    invited_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checkin TIMESTAMP NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inviter_id INTEGER NOT NULL,
                    invitee_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    verification_type TEXT NOT NULL,
                    verification_url TEXT,
                    verification_id TEXT,
                    status TEXT NOT NULL,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS card_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_code TEXT UNIQUE NOT NULL,
                    balance INTEGER NOT NULL,
                    max_uses INTEGER DEFAULT 1,
                    current_uses INTEGER DEFAULT 0,
                    expire_at TIMESTAMP NULL,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS card_key_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_code TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            logger.info("SQLite 数据库表初始化完成")
        except Exception as e:
            logger.error(f"初始化 SQLite 数据库失败: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def create_user(
        self, user_id: int, username: str, full_name: str, invited_by: Optional[int] = None
    ) -> bool:
        """创建新用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (user_id, username, full_name, invited_by, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, username, full_name, invited_by),
            )
            if invited_by:
                cursor.execute(
                    "UPDATE users SET balance = balance + 2 WHERE user_id = ?",
                    (invited_by,),
                )
                cursor.execute(
                    """
                    INSERT INTO invitations (inviter_id, invitee_id, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (invited_by, user_id),
                )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            conn.rollback()
            return False
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def user_exists(self, user_id: int) -> bool:
        """检查用户是否存在"""
        return self.get_user(user_id) is not None

    def is_user_blocked(self, user_id: int) -> bool:
        """检查用户是否被拉黑"""
        user = self.get_user(user_id)
        return bool(user and user.get("is_blocked") == 1)

    def block_user(self, user_id: int) -> bool:
        """拉黑用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"拉黑用户失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def unblock_user(self, user_id: int) -> bool:
        """取消拉黑用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"取消拉黑失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_blacklist(self) -> List[Dict]:
        """获取黑名单列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE is_blocked = 1")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def add_balance(self, user_id: int, amount: int) -> bool:
        """增加用户积分"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"增加积分失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def deduct_balance(self, user_id: int, amount: int) -> bool:
        """扣除用户积分"""
        user = self.get_user(user_id)
        if not user or user["balance"] < amount:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (amount, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"扣除积分失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def can_checkin(self, user_id: int) -> bool:
        """检查用户今天是否可以签到"""
        user = self.get_user(user_id)
        if not user:
            return False

        last_checkin = user.get("last_checkin")
        if not last_checkin:
            return True

        try:
            if isinstance(last_checkin, str):
                last_date = datetime.fromisoformat(last_checkin.replace("Z", "")).date()
            else:
                last_date = last_checkin.date()
            today = datetime.now().date()
            return last_date < today
        except Exception:
            return True

    def checkin(self, user_id: int) -> bool:
        """用户签到"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE users
                SET balance = balance + 1, last_checkin = CURRENT_TIMESTAMP
                WHERE user_id = ? 
                AND (
                    last_checkin IS NULL 
                    OR DATE(last_checkin) < DATE('now')
                )
                """,
                (user_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"签到失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def add_verification(
        self, user_id: int, verification_type: str, verification_url: str,
        status: str, result: str = "", verification_id: str = ""
    ) -> bool:
        """添加验证记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO verifications
                (user_id, verification_type, verification_url, verification_id, status, result, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, verification_type, verification_url, verification_id, status, result),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"添加验证记录失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_verifications(self, user_id: int) -> List[Dict]:
        """获取用户的验证记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM verifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def create_card_key(
        self, key_code: str, balance: int, created_by: int,
        max_uses: int = 1, expire_days: Optional[int] = None
    ) -> bool:
        """创建卡密"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            expire_at = None
            if expire_days:
                expire_at = (datetime.now() + timedelta(days=expire_days)).isoformat()

            cursor.execute(
                """
                INSERT INTO card_keys (key_code, balance, max_uses, created_by, created_at, expire_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """,
                (key_code, balance, max_uses, created_by, expire_at),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.error(f"卡密已存在: {key_code}")
            conn.rollback()
            return False
        except Exception as e:
            logger.error(f"创建卡密失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def use_card_key(self, key_code: str, user_id: int) -> Optional[int]:
        """使用卡密，返回获得的积分数量"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM card_keys WHERE key_code = ?",
                (key_code,),
            )
            card = cursor.fetchone()
            if not card:
                return None

            card = dict(card)
            if card.get("expire_at"):
                expire_dt = datetime.fromisoformat(card["expire_at"])
                if datetime.now() > expire_dt:
                    return -2

            if card["current_uses"] >= card["max_uses"]:
                return -1

            cursor.execute(
                "SELECT COUNT(*) as count FROM card_key_usage WHERE key_code = ? AND user_id = ?",
                (key_code, user_id),
            )
            count = cursor.fetchone()["count"]
            if count > 0:
                return -3

            cursor.execute(
                "UPDATE card_keys SET current_uses = current_uses + 1 WHERE key_code = ?",
                (key_code,),
            )
            cursor.execute(
                "INSERT INTO card_key_usage (key_code, user_id, used_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key_code, user_id),
            )
            cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (card["balance"], user_id),
            )
            conn.commit()
            return card["balance"]
        except Exception as e:
            logger.error(f"使用卡密失败: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def get_card_key_info(self, key_code: str) -> Optional[Dict]:
        """获取卡密信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM card_keys WHERE key_code = ?", (key_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def get_all_card_keys(self, created_by: Optional[int] = None) -> List[Dict]:
        """获取所有卡密（可按创建者筛选）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if created_by:
                cursor.execute(
                    "SELECT * FROM card_keys WHERE created_by = ? ORDER BY created_at DESC",
                    (created_by,),
                )
            else:
                cursor.execute("SELECT * FROM card_keys ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def get_all_user_ids(self) -> List[int]:
        """获取所有用户ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM users")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            cursor.close()
            conn.close()
