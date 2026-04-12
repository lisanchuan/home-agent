# BrowserUse qa-use 学习方案

## 项目概览
- **定位**：AI-Powered E2E Testing Platform
- **官网**：[github.com/browser-use/qa-use](https://github.com/browser-use/qa-use)
- **文档**：[docs.browser-use.com](https://docs.browser-use.com)
- **技术栈**：Next.js + TypeScript + Docker + PostgreSQL + Inngest
- **学习优先级**：⭐⭐⭐⭐

---

## 核心理念

**用自然语言描述测试用例，AI Agent 自动执行验证**

```
用户写测试步骤（自然语言）
    ↓
AI Agent 模拟人类操作浏览器
    ↓
智能验证结果（不只是断言，而是 AI 判断）
    ↓
截图 + 录屏 + 详细报告
```

---

## 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/browser-use/qa-use.git
cd qa-use

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 添加 API Key

# 3. 启动（需要 Docker）
docker compose up
# 访问 http://localhost:3000
```

### 环境要求
- Docker & Docker Compose
- BrowserUse API Key（cloud.browser-use.com）
- Resend API Key（可选，邮件通知）

---

## 核心功能

### 1. 自然语言测试步骤
```
Steps:
1. Go to example.com
2. Click the search button
3. Type "laptop" in the search field
4. Press enter and wait for results

Success Criteria:
The page should show at least 3 laptop search results
```

### 2. AI Agent 执行
- 像人类一样浏览页面
- 智能处理弹窗和对话框
- 适应布局变化和动态内容

### 3. 智能验证
- AI 判断最终页面状态
- 对比实际 vs 预期结果
- 截图 + 录屏记录

### 4. 测试套件管理
- 组织多个测试用例
- 并行运行
- 定时执行（每小时/每天）

### 5. 邮件通知
- 测试失败自动发邮件
- 可选 Resend API 集成

---

## 架构解析

### 技术栈
```
Next.js 14 (App Router)
TypeScript
PostgreSQL (数据存储)
Inngest (后台任务)
BrowserUse SDK (浏览器自动化)
Resend (邮件)
Docker Compose
```

### 关键文件
```
qa-use/
├── app/                    # Next.js App Router
│   ├── page.tsx           # 首页
│   ├── suites/            # 测试套件页面
│   └── runs/              # 运行记录
├── components/
│   ├── editor/            # 测试编辑器
│   └── dashboard/         # 仪表盘
├── lib/
│   ├── browseruse.ts      # BrowserUse 集成
│   └── inngest.ts         # 后台任务
├── docker-compose.yml
└── .env.example
```

---

## 学习路径

### 第一阶段：跑起来（1-2 小时）

1. 克隆仓库 + 启动 Docker
2. 申请 BrowserUse API Key
3. 跑通第一个测试用例
4. 理解测试编辑器 UI

**验证目标：** 能创建并运行一个简单测试

### 第二阶段：理解原理（2-3 小时）

1. 读 qa-use 源码，理解测试执行流程
2. 看 BrowserUse SDK 文档，理解 Agent 如何控制浏览器
3. 理解 Inngest 后台任务调度
4. 研究 Success Criteria 的 AI 验证逻辑

**验证目标：** 能画出演示架构图

### 第三阶段：实战应用（3-4 小时）

1. 为自己的 Web 项目写测试用例
2. 搭建本地测试环境
3. 配置定时执行
4. 集成邮件通知

**验证目标：** 测试套件能稳定运行

---

## 实战练习题目

### 练习 1：登录流程测试
```
Steps:
1. Go to [your app]/login
2. Type "test@example.com" in email field
3. Type "password123" in password field
4. Click login button
5. Wait for redirect

Success Criteria:
The page should contain "Welcome" or redirect to /dashboard
```

### 练习 2：表单提交测试
```
Steps:
1. Go to [your app]/form
2. Fill in name field with "John Doe"
3. Select "Developer" from role dropdown
4. Check the terms checkbox
5. Click submit button

Success Criteria:
The page should show success message "Form submitted"
```

### 练习 3：多步骤向导测试
```
Steps:
1. Go to [your app]/wizard
2. Step 1: Fill "Company Name" and click Next
3. Step 2: Select 3 features and click Next
4. Step 3: Review and click Complete

Success Criteria:
The page should show confirmation with company name
```

---

## 与 OpenClaw 的结合点

### 1. Cron 触发测试
- OpenClaw Cron Job 每天定时触发 qa-use 测试
- 测试失败自动发邮件/微信通知

### 2. 自然语言查询测试结果
- 用自然语言问贾维斯："昨天跑的登录测试结果如何？"
- 贾维斯查询 qa-use API 返回结果

### 3. 报警自动化
- 测试失败 → 贾维斯收到通知 → 自动分析原因 → 给出修复建议

---

## 参考资源

| 资源               | 链接                                    |
| ---------------- | ------------------------------------- |
| qa-use 仓库        | https://github.com/browser-use/qa-use |
| BrowserUse 文档    | https://docs.browser-use.com          |
| BrowserUse Cloud | https://cloud.browser-use.com         |
| Inngest 文档       | https://inngest.com/docs              |
| Resend 文档        | https://resend.com/docs               |

---

## 下一步

1. **克隆 qa-use 到本地**
2. **申请 BrowserUse API Key**
3. **启动 Docker 环境**
4. **跑通第一个测试**

需要我帮你准备哪个环节的详细步骤？
