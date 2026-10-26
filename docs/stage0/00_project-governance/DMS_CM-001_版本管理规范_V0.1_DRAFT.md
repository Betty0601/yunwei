# DMS-CM-001 版本管理规范

| 字段 | 内容 |
|------|------|
| 文档编号 | DMS-CM-001 |
| 文档类型 | 版本管理规范 (Configuration & Version Management) |
| 版本 | V0.1 |
| 状态 | **DRAFT — 草案** |
| 关联文档 | DMS-PM-001（基线体系）、DMS-AI-001（AI 操作）、DMS-WBS-001 |
| 创建日期 | 2026-10-26 |

---

## 1. 三层版本管理架构

本项目采用 **Git + GitHub + Fusion Team Hub** 三层管理架构，分别管理文本/代码文件与 Fusion 原生 CAD 文件：

| 层级 | 平台 | 管理对象 | 版本粒度 | 关键能力 |
|------|------|----------|----------|----------|
| **L1 Git** | Git + GitHub | Markdown 文档、脚本、Python 代码、配置文件 | Commit / Tag | 分布式版本历史、分支合并 |
| **L2 GitHub** | GitHub Issues/PRs | 任务管理、变更请求、代码评审 | Issue / PR | 关联追踪、审核流程 |
| **L3 Fusion** | Fusion Team Hub | .f3d/.f3a Fusion 原生 CAD 文件 | 数据管理版本 | 参数化历史、装配快照、Release |

### 1.1 管理范围矩阵

| 文件类型 | Git | GitHub | Fusion | 说明 |
|----------|-----|--------|--------|------|
| Markdown 文档 (.md) | ✅ | ✅ | ❌ | 全 Git 管理 |
| Python 脚本 (.py) | ✅ | ✅ | ❌ | 全 Git 管理 |
| Fusion 导出文件 (.step/.iges/.dxf) | ✅ | ✅ | ❌ | 只读归档，不用于参数化编辑 |
| Fusion 工程图导出 (.pdf/.dwg) | ✅ | ✅ | ❌ | 只读归档 |
| Fusion 原生模型 (.f3d/.f3a) | ❌ | ❌ | ✅ | 只能在 Fusion 内操作 |
| Fusion 数据管理快照 | ❌ | ❌ | ✅ | Team Hub Release |

---

## 2. 文件命名规则

### 2.1 通用命名格式

```
DMS_{类型缩写}_{主题}_{编号}_V{版本}_{状态}.{扩展名}
```

| 字段 | 取值示例 | 说明 |
|------|----------|------|
| DMS | 固定前缀 | 项目代号 |
| 类型缩写 | CH / PR / PM / WBS / AI / CM / SG / RSK / DEC / SOW / RTM / PRS / FMEA 等 | 见类型缩写表 |
| 主题 | 中文或英文 | 简明描述文档主题 |
| 编号 | XXX | 三位数字 |
| V{版本} | V0.1 / V1.0 / V2.3 | 主版本.次版本 |
| 状态 | DRAFT / REVIEWED / APPROVED / OBSOLETE | 状态标记 |
| 扩展名 | .md / .py / .json | 文件类型 |

### 2.2 Fusion CAD 文件命名

```
{组件类型}_{功能描述}_{版本}_{日期}.f3d
```

| 组件类型前缀 | 说明 |
|--------------|------|
| ASM | 顶层装配体 |
| SUB | 子装配体 |
| PRT | 零件 |
| STD | 标准件 |
| PCB | PCB 板框/结构件 |

**示例**：`ASM_DMS-V1_TopAssembly_v0.1_20261026.f3a`

### 2.3 Fusion Team Hub 项目命名

```
DMS-V{主版本}-{简称}
```

**示例**：`DMS-V1-TopLevel`、`DMS-V1-Housing`、`DMS-V1-DriveAssembly`

---

## 3. Git 分支策略

### 3.1 分支类型

| 分支类型 | 命名格式 | 用途 | 生命周期 |
|----------|----------|------|----------|
| **main** | `main` | 主干，存放已评审/冻结的稳定版本 | 永久 |
| **develop** | `develop` | 集成分支，存放正在开发的汇总版本 | 永久 |
| **feature** | `feature/{wbs-number}-{brief}` | 单个工作包的开发 | 短期 → 合并后删除 |
| **release** | `release/v{version}` | 发布准备分支（冻结 bugfix） | 短期 → 合并后删除 |
| **hotfix** | `hotfix/{issue-id}-{brief}` | 紧急修复 | 极短期 → 合并后删除 |

### 3.2 分支工作流

```
main ←────────── merge (release) ────────── release/v1.0
  ↑                                          ↑
  │ 基线 tag                                 │
  │ BL-{N}                                   │ 冻结开发，仅修 bug
  │                                          │
develop ←──── merge PR ──── feature/5.0.2-bearing
  ↑         ↑                       ↑
  │         │ PR Review             │ 开发完成
  │         │                       │
  └───────── PR ───────── feature/2.0.4-prs
              ↑
              │ PR Review + AI-E 审核
```

### 3.3 合并规则

| 合并类型 | 必要条件 | 操作 |
|----------|----------|------|
| feature → develop | 至少 1 名 AI 角色 Review + AI-E 审核通过 | Squash merge |
| develop → release | WBS 工作包 100% 完成、测试通过 | Normal merge + tag |
| release → main | 阶段门评审通过、发起人审批 | Merge commit + 基线 tag |
| hotfix → main + develop | 发起人紧急批准 | Cherry-pick 到两个分支 |

### 3.4 Commit Message 规范

```
[类型][WBS-{编号}] 简短描述

详细说明（可选）

关联: TASK-{NNN}, DEC-{NNN}
```

| 类型 | 说明 |
|------|------|
| docs | 文档更新 |
| feat | 新功能/新设计 |
| fix | 修复 |
| refactor | 重构（无功能变化） |
| test | 测试相关 |
| chore | 构建/工具/配置 |
| cad | CAD 相关（导出文件） |

---

## 4. Fusion 原生 CAD 版本管理

### 4.1 Team Hub 工作流

Fusion 360 使用 Team Hub 进行原生 CAD 文件的版本管理，与 Git 管理的文本文件并行：

```
┌─────────────────────────────────────────────────┐
│          Fusion 360 Team Hub                     │
│                                                   │
│  Draft State  ── 发布为 ──→  Released State       │
│  (草稿/进行中)                 (冻结/只读)         │
│                                                   │
│  Draft State:                                     │
│  - 多人可编辑 (Co-Edit)                           │
│  - 可保存多个历史版本                              │
│  - 支持 Parametric History 回退                    │
│                                                   │
│  Released State:                                  │
│  - 冻结版本，不可编辑                              │
│  - 生成 PDF/DXF 快照                               │
│  - 可创建下一个 Draft 版本                         │
│  - 与 Git 基线 tag 同步                            │
└─────────────────────────────────────────────────┘
```

### 4.2 Fusion 版本与 Git 基线的同步

**关键规则：Fusion 发布版本必须与 Git 基线 tag 一一对应**

| 同步操作 | 触发条件 | 执行 |
|----------|----------|------|
| Fusion Release → Git tag | 阶段门冻结基线时 | AI-D 执行 Fusion Release → AI-A 在 Git 打对应 tag |
| Git tag → Fusion 版本号 | Git 基线 tag 创建后 | AI-D 更新 Fusion 文件属性中的版本字段 |
| 双轨一致性检查 | 每次阶段门 | AI-E 检查 Git tag 与 Fusion Release 是否匹配 |

### 4.3 Fusion CAD 文件的 Git 存档规则

由于 Fusion 原生格式 (.f3d/.f3a) **不适合直接存入 Git**（二进制文件、体积大、无法 diff），采用以下策略：

| 内容 | Git 存储方式 | Fusion 存储方式 |
|------|--------------|------------------|
| 模型结构参数 | Markdown 参数清单 (.md) | .f3d 原生文件 |
| 版本快照 | STEP 文件 (.step) | Team Hub Release |
| 工程图导出 | PDF/DWG (.pdf/.dwg) | Fusion 工程图定义 |
| 变更日志 | Git commit message | Fusion 数据管理版本说明 |
| 模型预览 | PNG 缩略图 | Fusion 内 3D 预览 |

### 4.4 Fusion Team Hub 权限

| 角色 | Team Hub 权限 | 说明 |
|------|---------------|------|
| 发起人 | 查看 + Release 审批 | 只读操作 |
| AI-A | 查看 | 只读，用于状态确认 |
| AI-B | 查看 | 只读，用于文档截图 |
| AI-C | 查看 + 仿真导出 | 用于力学仿真 |
| AI-D | 完全控制 | 唯一可编辑原生 CAD 的角色 |
| AI-E | 查看 | 只读，用于独立审核 |

---

## 5. 配置项标识与追踪

### 5.1 配置项 (CI) 定义

配置项是项目中需要独立版本管理和变更控制的最小单元：

| 配置项类型 | 示例 | 存放位置 |
|------------|------|----------|
| 治理文档 | CH-001 项目章程 | `docs/stage0/00_project-governance/` |
| 产品需求 | PRS v1.0 | `docs/stage2/requirements/` |
| 系统设计 | 系统架构图 | `docs/stage2/system/` |
| CAD 装配体 | ASM_DMS-V1_TopAssembly | Fusion Team Hub |
| CAD 零件 | PRT_DMS-V1_MotorMount | Fusion Team Hub |
| Python 工具 | fusion_tools/primitives.py | `src/fusion_tools/` |
| 验证报告 | VR-018 温升测试 | `docs/stage5/verification/` |

### 5.2 配置项状态

| 状态 | 含义 | 可否变更 |
|------|------|----------|
| 🔵 Draft | 草稿，进行中 | 自由编辑 |
| 🟡 Reviewed | 已 AI-E 审核通过 | 需修改 → 回到 Draft |
| ✅ Approved | 已评审/批准，纳入基线 | 变更需走 CCB |
| ❌ Obsolete | 废弃，被新版本替代 | 只读，不删除 |

### 5.3 配置项追踪矩阵

每次基线冻结时，必须生成完整的配置项追踪矩阵：

```markdown
| CI 编号 | 名称 | 位置 | 版本 | 状态 | 基线 | Fusion Release | Git Tag |
|---------|------|------|------|------|------|----------------|---------|
| CI-001 | 项目章程 | docs/... | V0.1 | Draft | - | - | - |
| CI-015 | 顶装配体 | Fusion Hub | v1.0 | Approved | BL-3 | Release #42 | BL-3 |
```

---

## 6. 变更控制流程（简述）

详细变更流程见 DMS-PM-001 第 6 节，此处补充版本管理相关操作步骤：

```
变更申请 (CR) → 影响分析 → CCB 审批
    ↓
1. 创建 feature 分支 → 执行变更
2. Fusion 内修改 → 创建新 Draft 版本
3. AI-E 审核 → 修改通过
4. 合并到 develop → Fusion 保存快照
5. 阶段门冻结 → 打 Git tag + Fusion Release
6. 记录到变更日志 decisions/
```

---

## 7. 版本冲突处理

### 7.1 Git 冲突

| 场景 | 处理 |
|------|------|
| Markdown 文档冲突 | AI-B 人工合并，优先保留新版本内容 |
| Python 脚本冲突 | AI-D 合并，保留双方有效修改 |
| 同一文件多角色同时编辑 | **禁止**，通过 PR 串行化 |

### 7.2 Fusion 冲突

| 场景 | 处理 |
|------|------|
| 同一组件多 AI-D 并行编辑 | **禁止**，Co-Edit 仅单人或串行 |
| 参数被错误修改 | 使用 Fusion 历史版本回退 |
| Release 被覆盖 | **禁止**，Release 状态不可编辑 |

### 7.3 Git-Fusion 脱节

**风险登记：R-017（Git-Fusion 版本脱节）**

| 脱节场景 | 检测方式 | 处理 |
|----------|----------|------|
| Fusion Release 已发布但 Git tag 未打 | AI-E 阶段门检查 | 立即补打 tag |
| Git 已变更但 Fusion 未同步 | AI-E 双轨比对 | AI-D 同步 Fusion |
| Fusion Draft 有未提交的大改动 | AI-E 检查 Fusion 历史 | 评估是否需要走变更流程 |

---

## 8. 备份与归档

### 8.1 备份策略

| 对象 | 频率 | 方式 | 保留 |
|------|------|------|------|
| Git 仓库 | 每次 push 自动 | GitHub 冗余存储 | 永久 |
| Fusion Team Hub | 实时同步 | Autodesk 云端 + 本地导出 | 永久 |
| 里程碑快照 | 每个阶段门 | Git bundle + Fusion 导出 STEP + 归档 | 永久 |
| 变更日志 | 每次变更批准 | decisions/ 目录 | 永久 |

### 8.2 归档要求

项目关闭时，完整归档包包括：

1. Git 仓库完整 bundle
2. Fusion Team Hub 所有 Release 的 STEP 导出
3. 所有 Approved 状态的配置项 PDF 归档
4. 变更日志 decisions/
5. 基线版本清单

---

## 9. 文档版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| V0.1 | 2026-10-26 | AI-A + AI-D | 初始 DRAFT |

---

**本规范确保 Git 文本文件与 Fusion 原生 CAD 的双轨版本一致，是配置管理的核心规则。任何偏离必须记录并批准。**
