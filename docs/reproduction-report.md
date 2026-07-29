# 三子集可分性论文复现报告

## 当前状态

更新时间：2026-07-27

当前实现已经完成分组密码侧的数学内核、Algorithm 1/2 框架、SIMON、PRESENT、RECTANGLE、LBlock 模型和 Tables 3--6 服务器实验入口。由于本机 Gurobi License 已过期，尚未声称论文任一端到端表格已经复现成功。

## 已通过的独立验证

| 项目 | 状态 | 验证方式 |
|---|---|---|
| BDPT 三值语义 | 通过 | 原始论文 Example 1 的 16 项 parity 表 |
| 初始 \(K/L\) | 通过 | 穷举全部未知常量赋值，与理论公式比较 |
| Reduce0/Reduce1 | 通过 | 穷举全部指数的规范化前后语义 |
| Copy/AND/XOR | 通过 | 3-bit 状态空间全部 256 个子集 |
| 未知轮密钥 XOR | 通过 | 枚举 key=0/1 的多重集族 |
| ANF/S-box 定理 | 通过 | 小型非线性函数全部输入多重集 |
| SIMON 4-bit 核心 | 通过 | 原论文传播表全部 16 行 |
| 主论文 \(Q_{1,15}\) | 通过 | 三路传播及重复向量奇偶抵消 |
| 主论文 \(Q_{1,16}\) | 通过 | 密钥异或、Reduce1 和左右交换后的 \(K/L\) |
| Algorithm 2 停止规则 | 通过 | 独立 mock suffix oracle 单元测试 |
| SIMON 紧凑 L1--L4 方程 | 通过 | 稀疏分支枚举与局部精确传播比较，含部分轮 |
| Gurobi 基本模型 | 待服务器 | 本机无可用 License |
| SIMON 紧凑一轮模型 | 待服务器 | 已提供精确 BDPT 交叉测试 |
| Table 3 | 服务器通过 | Gurobi 13.0.2：目标位为 zero，Table 3 前缀规模一致 |
| Table 4 SIMON32/SIMON64 | 待服务器 | 已提供逐目标位检查点脚本 |
| PRESENT 位序/S 盒/P 层 | 通过 | 原始规范常数与全部 64 个基向量置换测试 |
| RECTANGLE 位序/S 盒/ShiftRow | 通过 | 原始规范列布局与全部 64 个基向量行旋转测试 |
| SPN 通用后缀 MILP | 待服务器 | 已提供单 S 盒精确 BDPT 交叉测试与模型复用测试 |
| LBlock 数据路径 | 通过 | 修订版规范的两组官方 32 轮测试向量 |
| LBlock keyed core | 通过 | 16 种 nibble 密钥穷举的三值可靠性测试 |
| LBlock 一轮 MILP | 待服务器 | 已提供精确公开 BDPT 交叉测试 |
| Table 5 PRESENT/RECTANGLE | 待服务器 | 已提供三组逐目标位检查点脚本 |
| Table 6 LBlock | 待服务器 | 已提供 16/17 轮逐目标位检查点脚本 |

## 本地测试结果

当前本地测试为：

```text
76 passed, 12 skipped
```

12 个跳过项全部位于 `tests/milp/`，原因是当前 Python 环境没有可用的 `gurobipy`。它们不是算法失败，也不能算作通过。

## 本地 Gurobi 环境

- Gurobi Optimizer：12.0.2；
- 对应 `gurobipy`：12.0.2，位于 Gurobi 自带 Python 3.11 环境；
- License 到期日：2026-06-10；
- 当前日期：2026-07-26。

创建模型时 Gurobi 明确返回 `License expired 2026-06-10`。实现将该错误映射为异常，不会映射为 `INFEASIBLE`。

## Table 3 服务器结果

服务器环境为 Python 3.11.15、Linux 6.8 和 Gurobi 13.0.2。14 轮 SIMON32 的内部目标位 16 得到 `zero`，停止原因为 `l_empty`，共执行 198 次 oracle 查询，用时约 7.54 秒。

观测到的轮边界规模为：

```text
K: 1, 0, 0, 0, 0, 0
L: 1, 1, 1, 2, 2, 0
```

这与论文 Table 3 完全一致。首次结果文件中的 `table3_prefix.matches=false` 来自报告脚本漏记“在一轮内部剪空后”的输出边界零值，不是模型失败；汇总逻辑现已修复并加入回归测试。

## 已确认论文勘误

SIMON 约束 \(L_3\) 的右端 `1` 与论文自身的 XOR Model 2 矛盾，实现采用右端 `0`。完整证据见 [paper-errata.md](paper-errata.md)。

## LBlock 局部分解说明

主论文的局部公式在同一个右半状态上逐 nibble 写入，同时又要求后续步骤读取旋转前的右半分量。实现没有按可能产生覆盖依赖的字面顺序编码，而是先完成公开的 8-bit 循环左移，再依次异或 8 个 keyed S 盒输出，最后交换两半。该电路与 LBlock 真实轮函数等价，且不会改变每轮 9 个搜索边界的数量。完整说明见 [lblock-model-note.md](lblock-model-note.md)。

## Table 5 首次冒烟结果说明

早期服务器运行中，PRESENT60 的内部目标 0 和 RECTANGLE60 的内部目标 0 均得到 `zero`，但继续计算发现 PRESENT60 的目标 4、8 与论文不符，因此这些结果整体作废，不能作为阶段验收。

根因是 S 盒 MILP 把 CBDP Rule 5 产生的全部候选输出直接当作 division trails，遗漏了 `Reduce0`。以 PRESENT 为例，错误模型包含 190 条候选转移，而 Xiang 等人的原始论文附录 B 明确给出约化后应为 47 条。该过近似会制造虚假可达路径并漏报 balanced 位。修复后，PRESENT/RECTANGLE 的约化 trail 数分别为 47/49，并由穷举测试验证附录 C 的 11/17 条紧凑不等式与它们完全等价。

PRESENT 原始规范明确规定 bit 0 位于分组最右侧，状态写为 \(b_{63}\cdots b_0\)，每个 nibble 为 \(b_{4i+3}\|b_{4i+2}\|b_{4i+1}\|b_{4i}\)。因此 Table 5 按 \(x_{63},\ldots,x_0\) 解析，PRESENT60 的预期 balanced 内部位是 0、4、8、12。曾尝试的 \(x_0,\ldots,x_{63}\) 配置在初始边界第一次 K 查询就返回 unknown，已证实不是论文实验的布局并予以撤回。

正确布局下，主论文 Algorithm 2 对目标 0 返回 zero，但目标 4、8、12 在轮密钥 Rule 4 产生 K 后返回 unknown，与 Table 5 不符。K-BDPT 对目标 4 的服务器实验同样返回 unknown，耗时约 845 秒、调用 oracle 7276 次；该路线现已暂停，不能用来替代对主论文的核验。

现已逐页检查主论文的全部 30 页，并把 Algorithm 2、PRESENT 的 17 部件轮划分、S 盒定理和停止规则逐项映射到实现。发现并修正了一处确定偏差：主论文第 412 页 Algorithm 2 第 22 行规定遍历全部部件后返回 one，主论文模式现严格遵守该终点规则。这不影响目标 4 在第二轮提前触发的 Stopping Rule 1。

为判断该提前停止究竟来自实现错误还是论文方法本身，Table 5 脚本新增 `--record-witness`：它会导出决定性 K 向量到目标单位向量的完整 CBDP trail，并使用独立代码逐个检查 47 条 PRESENT S 盒合法 transition 和位排列。只有该证据完成核验后，才会决定是否需要参考后续工作。详细审计见 `docs/main-paper-audit.md`。

LBlock63 的目标 32 在旧模型的首个后缀查询中长时间未返回。修复后的通用 S 盒扩展凸包只对约化后的 division trails 引入权重，不再对全部候选输出建模；仍需服务器的 S 盒穷举测试和 LBlock 一轮交叉测试确认性能与结果。

## 性能实现说明

- 固定 S 盒只保留 `Reduce0` 后的合法 CBDP division trails；
- PRESENT/RECTANGLE 使用原论文的 11/17 条紧凑不等式，其他 S 盒使用约化 trail 集的精确扩展凸包；
- 同一 Algorithm 2 边界内的后缀 MILP 会复用，仅修改输入/输出固定约束；
- 边界推进后释放旧模型，避免为所有边界同时保留大模型；
- 每个输出位写入一次 JSON 检查点，可安全断点续跑。

## 服务器验收顺序

1. 确认服务器 `gurobipy` 版本和 License 可用。
2. 运行全部测试，要求 `tests/milp/` 不再跳过。
3. 检查 SIMON 紧凑一轮模型与精确 BDPT 的交叉测试。
4. 运行 `experiments/reproduce_table3.py`。
5. 检查 JSON 中 `table3_prefix.matches` 是否为 `true`。
6. 对 Table 5/6 各选择一个论文标为 balanced 的目标位做冒烟测试。
7. 冒烟测试通过后运行全部输出位，检查每个 JSON 的 `comparison.matches`。
8. 汇总版本、耗时、oracle 查询数和逐边界轨迹，形成最终实验复现结论。

PRD 原开发顺序要求 SIMON 服务器阶段门通过后再扩展其他密码；用户在服务器暂不可用的情况下明确要求继续实现，因此当前只完成了后续模型与离线验证，没有越过“服务器结果通过”这一验收门。
