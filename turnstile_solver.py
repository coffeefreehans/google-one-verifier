"""Cloudflare Turnstile 第三方打码平台求解器 (CapSolver / 2Captcha)"""
import os
import time
import logging
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SHEERID_TURNSTILE_SITEKEY = "0x4AAAAAAACaWNlR_tN9-HfHj"


def solve_turnstile_capsolver(page_url: str, site_key: str = SHEERID_TURNSTILE_SITEKEY) -> Optional[str]:
    """使用 CapSolver 识别 Turnstile"""
    api_key = os.getenv("CAPSOLVER_API_KEY")
    if not api_key:
        return None

    logger.info("正在调用 CapSolver 识别 Cloudflare Turnstile...")
    client = httpx.Client(timeout=30.0)
    try:
        task_res = client.post(
            "https://api.capsolver.com/createTask",
            json={
                "clientKey": api_key,
                "task": {
                    "type": "AntiTurnstileTaskProxyLess",
                    "websiteURL": page_url,
                    "websiteKey": site_key,
                },
            },
        ).json()

        if task_res.get("errorId") != 0:
            logger.error(f"CapSolver 创建任务失败: {task_res}")
            return None

        task_id = task_res.get("taskId")
        for _ in range(40):
            time.sleep(1.5)
            result = client.post(
                "https://api.capsolver.com/getTaskResult",
                json={"clientKey": api_key, "taskId": task_id},
            ).json()

            if result.get("status") == "ready":
                token = result.get("solution", {}).get("token")
                logger.info("✅ CapSolver 识别成功！")
                return token
            elif result.get("status") == "failed":
                logger.error(f"CapSolver 识别失败: {result}")
                return None

        logger.error("CapSolver 识别超时")
        return None
    except Exception as e:
        logger.error(f"CapSolver 请求异常: {e}")
        return None


def solve_turnstile_2captcha(page_url: str, site_key: str = SHEERID_TURNSTILE_SITEKEY) -> Optional[str]:
    """使用 2Captcha 识别 Turnstile"""
    api_key = os.getenv("TWOCAPTCHA_API_KEY")
    if not api_key:
        return None

    logger.info("正在调用 2Captcha 识别 Cloudflare Turnstile...")
    client = httpx.Client(timeout=30.0)
    try:
        in_res = client.post(
            "https://2captcha.com/in.php",
            data={
                "key": api_key,
                "method": "turnstile",
                "sitekey": site_key,
                "pageurl": page_url,
                "json": 1,
            },
        ).json()

        if in_res.get("status") != 1:
            logger.error(f"2Captcha 创建任务失败: {in_res}")
            return None

        request_id = in_res.get("request")
        for _ in range(40):
            time.sleep(2)
            res = client.get(
                "https://2captcha.com/res.php",
                params={"key": api_key, "action": "get", "id": request_id, "json": 1},
            ).json()

            if res.get("status") == 1:
                logger.info("✅ 2Captcha 识别成功！")
                return res.get("request")
            elif res.get("request") != "CAPCHA_NOT_READY":
                logger.error(f"2Captcha 识别失败: {res}")
                return None

        logger.error("2Captcha 识别超时")
        return None
    except Exception as e:
        logger.error(f"2Captcha 请求异常: {e}")
        return None


def get_turnstile_token(page_url: str, site_key: str = SHEERID_TURNSTILE_SITEKEY) -> Optional[str]:
    """尝试通过已配置的打码平台获取 Turnstile Token"""
    if os.getenv("CAPSOLVER_API_KEY"):
        token = solve_turnstile_capsolver(page_url, site_key)
        if token:
            return token

    if os.getenv("TWOCAPTCHA_API_KEY"):
        token = solve_turnstile_2captcha(page_url, site_key)
        if token:
            return token

    return None
