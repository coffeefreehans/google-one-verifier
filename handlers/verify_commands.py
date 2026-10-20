"""验证命令处理器 - 仅保留 Google One Pro (Gemini Advanced)"""
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message

try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(5)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify 与 /one 命令 - Google One Pro (Gemini Advanced) 学生认证"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("您已被拉黑，无法使用此功能。")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("请先使用 /start 注册。")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Google One Pro (Gemini Advanced)")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        # 支持直接输入 verificationId
        clean_url = url.strip().strip("'\"")
        if len(clean_url) in (24, 32) and all(c in "0123456789abcdefABCDEF" for c in clean_url):
            verification_id = clean_url
        else:
            await update.message.reply_text("❌ 无效的 SheerID 链接，请检查链接中是否包含 verificationId 参数。")
            return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("扣除积分失败，请稍后重试。")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 开始处理 Google One Pro (Gemini) 学生认证...\n"
        f"📋 验证ID: {verification_id}\n"
        f"💰 已扣除 {VERIFY_COST} 积分\n\n"
        "🎨 正在生成学生证并上传 SheerID，请稍候（约需 30-60 秒）..."
    )

    semaphore = get_verification_semaphore("gemini_one_pro")

    try:
        async with semaphore:
            verifier = OneVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
            verification_id,
        )

        if result["success"]:
            result_msg = "✅ Google One Pro 认证文档已成功提交！\n\n"
            if result.get("pending"):
                result_msg += "📌 文档已上传完毕，等待 SheerID 审核确认（通常几分钟内生效）。\n"
            if result.get("redirect_url"):
                result_msg += f"\n🔗 完成跳转链接：\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ 认证失败：{result.get('message', '未知错误')}\n\n"
                f"💰 已自动退回 {VERIFY_COST} 积分。"
            )
    except Exception as e:
        logger.error("验证过程出错: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ 处理过程中出现异常：{str(e)}\n\n"
            f"💰 已自动退回 {VERIFY_COST} 积分。"
        )
