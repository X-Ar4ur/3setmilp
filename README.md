# 3setMILP

本项目独立复现论文 *MILP-aided Method of Searching Division Property Using Three Subsets and Applications* 中面向分组密码的三子集比特可分性分析方法。

当前状态：分组密码侧的数学内核、Algorithm 1/2、SIMON、PRESENT、RECTANGLE 和 LBlock 模型及 Tables 3--6 实验入口均已实现。受本机 Gurobi License 限制，端到端论文结果仍需在服务器验证，不能把“代码完成”表述为“实验复现成功”。项目范围和验收标准见 [docs/PRD.md](docs/PRD.md)。

## 本地测试

项目要求 Python 3.11 或更高版本。不含求解器的数学测试只依赖 pytest：

```powershell
python -m pytest
```

CBDP-MILP 通过服务器环境中与许可证匹配的 `gurobipy` 运行。

## 服务器上的 Gurobi 验证

先确认服务器现有 Python 环境能够导入与许可证匹配的 Gurobi：

```console
python -c "import gurobipy as gp; print(gp.gurobi.version())"
```

然后安装本项目。不要为了本项目盲目升级服务器的 `gurobipy`：

```console
python -m pip install -e . --no-deps
python -m pip install "pytest>=8"
python -m pytest
```

真实 Gurobi 测试在没有 `gurobipy` 或有效 License 时会明确跳过。服务器上应确认测试汇总中不存在 `tests/milp/` 的跳过项。

复现论文 Table 3 中 SIMON32 最右侧输出位的剪枝轨迹：

```powershell
python experiments/reproduce_table3.py
```

默认配置为 14 轮、输入打印最左侧位 \(x_{15}\) 固定、目标为打印最右侧位 \(y_0\)。结果写入 `output/results/`。任何 Gurobi 未确定状态都会终止实验，不会被解释为 balanced。

逐位复现 Table 4，并在每个目标位结束后保存检查点：

```console
python experiments/reproduce_table4_simon.py simon32
python experiments/reproduce_table4_simon.py simon64
```

可用 `--targets 16 23 30` 只运行指定内部位。重复执行同一命令会跳过检查点中已完成的目标位。

复现 Table 5 的三组 SPN 实验：

```console
python experiments/reproduce_table5_spn.py present60
python experiments/reproduce_table5_spn.py present63
python experiments/reproduce_table5_spn.py rectangle60
```

Table 5 使用逐密码显式 layout：PRESENT 按规范的 `x63,...,x0`，RECTANGLE 按 row0--row3 且每行 column15--column0。PRESENT/RECTANGLE 的 CBDP S 盒分别使用原论文附录的 11/17 条紧凑不等式。若服务器上存在早期版本生成的 Table 5 检查点，请先改名保存；新脚本会拒绝混用旧位序、搜索算法或未约化 S 盒结果。

Table 5 脚本默认执行主论文 Algorithm 2。后续论文的 `--algorithm k-bdpt` 入口仍保留为实验代码，但在主论文方法完成审计前不作为 Table 5 的验收路径。主论文的逐页审计记录见 [docs/main-paper-audit.md](docs/main-paper-audit.md)。

若某个目标位由 Stopping Rule 1 返回 unknown，可使用 `--record-witness` 重新求解决定性 K 向量，导出完整 CBDP trail，并逐个核验 S 盒 transition 和位排列：

```console
python experiments/reproduce_table5_spn.py present60 --targets 4 --record-witness --output output/results/table5_present60_bdpt_target4_witness.json
```

复现 Table 6 的 LBlock 实验：

```console
python experiments/reproduce_table6_lblock.py lblock63
python experiments/reproduce_table6_lblock.py lblock62
```

建议先各运行一个论文预期 balanced 的目标位作为服务器冒烟测试：

```console
python experiments/reproduce_table5_spn.py present60 --targets 4 --record-witness --output output/results/table5_present60_bdpt_target4_witness.json
python experiments/reproduce_table5_spn.py rectangle60 --targets 0
python experiments/reproduce_table6_lblock.py lblock63 --targets 32
```

所有逐位脚本都支持 `--time-limit`、`--gurobi-log`、`--output` 和断点续跑。只要某次求解没有严格证明可行或不可行，脚本就会停止，绝不会把超时解释为 balanced。

LBlock 使用与真实轮函数等价的“先旋转右半、再执行 8 个 keyed core、最后交换”分解。采用该分解的原因和校验证据见 [docs/lblock-model-note.md](docs/lblock-model-note.md)。
