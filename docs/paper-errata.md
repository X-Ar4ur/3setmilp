# 论文疑点与勘误记录

本文档只记录已经通过定义、公式或独立测试获得证据的问题。尚未确认的解释不会作为实现依据。

## 1. SIMON 的 \(L_3\) 约束右端

### 论文位置

*MILP-aided Method of Searching Division Property Using Three Subsets and Applications*，正文第 414 页，SIMON 一轮 CBDP trail 描述。

论文打印为：

\[
L_3:\quad a_j^{i+1}-b_j^i-t_j^i-w_{(j-2)\bmod n}^i=1.
\]

### 判断

右端的 `1` 是排版错误，实现应采用 `0`：

\[
a_j^{i+1}=b_j^i+t_j^i+w_{(j-2)\bmod n}^i.
\]

### 证据

1. 同一论文第 406 页的 Model 2 将 XOR 的 CBDP transition 定义为“输出变量等于全部输入变量之和”。
2. SIMON 轮函数对应位为

   \[
   a_j^{i+1}=b_j^i\oplus t_j^i\oplus w_{(j-2)\bmod n}^i.
   \]

   因此按 Model 2 应得到右端为 0 的线性等式。
3. 若右端取 1，因为变量均为二进制且右侧输入之和非负，等式只允许

   ```text
   a_next = 1, b = t = w = 0
   ```

   这既排除了全部正常 XOR division transition，也与论文 Model 2 直接矛盾。
4. 项目的基本 XOR transition 已由穷举测试验证为：

   ```text
   00 -> 0
   10 -> 1
   01 -> 1
   ```

   这对应等式 `output - sum(inputs) = 0`。

### 实现原则

- SIMON 紧凑 MILP 模型采用右端 0。
- 服务器实验报告必须注明此修正。
- 不为匹配论文结果保留右端 1 的隐藏兼容分支；如需比较，只能作为显式诊断实验。

## 2. Algorithm 2 第 22 行的无条件 `return 1`

### 论文位置

主论文第 412 页 Algorithm 2 第 22 行；后续论文 Algorithm 1 的末行沿用了
相同写法。

### 判断

全部局部函数传播完成后，不能无条件返回 1。应读取最终输出 BDPT 中目标单位
向量的真实 zero/one/unknown，或追加一个输出恒等边界并再次执行剪枝。

### 证据

1. Algorithm 2 在每个局部函数的输入边界分别保留能够通过 CBDP 到达目标的
   `L` 向量；“每个向量各自可达”不保证它们在精确 BDPT 传播后的贡献为奇数。
2. 两个 surviving `L` 向量可以在最后一个公开函数中对同一输出单项式各贡献
   一次，最终按模 2 抵消为 zero。
3. 最后一个局部函数也可能由 `L` 生成 `K`；若没有新的边界检查，字面末行仍
   会错误返回 one。
4. 后续论文 Example 2 明确依赖这种末端抵消。按字面 `return 1` 执行时，该
   例无法得到论文声称的密钥旁路结果。

### 实现原则

- `search_bdpt()` 保留字面 `return 1`，用于审计论文原算法；
- `search_bdpt_exact()` 读取最终三值，作为主论文修正模式；
- `search_k_bdpt()` 使用后续论文 Example 2 要求的正确终态；
- 各模式写入不同的算法版本和检查点，禁止静默混用。
