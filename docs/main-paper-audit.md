# 主论文逐页审计记录

本文档只审计 *MILP-aided Method of Searching Division Property Using Three Subsets and Applications* 的方法及其分组密码实验。后续论文的 K-BDPT 暂不作为 Table 5 复现依据。

## 1. 阅读范围

已逐页检查 PDF 的全部 30 页（论文页码 398--427），包括：

- BDPT 定义、`Reduce0`、`Reduce1` 与四条基本传播规则；
- S 盒传播定理 1；
- 剪枝定理 2、3 与 fast propagation；
- Algorithm 1 `SCBDP`、三条停止规则和 Algorithm 2；
- SIMON、SIMECK、PRESENT、RECTANGLE、LBlock 的局部函数划分；
- Trivium 部分、结论、附录 Table 7 和参考文献。

## 2. Algorithm 2 与实现映射

| 论文步骤 | 代码位置 | 审计结果 |
| --- | --- | --- |
| 初始 `K={u' | u' ≻ u_I}`、`L={u_I}` | `core/oracle.py` | 使用 `Reduce0` 后的最小严格超集，语义等价 |
| 对当前 `K` 调用后缀 `SCBDP` | `search/bdpt_search.py` | 一致 |
| 任一 `K` 可达 `e_m` 时返回 unknown | `search/bdpt_search.py` | 一致 |
| 仅保留可达 `e_m` 的 `L'` | `search/bdpt_search.py` | 一致 |
| `L'` 为空时返回 0 | `search/bdpt_search.py` | 一致 |
| 传播 `BDPTP(Q_i,j,D_{∅,L'})` | `search/bdpt_search.py` | 一致，传播前显式清空 `K` |
| 全部局部函数完成后返回 1 | `search/bdpt_search.py` | 默认 `bdpt` 严格执行第 22 行；`bdpt-exact` 独立诊断正确终态 |

论文第 403 页把严格偏序写成“每一位都严格大于”，这在二进制向量含 1 时不可能成立。第 415 页 SIMON32 的初始状态明确给出 `K={(1,...,1)}`、`L={(0,1,...,1)}`，因此实际含义只能是“逐位支配且不相等”。项目当前实现采用这一含义。

## 3. PRESENT 模型映射

主论文把一轮 PRESENT 分成 17 个局部函数：

1. `Q_i,0` 到 `Q_i,15` 依次作用于 `(x_4j,...,x_4j+3)`；
2. `Q_i,16` 执行位排列 `P`，再异或独立未知轮密钥。

项目当前模型与该划分一致。PRESENT S 盒的 CBDP 模型包含 47 条约化 division trail；紧凑的 11 条不等式在全部 256 个二进制输入输出点上与这 47 条 trail 完全一致。

## 4. 当前尚未闭合的矛盾

服务器上的主论文 BDPT 结果对 PRESENT60 的内部位 0 返回 balanced，但内部位 4、8、12 在第二轮后由 Stopping Rule 1 返回 unknown。Table 5 在当前 PRESENT 打印约定下要求这四位均 balanced。

这不能用运行超时解释：Gurobi 返回的是可行，而不是未确定。下一步必须导出触发 Stopping Rule 1 的决定性 `K` 向量以及从该向量到 `e_4` 的完整 CBDP trail，并逐个核验 S 盒 transition 和位排列：

- 若轨迹核验失败，说明实现或轨迹提取存在错误；
- 若轨迹核验成功，则按主论文 Stopping Rule 1，该目标位必然是 unknown，需要继续检查论文实验是否使用了正文未说明的密钥处理方式；
- 在上述证据闭合前，不采用后续论文的 K-BDPT 作为修复。

## 5. Stopping Rule 1 对照与 Rule 4 诊断

主论文第 411 页的 Stopping Rule 1 规定：在局部后缀 `E_i,j` 的输入 BDPT
`D_{K_i,j,L_i,j}` 上，只要存在任意 `k in K_i,j`，使 CBDP trail
`k -> e_m` 存在，就立即停止并把第 `m` 个输出位判为 unknown。Algorithm 2
第 4--9 行给出了相同实现。

项目的 `search_bdpt()` 在每个局部边界先遍历当前 `K`。后缀 oracle 返回
`FEASIBLE` 时，代码立即返回 `Parity.UNKNOWN/K_REACHABLE`；如果全部不可达，
才清空 `K`、剪枝 `L` 并继续执行第 19 行的 BDPT 传播。因此当前 Stopping
Rule 1 的量词、边界、CBDP 可达条件和返回值均与论文一致。向量排序和缓存
只改变执行顺序及耗时，不改变判定。

Rectangle 的新增 11 位都在轮密钥 Rule 4 从 `L` 生成 `K` 后触发该规则。
为区分“Stopping Rule 1 实现错误”和“作者实验采用了未公开的密钥处理”，
Table 5 脚本增加 `--key-treatment ignore-rule4`。该模式仍执行相同的 CBDP
剪枝、Stopping Rule 1 和 BDPT S 盒传播，只在轮末跳过 Rule 4 的 `L -> K`
生成。JSON 会记录 `key_treatment=ignore-rule4` 以及诊断偏离说明，默认
`paper` 模式不变。

该对照模式不是论文复现结果。若它恰好恢复全部 11 位，只能说明差异被
定位到密钥 Rule 4 路径，不能据此认定应从正式实现中删除 Rule 4。

## 6. Algorithm 2 终态勘误与隐藏语义矩阵

主论文 Algorithm 2 第 22 行无条件返回 1，但最后一个局部函数仍可能使多个
`L` 贡献模 2 抵消，或从 `L` 生成最终 `K`。因此，字面伪代码不能在所有局部
划分上正确区分 zero、one 和 unknown。项目保留两种互不混用的模式：

- `bdpt`：严格保留论文第 22 行，作为字面复现基线；
- `bdpt-exact`：完成全部局部传播后读取最终 BDPT 的实际三值。

终态修正不会改变 PRESENT60 目标 4 在第二轮入口提前触发 Stopping Rule 1
的事实，但可排除另一类独立歧义。单元测试分别覆盖最终 `L` 抵消为 zero 和
最后一个局部函数生成 unknown 的情形。

为继续定位 Table 5 的隐藏实验设置，`reproduce_table5_spn.py` 还提供三种
显式密钥语义：

- `paper`：逐位应用 Rule 4，表示正文的未知轮密钥；
- `ignore-rule4`：只传播公开置换，等价于每轮密钥固定为零；
- `fixed`：按公开仿射变换精确传播命令行给出的逐轮固定密钥。

`run_table5_hypothesis_matrix.py` 先检查 PRESENT60 目标 4 和 RECTANGLE60
目标 10、12，再按需穷举四个输入常量或若干固定轮密钥指纹。每个配置拥有
独立 JSON 检查点；只有全部请求目标均为 zero 才进入候选列表。即使某个配置
匹配，也只能称为“Table 5 历史实现候选”，不能替代 `paper` 模式下的任意
密钥证明。
