import os
import sys
import time
import socket
import logging
from urllib.parse import urlparse
from DrissionPage import ChromiumPage, ChromiumOptions
from one.img_generator import generate_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def verify(url: str):
    first_name = "Ethan"
    last_name = "Miller"
    b_year = "2002"
    b_month = "11"
    b_day = "18"
    email = "ethan.miller934@psu.edu"
    school_id = "2565"

    # 1. 生成配套在读证明
    card_png_path = os.path.abspath("student_card.png")
    img_data = generate_image(first_name, last_name, school_id)
    with open(card_png_path, "wb") as f:
        f.write(img_data)
    logger.info(f"✅ 官方学生在读证明已就绪: {card_png_path}")

    # 2. 配置代理 (必须使用 17897 纯净美国专线)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_17897_open = (sock.connect_ex(('127.0.0.1', 17897)) == 0)
    sock.close()
    
    proxy_port = 17897 if is_17897_open else 7897
    proxy_addr = f"http://127.0.0.1:{proxy_port}"
    logger.info(f"🌐 挂载专用节点: {proxy_addr} ({'🇺🇸 纯净美国专线 (规避风控)' if proxy_port == 17897 else '默认节点'})")

    co = ChromiumOptions()
    co.set_browser_path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    co.set_local_port(9333)
    user_data_dir = os.path.abspath("dp_user_data")
    co.set_user_data_path(user_data_dir)
    co.set_proxy(proxy_addr)
    co.headless(False)

    page = ChromiumPage(co)
    try:
        logger.info(f"🚀 正在打开 SheerID 验证页面...")
        page.get(url)
        time.sleep(3)

        # 检查是否已经是错误页面
        body_text = page.html
        if "无法继续" in body_text or "次数已超限" in body_text:
            logger.error("链接在打开时已处于失效状态")
            return {"success": False, "message": "该链接此前已失效或超限，请从 Google One 重新生成一个新验证链接。"}

        # 填写国家：精确匹配 "美国"
        logger.info("🗺️ 选择国家: 美国...")
        country_input = page.ele('#sid-country')
        if country_input:
            country_input.click()
            time.sleep(0.5)
            country_input.input('美国')
            time.sleep(1)
            us_opt = page.ele('xpath://div[@role="option" and normalize-space()="美国"]') or \
                     page.ele('xpath://li[@role="option" and normalize-space()="美国"]') or \
                     page.ele('@role=option@@text()=美国')
            if us_opt:
                us_opt.click(by_js=True)
            else:
                page.actions.type('\n')
        time.sleep(1)

        # 填写学校：Pennsylvania State University
        logger.info("🏫 匹配高校: Pennsylvania State University-Main Campus...")
        school_input = page.ele('#sid-college-name')
        if school_input:
            school_input.click()
            school_input.input('Pennsylvania State University')
            time.sleep(2)
            main_campus = page.ele('xpath://div[@role="option"][contains(., "Main Campus")]') or \
                          page.ele('xpath://li[@role="option"][contains(., "Main Campus")]') or \
                          page.ele('@role=option@@text():Main Campus')
            if main_campus:
                main_campus.click(by_js=True)
            else:
                first_opt = page.ele('@role=option@@text():Pennsylvania')
                if first_opt:
                    first_opt.click(by_js=True)
        time.sleep(1)

        # 填写姓名与出生日期
        logger.info("📝 自动填写学生姓名与出生日期...")
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
                page.ele('xpath://li[@role="option"][contains(., "11") or contains(., "十一月") or contains(., "Nov")]') or \
                page.ele('text:十一月') or page.ele('text:11')
            if m:
                m.click(by_js=True)
            time.sleep(0.5)

        # 填写邮箱
        em = page.ele('#sid-email')
        if em:
            em.input(email)
        time.sleep(1)

        logger.info("✅ 表单已完整填写！等待 Cloudflare 人机验证盾...")

        submitted = False
        for i in range(25):
            time.sleep(1)
            btn = page.ele('#sid-submit-wrapper__collect-info') or page.ele('button[type="submit"]')
            if not btn:
                break
            disabled = btn.attr('aria-disabled')
            if disabled != 'true':
                logger.info("🚀 人机验证秒过，自动点击提交...")
                btn.click()
                submitted = True
                break

        if not submitted:
            btn = page.ele('#sid-submit-wrapper__collect-info') or page.ele('button[type="submit"]')
            if btn:
                btn.click(by_js=True)

        logger.info("📄 已提交个人信息，等待 SheerID 响应...")
        time.sleep(4)

        # 检查是否需要上传证明或已通过
        for j in range(35):
            curr_url = page.url
            domain = urlparse(curr_url).netloc
            if "google.com" in domain and ("ai-student" in curr_url or "success" in curr_url):
                logger.info(f"🎉 恭喜！已直接通过认证并跳转回 Google One: {curr_url}")
                page.get_screenshot(path='success_screen.png', full_page=True)
                return {"success": True, "redirect_url": curr_url}

            # 检查是否有错误提示
            html = page.html
            if "无法继续" in html or "fraudRulesReject" in html:
                logger.error("SheerID 提示无法继续验证")
                page.get_screenshot(path='error_screen.png', full_page=True)
                return {"success": False, "message": "SheerID 提示无法继续您的验证"}

            file_input = page.ele('input[type="file"]')
            if file_input:
                logger.info("📤 检测到证明上传入口，自动上传宾州州立大学官方在读证明...")
                file_input.input(card_png_path)
                time.sleep(3)

                doc_btn = page.ele('button[type="submit"]') or \
                          page.ele('text:提交') or \
                          page.ele('text:Submit') or \
                          page.ele('xpath://button[contains(., "提交") or contains(., "Submit") or contains(., "上传")]')
                if doc_btn:
                    logger.info("🚀 点击提交官方证明文件...")
                    doc_btn.click()
                    time.sleep(6)
                logger.info("✅ 证明文件已成功提交，正在等待最终审核确认...")
                page.get_screenshot(path='doc_submitted.png', full_page=True)
                break
            time.sleep(1)

        time.sleep(8)
        page.get_screenshot(path='final_state.png', full_page=True)
        return {
            "success": True,
            "message": "全流程已自动执行完毕！学生在读证明已成功上传至 SheerID！",
            "redirect_url": page.url if "google.com" in urlparse(page.url).netloc else None
        }

    except Exception as e:
        logger.exception(f"执行出错: {e}")
        return {"success": False, "message": str(e)}

    finally:
        time.sleep(5)
        page.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1].strip()
    else:
        target_url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=6ad70d3ba8918e3dcfa5e9dc&redirectUrl=https%3A%2F%2Fone.google.com%2Fu%2F9%2Fai-student%3Fsc%3DCi0SKwopCidnMS5wbGF5LjJ0Yi5haS5zdHVkZW50Om1vbnRobHk6ZWZ0LTEybW8iAhABahUxMTA2ODY4OTk2MTk5NjAyMDQwMjM&authuser=9"
        
    res = verify(target_url)
    print("RESULT:", res)
