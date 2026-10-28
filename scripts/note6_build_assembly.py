#!/usr/bin/env python3
"""
NOTE6 总装分解图 (draft v1.0)
基于 docs/NOTE6_reverse_engineering_execution_manual.md 2.2 节
和 docs/NOTE6_system_technical_specification.md 第 9 章硬指标

7 大组件：
  1. 电机 (100_Motor)           φ55×60mm, 轴 φ6×75mm
  2. 偏心轮 (200_EccentricWheel) 偏心距 e=10mm
  3. 轴承 (210_Bearing_608)      608ZZ ID8×OD22×W7
  4. 连杆 (300_ConnectingRod)    L=50mm
  5. 活塞杆 (310_PistonRod)      φ10×80mm
  6. 滑套 (320_PistonBushing)    φ18OD×φ10.1ID×25mm
  7. 按摩头 (400_MassageHead)    φ40mm 球
"""
import sys; sys.path.insert(0, '.')
from src.mcp_client.fusion_mcp import FusionMCPClient
c = FusionMCPClient(timeout=180)  # 长超时，Fusion 脚本执行可能慢
c.connect()
print(f"✅ MCP Session: {c.session_id[:8]}...")

# ═══════════════════════════════════════════════════════════
# STEP 1: 创建设计文档 + UserParameters
# ═══════════════════════════════════════════════════════════
STEP1_SCRIPT = r'''
import adsk.core, adsk.fusion, traceback

app = adsk.core.Application.get()
ui = app.userInterface
log = []

try:
    # 1.1 创建新设计文档
    des_doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
    des_doc.name = "NOTE6_Assembly_draft_v1"
    design = des_doc.design
    root = design.rootComponent
    log.append(f"DOC_CREATED:{des_doc.name}")

    # 1.2 参数化定义 (全部 draft v1.0 — 待拆机验证后升级 v2.0)
    # 格式: (name, value, unit, comment)
    params_def = [
        # ── 运动学 (第9章硬指标) ──
        ("amplitude",        10.0, "mm",    "单机振幅 A — 硬指标 10±0.1mm"),
        ("eccentricity",     10.0, "mm",    "偏心距 e = A"),
        ("stroke",           20.0, "mm",    "峰-峰行程 S = 2e — 硬指标 20±0.2mm"),
        ("rod_length",       50.0, "mm",    "连杆长度 L — 估计值，待拆机"),
        ("rod_ratio",         0.2, "",      "连杆比 λ = e/L ≤ 0.25 硬指标"),
        ("max_rod_angle",    11.5, "deg",   "连杆最大摆角 β_max = arcsin(λ) ≤ 15° 硬指标"),

        # ── 频率档位 (第9章) ──
        ("rpm_1",          2100.0, "rpm",   "1档转速"),
        ("rpm_2",          2400.0, "rpm",   "2档转速"),
        ("rpm_3",          2700.0, "rpm",   "3档转速"),
        ("rpm_4",          3000.0, "rpm",   "4档转速"),
        ("rpm_5",          3300.0, "rpm",   "5档转速 — 设计基准"),
        ("freq_5",           55.0, "Hz",    "5档频率"),
        ("omega_5",         345.6, "rad/s", "5档角速度 ω = 2πn/60"),

        # ── 电机参数 (已知) ──
        ("motor_od",         55.0, "mm",    "电机外径 — PRO6 官网明示"),
        ("motor_length",     60.0, "mm",    "电机长度 — 估计值，待拆机"),
        ("motor_shaft_d",     6.0, "mm",    "电机输出轴直径 — 估计值"),
        ("motor_shaft_l",    75.0, "mm",    "电机输出轴总长"),
        ("motor_kv",        110.0, "rpm/V", "电机 KV 值 — 反推 2400/22.2≈108"),
        ("motor_voltage",    22.2, "V",     "额定电压 6S LiPo"),
        ("motor_power",      25.0, "W",     "额定功率 — NOTE6 官网明示"),
        ("motor_torque",    0.51, "N·m",   "堵转转矩 ≥510mN·m — 反推计算"),

        # ── 轴承 608ZZ 参数 (已知行业标准) ──
        ("bearing_id",        8.0, "mm",    "608ZZ 内径 d=8mm"),
        ("bearing_od",       22.0, "mm",    "608ZZ 外径 D=22mm"),
        ("bearing_width",     7.0, "mm",    "608ZZ 宽度 B=7mm"),

        # ── 活塞杆参数 ──
        ("piston_d",         10.0, "mm",    "活塞杆直径 — 估计值"),
        ("piston_l",         80.0, "mm",    "活塞杆总长 — 估计值"),
        ("piston_joint_hole", 5.0, "mm",    "活塞杆底端铰接孔 φ5mm"),

        # ── 滑套参数 ──
        ("bushing_od",       18.0, "mm",    "滑套外径 — 估计值"),
        ("bushing_id",       10.1, "mm",    "滑套内径 (与活塞杆间隙配合)"),
        ("bushing_l",        25.0, "mm",    "滑套长度 — 估计值"),

        # ── 按摩头参数 ──
        ("massage_head_d",   40.0, "mm",    "标准球形按摩头直径"),
        ("massage_stem_d",    8.0, "mm",    "按摩头连接柱直径"),
        ("massage_stem_l",   15.0, "mm",    "按摩头连接柱长度"),

        # ── 尺寸链验证参数 ──
        ("a_max_5",        1309.0, "m/s²",  "5档峰值加速度 a_max=ω²e(1+λ)=133g"),
        ("mass_note6",     1200.0, "g",     "整机净重 1.2kg — 官网"),
    ]

    params = design.userParameters
    vi = adsk.core.ValueInput.createByReal
    for nm, val, unit, desc in params_def:
        if not params.itemByName(nm):
            params.add(nm, vi(val), unit, desc)
    log.append(f"PARAMS_ADDED:{len(params_def)}")

    # 保存文档 (Fusion 2026+: save(description) )
    try:
        ok = des_doc.save("draft v1.0 — NOTE6 逆向工程总装参数化模型")
        log.append(f"SAVED:{ok}")
    except Exception as se:
        log.append(f"SAVE_WARN:{str(se)[:100]}")
    print("|".join(log))

except Exception as e:
    print(f"ERROR:{str(e)[:300]}")
'''

print("\n📐 STEP 1: Create design + parameters...")
r1 = c.execute_script(STEP1_SCRIPT, read_only=False)
msg1 = r1.get('message', str(r1)) if isinstance(r1, dict) else str(r1)
print(f"   {msg1[:500]}")

c.disconnect()
print("\n✅ Step 1 complete")
