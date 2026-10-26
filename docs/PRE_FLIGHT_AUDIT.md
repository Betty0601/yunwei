# PRE_FLIGHT_AUDIT.md — 环境预检报告

**任务 ID**: BASELINE-001  
**审计时间**: 2026-10-26  
**审计状态**: ✅ 部分通过 — 主链路可用，saveAs/Joint 待深度验证

---

## 0. 总览

| 类别 | 检查项数 | 通过 | 阻塞 | 状态 |
|------|---------|------|------|------|
| 系统 | 7 | 7 | 0 | ✅ 通过 |
| Git/GitHub | 6 | 6 | 0 | ✅ 通过 |
| Fusion 360 | 12 | 10 | 2 | ⚠️ 部分通过 |
| API 能力 | 14 | 14 | 0 | ✅ 已确认存在 |

---

## 1. 系统环境

| # | 项目 | 实际值 | 状态 |
|---|------|--------|------|
| 1.1 | 操作系统 | macOS 26.5.1 (Build 25F80) | ✅ |
| 1.2 | CPU 架构 | arm64 (Apple Silicon) | ✅ |
| 1.3 | Python | 3.9.6 (/usr/bin/python3) | ✅ |
| 1.4 | Git | 2.55.0 | ✅ |
| 1.5 | GitHub CLI | gh v2.103.2 | ✅ |
| 1.6 | Homebrew | 7.0.10 | ✅ |
| 1.7 | uv (Python 管理) | 0.13.5 (~/.local/bin/uv) | ✅ |

---

## 2. Git 与 GitHub

| # | 项目 | 实际值 | 状态 | 证据 |
|---|------|--------|------|------|
| 2.1 | 仓库 URL | `https://github.com/Betty0601/yunwei.git` | ✅ | remote -v |
| 2.2 | 认证方式 | HTTPS + gh token (gho_...) | ✅ | `gh auth status` |
| 2.3 | SSH Key | 0 个公钥 (~/.ssh/*.pub 不存在) | ✅ | 无 SSH 需求 |
| 2.4 | credential helper | `osxkeychain` 已配置 | ✅ | git config |
| 2.5 | 远程同步 | main HEAD 本地 === 远程 | ✅ | commit 7060400 |
| 2.6 | 测试分支 | test/fusion360-baseline 已推送到远程 | ✅ | 2026-10-26 push |

**⚠️ 注意**: osxkeychain 需在真实 Terminal 首次 push 时点 "Always Allow"。沙箱环境无此限制。

---

## 3. Fusion 360

| # | 项目 | 实际值 | 状态 | 证据 |
|---|------|--------|------|------|
| 3.1 | 版本 | 2706.1.14 (2026 June Update) | ✅ | MCP licensing |
| 3.2 | 许可证 | Student Premium + Manufacturing Extension | ✅ | MCP licensing |
| 3.3 | MCP 端点 | `http://127.0.0.1:27182/mcp` | ✅ | Streamable HTTP |
| 3.4 | 协议版本 | 2024-11-05 | ✅ | initialize response |
| 3.5 | 可用 MCP 工具数 | 4 | ✅ | tools/list |
| 3.6 | 当前打开文档数 | 1 (Untitled) | ✅ | document:operation=open |
| 3.7 | `isSaved` | False (Untitled 从未 saveAs) | ⚠️ | 预期行为 |
| 3.8 | 创建新文档 | ✅ 可行，`_app.documents.add()` | ✅ | primitives.py 已实现 |
| 3.9 | 创草图/特征 | ✅ 可行，已验证 Extrude/Revolve | ✅ | primitives.py |
| 3.10 | STEP 导出 | ✅ 已验证落盘 (30249 bytes) | ✅ | test_export.py |
| 3.11 | STL 导出 | ✅ 已验证落盘 (684 bytes) | ✅ | test_export.py |
| 3.12 | **saveAs → Team Hub** | ⚠️ API 存在，未端到端验证 | 🚧 | `saveAs` 函数已在 API 文档确认 |

### MCP 工具清单

| 工具名 | 用途 | 参数 | 已测试 |
|--------|------|------|--------|
| `fusion_mcp_read` | 查询几何/API/文档/截图 | queryType + args | ✅ |
| `fusion_mcp_execute` | 执行 Fusion Python 脚本 | code | ✅ |
| `fusion_mcp_update` | CRUD 更新 | — | ❌ 未用 |
| `fusion_mcp_electronics_read` | PCB 查询 | — | ❌ 未用 |

---

## 4. Fusion API 能力确认

通过 `apiDocumentation` 查询 (apiCategory=class/member)，确认以下 API 存在：

| 能力 | 类/成员 | 确认 | 备注 |
|------|--------|------|------|
| 组件层级 | `Component`, `DataComponent` | ✅ | 可创建组件层级 |
| 装配关节 | `Joint`, `JointDirections`, `JointGeometryTypes` | ✅ | 旋转/直线关节 |
| 用户参数 | `UserParameter`, `design.userParameters` | ✅ | 可驱动特征 |
| 参数导入导出 | `exportUserParameters()`, `importUserParameters()` | ✅ | CSV 格式 |
| 文档保存 | `document.saveAs()`, `document.save()` | ✅ | saveAs 首次保存 |
| Team Hub 云 | `DataFile`, `DataFolder` | ✅ | Fusion Team Hub 对象 |
| 归档导出 | `createFusionArchiveExportOptions()` | ✅ | .f3d / .f3z 格式 |
| 归档导入 | `createFusionArchiveImportOptions()` | ✅ | 恢复原生参数化设计 |
| 草图 | `Sketch` | ✅ | 2D 草图 |
| 拉伸 | `ExtrudeFeatureInput`, `ExtrudeFeatures` | ✅ | 已有 |
| STEP 导出 | `createSTEPExportOptions()` | ✅ | 已有 |
| SAT 导出 | `createSATExportOptions()` | ✅ | Parasolid 格式 |
| IGES 导出 | `createIGESExportOptions()` | ✅ | — |
| 参数对象 | `Parameter`, `getLengthAtParameter()` | ✅ | 特征参数查询 |

**⚠️ 未确认能力**:
- `Joint.createInput()` — 关节创建的完整调用签名需实测
- `saveAs` 接受的 `DataFolder` 参数类型 — 需实测 Fusion Team Hub 云端文件夹的选择方式
- `.f3d` 归档导出的完整流程 — 需实测 exportManager 接口

---

## 5. 已知限制与阻塞

| # | 限制 | 影响 Gate | 缓解 | 状态 |
|---|------|----------|------|------|
| B1 | Untitled 文档未 saveAs 时 `isSaved=False` | G4 保存恢复 | saveAs 到 Team Hub 后可解决 | 🚧 待验证 |
| B2 | osxkeychain 首次授权需真实 Terminal | G6 git push | 已推送 test/fusion360-baseline 成功 | ✅ 已解决 |
| B3 | GitHub Actions CI 无 Fusion 360 | G7 回归测试 | CI 跑 mock + lint，live 测试本地执行 | ✅ 已标记 |
| B4 | SSH Key 不存在 | — | HTTPS + osxkeychain 已工作 | ℹ️ 信息 |
| B5 | Fusion 2026+ API 变更（DistanceExtentDefinition 等） | G2-G5 | primitives.py 已适配 | ✅ 已解决 |

---

## 6. 审计结论

**状态**: 🟡 **有条件通过**

- ✅ Gate 0（环境权限检查）通过 — 所有系统级工具就位，Git/GitHub/Fusion MCP 可连接
- ✅ API 能力面覆盖完整 — saveAs, Component, Joint, UserParameter, 归档导出均已在 API 文档确认
- 🚧 Gate 4（保存恢复）仍需端到端实测 saveAs → DataFolder → 恢复完整流程
- 🚧 Gate 3（装配关系）需实测 Joint API 调用签名

**下一步**: 推进 Gate 1（工作区）→ Gate 2（参数化装配体），同步实测 saveAs 和 Joint。
