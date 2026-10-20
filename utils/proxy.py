"""代理自动检测工具"""
import os
import winreg
from typing import Optional


def get_system_proxy() -> Optional[str]:
    """获取系统代理（支持 Windows 注册表与环境变量）"""
    # 1. 检查环境变量 PROXY / HTTPS_PROXY / HTTP_PROXY
    env_proxy = os.getenv("PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if env_proxy:
        if not env_proxy.startswith("http://") and not env_proxy.startswith("https://") and not env_proxy.startswith("socks5://"):
            env_proxy = f"http://{env_proxy}"
        return env_proxy

    # 2. 检查 Windows 注册表 Internet Settings
    try:
        reg = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        )
        enable, _ = winreg.QueryValueEx(reg, "ProxyEnable")
        if enable:
            server, _ = winreg.QueryValueEx(reg, "ProxyServer")
            if server:
                if not server.startswith("http://") and not server.startswith("https://"):
                    server = f"http://{server}"
                return server
    except Exception:
        pass

    return None
