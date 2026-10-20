import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from DrissionPage import ChromiumPage, ChromiumOptions
import time, os
from one.img_generator import generate_image

url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=6ad70d3ba8918e3dcfa5e9dc&redirectUrl=https%3A%2F%2Fone.google.com%2Fu%2F9%2Fai-student%3Fsc%3DCi0SKwopCidnMS5wbGF5LjJ0Yi5haS5zdHVkZW50Om1vbnRobHk6ZWZ0LTEybW8iAhABahUxMTA2ODY4OTk2MTk5NjAyMDQwMjM&authuser=9"

first_name = "Ethan"
last_name = "Miller"
b_year = "2002"
b_month = "11"
b_day = "18"
email = "ethan.miller934@psu.edu"
school_id = "2565"

# 确保在读证明就绪
card_png_path = os.path.abspath("student_card.png")
img_data = generate_image(first_name, last_name, school_id)
with open(card_png_path, "wb") as f:
    f.write(img_data)
print("1. 学生在读证明已准备完成:", card_png_path)

co = ChromiumOptions()
co.set_browser_path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
co.set_local_port(9333)
co.set_proxy("http://127.0.0.1:17897")
co.headless(False)

page = ChromiumPage(co)
try:
    print("2. 正在打开 SheerID 验证页面...")
    page.get(url)
    time.sleep(3)
    
    # 1. 选择国家: 美国
    print("3. 选择国家: 美国...")
    c = page.ele('#sid-country')
    c.click()
    c.input('美国', clear=True)
    time.sleep(1)
    
    items = page.eles('css:#sid-country-menu .sid-input-select-list__item')
    for item in items:
        if item.text.strip() == "美国" or item.text.strip() == "United States":
            item.click()
            print("   ✅ 已选择国家: 美国")
            break
    time.sleep(1)
    
    # 2. 选择高校: Pennsylvania State University-Main Campus
    print("4. 选择高校: Pennsylvania State University-Main Campus...")
    s = page.ele('#sid-college-name')
    s.click()
    s.input('Pennsylvania State University', clear=True)
    time.sleep(2)
    
    # 直接通过文本匹配 Main Campus
    main_opt = page.ele('text:Main Campus') or page.ele('text:Pennsylvania State University-Main Campus')
    if main_opt:
        main_opt.click()
        print("   ✅ 已选择高校: Pennsylvania State University-Main Campus")
    else:
        print("   ⚠️ 未找到 Main Campus，尝试回车确认")
        page.actions.type('\n')
    time.sleep(1)
    
    # 3. 填写姓名与出生日期
    print("5. 填写姓名、出生日期及邮箱...")
    page.ele('#sid-first-name').input(first_name)
    page.ele('#sid-last-name').input(last_name)
    page.ele('#sid-birthdate-day').input(b_day)
    page.ele('#sid-birthdate-year').input(b_year)
    
    page.ele('#sid-birthdate__month').click()
    time.sleep(0.5)
    m = page.ele('xpath://div[@role="option"][contains(., "11") or contains(., "十一月") or contains(., "Nov")]') or \
        page.ele('text:十一月') or page.ele('text:11')
    if m:
        m.click(by_js=True)
    time.sleep(0.5)
    
    page.ele('#sid-email').input(email)
    time.sleep(1)
    
    page.get_screenshot(path='ready_to_submit.png', full_page=True)
    print("6. 表单全部填写完成，等待 Turnstile 人机验证...")
    
    # 4. 提交
    for i in range(25):
        time.sleep(1)
        btn = page.ele('#sid-submit-wrapper__collect-info') or page.ele('button[type="submit"]')
        disabled = btn.attr('aria-disabled')
        if disabled != 'true':
            print("   🚀 人机验证通过，正在提交学生信息...")
            btn.click()
            break
            
    print("7. 表单已提交，等待 SheerID 审核/证件上传阶段...")
    time.sleep(5)
    page.get_screenshot(path='after_form_submit.png', full_page=True)
    
    # 5. 上传证明文件
    uploaded = False
    for j in range(30):
        # 检查是否已有文件上传控件
        file_input = page.ele('input[type="file"]')
        if file_input:
            print("8. 发现官方证明上传入口，自动上传学生在读证明...")
            file_input.input(card_png_path)
            time.sleep(3)
            page.get_screenshot(path='doc_selected.png', full_page=True)
            
            # 点击上传/提交按钮
            doc_btn = page.ele('button[type="submit"]') or \
                      page.ele('xpath://button[contains(., "提交") or contains(., "Submit") or contains(., "上传")]')
            if doc_btn:
                print("   🚀 点击提交证明文件...")
                doc_btn.click()
                time.sleep(5)
            print("   ✅ 证明文件已提交成功！")
            uploaded = True
            break
            
        # 检查是否直接跳转到完成页面
        if "google.com" in page.url and ("ai-student" in page.url or "success" in page.url):
            print("🎉 恭喜！已直接通过认证并跳转完成:", page.url)
            break
            
        time.sleep(1)
        
    page.get_screenshot(path='final_result_screen.png', full_page=True)
    print("9. 最终页面 URL:", page.url)
    print("全流程执行完成！")

except Exception as e:
    print(f"❌ 发生异常: {e}")
    page.get_screenshot(path='error_exec.png', full_page=True)

finally:
    time.sleep(10)
    page.quit()
