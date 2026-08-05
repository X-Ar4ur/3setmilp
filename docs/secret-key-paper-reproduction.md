# 《Exploring Secret Keys》完整方法与实现映射

本文档对应 Wang、Hu、Guan、Zhang、Shi 的论文 *Exploring Secret Keys in Searching Integral Distinguishers Based on Division Property*（ToSC 2020(3), 288--304）。PDF 共 17 页，已逐页核对定义、公式、Lemma 1、Theorem 3、Algorithm 1、Figures 1--4、Tables 1--6、结论和参考文献。

本项目区分两种状态：

- **实现完成**：论文给出的数学步骤、密码轮函数、CBDP 后缀模型、K-BDPT 搜索顺序、表格配置、检查点和离线回归已经进入代码。
- **实验复现成功**：必须在可用 Gurobi 环境中完成全部目标位并与表格逐字符一致。本机没有 `gurobipy`，因此本文档不会把前者写成后者。

## 1. 数学语义

### 1.1 CBDP 与 BDPT

对 \(n\) bit 多重集 \(X\) 和指数向量 \(u\)，CBDP 用 \(K\) 的上闭包描述未知单项式奇偶性：若存在 \(k\in K\) 且 \(u\succeq k\)，则奇偶性未知；否则为 0。

BDPT 用 \(D^{1^n}_{K,L}\) 表示三值语义：

1. 若 \(u\) 支配某个 \(k\in K\)，结果为 unknown；
2. 否则若 \(u\in L\)，结果为 1；
3. 否则为 0。

`Reduce0(K)` 删除被更小向量覆盖的冗余 \(K\)；`Reduce1(K,L)` 删除已落入 \(K\) 上闭包的 \(L\)。同一输出 \(L\) 向量由多个分支产生时必须按模 2 抵消。

实现位置：

- `src/three_set_milp/core/bdpt.py`
- `src/three_set_milp/core/order.py`
- `src/three_set_milp/core/propagation.py`

### 1.2 论文复用的两条传播规则

对状态位 \(x_i\leftarrow x_i\oplus rk\)，普通 BDPT 保留原 \((K,L)\)，并对每个满足 \(\ell_i=0\) 的 \(\ell\in L\) 向 \(K\) 加入 \(\ell\lor e_i\)。实现为 `xor_secret_key()`。

公开 S 盒或一般向量布尔函数通过输出单项式的 ANF 传播。项目从真值表计算所有输出单项式 ANF，分别传播 \((K,L)\)，随后执行模 2 合并、`Reduce0` 和 `Reduce1`。

### 1.3 MILP 辅助剪枝

对当前边界 \(i\)、向量 \(v\) 和目标输出单位向量 \(e_m\)，CBDP 后缀 MILP 只回答是否存在 trail

\[
v\xrightarrow{E_i}e_m.
\]

搜索循环严格执行：

1. 任一 \(K_i\) 向量可达目标时返回 unknown；
2. 删除所有不可达的 \(K_i\)；
3. \(L_i\) 只保留可达向量；
4. 若 \(L_i=\varnothing\)，返回 0；
5. 否则精确传播下一个局部函数。

只有求解器明确返回 infeasible 才能证明不可达。超时、数值错误或没有可行解证书的状态一律中止，不能解释为 balanced。

## 2. 密钥旁路定理与 K-BDPT

论文 Lemma 1 考虑同一输入多重集分别经过 \(x_j\oplus0\) 和 \(x_j\oplus1\) 后的并集。其 \(K\) 不变，而 \(L\) 变为

\[
L'_i=\{\ell\lor e_j\mid \ell\in L_i,\ \ell_j=0\}.
\]

Theorem 3 的可执行判据是：若原始 BDPT 在当前密钥 XOR 之后的公开后缀上，以 \(D_{K_i,L'_i}\) 为输入，对目标 \(e_m\) 返回 0，则固定该密钥位为 0 或 1 的输出奇偶性相同。当前密钥 XOR 可按恒等映射旁路；否则必须执行普通密钥 XOR 规则，把 \(L'_i\) 加入 \(K\)。

实现 `search_k_bdpt()` 在每个标量密钥 XOR 上执行上述嵌套查询；内层始终是原始 BDPT，不递归使用 K-BDPT。轨迹记录：

- 状态位索引和论文式密钥标签；
- \(L'_i\) 大小、子搜索三值结果和停止原因；
- 可选的完整 \(L'_i\)、阻塞向量、阻塞边界及其生成/检查密钥位。

### 2.1 两种初始 cube

若只知道非活动位是固定常量但不知道值：

\[
K_0=\{u\mid u\succ u_I\},\qquad L_0=\{u_I\}.
\]

若常量值全部已知，设 \(J\) 为值为 1 的常量位置：

\[
K_0=\varnothing,\qquad
L_0=\{u\mid u_I\preceq u\preceq u_I\lor u_J\}.
\]

所有表格默认使用第一种语义。`--constant-values` 仅用于显式已知常量的交叉验证，不会静默把论文中的 `c` 当成 0。

### 2.2 Algorithm 1 末行歧义

论文 Algorithm 1 第 27 行无条件写 `return 1`，但同文 Example 2 要求公开 S 盒后的两个 \(L\) 分支抵消并得到 0。机械执行末行会使 Example 2 返回 1，无法旁路密钥位。

项目同时保留：

- `search_k_bdpt()`：默认采用 Example 2 可验证的终态三值语义；
- `search_k_bdpt_literal()`：严格执行字面 `return 1`，只用于论文歧义诊断。

两种模式写入不同算法版本，检查点不能混用。

### 2.3 轮密钥建模范围

论文的传播规则作用于每一次标量轮密钥 XOR，并未把主密钥扩展方程加入 CBDP/K-BDPT。项目遵循这一范围，把每次出现的轮密钥位视为独立未知常量；相同的论文标签只用于追踪来源，不额外施加相等约束。这是在扩大后的轮密钥空间中搜索：若某性质在该模型下对所有独立轮密钥均成立，则对任何具体 SPECK、KATAN/KTANTAN、SIMON/SIMECK 或 SPN 密钥编排的子集也成立，但可能漏掉只能利用密钥扩展相关性证明的性质。

## 3. 逐密码实现

### 3.1 SPECK（Table 2）

论文直接搜索 6 轮区分器；Table 1 的 7 轮数字包含引用文献中的自然扩展一轮技巧，不能写成 K-BDPT 直接搜索 7 轮。

分析状态由真实 \(2n\) bit 加一个值为 0 的进位辅助位组成。每轮严格拆成：

1. 第一字循环右移；
2. 从低位到高位执行 \(n\) 个全加器
   \((x_i,y_i,c_i)\mapsto(s_i,y_i,c_{i+1})\)；
3. 对第一字执行 \(n\) 个标量轮密钥 XOR；
4. 第二字循环左移；
5. 逐位执行 \((x_i,y_i)\mapsto(x_i,x_i\oplus y_i)\)；
6. 丢弃最高进位，并把辅助位显式恢复为 0。

全加器和 XOR 都由真值表同时驱动精确 BDPT 传播与 CBDP MILP，避免维护两套语义。小尺寸穷举验证整个分析电路与具体 SPECK 轮函数完全一致。

同一轮连续标量密钥 XOR 在 CBDP 中都是恒等映射，因此它们与紧随其后的公开旋转共用同一个规范化后缀边界；K-BDPT 的逐密钥语义不变，但服务器不会为每个密钥位重复构建等价 MILP。

实现：

- `src/three_set_milp/ciphers/speck.py`
- `src/three_set_milp/milp/speck.py`
- `src/three_set_milp/search/speck.py`
- `experiments/reproduce_secret_keys_table2_speck.py`
- `configs/secret_keys/table2/`

`compare` 模式先运行 K-BDPT，再运行普通 BDPT，并从普通 BDPT 首次触发 Stopping Rule 1 前的生成步骤定位 Table 2 的 \(k^0_7\) 或 \(k^0_8\)。

### 3.2 KATAN/KTANTAN（Table 3）

项目采用原始规格的寄存器长度和抽头：

| 分组 | \(|L_1|\) | \(|L_2|\) | \(x_1,\ldots,x_5\) | \(y_1,\ldots,y_6\) | 每轮时钟 |
| --- | ---: | ---: | --- | --- | ---: |
| 32 | 13 | 19 | 12,7,8,5,3 | 18,7,12,10,8,3 | 1 |
| 48 | 19 | 29 | 18,12,15,7,6 | 28,19,21,13,15,6 | 2 |
| 64 | 25 | 39 | 24,15,20,11,9 | 38,25,33,21,14,9 | 3 |

254 位 IR 序列逐位固化在代码中。同一轮的 2/3 次时钟复用同一个 IR 与 `ka/kb` 标签。

分析状态不增加辅助位。由于 \(x_1\) 和 \(y_1\) 正是本次移位后丢弃的两个最高位，电路先分别在这两个位置原位累加 \(f_a\) 和 \(f_b\)：线性项使用 2-bit XOR 累加器，乘积项使用 3-bit \(acc\leftarrow acc\oplus(a\land b)\) 门。随后执行 `ka`、`kb` 两个标量密钥 XOR，最后一次公开排列把 \(f_b\) 送入 \(L_1\) 最低位、把 \(f_a\) 送入 \(L_2\) 最低位。这样既与具体时钟函数逐点等价，也避免“已知零辅助位”在高阶单项式上造成不必要的过近似。

每个时钟在公开反馈之后的 `ka`、`kb` 与移位前边界具有相同 CBDP 后缀，三者共用一个规范化边界和模型缓存。

Table 3 的 73.6 轮按论文“64-bit 每轮更新三次”解释为 73 轮再加 2 次更新，即 221 个时钟。KATAN 与 KTANTAN 的轮变换相同，区别只在密钥编排；CBDP/K-BDPT 把轮密钥位视为未知常量，因此同一数据路径模型覆盖两者。对同一轮重复使用的密钥位，当前模型用相同标签记录，但内层 BDPT 仍按独立未知出现保守处理；证明在更大的独立密钥族上成立时，对真实相等密钥子集也成立。

实现：

- `src/three_set_milp/ciphers/katan.py`
- `src/three_set_milp/milp/katan.py`
- `src/three_set_milp/search/katan.py`
- `experiments/reproduce_secret_keys_table3_katan.py`
- `configs/secret_keys/table3/`

### 3.3 SIMON、SIMECK 与 SIMON(102)

公共 Feistel 数据路径沿用主项目已经验证的 4-bit 局部核心

\[
(a,b,c,d)\mapsto(a,b,c,ab\oplus c\oplus d).
\]

新增 K-BDPT 序列在每轮 \(n\) 个核心之后，把轮密钥拆成 \(n\) 个标量 XOR，最后执行公开左右交换。支持：

- SIMON32/48/64/96/128：旋转常数 \((1,8,2)\)；
- SIMECK32/48/64：旋转常数 \((0,5,1)\)；
- SIMON(102)32/48/64：旋转常数 \((1,0,2)\)。

后续论文 Table 5 给出 SIMON(102) 的完整输入和输出，因此提供固定配置入口。论文对普通 SIMON/SIMECK 只写“与既有最长区分器一致”，没有列出各变体的完整轮数、输入 cube 和输出模式；项目提供 `run_secret_keys_simon_family.py`，要求调用者显式输入这些参数，不凭空补造表格。

### 3.4 PRESENT 与 RECTANGLE（Table 6）

两种密码继续复用已经验证的 4-bit S 盒、P 层/ShiftRow、CBDP 后缀模型和显式论文 layout。K-BDPT 把每轮 64-bit 密钥 XOR 拆成 64 个标量函数。

后续论文没有公开标量密钥扫描顺序。项目默认内部位 `0 -> 63`，同时提供 `descending` 对照；顺序写入检查点，不允许混用。PRESENT/RECTANGLE 的论文输入 `c` 未给具体 0/1 值，默认保持未知常量语义。

入口：

```console
python experiments/reproduce_table5_spn.py present60 --algorithm k-bdpt
python experiments/reproduce_table5_spn.py present63 --algorithm k-bdpt
python experiments/reproduce_table5_spn.py rectangle60 --algorithm k-bdpt
```

## 4. 表格复现命令

建议先运行论文明确给出值的目标位作为服务器冒烟测试：

```console
# Table 2：第一字最低打印位为 0，并比较普通 BDPT 的失准位置。
python experiments/reproduce_secret_keys_table2_speck.py speck32 --targets 16
python experiments/reproduce_secret_keys_table2_speck.py speck48 new --targets 24
python experiments/reproduce_secret_keys_table2_speck.py speck64 new --targets 32
python experiments/reproduce_secret_keys_table2_speck.py speck96 new --targets 48

# Table 3：最左打印位分别为 1/0/0。
python experiments/reproduce_secret_keys_table3_katan.py katan32 --targets 31
python experiments/reproduce_secret_keys_table3_katan.py katan48 --targets 47
python experiments/reproduce_secret_keys_table3_katan.py katan64 --targets 63

# Table 5：右字高两位为 01，最低位为 1。
python experiments/reproduce_secret_keys_table5_simon102.py simon10232 --targets 16 30 31
python experiments/reproduce_secret_keys_table5_simon102.py simon10248 --targets 24 46 47
python experiments/reproduce_secret_keys_table5_simon102.py simon10264 --targets 32 62 63
```

冒烟测试通过后省略 `--targets` 运行全部输出位。脚本逐目标写 JSON，可断点续跑；已有检查点的算法版本、常量语义、密码配置或密钥顺序不匹配时会拒绝继续。

## 5. 论文平台、Table 1 与外延轮

论文实验平台为 Intel Core i5-9300 @ 3.98GHz、32GB RAM、Gurobi 8.1.0。Table 1 中属于本文新增结果的行如下；完整的新旧对照、数据量、区分器数和原样时间字符串固化在 `configs/secret_keys/table1.json`。

| 密码 | 数据量 | Table 1 轮数 | 常量位 | 区分器数 | 论文时间 |
| --- | ---: | ---: | ---: | ---: | ---: |
| SPECK32 | \(2^{30}\) | 7 | 1 | 1 | 1h5m |
| SPECK48 | \(2^{45}\) | 7 | 1 | 2 | 12h57m |
| SPECK64 | \(2^{61}\) | 7 | 1 | 2 | 17h40m |
| SPECK96 | \(2^{93}\) | 7 | 1 | 2 | 7d10h25m |
| KATAN/KTANTAN64 | \(2^{63}\) | 73.6 | 1 | 1 | 44h24m |
| SIMON(102)32 | \(2^{31}\) | 20 | 3（值已确定） | 32 | 22m |
| SIMON(102)48 | \(2^{47}\) | 28 | 3（值已确定） | 48 | 1h10m |
| SIMON(102)64 | \(2^{63}\) | 36 | 3（值已确定） | 64 | 3h27m |

SPECK 和 SIMON(102) 的 Table 1 轮数均在直接区分器前使用 `[WLV+14]` 技巧增加一轮。论文明确说明这些外延性质不能由其方法直接找到。因此项目分别搜索 Table 2 的 6 轮 SPECK 与 Table 5 的 19/27/35 轮 SIMON(102)，同时用 `paper_rounds_with_extension` 和 Table 1 配置记录 7 与 20/28/36，绝不把外延轮作为直接搜索结果。

Table 4 的 `*` 表示输出和是常量但准确值未知；Table 5 把 SIMON(102) 右字的 `0*...*` 分别收紧为 `01...1`。配置同时保留 `previous_output` 和 `expected_output`，可审计这三个准确常量值是如何变化的。

## 6. 验证层次

### 6.1 不依赖 Gurobi

- CBDP/BDPT 三值语义、Reduce0/Reduce1 和奇偶抵消；
- Example 1 与 Example 2；
- K-BDPT 默认/字面终态差异；
- 已知与未知常量 cube；
- SPECK 小字长完整轮电路与具体多重集穷举；
- KATAN 小寄存器完整时钟电路、未知常量 cube 与具体多重集穷举；
- KATAN IR、抽头、73.6 轮时钟换算；
- SIMON/SIMECK/SIMON(102) 参数、位序和标量密钥序列；
- Tables 2、3、5 的输入/输出字符串长度和内部位映射。

当前结果：`105 passed`。

### 6.2 需要 Gurobi

新增测试会把小型 SPECK 一轮和 KATAN 一时钟的后缀 MILP，对每个输出目标与精确 BDPT 传播交叉比较。连同原有测试，本机共有 `18 skipped`，原因都是没有 `gurobipy`，不是断言失败。

服务器验收：

```console
python -m pip install -e . --no-deps
python -m pip install "pytest>=8"
python -m pytest
```

要求 `tests/milp/` 无跳过后，再运行上一节的表格命令。

## 7. 论文没有公开、因而无法逐字复原的信息

1. 普通 SIMON/SIMECK 各变体的完整实验参数和输出模式；
2. PRESENT/RECTANGLE 标量轮密钥函数的扫描顺序；
3. SPECK、KATAN/KTANTAN 的具体实现代码和 MILP 局部分解；
4. Table 6 中 `c` 的具体 0/1 值；
5. 每个目标位的独立耗时、模型规模和求解器参数；
6. Algorithm 1 第 27 行与 Example 2 的终态语义冲突。

项目对 1 使用显式自定义入口，对 2 保留升/降序并记录元数据，对 3 给出可穷举验证的等价布尔电路，对 4 保持未知常量语义，对 5 在 JSON 中补充本机数据，对 6 同时保留语义模式和字面模式。所有这些处理都显式记录，不把推断伪装成论文原文。

## 8. 论文结论的证据边界

论文称其对 SPECK32、SIMON32、SIMECK32、SIMON(102)32 和 KATAN/KTANTAN32 枚举固定密钥下的全部明文行为，并据此作出“所得区分器是在所有密钥上成立的最佳区分器”的实验性判断；对较大分组，论文明确表示受计算资源限制而没有给出同类实验证明，并把可证明的积分攻击安全性留作未来工作。

本项目没有论文使用的全部固定密钥实验数据，因而只把这段话记录为论文结论，不把它升级为本次复现已独立验证的结论。当前可独立验证的是数学传播、局部电路和配置；完整目标位表格仍以可用 Gurobi 环境中的结构化结果为验收门。
