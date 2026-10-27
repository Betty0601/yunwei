# Dr. Fuji DMS PRO6 公开资料证据分级表

> 证据编号格式：PRO6-EVD-xxx
> 信息类别：A=已确认事实；B=厂商宣传标称；C=合理工程推断；D=待验证假设
> 来源类型：官方/宣传/手册/评测/专利/拆解/第三方经销

---

## 证据表

| 证据编号 | 声明/数据 | 来源 URL | 来源类型 | 类别 | 可信度 | 歧义/差异 | 设计影响 | 需要验证 |
|---------|----------|----------|---------|------|--------|-----------|---------|---------|
| PRO6-EVD-001 | 产品型号：QL/DMS.PRO6-A；制造商：四川千里倍益康医疗科技股份有限公司（beoka） | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html, https://www.beoka.com/zhuanye/202203/7.html | 用户手册+厂商官网 | **A** | **High** | 明确标注 Dr. Fuji 品牌，实为倍益康 OEM/ODM 产品，型号在不同渠道存在 Dr. Fuji 与倍益康 NOTE6 双轨命名 | 可以直接参考倍益康 NOTE6 技术资料；电机、传动、轴承等内部件可能同源于 beoka 体系 | 拆机核对内部结构与倍益康 NOTE6 是否完全一致 |
| PRO6-EVD-002 | 频率范围：最大 ≤60Hz（官方手册）；经销商给出 2100~3300 次/min 五档 | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=3, https://heartwellmed.com/products/dr-fuji-pro6-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head | 用户手册+经销商 | **A** | **High** | 2100c/min = 35Hz；3300c/min = 55Hz；"≤60Hz"为上限规格。起始档位 2100c/min 对应 35Hz 而非 15Hz | 设计目标 15~60Hz 需实测确认，低档可能从 ~35Hz 起；整机是否覆盖 15~60Hz 存疑 | 用加速度计实测各档频率，特别是低档最低频 |
| PRO6-EVD-003 | 5 档转速（次/min）：2100 / 2400 / 2700 / 3000 / 3300 | https://heartwellmed.com/products/dr-fuji-pro6-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head, https://beoka.com/meitizixun/202210/142.html | 经销商+倍益康官网 | **A** | **High** | 换算为 Hz：35 / 40 / 45 / 50 / 55 Hz；与 60Hz 上限未对齐，存在潜在差异 | 频率档位为离散值，未连续调节；动力学计算针对 15-60Hz 范围可能超出原机实际覆盖 | 实机扫频测试，确认是否存在 55~60Hz 区间 |
| PRO6-EVD-004 | 单边振幅：10mm | 多份手册和经销商规格表一致 | 用户手册+经销商 | **A** | **High** | 倍益康 PRO6 主页曾出现 "9mm 振幅"字样，手册和其他渠道为 10mm；可能存在空载 10mm、带载下降差异 | 动力学计算以 10mm 为基准需验证；带载时振幅损失量未知 | 测振仪实测空载与 1kg/2kg 负载下的实际振幅 |
| PRO6-EVD-005 | 电池规格：22.2V / 2500mAh 锂电池 | https://heartwellmed.com/products/dr-fuji-pro6-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head, https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=3 | 手册+经销商 | **A** | **High** | 倍益康 NOTE6 称"天津力神 3C 动力型 18650 电芯"，PRO6 是否同款待确认 | 22.2V = 6S 锂电；E=55.5Wh；与理想功耗计算 18.5W@3h 吻合，电池配置合理 | 拆机查看电池组标签（厂商、容量、C-rate） |
| PRO6-EVD-006 | 续航：≥3 小时 | https://heartwellmed.com/products/dr-fuji-pro6-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head | 经销商 | **B** | **Med** | 条件未指明（空载/带载/何档）；理想平均功率 55.5/3=18.5W | 电池能量 55.5Wh 除以续航得平均功耗；需定义测试工况 | 不同档位不同负载下实测续航 |
| PRO6-EVD-007 | 额定功率：25W | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=3 | 用户手册 | **A** | **High** | 与 18.5W 理想功耗存在差距，25W 应为电机额定输入功率（含损耗余量） | 选择电机驱动、电池容量、散热均应以 25W 为基准 | 不同工况下实测电流/功率 |
| PRO6-EVD-008 | 整机重量：约 1.6kg | https://heartwellmed.com/products/dr-fuji-pro6-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head | 经销商+倍益康官网 | **A** | **High** | furnisofas 渠道写 "Approx. 1.2-1.6 kg"；beoka NOTE6 标注"机身重 1.2kg"——可能 1.2kg 为不含电池或头，1.6kg 为含电池含头整机 | 重量预算必须拆分：机壳+电机+传动+电池+头+线路板 | 拆件称重，或查 Dr. Fuji OEM/倍益康 NOTE6 的 BOM |
| PRO6-EVD-009 | 噪声：≤55 dB | https://heartwellmed.com/products/dr-fuji-pro6-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head, furnisofas 渠道写 55-60dB | 经销商 | **B** | **Med** | 未明确 dB(A)、测量距离、空载/带载；55~60dB 差异较大 | 目标 45dB 有较明显差距；样机需独立测试 | 标准化条件（10cm/1m/2m，A计权，各档位各负载）实测 |
| PRO6-EVD-010 | 电机：Professional custom super torque motor / 55mm Brushless Motor with Metal Bearings / 有感无刷电机 | https://saunanook.com/products/dr-fuji%C2%AE-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head, 倍益康官网 | 经销商+厂商官网 | **B** | **Med** | 不同渠道描述不一："德国部件"、"55mm"、"有感无刷"、"自研有感无刷"——缺少型号、KV 值、电流、额定转速 | 电机选型和匹配需要独立台架测试；55mm 直径暗示较高功率密度 | 拆机看电机标签，或反向测绘定子/转子尺寸 |
| PRO6-EVD-011 | 推力：28kg（倍益康 PRO6/NOTE6） | https://www.beoka.com/zhuanye/202203/7.html, https://beoka.com/meitizixun/202210/142.html | 倍益康官网 | **B** | **Med** | 推力定义（峰值/稳态/何种台架条件）未说明；Dr. Fuji 渠道未给出该数字 | 28kg 推力对应的峰值力约 275N（g=9.8），对机构和传动选型有约束 | 开发推力测试台实测 |
| PRO6-EVD-012 | 治疗头：钛合金材质，倍益康 PRO6 官方列 3 款（小平头、圆柱头大、圆柱头小）；部分经销商写 6 款 | https://www.beoka.com/zhuanye/202203/7.html, heartwellmed | 厂商+经销商 | **B** | **Med** | 数量差异（3 vs 6）；钛合金为共同结论，但头的直径规格（20/25/35mm）未在 PRO6 官方页面明确 | 头的连接方式、尺寸公差、装拆力影响接口设计 | 拆机核对实际标配头数量和规格 |
| PRO6-EVD-013 | 治疗头装拆：直接插拔，不允许旋转 | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=5 | 用户手册 | **A** | **High** | 明确无螺纹，靠弹簧/卡扣固定 | 前端输出轴需设计插拔接口；但倍益康 PRO6 宣传"金属螺纹连接头"（https://www.beoka.com/zhuanye/202203/7.html）——矛盾点待核实 | 确认 Dr. Fuji PRO6 与倍益康 PRO6 前端接口是否不同 |
| PRO6-EVD-014 | 主材质：锌合金、ABS、硅胶 | heartwellmed 规格表 | 经销商 | **B** | **Med** | 未指明哪些部件为锌合金（机壳框架/头部/连接件？）；倍益康 NOTE6 称机身外壳为 ABS | 对结构刚度、散热、重量有影响 | 拆机看各部件材质 |
| PRO6-EVD-015 | 电池保护：过压、过流、短路、超温保护 | https://saunanook.com/products/dr-fuji%C2%AE-dms-pro6-deep-muscle-stimulator-with-professional-ti-alloy-head | 经销商 | **B** | **Med** | 常规锂电保护电路，无特殊 | BMS 设计参考 | 拆电池查看 BMS 方案 |
| PRO6-EVD-016 | 充电时间：2.5~3h | 多渠道规格 | 经销商 | **B** | **Med** | 需知道充电电流才能反推充电器功率 | 充电器选型参考 | 实测充电电流 |
| PRO6-EVD-017 | 10 分钟智能定时 | 多渠道规格 | 手册+经销商 | **A** | **High** | 重复信息，控制策略细节未知 | 微控制器功能之一 | 代码分析或硬件探测 |
| PRO6-EVD-018 | 档位调节：0-5 档触摸键；长按 2 秒急停 | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=5 | 用户手册 | **A** | **High** | 档位为离散切换而非连续调速 | 电机驱动需支持多档固定转速 | 观察控制板电路 |
| PRO6-EVD-019 | "双轴传动结构" / "Biaxial Transmission Structure" | Dr. Fuji 官方描述曾出现，倍益康 PRO6 宣传"机械传动降噪技术" | 宣传 | **C** | **Low** | 无专利、无图纸、无拆机图；"双轴传动"可指：①偏心轮+从动轴 ②两根平行输出轴 ③齿轮副+曲柄 ④其他 | **严禁**直接等同为某一特定机构；需通过拆机或运动学测试证实 | **最高优先级**拆机或 X 射线透视；运动捕捉测末端轨迹 |
| PRO6-EVD-020 | "双轴承旋转结构" / "Dual Bearing Rotating Structure" | 倍益康 NOTE6 宣传"日本进口静音轴承"；saunanook 渠道称 "Metal Bearings" | 厂商+经销商 | **C** | **Low** | 无法确认是电机端双轴承还是输出端支撑轴承；型号未知 | 需选合适的轴承方案；轴承寿命计算 L10h 待实际载荷代入 | 拆机清点轴承数量/位置/型号 |
| PRO6-EVD-021 | 往复冲击输出（percussion/reciprocating impact） | 所有产品描述一致 | 宣传 | **A** | **High** | 仅确认末端为直线往复，未确认机构形式 | 运动学约束 | 高频摄像测轨迹 |
| PRO6-EVD-022 | 倍益康 NOTE6 使用"CNC 精加工偏心轮"作为运动转换 | https://beoka.com/meitizixun/202210/142.html, https://beoka.com/meitizixun/202511/296.html | 倍益康官网 | **C** | **Med** | 明确 NOTE6 使用偏心轮机构，但 Dr. Fuji PRO6 是否完全同款未知（PRO6 标注"双轴传动"而 NOTE6 未见此词） | 偏心轮是高成熟度方案，但与"双轴传动"是否矛盾？可能偏心轮+从动轴 = 双轴 | 若 PRO6=NOTE6 ODM，则偏心轮为高可信候选；若不同款，需独立验证 |
| PRO6-EVD-023 | 倍益康 NOTE6 使用"高光洁度活塞杆、机加成型滑套、CNC 精加工传动臂" | https://beoka.com/meitizixun/202210/142.html | 倍益康官网 | **C** | **Med** | 部件描述暗示"电机→偏心轮→传动臂→活塞杆→滑套→治疗头"的经典筋膜枪架构 | 若 PRO6=NOTE6 ODM，此架构为首选参考 | 拆机核对 |
| PRO6-EVD-024 | 电池为可拆式，底部手柄处有锁扣 | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=5 | 用户手册 | **A** | **High** | 手柄兼作电池盒；充电口在电池底部 | 机械设计考虑快拆结构 | 样机设计参考 |
| PRO6-EVD-025 | 工作模式：间歇加载（intermittent loading） | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=3 | 用户手册 | **B** | **Med** | 含义模糊，可能指电机驱动电流非恒定直流，或指使用建议 | 电机驱动策略需要考虑载荷变化 | 测电流波形 |
| PRO6-EVD-026 | 运输/存储温度 -40~+50℃，湿度 ≤90% | https://www.manualslib.com/manual/1822517/Dr-Fuji-Ql-Dms-Pro6-A.html?page=5 | 用户手册 | **A** | **High** | 标准工业级要求 | 环境设计参考 | 样机验证 |
| PRO6-EVD-027 | Dr. Fuji 为美国品牌，产品在中国大陆生产（倍益康工厂） | 多渠道交叉 | 行业公开 | **C** | **Med** | OEM/ODM 关系，设计主体为 beoka | 可重点参考 beoka 技术资料 | 核实供应链 |
| PRO6-EVD-028 | **未找到 DMS PRO6 相关专利** | Google Patents / USPTO / CNIPA 搜索 | 专利 | **C** | **Low** | Dr. Fuji 或 beoka 可能以不同名称/同族专利申请，或未申请 | 无法参考专利图 | 扩大搜索范围：beoka 筋膜枪、QL/DMS 系列、倍益康 |

---

## 关键发现摘要

### 已确认事实（A 类，共 9 条）
- **OEM 关系**：Dr. Fuji DMS PRO6 = 四川千里倍益康医疗科技 "PRO6/NOTE6" 型号贴牌（QL/DMS.PRO6-A）
- **振幅**：单边 10mm（手册一致）
- **频率档位**：2100/2400/2700/3000/3300 次/min → 35/40/45/50/55 Hz（非连续）
- **电池**：22.2V / 2500mAh（6S 锂电，E=55.5Wh）
- **额定功率**：25W
- **重量**：~1.6kg（含电池含头）
- **电机**：有刷或有感无刷、55mm 外径、高扭矩（B 类但多渠道一致，实际可信度接近 A）
- **控制接口**：0-5 档触摸键，10 分钟定时，长按急停
- **治疗头接口**：直接插拔（手册），无旋转；部分渠道宣传螺纹接口——待核查
- **结构组成**：控制部分 + 治疗头 + 锂电池（手册）

### 厂商宣传标称（B 类，共 7 条）
- 噪声 ≤55dB（条件未明，furnisofas 写 55-60dB）
- 推力 28kg（倍益康宣传）
- 续航 ≥3 小时
- 充电时间 2.5-3h
- 钛合金治疗头（数量 3 vs 6 待核实）
- 锌合金/ABS/硅胶材质分配
- 电池保护功能

### 合理工程推断（C 类，共 6 条）
- "双轴传动" ≈ 偏心轮+从动轴 两轴架构（基于倍益康 NOTE6 公开描述）
- "双轴承旋转结构" ≈ 电机端 + 输出端各一组轴承支撑
- 运动转换：高概率为**偏心轮机构**（倍益康 NOTE6 官网明确使用 CNC 偏心轮）
- Dr. Fuji 为美国品牌，中国 OEM（beoka 工厂）
- 无公开专利可查

### 完全未知（D 类，待验证假设）
- **内部轴系布置**：双轴具体指什么？
- **轴承型号、数量、布置**
- **电机具体参数**：KV 值、额定电流、堵转转矩、转速范围
- **带载下振幅衰减**：10mm 振幅是空载还是带载
- **控制算法细节**：是否有闭环速度调节
- **真实噪声、推力、续航测试条件**
- **倍益康 PRO6 与 NOTE6 是否同一架构**（倍益康官网同时出现两个名称，Dr. Fuji PRO6 可能对应其中之一或另一个改版）

### 立即行动项
1. **最高优先级**：确认 Dr. Fuji PRO6 = 倍益康 NOTE6 还是倍益康 PRO6（官网同时有这两个型号，参数高度重叠但细节有差）
2. 通过运动捕捉（高速摄像机）测末端轨迹，直接验证是偏心轮还是其他机构
3. 在淘宝/闲鱼/ebay 购入 Dr. Fuji PRO6 或倍益康 NOTE6 一台进行拆机
