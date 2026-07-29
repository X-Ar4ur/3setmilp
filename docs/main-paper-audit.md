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
| 全部局部函数完成后返回 1 | `search/bdpt_search.py` | 已修正为严格执行论文第 412 页第 22 行 |

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

