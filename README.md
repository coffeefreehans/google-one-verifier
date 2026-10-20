# Google One AI Pro (Gemini Advanced 2TB) 学生优惠全自动认证工具

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/Engine-DrissionPage-green.svg" alt="Automation Engine" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License" />
</p>

> 🚀 **Google One AI Premium (Gemini Advanced 2TB) 学生特惠 SheerID 自动化认证工具**  
> 基于 **DrissionPage 原生无痕浏览器引擎**，实现 **0秒秒过 Cloudflare Turnstile 人机验证盾（完全免打码费）**，自动生成全套高校官方在读证明并全自动上传提交！

---

## ✨ 核心特性

- 🛡️ **原生无痕过盾**：彻底解决 Playwright / Selenium 被 Cloudflare 识别为自动化工具的问题，Turnstile 人机盾 0 秒通过，免去购买第三方打码平台 API 的繁琐与成本。
- 🎓 **官方在读证明自动生成**：内置宾夕法尼亚州立大学（Pennsylvania State University）官方 LionPATH 选课表与在读证明生成引擎，智能渲染真实学生信息与学期数据。
- 📝 **全要素精准匹配**：自动精准选中国家（美国）、高校（PSU Main Campus）、出生年月、学生姓名及专属 EDU 邮箱。
- 📤 **自动材料提交**：识别 SheerID 证件上传页面，全自动上传并提交证明材料，全程无需手动干预。
- 🌐 **代理节点支持**：自动读取与适配本地 Clash 等网络代理，防止因地区不匹配触发 SheerID 的 `fraudRulesReject` 地区风控。
- 💻 **极简开箱即用**：Windows 支持一键双击运行，无需配置任何复杂数据库或 Telegram 机器人。

---

## 🚀 快速上手

### 1. 克隆仓库与安装依赖

确保本地已安装 Python 3.11+ 以及 Google Chrome 浏览器：

```bash
git clone https://github.com/coffeefreehans/google-one-verifier.git
cd google-one-verifier
pip install -r requirements.txt
```

### 2. 获取 SheerID 认证链接

1. 在浏览器中登录您的 Google 账号，访问 [Google One AI 学生优惠活动页](https://one.google.com/ai-student)。
2. 点击页面中央的 **【开始验证】 / 【获取优惠】** 按钮。
3. 网页会跳转至以 `https://services.sheerid.com/verify/...` 开头的 SheerID 专属验证链接，**复制该完整 URL**。

### 3. 一键启动自动认证

#### 方式一：Windows 一键双击（最推荐）
直接双击运行项目目录下的 **`一键验证.bat`**，按提示粘贴验证链接并回车即可。

#### 方式二：命令行运行
```bash
python verify_one.py "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=xxxxxx"
```

程序将全自动唤起浏览器完成：
1. 填选国家与宾州州立大学主校区
2. 填入配套学生真实姓名、生日及官方邮箱
3. 秒过 Cloudflare Turnstile 人机盾并提交
4. 自动生成并上传官方 LionPATH 在读证明图片
5. 最终审核提交并自动完成验证！

---

## 🛠️ 项目结构

```text
├── 一键验证.bat           # Windows 一键双击运行脚本
├── run.bat               # 备用启动脚本
├── verify_one.py         # 命令行主入口程序
├── browser_automation.py # DrissionPage 全自动化与无痕过盾引擎
├── dp_full_verify.py     # 独立端到端认证模块
├── turnstile_solver.py   # Turnstile 辅助识别模块
├── requirements.txt      # 依赖包列表
├── utils/
│   └── proxy.py          # 本地代理检测与挂载工具
└── one/
    ├── config.py         # 高校及活动配置
    ├── img_generator.py  # 官方 LionPATH 在读证明生成器
    ├── name_generator.py # 学生姓名与生日生成器
    └── sheerid_verifier.py
```

---

## ⚠️ 常见问题排查（FAQ）

### Q1: 提示 `fraudRulesReject`（“我们无法继续您的验证，请检查并未未使用 VPN”）
- **原因**：SheerID 检测到所使用的代理 IP 归属地与申请学校国家（美国）不匹配（例如挂着日本/香港代理申请美国大学），或使用了高风险公共机房 IP。
- **解决**：在代理客户端（如 Clash Verge）中将节点切换为**美国专线 / 美国节点**后重新获取新链接尝试。

### Q2: 提示 `verificationLimitExceeded`（“验证次数已超限”）
- **原因**：Google One 与 SheerID 对单个 Google 账号有防刷限制（通常每个账号仅允许提交 3 次）。若连续错误尝试超过 3 次，该 Google 账号会被活动暂时锁定。
- **解决**：在 Chrome 浏览器中切换至其他 Google 账号，重新点击活动页生成新的 SheerID 链接进行验证。

---

## 📄 开源许可

本项目遵循 [MIT License](LICENSE) 开源协议。仅供网络安全技术研究与自动化测试学习交流使用，严禁用于任何非法用途。
