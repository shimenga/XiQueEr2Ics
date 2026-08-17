# XiQueEr2ICS

一个可以把喜鹊儿课程表转成 `.ics` 日历订阅文件的小工具，支持 **Web 服务在线生成订阅链接** 与 **本地脚本直接生成** 两种模式。

---

## ✨ 功能特性

- 🔔 **课表转日历订阅**：把喜鹊儿课表自动转换成标准 `.ics` 文件，可导入 iOS 日历、Google 日历、Outlook 等
- 🌐 **Web 在线订阅**：部署服务后，网页端输入学号密码即可生成永久订阅链接，日历自动更新
- 🏫 **多学校支持**：`schools/` 目录下按学校代码存放配置，新增学校只需复制目录改配置
- 📅 **自动校历同步**：内置脚本自动拉取各学期起止日期与假期时间
- 🔒 **密码安全**：仅提交 MD5 哈希后的密码，不保存明文

---

## 🚀 快速开始

### 方式一：Web 服务（主要方式）

启动服务后，浏览器打开页面填写学号密码，生成订阅链接添加到日历 App 即可。

#### 在线公开服务（免搭建）
由作者维护的公开实例：
[🔗 点击访问公开服务](https://blog.hishutdown.cn/?p=201) （由 [5hUtd0wN](https://blog.hishutdown.cn/?p=201) 提供）

#### 自行搭建

**Docker Compose（推荐）：**

```bash
mkdir -p user          # 用户数据持久化目录
docker compose up -d
# 服务默认运行在 http://localhost:8080
```

> ⚠️ `user` 目录需挂载到容器内 `/app/user`，否则重启后缓存丢失。

**手动部署：**

```bash
pip install -r requirements.txt
./run-web.sh          # 默认 127.0.0.1:8080
# 或指定端口：
# api_host=0.0.0.0 web_port=3000 ./run-web.sh
```

#### 使用 Web 服务

1. 浏览器打开服务地址
2. 选择学校、输入学号密码、设置提醒时间
3. 点击生成，得到订阅链接
4. 把链接添加到日历 App（iOS/Google/Outlook 均支持）

订阅链接格式：

```
https://你的域名/{学号}.ics?pwd={32位MD5密码}&remindTime=30&school_code=12623
```

**API 参数说明：**

| 参数 | 说明 | 默认值 |
|---|---|---|
| `pwd` | **必填**。32位小写 MD5 密码 | - |
| `school_code` | 学校代码（如 `12623`） | `12623` |
| `remindTime` | 课前提醒时间（分钟） | `30` |
| `school_year` / `term` | 指定学年/学期 | 全部学期 |
| `all_semesters` | 是否包含所有学期 | `true` |
| `force` | 强制重新获取，忽略缓存 | `false` |

> 📌 公开服务中 `school_code` 未填时默认使用 `12623`（华南农业大学珠江学院）。

**环境变量：**

| 变量 | 说明 | 默认值 |
|---|---|---|
| `api_host` | 监听地址 | `127.0.0.1` |
| `web_port` | 监听端口 | `8080` |
| `root_path` | API 根路径前缀（反向代理场景） | 空 |
| `DEBUG` | 设为任意非空值开启调试日志 | 关闭 |

**反向代理子路径示例：**

```bash
api_host=0.0.0.0 web_port=3000 root_path=/xqe2ics ./run-web.sh
# 对应 Nginx: location /xqe2ics/ → http://localhost:3000/
```

---

### 方式二：本地脚本直接运行（无需搭建服务）

适合只想一次性导出课表、不需要订阅的场景。

#### 1. 安装依赖

```bash
cd XiQueEr2ICS
pip install -r requirements.txt   # 需 Node.js 环境（pyexecjs 依赖）
```

#### 2. 同步校历（每学期开学前运行一次）

```bash
# 同步所有学校：
python run_maintain_all.py
# 或只同步指定学校：
python run_maintain_all.py --only 12623
```

> 该脚本访问**公开**校历接口，无需登录，自动拉取最近 5 年所有学期的起止日期与假期时间。**建议每个学期开学前运行一次**，确保日历数据最新。

#### 3. 生成课表 ICS

```bash
python xqe.py <学号> <32位MD5密码> <提醒时间分钟> <学校代码> [FORCE] [学年] [学期]
```

**示例：**

```bash
python xqe.py 202534140102 e19d5cd5af0378da05f63f891c7467af 30 12623
```

提示 `save or print? (s/P)` 时输入 `s` 保存为 `test.ics`，或直接回车打印内容。

**参数说明：**

| 参数 | 说明 |
|---|---|
| 学号 | 学校学号 |
| 32位MD5密码 | 密码的 MD5 哈希（`echo -n 密码 | md5sum`） |
| 提醒时间 | 课前提醒分钟数 |
| 学校代码 | 如 `12623` |
| `FORCE` | 忽略缓存强制重新获取（可省略） |
| 学年/学期 | 指定学期（如 `2026 0`），默认全部 |

> 💡 忘记 MD5 怎么算？Linux/Mac：`echo -n "你的密码" | md5sum`；Windows PowerShell：
> `[System.BitConverter]::ToString([System.Security.Cryptography.MD5]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes("密码"))).Replace("-","").ToLower()`

---

## 🏫 添加自己的学校

喜鹊儿接口各学校差异不大，可复制已有学校配置修改：

1. 在 `schools/` 下创建以**学校代码**命名（纯数字）的文件夹
2. 复制其他学校的 `config.json`、`timetable.json`、`jkingo.des.js`、`maintain.py` 等文件作为模板
3. 修改 `config.json` 匹配你的学校（`title`/`schoolCode`/`rootUrl`）
4. 修改 `timetable.json` 配置上下课时间（各校作息不同，需手动配置）

---

## 📅 学期校历数据结构

每个学校的 `school_calendar.json` 由 `maintain.py` 自动生成，结构如下：

```json
{
  "2026-0": {
    "termStartDate": "2026-08-31",
    "termEndDate": "2027-01-15",
    "termVacationStartDate": "2027-01-16",
    "termVacationEndDate": "2027-02-28"
  }
}
```

---

## 📂 项目结构

```
XiQueEr2ICS/
├── api.py                  # FastAPI Web 服务（订阅链接生成）
├── xqe.py                  # 核心逻辑：课表获取 + ICS 生成
├── run_maintain_all.py     # 批量校历同步脚本（推荐）
├── run-web.sh              # Web 服务启动脚本
├── docker-compose.yml      # Docker 部署
├── web/                    # 前端页面
│   ├── index.html          # 主页面
│   ├── subscribe.html      # 订阅设置页
│   └── schools.json        # 学校列表
└── schools/
    └── 12623/              # 学校代码
        ├── config.json     # 学校配置
        ├── maintain.py     # 校历同步脚本
        ├── main.py         # 课表获取模块
        ├── jkingo.des.js   # 加密脚本
        └── school_calendar.json  # 已同步的学期校历
```

---

## 📝 版权与使用说明

Copyright © 2026 [5hUtd0wN](https://blog.hishutdown.cn). All rights reserved.

本项目源代码公开可见，但**未采用任何开源协议**：
- **禁止二次分发**：未经明确许可，不得将本项目代码用于其他项目或进行二次分发。
- **个人使用授权**：项目所有者授权任何人出于**个人学习或使用目的**自行搭建和运行本项目。
- **保留撤回权利**：项目所有者保留随时无条件撤回上述授权的权利。