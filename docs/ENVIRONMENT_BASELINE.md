# 环境基线报告 (ENVIRONMENT BASELINE)

**检查时间**: 2026-10-26
**项目**: yunwei — AI + Git + Fusion 360 自动化工作流
**检查方式**: 真实命令执行 + Fusion MCP 查询

---

## 1. macOS 系统

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| 操作系统 | macOS 26.5.1 | `sw_vers` | ✅ |
| CPU 架构 | arm64 (Apple Silicon) | `uname -m` | ✅ |
| 根分区容量 | 1.8Ti 总量 / 1.7Ti 可用 | `df -h /` | ✅ 充足 |

## 2. Python

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| 系统 Python | 3.9.6 | `/usr/bin/python3 --version` | ⚠️ 偏旧 |
| Fusion 内置 Python | 3.14 | Fusion.app/Frameworks/Python.framework | ✅ 新 |
| uv 包管理器 | 0.13.5 (aarch64-apple-darwin) | `~/.local/bin/uv --version` | ✅ |
| Node.js | 已安装 (~/.local/bin/node) | 磁盘发现 | ✅ |
| PyGithub | 2.9.1 | `pip3 list` | ✅ |
| requests | 2.32.5 | `pip3 list` | ✅ |

## 3. Git / GitHub CLI

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| Git 版本 | 2.55.0 | `git --version` | ✅ |
| Git user | Betty0601 / eastyouq@gmail.com | `git config` | ✅ |
| GitHub CLI | 2.103.2 (2026-10-23) | `gh --version` | ✅ |
| gh 登录账号 | Betty0601 | `gh auth status` | ✅ |
| 认证方式 | HTTPS + Token (keyring) | `gh auth status` | ✅ |
| Token scopes | gist, read:org, repo, workflow | `gh auth status` | ✅ 覆盖 |
| SSH keys | 不存在 (~/.ssh/ 目录缺失) | `ls -la ~/.ssh/` | ⚠️ 未配置（用 HTTPS 可工作） |

## 4. 远程仓库

| 项目 | 值 | 状态 |
|---|---|---|
| 仓库 URL | https://github.com/Betty0601/yunwei.git | ✅ |
| 可见性 | PUBLIC | ✅ |
| 默认分支 | main | ✅ |
| 已推送分支 | main, develop | ✅ |
| HTTPS 推送 | 已验证 OK | ✅ |
| CI workflow | 已触发（首次 failure — 缺 requirements.txt） | ⚠️ 待修复后重跑 |

## 5. Fusion 360

| 项目 | 值 | 来源 | 状态 |
|---|---|---|---|
| 产品 | Autodesk Fusion | `ps aux` | ✅ 运行中 |
| 版本 | 2706.1.14 | Fusion360_2706.1.14_*.xml | ✅ |
| 安装路径 | ~/Library/Application Support/Autodesk/webdeploy/production/... | 磁盘发现 | ✅ |
| Python 版本 | 3.14 | Fusion 内置 | ✅ |
| Fusion MCP Server | localhost:27182 | `lsof -i :27182` | ✅ 监听中 |
| 许可证类型 | Student Premium | MCP `fusion_mcp_read queryType=licensing` | ✅ |
| Manufacturing 扩展 | 已激活 | MCP licensing 返回 | ✅ |
| 当前打开文档 | 0 | MCP `document operation=open` | ✅ |
| 可用工具数量 | 4 (fusion_mcp_read/execute/update/electronics_read) | MCP `tools/list` | ✅ |

## 6. Fusion API 兼容性 (2026 新版本)

**重要**: Fusion 2026 年更新改变了部分拉伸 API 签名！旧代码会报错。
我们的 primitives 库已适配新 API。

| 旧 API (已废弃) | 新 API (2026+) | 影响 |
|---|---|---|
| `extInput.setOneSideExtent(value, dir)` | `DistanceExtentDefinition.create(val)` → `setOneSideExtent(extent, dir)` | 中等 |
| `AllExtentDefinition.create()` | `ThroughAllExtentDefinition.create()` | 低 |
| `doc.products.itemByIndex(0)` | `doc.products.item(0)` | 低 |

## 7. Homebrew

| 项目 | 值 | 状态 |
|---|---|---|
| Homebrew 版本 | 7.0.10 | ✅ |
| 已安装 formulae | 46 个 | ✅ |

## 8. 项目文件清单

```
yunwei/
├── .github/workflows/ci.yml          # GitHub Actions CI
├── .gitignore                         # 敏感文件排除
├── requirements.txt                   # Python 依赖清单
├── docs/                              # 文档目录 (待补充)
├── src/
│   ├── mcp_client/fusion_mcp.py       # Fusion MCP HTTP 客户端 (stdin/HTTP)
│   └── fusion_tools/primitives.py     # CAD 原语生成器 (Cube/Cylinder/Bracket)
├── scripts/
│   ├── quick_start.py                 # 一键体验
│   └── multi_primitive_test.py       # 多原语测试
├── tests/                             # 单元测试 (待补充)
├── configs/                           # 配置目录 (待补充)
├── models/                            # 生成的模型 (.gitkeep)
└── assets/                            # 截图资源 (.gitkeep)
```

## 9. 真实测试证据 (已在本地验证)

| 测试 | 结果 | 命令/方式 |
|---|---|---|
| MCP 连接握手 | ✅ | `curl -X POST http://127.0.0.1:27182/mcp` |
| 查询许可证 | ✅ Student Premium | `fusion_mcp_read queryType=licensing` |
| API 文档搜索 | ✅ DistanceExtentDefinition | `fusion_mcp_read queryType=apiDocumentation` |
| 创建立方体 10³ | ✅ volume=1000 cm³ | `fusion_mcp_execute featureType=script` |
| 创建立方体 20³ | ✅ volume=8000 cm³ | 同上 |
| 创建立方体 15³ | ✅ volume=3375 cm³ | 同上 |
| 创建圆柱 r=10 h=30 | ✅ volume=9424.78 cm³ | 同上 |
| 创建带孔支架 | ✅ 带 4 通孔 | 同上 |
| Undo 撤销 | ✅ | `fusion_mcp_update featureType=undo` |
| 远程仓库创建 | ✅ | `gh repo create yunwei --source=$(pwd) --push` |
| develop 分支推送 | ✅ | `git push -u origin develop` |
| 文档复用（避免多余 Untitled） | ✅ 执行前后都是 1 个文档 | primitives.py FUSION_HEADER |
| **STEP 导出** | ✅ ISO-10303-21, 30KB/20³cube | `scripts/test_export.py` |
| **STL 导出** | ✅ Binary STLB, 684B/20³cube | 同上 |
| **导出后落盘验证** | ✅ `ls -la models/test_cube.{step,stl}` | 文件系统确认 |
| document save | ⚠️ saveAs 需 Fusion Team 云端权限 | `doc.isSaved` 返回 False（正常，非 bug） |
| 装配体 | ❌ 未实现 | 需研究 Joints/Components API |

## 10. 已知风险与限制

| # | 风险 | 影响 | 缓解 |
|---|---|---|---|
| 1 | 系统 Python 3.9.6 偏旧 | 少量新语法不可用 | 可用 uv 装 Python 3.11+ |
| 2 | 无 SSH keys | 只能 HTTPS 推送（Token 有效期） | 可手动生成 SSH key |
| 3 | Fusion MCP 每次 script 调用是独立进程 | 不能在多次调用间共享变量 | 通过 design.components 持久化 |
| 4 | CI 无法运行真实 Fusion 测试 | CI 只能 Mock | 本地跑 Live 测试 |
| 5 | GitHub CLI 网络不稳定 | 部分命令超时 | 重试或用完整路径 |
| 6 | Fusion 2026+ API 变化 | 旧脚本需适配 | MCP apiDocumentation 动态查询 |

## 11. 兼容性依据

- Fusion 360 API 官方文档: https://help.autodesk.com/view/fusion360/ENU/
- Fusion MCP 官方: https://www.autodesk.com/products/fusion-360/blog/build-your-own-fusion-add-ins-with-the-fusion-mcp/
- MCP 协议版本: 2024-11-05 (Streamable HTTP)
- GitHub CLI 官方: https://cli.github.com/

---

## 下一步优先级

1. ✅ 已修复: FUSION_HEADER 复用已有文档（避免多余 Untitled）
2. ✅ 已修复: CI 缺 requirements.txt（已创建 + cache-dependency-path）
3. 🔜 创建 .env.example + 配置加载模块 (阶段 C)
4. 🔜 验证 Fusion document save (阶段 D1)
5. 🔜 实现 STEP/STL 导出 (阶段 D2)
6. 🔜 重跑 CI 验证绿
7. 🔜 提交 ENVIRONMENT_BASELINE.md + 其他改动 → 推送 → 确认 CI 绿
