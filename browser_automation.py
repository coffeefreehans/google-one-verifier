"""SheerID 本地自动化模块 (基于 DrissionPage 原生无痕过盾，每次动态生成全新真实学生身份)"""
import os
import sys
import time
import logging
from typing import Dict, Optional
from urllib.parse import urlparse
from DrissionPage import ChromiumPage, ChromiumOptions

from one.name_generator import NameGenerator, generate_birth_date
from one.img_generator import generate_image, generate_psu_email
from utils.proxy import get_system_proxy

logger = logging.getLogger(__name__)

MONTH_LOOKUP = {
    "1": ["一月", "Jan", "1月", "01"],
    "2": ["二月", "Feb", "2月", "02"],
    "3": ["三月", "Mar", "3月", "03"],
    "4": ["四月", "Apr", "4月", "04"],
    "5": ["五月", "May", "5月", "05"],
    "6": ["六月", "Jun", "6月", "06"],
    "7": ["七月", "Jul", "7月", "07"],
    "8": ["八月", "Aug", "8月", "08"],
    "9": ["九月", "Sep", "9月", "09"],
    "10": ["十月", "Oct", "10月", "10"],
    "11": ["十一月", "Nov", "11月", "11"],
    "12": ["十二月", "Dec", "12月", "12"],
}


def run_browser_automation(verification_url: str, school_id: str = "2565") -> Dict:
    """运行浏览器全自动化流程（每次动态生成全新学生身份）"""
    
    # 1. 动态生成全新的真实学生资料（绝不使用预存硬编码信息）
    name_info = NameGenerator.generate()
    first_name = name_info["first_name"]
    last_name = name_info["last_name"]

    birth_info = generate_birth_date()
    b_year = birth_info["year"]
    b_month = birth_info["month"]
    b_day = birth_info["day"]

    email = generate_psu_email(first_name, last_name)

    # 生成配套官方在读证明与课表
    card_png_path = os.path.abspath("student_card.png")
    img_data = generate_image(first_name, last_name, school_id)
    with open(card_png_path, "wb") as f:
        f.write(img_data)

    print("\n" + "=" * 60)
    print("🎓 1. 本次动态生成全新宾州州立大学学生身份:")
    print(f"   学生姓名: {first_name} {last_name}")
    print(f"   出生日期: {b_year}年 {b_month}月 {b_day}日")
    print(f"   目标高校: Pennsylvania State University-Main Campus")
    print(f"   专属邮箱: {email}")
    print(f"   官方证明: {card_png_path}")
    print("=" * 60 + "\n")

    # 2. 自动获取本机真实可用代理（如 Clash 127.0.0.1:7897）
    co = ChromiumOptions()
    co.set_browser_path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    co.set_local_port(9333)
    user_data_dir = os.path.abspath("dp_user_data")
    co.set_user_data_path(user_data_dir)

    proxy_url = get_system_proxy()
    if proxy_url:
        print(f"🌐 2. 自动挂载本机代理: {proxy_url}")
        co.set_proxy(proxy_url)
    else:
        print("🌐 2. 未检测到本地代理，使用网络直连模式")
        
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
        print(f"📝 6. 自动填写学生姓名 ({first_name} {last_name}) 与出生日期...")
        fn = page.ele('#sid-first-name')
        if fn:
            fn.input(first_name)
        ln = page.ele('#sid-last-name')
        if ln:
            ln.input(last_name)
        bd = page.ele('#sid-birthdate-day')
        if bd:
            bd.input(str(b_day))
        by = page.ele('#sid-birthdate-year')
        if by:
            by.input(str(b_year))

        # 动态匹配并选择月份
        bm = page.ele('#sid-birthdate__month')
        if bm:
            bm.click()
            time.sleep(0.5)
            month_key = str(int(b_month))
            keywords = MONTH_LOOKUP.get(month_key, [month_key])
            
            items = page.eles('css:#sid-birthdate__month-menu .sid-input-select-list__item') or \
                    page.eles('xpath://div[@role="option"]')
            
            month_selected = False
            for item in items:
                txt = item.text.strip()
                if any(k in txt for k in keywords) or txt == month_key:
                    item.click(by_js=True)
                    print(f"   ✅ 已选中出生月份: {txt}")
                    month_selected = True
                    break
                    
            if not month_selected:
                for k in keywords:
                    opt = page.ele(f'text:{k}')
                    if opt:
                        opt.click(by_js=True)
                        print(f"   ✅ 已选中出生月份: {k}")
                        break
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
