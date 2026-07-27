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
| Table 3 | 待服务器 | 已提供运行脚本 |
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
65 passed, 10 skipped
```

10 个跳过项全部位于 `tests/milp/`，原因是当前 Python 环境不能使用有效的 Gurobi License。它们不是算法失败，也不能算作通过。

## 本地 Gurobi 环境

- Gurobi Optimizer：12.0.2；
- 对应 `gurobipy`：12.0.2，位于 Gurobi 自带 Python 3.11 环境；
- License 到期日：2026-06-10；
- 当前日期：2026-07-26。

创建模型时 Gurobi 明确返回 `License expired 2026-06-10`。实现将该错误映射为异常，不会映射为 `INFEASIBLE`。

## 已确认论文勘误

SIMON 约束 \(L_3\) 的右端 `1` 与论文自身的 XOR Model 2 矛盾，实现采用右端 `0`。完整证据见 [paper-errata.md](paper-errata.md)。

## LBlock 局部分解说明

主论文的局部公式在同一个右半状态上逐 nibble 写入，同时又要求后续步骤读取旋转前的右半分量。实现没有按可能产生覆盖依赖的字面顺序编码，而是先完成公开的 8-bit 循环左移，再依次异或 8 个 keyed S 盒输出，最后交换两半。该电路与 LBlock 真实轮函数等价，且不会改变每轮 9 个搜索边界的数量。完整说明见 [lblock-model-note.md](lblock-model-note.md)。

## 性能实现说明

- 固定 S 盒的非法 CBDP transition 已缓存；
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
