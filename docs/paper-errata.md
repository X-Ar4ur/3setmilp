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

