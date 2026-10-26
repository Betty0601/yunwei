# TEST_PLAN.md — 测试计划

**任务 ID**: BASELINE-001  
**创建日期**: 2026-10-26  
**状态**: 执行中

---

## 测试矩阵

| # | 测试名称 | Gate | 类型 | 优先级 | 前置条件 |
|---|----------|------|------|--------|----------|
| T1 | 文档创建与读取 | G2 | CAD-基础 | High | Fusion 运行 |
| T2 | 用户参数体系 | G2 | CAD-参数化 | High | T1 通过 |
| T3 | 组件层级创建 | G2 | CAD-组件 | High | T2 通过 |
| T4 | 草图与特征质量 | G2 | CAD-几何 | High | T3 通过 |
| T5 | 参数修改与传播 | G2 | CAD-参数化 | High | T3 通过 |
| T6 | 装配关节创建 | G3 | CAD-装配 | High | T3 通过 |
| T7 | 装配关系检查 | G3 | CAD-装配 | High | T6 通过 |
| T8 | 干涉检查 | G3 | CAD-装配 | Medium | T7 通过 |
| T9 | saveAs → Team Hub | G4 | CAD-保存 | Critical | T7 通过 |
| T10 | .f3d 归档导出 | G4 | CAD-保存 | Critical | T9 通过 |
| T11 | 文档恢复验证 | G4 | CAD-保存 | Critical | T9+T10 通过 |
| T12 | STEP 导出 | G5 | CAD-导出 | High | T7 通过 |
| T13 | STEP 几何验证 | G5 | CAD-导出 | High | T12 通过 |
| T14 | STL 导出 | G5 | CAD-导出 | High | T7 通过 |
| T15 | STL 网格验证 | G5 | CAD-导出 | Medium | T14 通过 |
| T16 | 异常输入处理 | G5 | 异常 | Medium | T1-T15 通过 |
| T17 | 幂等性与重复执行 | G5 | 异常 | Medium | T1-T15 通过 |
| T18 | Git 分支管理 | G6 | Git | High | — |
| T19 | 远程同步验证 | G6 | Git | High | T18 通过 |
| T20 | 敏感信息检查 | G6 | 安全 | High | — |
| T21 | 独立质量审核 | G7 | 审核 | Critical | T1-T20 执行完 |
| T22 | 回归测试 | G7 | 测试 | High | T1-T20 执行完 |
| T23 | 最终验收 | G8 | 验收 | Critical | T21+T22 通过 |

---

## T1-T5：基础与参数化

### T1 文档创建与读取
- **步骤**: (1) 调用 Fusion 创建/复用文档 (2) 读取 document.name, document.isSaved, design 存在性
- **预期**: 文档状态正确，design 对象可访问
- **证据**: API 返回值

### T2 用户参数体系
- **步骤**: (1) 创建 13 个 UserParameter（见 PARAMETER_MANIFEST.json） (2) 验证每个参数的 name/value/unit
- **预期**: 全部参数创建成功，值和单位正确
- **证据**: API 查询 design.userParameters

### T3 组件层级创建
- **步骤**: (1) 创建根组件 TestAssembly (2) 创建 8 个子组件 C1-C8 (3) 建立层级关系
- **预期**: design.rootComponent.occurrences 有 8 个子组件
- **证据**: API 查询 component.occurrences

### T4 草图与特征质量
- **步骤**: (1) 每个组件创建草图 + 特征 (2) 检查草图约束 (3) 检查特征历史
- **预期**: 无失败特征，依赖关系清晰
- **证据**: API 查询 feature.timeline

### T5 参数修改与传播
- **步骤**: (1) 修改 `test_base_length` 从 200 → 250 (2) 等待 Fusion 更新 (3) 重新查询 C1 几何
- **预期**: C1 长度方向几何变化 50mm，其他组件不变
- **证据**: 修改前后的几何属性对比

---

## T6-T8：装配

### T6 装配关节创建
- **步骤**: (1) C3 轴 ↔ C2 轴承座: 旋转关节 (2) C5 滑块 ↔ C6 支架: 滑块关节 (3) C7 接口 ↔ C3: 固定关节
- **预期**: Joint 对象创建，关节类型正确
- **证据**: API 查询 joints 集合

### T7 装配关系检查
- **步骤**: (1) 读取 joint.geometry (2) 验证组件位置 (3) 移动 C3 检查 C7 是否跟随
- **预期**: 运动关系符合设定
- **证据**: API 查询组件变换

### T8 干涉检查
- **步骤**: (1) 调用 interference detection API (2) 检查所有组件间干涉
- **预期**: 无关键干涉（C1-C8 设计间隙合理）
- **证据**: API 查询结果

---

## T9-T11：保存与恢复（Critical）

### T9 saveAs → Team Hub
- **步骤**: (1) 调用 document.saveAs(name, folder) (2) 等待云端同步 (3) 检查 document.isSaved
- **预期**: saveAs 返回成功，isSaved = True
- **证据**: API 返回值 + isSaved 状态

### T10 .f3d 归档导出
- **步骤**: (1) 使用 DataFile + createFusionArchiveExportOptions (2) 导出到本地路径
- **预期**: .f3d 文件存在，大小合理 (通常 200-500KB)
- **证据**: 文件系统 + size

### T11 文档恢复验证
- **步骤**: (1) 关闭当前文档 (2) 重新打开 Team Hub 中的文档 (3) 验证 C1-C8 组件存在且参数正确
- **预期**: 所有组件/参数/特征恢复
- **证据**: 重新读取 API 返回值

---

## T12-T15：导出

### T12-T13 STEP
- 步骤: exportManager → createSTEPExportOptions → execute
- 预期: .step 文件 > 1KB，ISO-10303-21 格式，重新导入后几何一致

### T14-T15 STL
- 步骤: exportManager → createSTLExportOptions → execute
- 预期: .stl 文件 > 100B，三角面数量合理，非空网格

---

## T16-T17：异常与幂等

### T16 异常输入
- 不存在的参数名 → 明确错误
- 不合法尺寸值 (负数) → 拒绝
- 不存在的组件名 → 拒绝
- 无效导出路径 → 拒绝

### T17 幂等性
- 重复执行参数创建 → 检测已存在，跳过
- 重复执行组件创建 → 同名检测，跳过
- 安全策略：每个脚本支持 --force 覆盖

---

## T18-T20：Git/GitHub

### T18 分支
- test/fusion360-baseline 已创建，基于 main

### T19 远程同步
- 所有测试脚本 + 报告推送到远程，commit ID 一致

### T20 安全
- .gitignore 覆盖 .env, *.f3d, *.key, *.pem
- 仓库中无明文密钥
