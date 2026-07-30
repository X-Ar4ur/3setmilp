# 后续论文逐页审计、问题与解决方案

本文档审计论文 *Exploring Secret Keys in Searching Integral Distinguishers Based on Division Property*（ToSC 2020, pp. 288--304）。目标是把后续论文的 K-BDPT 作为一条独立的复现路线，而不是把它当作主论文 Table 5 结果不符时的默认替代方案。

## 1. 阅读范围与逐页记录

已逐页阅读 PDF 的全部 17 页，包含定义、定理、Algorithm 1、三个应用部分、Table 6 与参考文献。

| 论文页 | 内容 | 对本项目的结论 |
| --- | --- | --- |
| 288 | 标题、摘要 | 目标是通过绕过部分密钥位提高 BDPT 精度。 |
| 289 | 引言与贡献 | 论文声称能定位普通 BDPT 出现不精确的位置。 |
| 290 | 相关工作与组织 | 不引入额外的 PRESENT/RECTANGLE 实现细节。 |
| 291 | CBDP、BDPT 定义 | 延续三子集语义。 |
| 292 | Rule 1、Rule 2 | 密钥 XOR 与 S 盒传播规则与主论文一致。 |
| 293 | 主论文的剪枝/停止规则 | `BDPT` 的三种结果为 unknown、zero、one。 |
| 294 | Example 1、Lemma 1 起始 | 展示普通 BDPT 不能表达未知项抵消。 |
| 295 | Lemma 1、Theorem 3 | 给出密钥位旁路的数学前提。 |
| 296 | Theorem 3 证明、Example 2、已知常量初态 | Example 2 是 K-BDPT 终态语义的必要回归样例。 |
| 297 | Algorithm 1 | 给出 K-BDPT 第 1--27 行。 |
| 298 | Algorithm 1 逐行解释、错误位置定位 | 要求可追溯首个导致 unknown 的密钥 bit。 |
| 299 | SPECK 实验 | 与 PRESENT 数据路径无直接关系。 |
| 300 | KATAN/KTANTAN 实验 | 与本轮分组密码范围无直接关系。 |
| 301 | SIMON(102)、PRESENT/RECTANGLE 介绍 | 仅给出 PRESENT 轮结构图，没有补充 bit/密钥拆分顺序。 |
| 302 | Table 6、结论 | 原样重复 9-PRESENT/9-RECTANGLE 结果，未给常量 0/1 值或运行时间。 |
| 303--304 | 参考文献 | 确认主论文为 [WHG+19]。 |

## 2. Algorithm 1 与当前实现的对应关系

论文第 297--298 页的 Algorithm 1 对每个局部函数执行以下步骤：

1. 用 CBDP 后缀查询剪除 `K`；任意残留 `K` 可达目标则返回 unknown。
2. 用 CBDP 后缀查询保留 `L`；若集合为空则返回 zero。
3. 对公开局部函数调用 BDPT 传播。
4. 对一个标量密钥 XOR，构造
   \(L'_i=\{\ell\lor e_j\mid \ell\in L_i,\ell_j=0\}\)。
   只有后缀 `BDPT` 在该输入下返回 zero 时，才旁路该密钥 bit；否则执行 Rule 1。

实现中的对应关系如下：

| 论文内容 | 实现 | 状态 |
| --- | --- | --- |
| Theorem 3 的 `L'_i` | `src/three_set_milp/search/bdpt_search.py` | 已实现并有 Example 2 回归测试。 |
| 16 个 S 盒、P 层、64 个标量 key XOR | `src/three_set_milp/search/spn.py` | 已实现；标量 key 顺序固定为内部 bit `0` 到 `63`。 |
| 后缀 CBDP 查询 | `src/three_set_milp/search/spn.py` 的 `SPNGurobiOracle` | 复用边界 MILP 模型。 |
| Table 6 的标准 `c` 初态 | `core/oracle.py` 的 `theoretical_unknown_constant_cube_state()` | 继续作为默认模式。 |
| 已知常量初态 | `core/oracle.py` 的 `theoretical_known_constant_cube_state()` | 新增，仅由显式命令行参数启用。 |

## 3. 已发现的问题与处理决定

### P1：Algorithm 2 的末行与后续论文 Example 2 存在语义矛盾

**证据。** 主论文第 412 页 Algorithm 2 第 22 行、后续论文第 297 页 Algorithm 1 第 27 行都写为无条件 `return 1`。但后续论文第 296 页 Example 2 要求对一个 S 盒后缀得到 zero：两个 `L` 向量分别能够到达目标单项式，却在公开 S 盒传播后按模 2 抵消。若机械执行无条件 `return 1`，Example 2 会返回 unknown，无法旁路密钥 bit，和论文文字结论相反。

**解决方案。**

- 默认 `search_k_bdpt()` 使用“Example 2 终态语义”：后缀已传播到输出端时，读取精确 BDPT 中目标单位向量的 zero/one/unknown 值。这样能复现 Example 2。
- 新增 `search_k_bdpt_literal()` 与 CLI 值 `--algorithm k-bdpt-literal`，严格按伪代码的末行 `return 1` 执行，仅作论文歧义诊断。
- 主论文的 `search_bdpt()` 保持主论文 Algorithm 2 的字面终点规则，不把后续论文的语义补丁偷偷带入主论文实验。

这不是对论文结论的任意修补：两种模式都保留，并以单元测试固定其可观察差异。默认 K-BDPT 选择 Example 2 语义，是因为它是论文自己给出的可验证示例。

### P2：旁路轨迹以前无法证明“哪一个密钥 bit”产生了不精确性

**证据。** 论文第 298 页明确称可定位导致普通 BDPT 不精确的密钥 bit。原有 JSON 的 64 个密钥部件共享同一 `SPNBoundary`，只记录了边界和集合大小；必须靠 trace 序号才能反推 bit 编号。

**解决方案。** `TraceEntry` 现在记录：

- `secret_key_index`：当前标量轮密钥的内部 bit 编号；
- `bypass_l_count`：构造出的 \(L'_i\) 大小；
- `bypass_parity` 与 `bypass_reason`：旁路后缀是因 `l_empty`、终态 zero 或其他原因得到的结果。

当命令带有 `--record-witness` 且旁路失败时，轨迹还记录：

- `bypass_l_prime`：Theorem 3 的完整 \(L'_i\)，它也是随后 Rule 1 生成 K 的候选向量集合；
- `bypass_obstruction_boundary` 与 `bypass_obstruction_vector`：嵌套原始 BDPT 首个触发 Stopping Rule 1 的 CBDP 输入；
- `bypass_obstruction_witnesses`：对上述输入重新求解并逐步验证的 CBDP trail。

新输出会使用算法版本字段和轮密钥扫描顺序拒绝混用旧 K-BDPT 检查点。此前 `target=4` 的 JSON 因此不能作为后续论文的最终复现证据，必须重新运行。

若同一 v4 检查点先在未使用 `--record-witness` 的情况下完成，之后加上该参数时脚本会自动重跑缺少证据的目标位，而不会错误地跳过它。

### P3：`c` 的语义不能被擅自改成某个 0/1 赋值

**证据。** 主论文第 411 页和后续论文第 296 页区分两种明文集合：

- 未给定常量值的 Table 记号 `c`：
  \(K_0=\{u\mid u\succ u_I\},L_0=\{u_I\}\)；
- 全部常量值已知：
  \(K_0=\varnothing,L_0=\{u\mid u_I\preceq u\preceq u_I\cup u_J\}\)，其中 `J` 为值为 1 的常量位置。

Table 6 只写了 `c`，没有给出各 bit 的 0/1 值。因此 PRESENT60 的标准复现必须继续使用第一种状态；不能把 `cccc` 默认替换为 `0000` 或任意值来追求论文输出。

**解决方案。** 新增可选参数：

```console
python experiments/reproduce_table5_spn.py present60 \
  --algorithm k-bdpt \
  --constant-values 0101 \
  --targets 4 \
  --output output/results/present60_k_bdpt_known_0101_target4.json
```

`0101` 按输入模式中四个 `c` 的论文打印顺序解释。省略参数时，仍使用论文标准的未知常量初态。该功能只用于交叉验证，不替代标准 Table 6 复现。

### P4：PRESENT 的标量轮密钥顺序未由后续论文指定

**证据。** 论文给出泛化的“Xor with The Secret Key”函数，但在第 301--302 页没有说明 64 位 PRESENT 子密钥拆成标量函数的顺序。

**当前实现。** `--key-bit-order ascending` 使用内部编号 `0 -> 63`，保持原有默认语义；`--key-bit-order descending` 显式使用 `63 -> 0`。二者均写入 JSON 的 `key_bit_order`，并使用不同默认检查点文件，不能相互续跑。这一选择不会修改 CBDP 后缀模型，但可能影响 K-BDPT 的旁路次序和中间集合大小。

**诊断命令。** 反序仅是论文未公开细节的对照，不是新的默认模型：

```console
python experiments/reproduce_table5_spn.py present60 \
  --algorithm k-bdpt \
  --key-bit-order descending \
  --targets 4 \
  --record-witness \
  --output output/results/table5_present60_k_bdpt_key_descending_target4.json
```

### P5：Table 6 缺少可直接复核的性能与实现参数

**证据。** 后续论文第 302 页只说明结果与主论文一致；没有给出 PRESENT/RECTANGLE 的逐目标位耗时、具体常量值、轮密钥拆分顺序或 MILP 模型构造细节。

**解决方案。** 本项目把每个目标位的耗时、oracle 调用数、算法版本、常量语义、轮密钥扫描顺序及完整剪枝/旁路轨迹写入 JSON。带 `--record-witness` 的 K-BDPT 结果还会保存失败旁路的阻塞 CBDP witness。性能比较只在相同服务器、Gurobi 版本、目标位和算法模式下进行，不能直接拿论文平台的总时间作一一结论。

## 4. 已增加的验证

- 后续论文 Example 2：默认 K-BDPT 返回 zero，并确实旁路该密钥 bit。
- 字面伪代码模式：后续论文 Example 2 返回 unknown、不旁路；用来固定 P1 所述差异。另有一个末端小型案例验证字面模式的 `return 1` 行为。
- 已知常量初态：在 4 bit 穷举中，与精确 cube 的 BDPT 状态完全一致。
- 常量值字符串：按显式密码 layout 解析，避免把论文打印顺序误当作内部 bit 顺序。
- 轮密钥顺序：两轮 PRESENT 部件序列分别固定验证 `0 -> 63` 与 `63 -> 0`，并验证首尾局部函数确实作用于对应密钥 bit。
- 失败旁路来源：纯 Python 回归样例验证 `L'_i`、嵌套 BDPT 的阻塞边界和决定性 K 向量会被准确记录。

本地测试：`86 passed, 12 skipped`；跳过项均因本机没有 `gurobipy`。Gurobi 端到端结果仍需服务器验证。

## 5. 下一次服务器实验顺序

先在新的输出路径运行默认 K-BDPT（Example 2 语义）：

```console
python experiments/reproduce_table5_spn.py present60 \
  --algorithm k-bdpt \
  --targets 4 \
  --record-witness \
  --output output/results/table5_present60_k_bdpt_key_ascending_target4.json
```

再只改变标量轮密钥扫描方向：

```console
python experiments/reproduce_table5_spn.py present60 \
  --algorithm k-bdpt \
  --key-bit-order descending \
  --targets 4 \
  --record-witness \
  --output output/results/table5_present60_k_bdpt_key_descending_target4.json
```

然后以字面模式做同目标对照：

```console
python experiments/reproduce_table5_spn.py present60 \
  --algorithm k-bdpt-literal \
  --targets 4 \
  --output output/results/table5_present60_k_bdpt_literal_target4.json
```

最后在默认升序下对四个 `c` 的 16 种赋值执行独立诊断；这些结果不能替代通用 `c` 初态的论文复现：

```console
for c in 0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111; do
  python experiments/reproduce_table5_spn.py present60 \
    --algorithm k-bdpt \
    --constant-values "$c" \
    --targets 4 \
    --output "output/results/table5_present60_k_bdpt_known_${c}_target4.json"
done
```

只有默认 K-BDPT 在通用 `c` 初态上通过目标位 4 后，才继续跑 `0 4 8 12`。
