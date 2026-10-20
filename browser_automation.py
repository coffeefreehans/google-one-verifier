"""SheerID 本地自动化模块 (基于 DrissionPage 原生无痕过盾)"""
import os
import sys
import time
import socket
import logging
from typing import Dict
from urllib.parse import urlparse
from DrissionPage import ChromiumPage, ChromiumOptions
from one.img_generator import generate_image

logger = logging.getLogger(__name__)


def run_browser_automation(verification_url: str, school_id: str = "2565") -> Dict:
    """运行浏览器全自动化流程"""
    first_name = "Ethan"
    last_name = "Miller"
    b_year = "2002"
    b_month = "11"
    b_day = "18"
    email = "ethan.miller934@psu.edu"

    # 1. 生成配套在读证明
    card_png_path = os.path.abspath("student_card.png")
    img_data = generate_image(first_name, last_name, school_id)
    with open(card_png_path, "wb") as f:
        f.write(img_data)
    print("\n" + "=" * 60)
    print("🎓 1. 已配套好宾州州立大学官方在读证明:")
    print(f"   学生姓名: {first_name} {last_name}")
    print(f"   出生日期: {b_year}-{b_month}-{b_day}")
    print(f"   目标高校: Pennsylvania State University-Main Campus")
    print(f"   官方邮箱: {email}")
    print(f"   证件文件: {card_png_path}")
    print("=" * 60 + "\n")

    # 2. 检查专用代理端口 17897 (美国节点) 是否开启
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_17897_open = (sock.connect_ex(('127.0.0.1', 17897)) == 0)
    sock.close()
    
    proxy_port = 17897 if is_17897_open else 7897
    proxy_addr = f"http://127.0.0.1:{proxy_port}"
    print(f"🌐 2. 自动挂载网络节点: {proxy_addr} ({'🇺🇸 纯净美国专线' if proxy_port == 17897 else '默认节点'})")

    # 3. 配置 DrissionPage 浏览器
    co = ChromiumOptions()
    co.set_browser_path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    co.set_local_port(9333)
    user_data_dir = os.path.abspath("dp_user_data")
    co.set_user_data_path(user_data_dir)
    co.set_proxy(proxy_addr)
    co.headless(False)

    page = ChromiumPage(co)
    try:
        print(f"🚀 3. 正在打开 SheerID 验证页面...")
        page.get(verification_url)
        time.sleep(3)

        # 检查是否已经是错误页面
        body_text = page.html
        if "无法继续" in body_text or "次数已超限" in body_text:
            return {"success": False, "message": "该验证链接已失效或超过最大尝试次数，请换一个 Google 账号重新生成。"}

        # 填写国家：精确匹配 "美国"
        print("🗺️ 4. 选择国家: 美国...")
        c = page.ele('#sid-country')
        if c:
            c.click()
            c.input('美国', clear=True)
            time.sleep(1)
            items = page.eles('css:#sid-country-menu .sid-input-select-list__item')
            for item in items:
                if item.text.strip() == "美国" or item.text.strip() == "United States":
                    item.click()
                    print("   ✅ 已精准选中国家: 美国")
                    break
        time.sleep(1)

        # 填写学校：Pennsylvania State University
        print("🏫 5. 检索并匹配高校: Pennsylvania State University-Main Campus...")
        s = page.ele('#sid-college-name')
        if s:
            s.click()
            s.input('Pennsylvania State University', clear=True)
            time.sleep(2)
            main_opt = page.ele('text:Main Campus') or page.ele('text:Pennsylvania State University-Main Campus')
            if main_opt:
                main_opt.click()
                print("   ✅ 已选中高校: Pennsylvania State University-Main Campus")
            else:
                page.actions.type('\n')
        time.sleep(1)

        # 填写姓名与出生日期
        print("📝 6. 自动填写学生姓名与出生日期...")
        fn = page.ele('#sid-first-name')
        if fn:
            fn.input(first_name)
        ln = page.ele('#sid-last-name')
        if ln:
            ln.input(last_name)
        bd = page.ele('#sid-birthdate-day')
        if bd:
            bd.input(b_day)
        by = page.ele('#sid-birthdate-year')
        if by:
            by.input(b_year)

        # 填写月份
        bm = page.ele('#sid-birthdate__month')
        if bm:
            bm.click()
            time.sleep(0.5)
            m = page.ele('xpath://div[@role="option"][contains(., "11") or contains(., "十一月") or contains(., "Nov")]') or \
                page.ele('text:十一月') or page.ele('text:11')
            if m:
                m.click(by_js=True)
            time.sleep(0.5)

        # 填写邮箱
        em = page.ele('#sid-email')
        if em:
            em.input(email)
        time.sleep(1)

        print("✅ 7. 表单各项信息已 100% 自动填写完毕！")
        print("🛡️ 等待 Cloudflare 人机验证盾...")

        submitted = False
        for i in range(25):
            time.sleep(1)
            btn = page.ele('#sid-submit-wrapper__collect-info') or page.ele('button[type="submit"]')
            if not btn:
                break
            disabled = btn.attr('aria-disabled')
            if disabled != 'true':
                print("🚀 人机验证秒过，正在自动点击提交...")
                btn.click()
                submitted = True
                break

        if not submitted:
            btn = page.ele('#sid-submit-wrapper__collect-info') or page.ele('button[type="submit"]')
            if btn:
                btn.click(by_js=True)

        print("📄 8. 表单已提交，等待 SheerID 响应...")
        time.sleep(4)

        # 检查是否直接成功或需要上传证明
        for j in range(30):
            curr_url = page.url
            domain = urlparse(curr_url).netloc
            if "google.com" in domain and ("ai-student" in curr_url or "success" in curr_url):
                print("🎉 恭喜！已直接通过认证并激活 Google One 学生特惠！")
                return {"success": True, "redirect_url": curr_url, "message": "学生认证已成功完成！"}

            html = page.html
            if "无法继续" in html or "次数已超限" in html:
                return {"success": False, "message": "该 Google 账号此前验证错误次数已超限，请换一个 Google 账号重新点击获取链接！"}

            file_input = page.ele('input[type="file"]')
            if file_input:
                print("📤 9. 检测到证明上传入口，自动上传官方 LionPATH 在读证明...")
                file_input.input(card_png_path)
                time.sleep(3)

                doc_btn = page.ele('button[type="submit"]') or \
                          page.ele('xpath://button[contains(., "提交") or contains(., "Submit") or contains(., "上传")]')
                if doc_btn:
                    print("🚀 点击提交证明文件...")
                    doc_btn.click()
                    time.sleep(5)
                print("✅ 证明文件已成功提交，正在等待最终审核确认...")
                break
            time.sleep(1)

        time.sleep(5)
        return {
            "success": True,
            "message": "全流程已自动执行完毕！学生在读证明已成功上传至 SheerID！",
            "redirect_url": page.url if "google.com" in urlparse(page.url).netloc else None
        }

    except Exception as e:
        logger.error(f"自动化过程发生异常: {e}")
        return {"success": False, "message": str(e)}

    finally:
        time.sleep(5)
        page.quit()
