"""消息模板"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """获取欢迎消息"""
    msg = (
        f"🎉 欢迎，{full_name}！\n"
        "您已成功注册，获得 1 积分。\n"
    )
    if invited_by:
        msg += "感谢通过邀请链接加入，邀请人已获得 2 积分。\n"

    msg += (
        "\n本机器人专用于 Google One Pro (Gemini Advanced) 自动学生认证。\n"
        "快速开始：\n"
        "/verify <SheerID链接> - 提交 Google One Pro 认证\n"
        "/about - 了解机器人功能\n"
        "/balance - 查看积分余额\n"
        "/help - 查看完整命令列表\n\n"
        "获取更多积分：\n"
        "/qd - 每日签到\n"
        "/invite - 邀请好友\n"
    )
    if CHANNEL_URL:
        msg += f"官方频道：{CHANNEL_URL}\n"
    return msg


def get_about_message() -> str:
    """获取关于消息"""
    return (
        "🤖 Google One Pro 自动认证机器人\n"
        "\n"
        "功能介绍:\n"
        "- 专为 Google One Pro (Gemini Advanced 2TB) 学生优惠设计\n"
        "- 自动生成真实学生身份、大学邮箱及专属学生证\n"
        "- 一键通过 SheerID 资格审核\n"
        "\n"
        "积分获取:\n"
        "- 注册赠送 1 积分\n"
        "- 每日签到 +1 积分\n"
        "- 邀请好友 +2 积分/人\n"
        "- 使用卡密兑换积分\n"
        "\n"
        "使用方法:\n"
        "1. 在 Google One 学生优惠页面开始认证\n"
        "2. 复制浏览器地址栏中的完整 SheerID 验证链接\n"
        "3. 发送 /verify <链接> (或 /one <链接>)\n"
        "4. 等待 30-60 秒即可完成认证\n"
        "\n"
        "更多命令请发送 /help"
    )


def get_help_message(is_admin: bool = False) -> str:
    """获取帮助消息"""
    msg = (
        "📖 Google One Pro 认证机器人 - 帮助手册\n"
        "\n"
        "常用命令:\n"
        "/start - 开始使用（注册）\n"
        f"/verify <链接> - Google One Pro 认证（消耗 {VERIFY_COST} 积分）\n"
        f"/one <链接> - 同 /verify 命令\n"
        "/balance - 查看积分余额\n"
        "/qd - 每日签到（+1积分）\n"
        "/invite - 生成专属邀请链接（+2积分/人）\n"
        "/use <卡密> - 兑换卡密积分\n"
        "/about - 了解机器人\n"
        "/help - 查看此帮助信息\n"
    )

    if is_admin:
        msg += (
            "\n管理员命令:\n"
            "/addbalance <用户ID> <积分> - 增加用户积分\n"
            "/block <用户ID> - 拉黑用户\n"
            "/white <用户ID> - 解除拉黑\n"
            "/blacklist - 查看黑名单\n"
            "/genkey <卡密> <积分> [次数] [天数] - 生成充值卡密\n"
            "/listkeys - 查看所有卡密\n"
            "/broadcast <文本> - 向所有用户广播消息\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """获取积分不足消息"""
    return (
        f"⚠️ 积分不足！认证需要 {VERIFY_COST} 积分，您当前仅有 {current_balance} 积分。\n\n"
        "获取积分方式:\n"
        "- 每日签到：/qd\n"
        "- 邀请好友：/invite\n"
        "- 使用卡密：/use <卡密>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """获取验证命令使用说明"""
    return (
        f"使用方法: {command} <SheerID链接>\n\n"
        "示例:\n"
        f"{command} https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=xxx\n\n"
        "获取验证链接:\n"
        f"1. 访问 {service_name} 学生优惠认证页面\n"
        "2. 开始认证流程\n"
        "3. 复制浏览器地址栏中的完整 SheerID URL\n"
        f"4. 发送 {command} <URL> 提交"
    )
