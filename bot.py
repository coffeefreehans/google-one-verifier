"""Telegram 机器人主程序 - Google One Pro 专属版"""
import sys
import logging
from functools import partial

# 解决 Windows 控制台编码问题 (GBK 下打印 Emoji 报错)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from database import Database
from handlers.user_commands import (
    start_command,
    about_command,
    help_command,
    balance_command,
    checkin_command,
    invite_command,
    use_command,
)
from handlers.verify_commands import verify_command
from handlers.admin_commands import (
    addbalance_command,
    block_command,
    white_command,
    blacklist_command,
    genkey_command,
    listkeys_command,
    broadcast_command,
)

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """全局错误处理"""
    logger.exception("处理更新时发生异常: %s", context.error, exc_info=context.error)


def main():
    """主函数"""
    # 初始化数据库（支持 MySQL 或 SQLite）
    db = Database()

    # 创建应用 - 启用并发处理
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # 注册用户基础命令
    application.add_handler(CommandHandler("start", partial(start_command, db=db)))
    application.add_handler(CommandHandler("about", partial(about_command, db=db)))
    application.add_handler(CommandHandler("help", partial(help_command, db=db)))
    application.add_handler(CommandHandler("balance", partial(balance_command, db=db)))
    application.add_handler(CommandHandler("qd", partial(checkin_command, db=db)))
    application.add_handler(CommandHandler("invite", partial(invite_command, db=db)))
    application.add_handler(CommandHandler("use", partial(use_command, db=db)))

    # 注册 Google One Pro 认证命令（支持 /verify 与 /one）
    application.add_handler(CommandHandler("verify", partial(verify_command, db=db)))
    application.add_handler(CommandHandler("one", partial(verify_command, db=db)))

    # 注册管理员命令
    application.add_handler(CommandHandler("addbalance", partial(addbalance_command, db=db)))
    application.add_handler(CommandHandler("block", partial(block_command, db=db)))
    application.add_handler(CommandHandler("white", partial(white_command, db=db)))
    application.add_handler(CommandHandler("blacklist", partial(blacklist_command, db=db)))
    application.add_handler(CommandHandler("genkey", partial(genkey_command, db=db)))
    application.add_handler(CommandHandler("listkeys", partial(listkeys_command, db=db)))
    application.add_handler(CommandHandler("broadcast", partial(broadcast_command, db=db)))

    # 注册错误处理器
    application.add_error_handler(error_handler)

    logger.info("Google One Pro 认证机器人启动中...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
