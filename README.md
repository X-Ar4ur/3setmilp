# 3setMILP

本项目独立复现论文 *MILP-aided Method of Searching Division Property Using Three Subsets and Applications* 及其后续工作 *Exploring Secret Keys in Searching Integral Distinguishers Based on Division Property* 中面向分组密码的三子集比特可分性分析方法。

当前状态：主论文的数学内核与 Tables 3--6，以及后续论文的 K-BDPT、SPECK、KATAN/KTANTAN、SIMON/SIMECK、SIMON(102)、PRESENT 和 RECTANGLE 模型及表格入口均已实现。受本机缺少 `gurobipy`/有效 License 的限制，新增端到端论文结果仍需在服务器验证，不能把“代码完成”表述为“实验复现成功”。后续论文的完整方法映射、逐密码分解、实验命令和论文缺失信息见 [docs/secret-key-paper-reproduction.md](docs/secret-key-paper-reproduction.md)。

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

Table 5 脚本默认执行主论文 Algorithm 2。`--algorithm bdpt-exact` 只修正伪代码末行无条件 `return 1` 的终态缺陷，改为读取最终 BDPT 的 zero/one/unknown；默认 `bdpt` 仍保留字面论文语义。后续论文的 K-BDPT 已完成逐页审计：`--algorithm k-bdpt` 使用论文 Example 2 所要求的终态三值语义；`--algorithm k-bdpt-literal` 严格按伪代码末行 `return 1`，仅用于诊断论文中已记录的终态歧义。不同模式不能混用检查点。完整证据和处理方案见 [docs/followup-paper-audit-and-solutions.md](docs/followup-paper-audit-and-solutions.md)。

Table 5 隐藏实验语义使用分阶段判别矩阵。省略 `--execute` 时只打印命令并生成待运行清单；服务器确认 Gurobi 可用后再执行。每个子实验使用独立检查点，汇总文件只把所有请求目标均为 `zero` 的配置列为候选：

```console
# Rule 4、零轮密钥、c=0000 与 c=1111 的最小判别集。
python experiments/run_table5_hypothesis_matrix.py smoke
python experiments/run_table5_hypothesis_matrix.py smoke --execute --record-witness

# 仅在 smoke 仍未闭合时，枚举四个 c 的全部 16 种赋值。
python experiments/run_table5_hypothesis_matrix.py constants --execute

# 测试逐轮重复的全一和两种交替固定轮密钥。
python experiments/run_table5_hypothesis_matrix.py fixed-keys --execute
```

固定轮密钥模式使用 `--key-treatment fixed --round-keys ...`，必须恰好为每轮提供一个 64-bit 值。该模式和 `ignore-rule4` 都是历史实验配置诊断，不是主论文任意密钥模型；其中全零固定轮密钥与 `ignore-rule4` 语义相同。

## 后续论文完整实验入口

后续论文 Table 2 的 SPECK 区分器。`compare` 会同时运行 K-BDPT 与原始 BDPT，并记录导致原始 BDPT 首次不精确的 \(k^0_7/k^0_8\)：

```console
python experiments/reproduce_secret_keys_table2_speck.py speck32 --targets 16
python experiments/reproduce_secret_keys_table2_speck.py speck48 new --targets 24
python experiments/reproduce_secret_keys_table2_speck.py speck64 new --targets 32
python experiments/reproduce_secret_keys_table2_speck.py speck96 new --targets 48
```

这些命令直接搜索论文 Table 2 的 6 轮性质；Table 1 的 7 轮数是在其前方使用 `[WLV+14]` 技巧外延一轮，论文明确说明 K-BDPT 不能直接搜索该外延轮。对应元数据见 `configs/secret_keys/table1.json`。

后续论文 Table 3 的 KATAN/KTANTAN 区分器。KATAN64 的 `73.6` 轮按原密码每轮三次更新解释为 \(73\times3+2=221\) 个时钟：

```console
python experiments/reproduce_secret_keys_table3_katan.py katan32 --targets 31
python experiments/reproduce_secret_keys_table3_katan.py katan48 --targets 47
python experiments/reproduce_secret_keys_table3_katan.py katan64 --targets 63
```

后续论文 Table 5 的 SIMON(102) 精确常量位：

```console
python experiments/reproduce_secret_keys_table5_simon102.py simon10232 --targets 16 30 31
python experiments/reproduce_secret_keys_table5_simon102.py simon10248 --targets 24 46 47
python experiments/reproduce_secret_keys_table5_simon102.py simon10264 --targets 32 62 63
```

这里直接搜索 19/27/35 轮；Table 1 的 20/28/36 轮同样包含前置一轮外延。

后续论文没有列出普通 SIMON/SIMECK 各变体的完整输入、轮数与输出模式，因此项目提供要求显式参数的入口，不虚构论文未公开配置：

```console
python experiments/run_secret_keys_simon_family.py simeck32 \
  --rounds 10 \
  --input-pattern caaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaa \
  --targets 31 \
  --output output/results/simeck32_custom.json
```

后续论文 Table 6 的 PRESENT/RECTANGLE 数据与主论文表格相同，继续复用 `reproduce_table5_spn.py`，但显式选择 `--algorithm k-bdpt`。

Table 5 的 `c` 默认表示论文中“取值未给定的固定常量”，不能默认当作 0。若只想诊断全部常量值已知的特定 cube，可显式指定输入模式中 `c` 的论文打印顺序：

```console
python experiments/reproduce_table5_spn.py present60 --algorithm k-bdpt --constant-values 0101 --targets 4 --output output/results/present60_k_bdpt_known_0101_target4.json
```

K-BDPT 的轮密钥标量扫描顺序在后续论文中没有给定。默认 `ascending` 保持原有内部 bit `0 -> 63` 的诊断语义；`descending` 是独立对照，不会静默改变默认复现。使用 `--record-witness` 时，检查点还会导出每个失败旁路的 `L'_i`、阻塞 CBDP 输入向量和经重放验证的轨迹。

```console
# 标准未知常量初态下，仅测试反序轮密钥扫描。
python experiments/reproduce_table5_spn.py present60 \
  --algorithm k-bdpt \
  --key-bit-order descending \
  --targets 4 \
  --record-witness \
  --output output/results/table5_present60_k_bdpt_key_descending_target4.json
```

已知常量赋值仅作诊断，先在默认升序下枚举四个 `c` 的 16 种赋值；每个结果使用独立检查点，便于中断后续跑：

```console
for c in 0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111; do
  python experiments/reproduce_table5_spn.py present60 \
    --algorithm k-bdpt \
    --constant-values "$c" \
    --targets 4 \
    --output "output/results/table5_present60_k_bdpt_known_${c}_target4.json"
done
```

若某个目标位由 Stopping Rule 1 返回 unknown，可使用 `--record-witness` 重新求解决定性 K 向量，导出完整 CBDP trail，并逐个核验 S 盒 transition 和位排列：

```console
python experiments/reproduce_table5_spn.py present60 --targets 4 --record-witness --output output/results/table5_present60_bdpt_target4_witness.json
```

为定位 Rectangle 新增平衡位是否全部受轮密钥 Rule 4 影响，可运行显式对照模式。该模式只保留公开置换、不从 `L` 生成 `K`，因此不属于主论文 Algorithm 2，结果只能用于诊断：

```console
python experiments/reproduce_table5_spn.py rectangle60 \
  --key-treatment ignore-rule4 \
  --targets 10 12 17 \
  --record-witness \
  --output output/results/table5_rectangle60_bdpt_ignore_rule4_smoke.json
```

若上述三位均变为 balanced，再测试论文相对 CBDP 新增的全部 11 位：

```console
python experiments/reproduce_table5_spn.py rectangle60 \
  --key-treatment ignore-rule4 \
  --targets 10 12 17 19 20 24 25 28 29 30 31 \
  --record-witness \
  --output output/results/table5_rectangle60_bdpt_ignore_rule4_added11.json
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
