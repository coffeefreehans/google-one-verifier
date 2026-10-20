"""Google One Pro (Gemini Advanced) 终端全自动认证工具

支持两种全自动模式：
1. 本地浏览器全自动模式（免打码费）：自动打开 Chrome 填表、过人机验证并自动上传学生证。
2. API 极速打码模式（如果配置了 CAPSOLVER_API_KEY 或 TWOCAPTCHA_API_KEY）：全后台 3 秒极速过审。
"""
import sys
import os
import io

# 解决 Windows 控制台编码问题 (GBK 下打印 Emoji 报错)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import logging
from dotenv import load_dotenv

load_dotenv()
from one.sheerid_verifier import SheerIDVerifier
from turnstile_solver import get_turnstile_token
from browser_automation import run_browser_automation
from utils.proxy import get_system_proxy

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_url(url: str) -> bool:
    """处理单个验证链接"""
    url = url.strip().strip("'\"").strip("\ufeff")
    if not url:
        return False

    # 尝试解析 verificationId
    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        if len(url) in (24, 32) and all(c in "0123456789abcdefABCDEF" for c in url):
            verification_id = url
            url = f"https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId={verification_id}"
        else:
            print("\n❌ 错误: 无法解析 SheerID 验证 ID，请检查链接是否正确。")
            print("正确链接示例:")
            print("https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=67cb0f1234567890abcdef12\n")
            return False

    proxy_str = get_system_proxy()
    print("-" * 60)
    print(f"📋 提取验证 ID: {verification_id}")
    if proxy_str:
        print(f"🌐 自动挂载系统代理: {proxy_str}")
    print("-" * 60)

    # 模式 1: 检查是否配置了打码平台 API Key
    has_api_solver = bool(os.getenv("CAPSOLVER_API_KEY") or os.getenv("TWOCAPTCHA_API_KEY"))
    if has_api_solver:
        print("⚡ 检测到已配置打码平台，启动【全后台 API 极速模式】...")
        token = get_turnstile_token(url)
        if token:
            print("✅ 成功获取 Turnstile CaptchaToken，开始提交验证...")
            verifier = SheerIDVerifier(verification_id)
            result = verifier.verify(captcha_token=token)
            if result.get("success"):
                print("\n" + "=" * 60)
                print("✅ 恭喜！认证文档已成功提交！")
                if result.get("redirect_url"):
                    print(f"🔗 完成跳转链接: {result['redirect_url']}")
                print("=" * 60 + "\n")
                return True
            else:
                print(f"❌ 认证提交失败: {result.get('message')}")
                return False
        else:
            print("⚠️ 打码平台未能识别验证码，自动降级为【本地浏览器全自动模式】...\n")

    # 模式 2: 本地 Chrome 浏览器全自动化模式
    print("🤖 启动【本地 Chrome 浏览器全自动模式】...")
    print("   脚本将自动打开 Chrome，自动填表、自动过验证码、自动上传学生证！")
    result = run_browser_automation(url)

    print("\n" + "=" * 60)
    print("📌 执行结果:")
    print("=" * 60)
    if result.get("success"):
        print(f"✅ {result.get('message', '操作成功')}")
        if result.get("redirect_url"):
            print(f"🔗 跳转链接: {result['redirect_url']}")
        print("=" * 60 + "\n")
        return True
    else:
        print(f"❌ 失败: {result.get('message')}")
        print("=" * 60 + "\n")
        return False


def main():
    print("=" * 60)
    print("   Google One Pro (Gemini Advanced) 终端全自动认证工具")
    print("   （自动生成资料、自动填写表单、自动过盾、自动上传证件）")
    print("=" * 60)

    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
        success = process_url(url)
        sys.exit(0 if success else 1)

    print("\n💡 提示: 直接粘贴完整 SheerID 验证链接（输入 q 或 exit 退出）：")
    while True:
        try:
            url = input("\n请输入验证链接 (URL): ").strip().strip("'\"").strip("\ufeff")
            if not url:
                continue
            if url.lower() in ("q", "quit", "exit"):
                print("👋 已退出。")
                break

            process_url(url)

        except (KeyboardInterrupt, EOFError):
            print("\n👋 用户终止操作，已退出。")
            break


if __name__ == "__main__":
    main()
