# PROJECT_SPEC.md — Fusion 360 AI 工程自动化基准验证项目

**项目名称**: Fusion360_AI_Engineering_Baseline  
**中文名称**: Fusion 360 AI 工程自动化基准验证项目  
**任务 ID**: BASELINE-001  
**日期**: 2026-10-26  
**用途**: 本项目是 AI × GitHub × Fusion 360 协作链路的独立基准验证。**不是**正式深层肌肉刺激仪产品设计。

---

## 1. 设计目标

构建一个具有机械复杂度的参数化测试装配体，覆盖：

1. 基础组件创建（基座、轴、滑块、支架、外壳）
2. 用户参数体系（全参数驱动）
3. 组件层级与命名规范
4. 草图约束与特征依赖
5. 装配关系（关节/约束）
6. 文档保存、恢复与归档导出
7. STEP/STL 几何导出与验证
8. Git/GitHub 版本管理

## 2. 组件清单（TEST_ONLY）

| # | 组件 | Fusion 内部名 | 功能 | 测试目标 |
|---|------|---------------|------|----------|
| C1 | 基座 (Base) | `TestBase` | 安装基准 | 参数化尺寸、孔特征 |
| C2 | 支撑轴承座 | `TestBearingSupport` | 轴承安装 | 同轴约束 |
| C3 | 测试轴 | `TestShaft` | 旋转运动 | 旋转关节 |
| C4 | 偏心轮 | `TestEccentricWheel` | 偏心几何 | 偏心参数 |
| C5 | 直线滑块 | `TestSlider` | 直线运动 | 滑块关节 |
| C6 | 导向支架 | `TestGuideBracket` | 滑轨支撑 | 导向约束 |
| C7 | 测试端部接口 | `TestEndInterface` | 可替换端部 | 接口约束 |
| C8 | 外壳/防护罩 | `TestHousing` | 保护罩 | 外壳几何 |
| A1 | 装配总成 | `TestAssembly` | 全部组件装配 | 层级 + 关节 |

## 3. 参数体系（全部 TEST_ONLY）

| 参数名 | 单位 | 测试值 | 说明 | 驱动组件 |
|--------|------|--------|------|----------|
| `test_base_length` | mm | 200 | 基座长度 | C1 |
| `test_base_width` | mm | 150 | 基座宽度 | C1 |
| `test_base_height` | mm | 25 | 基座高度 | C1 |
| `test_bearing_od` | mm | 62 | 轴承外径 | C2 |
| `test_bearing_id` | mm | 35 | 轴承内径 | C2 |
| `test_shaft_diameter` | mm | 20 | 测试轴径 | C3 |
| `test_shaft_length` | mm | 120 | 测试轴长 | C3 |
| `test_eccentric_offset` | mm | 5 | 偏心量 | C4 |
| `test_slider_width` | mm | 40 | 滑块宽度 | C5 |
| `test_slider_height` | mm | 30 | 滑块高度 | C5 |
| `test_hole_diameter` | mm | 8 | 安装孔径 | C1, C6 |
| `test_clearance` | mm | 0.5 | 配合间隙 | C5, C6 |
| `test_part_spacing` | mm | 10 | 零件间距 | A1 |

## 4. 执行顺序

```
Gate 0 ✅: 环境审计
Gate 1   : 工作区建立 ← 当前
Gate 2   : C1基座 → C3轴 → C2轴承座 → C5滑块 → C6支架 → C7接口 → C8外壳 → C4偏心轮
Gate 3   : 装配关系 (Joint)
Gate 4   : saveAs → Team Hub → .f3d 导出 → 恢复验证
Gate 5   : STEP/STL 导出 + 几何验证
Gate 6   : Git 分支 + GitHub 推送
Gate 7   : 独立质量审核 + 回归测试
Gate 8   : 最终验收报告
```

## 5. 交付物

### Fusion 360 资产
- ✅ 真实 Fusion 设计文档（Team Hub saveAs）
- ✅ 参数化组件层级
- ✅ 装配关节
- ✅ .f3d 归档文件
- ✅ STEP 文件
- ✅ STL 文件

### GitHub 资产
- ✅ 测试脚本
- ✅ 参数清单 JSON
- ✅ 组件清单 JSON
- ✅ 测试计划 / 验收标准
- ✅ 执行日志
- ✅ 错误记录
- ✅ 最终验收报告
