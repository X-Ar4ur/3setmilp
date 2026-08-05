# 基于 MILP 辅助的三子集可分性搜索方法及其应用

王森鹏<sup>(B)</sup>，胡斌，关杰，张凯，石泰荣

中国郑州，解放军信息工程大学，wsp2110@126.com

摘要。Division property 是 Todo 在 EUROCRYPT 2015 上提出的一种广义积分性质，随后 Todo 和 Morii 在 FSE 2016 上提出了传统的基于比特的 division property（CBDP）以及使用三个子集的基于比特的 division property（BDPT）。最初，由于巨大的时间和内存复杂度，这两类基于比特的 division property 一度无法应用于大分组长度的密码。在 ASIACRYPT 2016 上，Xiang 等人将混合整数线性规划（MILP）方法扩展到基于 CBDP 搜索积分区分器。BDPT 能够比 CBDP 找到更精确的积分区分器，但它无法被高效建模。

本文重点研究基于 BDPT 搜索积分区分器的可行性。我们首次提出了 BDPT 的剪枝技术和快速传播方法。在此基础上，提出了一种用于 BDPT 传播的 MILP 辅助方法。随后，我们将该方法应用于若干分组密码。对于 SIMON64、PRESENT 和 RECT-ANGLE，我们找到了比先前最长区分器更多的平衡比特。对于 LBlock，我们找到了一种更优的 16 轮积分区分器，其活跃比特更少。对于其他分组密码，我们的结果与先前最长区分器一致。

立方攻击是针对对称密码系统的一种重要密码分析技术，尤其适用于流密码。而立方攻击中最重要的步骤是超多项式恢复。受 Todo 在 CRYPTO 2017 提出的基于 CBDP 的立方攻击启发，我们提出了一种使用 BDPT 在立方攻击中恢复超多项式的方法。我们将这一新方法应用于轮数缩减的 Trivium。具体而言，在 CRYPTO 2017 中，恢复 832 轮 Trivium 的超多项式的时间复杂度从 $2 ^ { 7 7 }$ 降至实际可行；在 CRYPTO 2018 中，恢复 839 轮 Trivium 的超多项式的时间复杂度从 $2 ^ { 7 9 }$ 降至实际可行。随后，我们提出了一种理论攻击，可恢复最高至 841 轮 Trivium 的超多项式。

关键词：积分区分器 划分性质 MILP 分组密码 Cube 攻击 流密码

# 1 引言

Division property 是 integral property [11] 的推广，由 Todo 于 EUROCRYPT 2015 [22] 提出。即使分组密码具有非双射、按比特导向或低代数次数的结构，它也能够利用分组密码的代数结构构造 integral distinguisher。随后，在 CRYPTO 2015 [20] 上，Todo 将这一新技术应用于 MISTY1，并实现了对完整轮数 MISTY1 的首次理论密码分析。Sun 等人 [18] 重新审视了 division property，并研究了满足某种 division property 的集合（多重集）的性质。在 CRYPTO 2016 [4] 上，Boura 和 Canteaut 引入了一个称为 parity set 的新概念来利用 division property。他们对 S-box 的 division property 进行了公式化描述和刻画，并找到了 PRESENT [3] 更优的 integral distinguisher。但这需要很大的时间和存储复杂度。为了解决这一问题，Xie 和 Tian [28] 提出了另一个称为 term set 的概念，并据此找到了一个具有 22 个平衡比特的 9 轮 PRESENT distinguisher。

为了利用轮函数的具体结构，Todo 和 Morii [21] 在 FSE 2016 上提出了基于比特的 division property。基于比特的 division property 有两种：传统的基于比特的 division property（CBDP）和使用三个子集的基于比特的 division property（BDPT）。CBDP 关注的是奇偶性 $\bigoplus _ { x \in \mathbb { X } } x ^ { u }$ 为 0 或未知，而 BDPT 关注的是奇偶性 $\oplus { \pmb x } ^ { \pmb { u } }$ 为 0、1 或未知。因此，BDPT 能够找到更精确的积分 x X

相比 CBDP 更强。例如，CBDP 证明了 SIMON32 的 14 轮积分区分器的存在性，而 BDPT 找到了 SIMON32 的 15 轮积分区分器 [21]。

尽管 CBDP 和 BDPT 能够找到准确的积分区分器，但巨大的复杂性一度限制了它们的广泛应用。2016 年 ASIACRYPT 上，Xiang 等人 [27] 将 MILP 方法应用于基于 CBDP 搜索积分区分器，从而使他们能够分析规模更大的分组密码。但当时仍然没有用于刻画 BDPT 传播的 MILP 方法。

Cube attack（立方攻击）由 Dinur 和 Shamir [6] 在 EUROCRYPT 2009 上提出，是针对对称密码体制的一类通用密码分析技术。对于一个具有 $n$ 个秘密变量 ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \dots , x _ { n - 1 } )$ 和 $m$ 个公开变量 $\pmb { v } = ( v _ { 0 } , v _ { 1 } , \dots , v _ { m - 1 } )$ 的密码，其输出比特可表示为一个多项式 $f \left( \pmb { x } , \pmb { v } \right)$ 。立方攻击的核心思想是通过对一组称为 cube 的公开变量求和来简化 $f \left( { \pmb x } , { \pmb v } \right)$ 。立方攻击的目标是从称为 superpoly 的简化多项式中恢复秘密变量。在立方攻击的原始论文 [6] 中，作者将流密码视为一个黑盒多项式，并引入了线性性测试来恢复 superpoly。近年来，人们提出了许多立方攻击的变体，例如动态立方攻击 [7]、条件立方攻击 [14]、相关立方攻击 [15]、基于 CBDP 的立方攻击 [23,26] 以及确定性立方攻击 [30]】【。

在 EUROCRYPT 2018 [15] 上，Liu 等人提出了相关立方攻击，该攻击可利用低维立方体攻击 835 轮 Trivium。随后，在 [30] 中，Ye 等人提出了一种新的立方攻击变体，称为确定性立方攻击。他们的攻击建立在 Liu 等人在 CRYPTO 2017 [16] 提出的次数评估方法之上。他们提出了一种特殊类型的立方体，其每一项的数值次数始终小于或等于立方体大小，称为有用立方体。利用一个 37 维有用立方体，他们恢复了对应的精确 superpoly，适用于最多 838 轮 Trivium。然而，正如作者在论文中所写，随着立方体大小的增加，提高攻击轮数似乎很困难。也就是说，他们的方法在大规模立方体上并不适用。此外，在 CRYPTO 2018 [9] 上，Fu 等人提出了针对 855 轮 Trivium 的密钥恢复攻击，该攻击在某种程度上类似于动态立方攻击。对于 [9] 中的攻击，论文 [12] 指出，正确密钥猜测与错误密钥猜测有可能共享相同的零和性质。这意味着该密钥恢复攻击可能退化为区分攻击。

值得注意的是，在 CRYPTO 2017 [23] 上，Todo 等人将多项式视为非黑盒，并将 CBDP 应用于流密码的立方攻击。由于有 MILP 辅助的 CBDP，他们能够在大立方维数下评估超多项式的代数正规形（ANF）。通过使用一个 72 维立方，他们提出了针对 832 轮 Trivium 的理论立方攻击。随后，在 CRYPTO 2018 [26] 上，Wang 等人改进了基于 CBDP 的立方攻击，并给出了针对 839 轮 Trivium 的密钥恢复攻击。对于基于 CBDP 的立方攻击，大立方的超多项式可以通过理论方法恢复。但 CBDP 的理论不能保证一个立方的超多项式是非常数。因此，该密钥恢复攻击可能仅仅是一种区分攻击。BDPT 能够利用其求和为 1 的积分区分器，这意味着 BDPT 可能给出一种确定的密钥恢复攻击。然而，与 CBDP 的传播相比，BDPT 的传播更为复杂，不能直接用 MILP 方法建模。文献 [13] 提出了用 STP 求解器自动搜索一种变体三子集 division property 的方法，但该变体弱于原始 BDPT。如何跟踪 BDPT 的传播仍是一个开放问题。

## 1.1 我们的贡献

In this paper, we propose an MILP-aided method for BDPT. Then, we apply it to search integral distinguishers of block ciphers and recover superpolies of stream ciphers.

### 1.1.1 用于 BDPT 的 MILP 辅助方法

BDPT 的剪枝性质。当我们评估 BDPT 的传播时，可能存在一些对输出比特的 BDPT 没有影响的向量。因此，我们给出 BDPT 的向量可以被移除时的剪枝性质。

快速传播与停止规则。受 [21] 中“惰性传播”的启发，我们提出“快速传播”的概念，该概念能够将 BDPT 转化为 CBDP，并表明某些比特是平衡的。随后，基于“惰性传播”和“快速传播”，我们得到三条停止规则。最后，提出了一种用于 BDPT 传播的 MILP 辅助方法。

### 1.1.2 分组密码积分区分器的搜索

我们将所提出的 MILP 辅助方法应用于搜索若干分组密码的积分区分器。主要结果如表 1 所示。

ARX 密码。对于 SIMON32，我们找到了 CBDP 无法找到的 15 轮积分区分器。对于 18 轮 SIMON64，我们找到了 23 个平衡比特，比此前最长的积分区分器多一个比特。

SPN 密码。对于 PRESENT，当输入数据量为 $2 ^ { 6 0 }$ 时，我们的方法相比此前最长的积分区分器可以找到多 3 个平衡比特。此外，当输入数据量为 $2 ^ { 6 3 }$ 时，我们得到的积分区分器相比文献 [28] 中通过项集得到的积分区分器多 6 个平衡比特。对于 RECTANGLE，当输入数据量为 $2 ^ { 6 0 }$ 时，我们的方法相比此前最长的 9 轮积分区分器也可以获得多 11 个平衡比特。

Generalized Feistel 密码。对于 LBlock，我们得到了一个 17 轮积分区分器，与此前最长的积分区分器相同。此外，还可以得到一个具有更少活跃比特的更优 16 轮积分区分器。

### 1.1.3 恢复流密码的超多项式

使用 BDPT 恢复超多项式的 ANF 系数。受 [23,26] 中基于 CBDP 的立方攻击启发，我们的新方法基于 BDPT 的传播，它能够找到和为 0 或 1 的积分区分器。但是，利用基于 BDPT 的积分区分器来恢复超多项式并非易事。因此，我们提出了相似多项式的概念。通过研究相应相似多项式的 BDPT 传播，我们可以恢复超多项式的 ANF 系数。为了更好地分析密码的安全性，我们将密码分为两类：公开更新密码和秘密更新密码。对于公开更新密码，我们证明了超多项式的精确 ANF 可以通过 BDPT 被完全恢复。

Trivium 应用。为验证我们方法的正确性和有效性，我们将 BDPT 应用于恢复轮数缩减的公开密码 Trivium 的超多项式。具体而言，CRYPTO 2017 中恢复 832 轮 Trivium 超多项式的时间复杂度从 $2 ^ { 7 7 }$ 降低到实际可行；CRYPTO 2018 中恢复 839 轮 Trivium 超多项式的时间复杂度从 $2 ^ { 7 9 }$ 降低到实际可行。随后，我们提出了一种理论攻击，可恢复最多 841 轮 Trivium 的超多项式。详细信息如表 2 所示。表中的时间复杂度表示恢复超多项式的时间复杂度。c 为使用 MILP 辅助方法追踪 BDPT 传播的平均计算复杂度。

表 1. 积分区分器的总结

<table><tr><td>密码</td><td>数据</td><td>轮数</td><td>平衡比特数</td><td>时间</td><td>参考文献</td></tr><tr><td rowspan="2">SIMON32</td><td rowspan="2"> $2^{31}$ </td><td>15</td><td>3</td><td></td><td>[21]</td></tr><tr><td>15</td><td>3</td><td>2m</td><td>第 5.1 节</td></tr><tr><td rowspan="2">SIMON64</td><td rowspan="2"> $2^{63}$ </td><td>18</td><td>22</td><td>6.7m</td><td>[27]</td></tr><tr><td>18</td><td>23</td><td>1h41m</td><td>第 5.1 节</td></tr><tr><td rowspan="4">PRESENT</td><td rowspan="2"> $2^{60}$ </td><td>9</td><td>1</td><td>3.4m</td><td>[27]</td></tr><tr><td>9</td><td>4</td><td>56m</td><td>第 5.2 节</td></tr><tr><td rowspan="2"> $2^{63}$ </td><td>9</td><td>22</td><td></td><td>[28]</td></tr><tr><td>9</td><td>28</td><td>10m</td><td>第 5.2 节</td></tr><tr><td rowspan="2">RECTANGLE</td><td rowspan="2"> $2^{60}$ </td><td>9</td><td>16</td><td>4.1m</td><td>[27]</td></tr><tr><td>9</td><td>27</td><td>10m</td><td>第 5.2 节</td></tr><tr><td rowspan="4">LBlock</td><td rowspan="3"> $2^{63}$ </td><td>16</td><td>32</td><td>4.9m</td><td>[27]</td></tr><tr><td>17</td><td>4</td><td></td><td>[8]</td></tr><tr><td>17</td><td>4</td><td>10h25m</td><td>第 5.3 节</td></tr><tr><td> $2^{62}$ </td><td>16</td><td>18</td><td>6h49m</td><td>第 5.3 节</td></tr></table>

表 2. Trivium 的超多项式恢复

<table><tr><td>轮数</td><td>立方大小</td><td>精确超多项式</td><td>复杂度</td><td>参考文献</td></tr><tr><td rowspan="3">832</td><td rowspan="3">72</td><td rowspan="3">是</td><td> $2^{77}$ </td><td>[23]</td></tr><tr><td> $2^{76.7}$ </td><td>[26]</td></tr><tr><td>实际可行</td><td>第 7.3 节</td></tr><tr><td>835</td><td>36/37</td><td>否</td><td></td><td>[15]</td></tr><tr><td>838</td><td>37</td><td>是</td><td>实际可行</td><td>[30]</td></tr><tr><td rowspan="2">839</td><td rowspan="2">78</td><td rowspan="2">是</td><td> $2^{79}$ </td><td>[26]</td></tr><tr><td>实际可行</td><td>第 7.3 节</td></tr><tr><td>841</td><td>78</td><td>是</td><td> $2^{41} \cdot c$ </td><td>第 7.4 节</td></tr></table>

## 1.2 论文结构

本文的结构如下：第 2 节介绍 MILP、division property 以及 cube attack 等背景。第 3 节给出 BDPT 的若干新的传播性质。第 4 节提出一种用于 BDPT 的 MILP 辅助方法。第 5 节展示其在分组密码中的应用。第 6 节使用 BDPT 来恢复 cube attack 中的 superpoly。第 7 节展示其在 Trivium 上的应用。第 8 节对全文进行总结。附录中提供了一些辅助材料。

# 2 预备知识

## 2.1 记号

设 $\mathbb { F } _ { 2 }$ 表示由 0 和 1 组成的有限域，且 $\textbf { \em a } = ~ ( a _ { 0 } , a _ { 1 } , \ldots , a _ { n - 1 } ) ~ \in ~ \mathbb { F } _ { 2 } ^ { n }$ 为一个 n 比特向量，其中 $a _ { i }$ 表示 $\boldsymbol { a }$ 的第 $i$ 位。对于 n 比特向量 $x$ 和 $u$，定义 $\begin{array} { r } { \pmb { x } ^ { u } = \prod _ { i = 0 } ^ { n - 1 } x _ { i } ^ { u _ { i } } } \end{array}$。那么，对于任意 $\boldsymbol { k } \in \mathbb { F } _ { 2 } ^ { n }$ 和 $\boldsymbol { k } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { n }$，若对所有 $i = 0 , 1 , \ldots , n - 1$ 都有 $k _ { i } \geq k _ { i } ^ { \prime }$，则定义 $k \succeq k ^ { \prime }$；若对所有 $i = 0 , 1 , \ldots , n - 1$ 都有 $k _ { i } > k _ { i } ^ { \prime }$，则定义 $k \succ k ^ { \prime }$。对于子集 $I \subset \{ 0 , 1 , \ldots , n - 1 \}$，$u$ 表示一个 n 维比特向量 $\left( u _ { 0 } , u _ { 1 } , \ldots , u _ { n - 1 } \right)$，满足当 $i \in I$ 时 $u _ { i } = 1$，否则 $u _ { i } = 0$。当 $\mathbb { K } : = \mathbb { K } \cup \{ k \}$ 时，我们简记为 $\mathbb { K } \gets k$；当 $\mathbb { K } : = \mathbb { K } \setminus \{ k \}$ 时，我们简记为 $\mathbb { K } \to k$。并且 $K$ 表示集合 $\mathbb { K }$ 中元素的个数。

## 2.2 混合整数线性规划

MILP 是一种优化或可行性规划，其目标函数和约束均为线性的，且变量被限制为整数。一般而言，一个 MILP 模型由变量 .var、约束 .con 和目标函数 .obj 组成。MILP 模型可以由 Gurob 等求解器求解 [10]。如果不存在可行解，求解器将返回 infeasible。当 中没有目标函数时，MILP 求解器将只返回其是否可行。

## 2.3 基于比特的 division property

Todo 和 Morii 在 FSE 2016 [21] 上提出了两种基于比特的 division property（CBDP 和 BDPT）。在本小节中，我们将简要介绍它们及其传播规则。

定义 1（CBDP [21]）。设 X 为一个多重集，其元素取值于 $\mathbb { F } _ { 2 } ^ { n }$。当多重集 X 具有 CBDP $\mathcal { D } _ { \mathbb { K } } ^ { 1 ^ { n } }$ 时，其中 K 表示一个由 n 维向量组成的集合，其第 i 个元素取 0 到 1 之间的值，它满足以下条件：

$$
\bigoplus_ {\boldsymbol {x} \in \mathbb {X}} \boldsymbol {x} ^ {\boldsymbol {u}} = \left\{ \begin{array}{l l} \text { 未知，若存在 } \boldsymbol {k} \in \mathbb {K} \text { 满足 } \boldsymbol {u} \succeq \boldsymbol {k}, \\ 0, & \text { 否则。 } \end{array} \right.
$$

定义 2（BDPT [21]）。设 X 是一个多重集，其元素取值于 $\mathbb { F } _ { 2 } ^ { n }$。设 K 和 L 是两个集合，其元素为 n 维比特向量。当多重集 X 具有 BDPT $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$ 时，它满足以下条件：

$$
\bigoplus_ {\boldsymbol {x} \in \mathbb {X}} \boldsymbol {x} ^ {\boldsymbol {u}} = \left\{ \begin{array}{l l} \text { 未知，若存在 } \boldsymbol {k} \in \mathbb {K} \text { 满足 } \boldsymbol {u} \succeq \boldsymbol {k}, \\ 1, & \text { 否则，若存在 } \boldsymbol {\ell} \in \mathbb {L} \text { 满足 } \boldsymbol {u} = \boldsymbol {\ell}, \\ 0, & \text { 其他情况。 } \end{array} \right.
$$

根据 [21]，如果存在 $k \in \mathbb { K }$ 和 $\pmb { k } ^ { \prime } \in \mathbb { K }$ 满足 $k \succeq k ^ { \prime }$，则可以将 $k$ 从 K 中删除，因为向量 $k$ 是冗余的。我们将这一过程记为 Reduce0 (K)。如果存在 $\ell \in \mathbb { L }$ 和 $k \in \mathbb { K }$ 满足 $\ell \succeq k$，则向量 - 也可以从 L 中删除。我们将这一过程记为 Reduce1 (K, L)。对于任意 $u$，K 和 L 中的冗余向量不会影响 - $\pmb { x } ^ { u }$ 的值

CBDP 中 K 的传播规则与 BDPT 相同。因此这里我们只展示 BDPT 的传播规则。更多细节请参见 [21]。

BDPT 规则 1（复制 [21]）。设 $\begin{array} { r } { \begin{array} { r c l } { { \pmb { y } } } & { { = } } & { { \pmb { f } \left( { \pmb x } \right) } } \end{array} } \end{array}$ 为一个复制函数，其中 $\begin{array} { r c l } { { \pmb x } } & { { = } } & { { \left( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } \right) \quad \in \quad { \mathbb { F } } _ { 2 } ^ { n } } } \end{array}$，且输出计算为 $\begin{array} { r l } { \pmb { y } } & { { } = } \end{array}$ $( x _ { 0 } , x _ { 0 } , x _ { 1 } , \dotsc , x _ { n - 1 } )$。假设输入多重集 X 具有 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$，则输出多重集 Y 具有 $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n + 1 } }$，其中

$$
\mathbb {K} ^ {\prime} \leftarrow \left\{ \begin{array}{l l} (0, 0, k _ {1}, \ldots , k _ {n - 1})  , & \text { 如果   } k _ {0} = 0 \\ (1, 0, k _ {1}, \ldots , k _ {n - 1})  , (0, 1, k _ {1}, \ldots , k _ {n - 1})  , & \text { 如果   } k _ {0} = 1 \end{array} \right.,
$$

$$
\mathbb {L} ^ {\prime} \leftarrow \left\{ \begin{array}{l l} (0, 0, \ell_ {1}, \ldots , \ell_ {n - 1})  , & 若   \ell_ {0} = 0 \\ (1, 0, \ell_ {1}, \ldots , \ell_ {n - 1})  , (0, 1, \ell_ {1}, \ldots , \ell_ {n - 1})  , (1, 1, \ell_ {1}, \ldots , \ell_ {n - 1})  , & 若   \ell_ {0} = 1 \end{array} \right.,
$$

分别由所有 $k \in \mathbb { K }$ 和所有 $\ell \in \mathbb { L }$ 计算得到。

BDPT 规则 2（And [21]）。令 $\begin{array} { r } { \mathbf { \boldsymbol { y } } = \mathbf { \boldsymbol { f } } \left( \mathbf { \boldsymbol { x } } \right) } \end{array}$ 为一个由 And 压缩的函数，其中输入为 $\pmb { x } = ( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n }$，输出计算为 $\pmb { y } = ( x _ { 0 } \wedge x _ { 1 } , x _ { 2 } , \dots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n - 1 }$。假设输入多重集 X 具有 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } } ,$，则输出多重集 Y 具有 $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n - 1 } }$，其中 $\mathbb { K } ^ { \prime }$ 由所有 $k \in \mathbb { K }$ 计算得到，如下所示：

$$
\mathbb {K} ^ {\prime} \leftarrow \left(\left\lceil \frac {k _ {0} + k _ {1}}{2} \right\rceil , k _ {2}, \dots , k _ {n - 1}\right),
$$

并且 $\mathbb { L } ^ { \prime }$ 是由 $\mathbb { L }$ 中所有满足 $( \ell _ { 0 } , \ell _ { 1 } ) = ( 0 , 0 ) \ o r \ ( 1 , 1 )$ 的 $\ell$ 计算得到的，如

$$
\mathbb {L} ^ {\prime} \leftarrow \left(\left\lceil \frac {\ell_ {0} + \ell_ {1}}{2} \right\rceil , \ell_ {2}, \dots , \ell_ {n - 1}\right).
$$

BDPT 规则 3（异或 [21]）。令 ${ \pmb y } = f \left( { \pmb x } \right)$ 为一个由 $X o r ,$ 压缩的函数，其中输入 $\pmb { x } = ( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n }$，输出计算为 $\pmb { y } = ( x _ { 0 } \oplus x _ { 1 } , x _ { 2 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n - 1 }$。假设输入多重集 X 具有 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } } ,$，则输出多重集 Y 具有 $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n - 1 } }$，其中 $\mathbb { K } ^ { \prime }$ 由所有满足 $\left( k _ { 0 } , k _ { 1 } \right) = \left( 0 , 0 \right) , \left( 1 , 0 \right) , o r \left( 0 , 1 \right)$ 的 $k \in \mathbb { K }$ 计算得到，如下所示：

$$
\mathbb {K} ^ {\prime} \leftarrow (k _ {0} + k _ {1}, k _ {2}, \dots , k _ {n - 1}),
$$

$\mathbb { L } ^ { \prime }$ 由所有满足 $( \ell _ { 0 } , \ell _ { 1 } ) = ( 0 , 0 ) , ( 1 , 0 ) , \text { 或 } ( 0 , 1 )$ 的 $\ell \in \mathbb { L }$ 计算得到，作为

$$
\mathbb {L} ^ {\prime} \stackrel {{x}} {{\leftarrow}} \left(\ell_ {0} + \ell_ {1}, \ell_ {2}, \dots , \ell_ {n - 1}\right).
$$

而 $\mathbb { L }  \ell$ 表示

$$
\mathbb {L} := \left\{ \begin{array}{l} \mathbb {L} \cup \{\boldsymbol {\ell} \} \text {   若   原始的   } \mathbb {L} \text {   不包含   } \boldsymbol {\ell}, \\ \mathbb {L} \setminus \{\boldsymbol {\ell} \} \text {   若   原始的   } \mathbb {L} \text {   包含   } \boldsymbol {\ell}. \end{array} \right.
$$

BDPT 规则 4（与秘密密钥异或 [21]）。设 X 为满足 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { \hat { n } } }$ 的输入多重集。对于输入 $\textbf { \em x } \in \mathrm { ~ \mathbb ~ X ~ }$，输出 $y \in \mathbb { Y }$ 计算为 $\pmb { y } = ( x _ { 0 } , \ldots , x _ { i - 1 } , x _ { i } \oplus r _ { k } , x _ { i + 1 } , \ldots , x _ { n - 1 } )$，其中 $r _ { k }$ 为秘密密钥。则输出多重集 Y 具有 $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } ; } ^ { 1 ^ { n } }$，其中 K 和 $\mathbb { L } ^ { \prime }$ 计算如下：

$$
\mathbb {L} ^ {\prime} \leftarrow \ell , \text{对于} \ell \in \mathbb {L},
$$

$$
\mathbb {K} ^ {\prime} \leftarrow \boldsymbol {k}, \text{对于 } \boldsymbol {k} \in \mathbb {K},
$$

$$
\mathbb {K} ^ {\prime} \leftarrow (\ell_ {0}, \ell_ {1}, \dots , \ell_ {i} \vee 1, \dots , \ell_ {n - 1}), \text{对于满足 } \ell_ {i} = 0 \text{ 的 } \ell \in \mathbb {L}.
$$

CBDP 规则 5（S 盒 [4,27]）。设 $\pmb { y } = f \left( \pmb { x } \right)$ 为一个 S 盒函数，其中输入 $\pmb { x } = ( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n }$，输出 $\pmb { y } = ( y _ { 0 } , y _ { 1 } , \dots , y _ { m - 1 } ) \in \mathbb { F } _ { 2 } ^ { m }$。则每个 $y _ { i } , i \in \{ 0 , 1 , \dotsc , m - 1 \}$ 都可以表示为 $( x _ { 0 } , \ldots , x _ { n - 1 } )$ 的一个布尔函数。对于输入 CBDP $K$，输出 CBDP $\mathbb { K } ^ { \prime }$ 是如下所示的向量集合：

$\mathbb { K } ^ { \prime } = \{ \pmb { u } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { m } |$ 对任意 $\pmb { u } \in \mathbb { K } , \ 若 \ y ^ { \pmb { u } ^ { \prime } }$ 包含任一满足 $v \succeq u$ 的项 $\pmb { x } ^ { v } \rbrace$

当时尚无有效方法对 BDPT 的传播进行建模，Todo 和 Morii [21] 提出了“惰性传播”的概念，以给出 SIMON 家族抵抗 BDPT 的可证明安全性。

定义 3（惰性传播 [21]）。令 $D _ { \mathbb { K } _ { i } , \mathbb { L } _ { i } } ^ { 1 ^ { n } }$ 为第 i 轮函数的输入 BDPT，令 $D _ { \mathbb { K } _ { i + 1 } , \mathbb { L } _ { i + 1 } } ^ { 1 ^ { n } }$ 为由惰性传播得到的 BDPT。则 $\overline { { \mathbb { K } } } _ { i + 1 }$ 仅由 $\mathbb { K } _ { i }$ 中的一部分向量计算得到，而 $\overline { { \mathbb { L } } } _ { i + 1 }$ 总是变为空集 $\varnothing .$。因此，如果惰性传播生成了 $\mathcal { D } _ { \mathbb { K } _ { r } , \varnothing } ^ { 1 ^ { n } }$，其中 $\overline { { \mathbb { K } } } _ { r }$ 含有 n 个不同的、汉明重量为一的向量，则精确传播也会在同一轮生成相同的 n 个不同向量。

## 2.4 CBDP 的 MILP 表示

对于规模为 $n ,$ 的 $r$ 轮迭代密码，攻击者确定指标集 $I =$ $\left\{ i _ { 0 } , i _ { 1 } , \dotsc , i _ { | I | - 1 } , \right\} \subset \left\{ 0 , 1 , \dotsc , n - 1 \right\}$，并准备 $2 ^ { | I | }$ 个选择明文，其中由 I 索引的变量取遍所有可能的取值组合，而其他变量被设置为常数。此类选择明文的 CBDP 为 $\mathscr { D } _ { \mathbb { K } _ { 0 } = \{ k _ { I } \} } ^ { 1 ^ { n } }$。基于传播规则，从 $\boldsymbol { \mathcal{ D } _ { \{ k_{ I } \} } ^ { 1 } }_{ } ^ { n }$ 出发的 CBDP 传播可表示为 $\{ \pmb { k } _ { I } \} \overset { d e f } { = } \mathbb { K } _ { 0 }  \mathbb { K } _ { 1 }  \cdots  \mathbb { K } _ { r }$，其中 $\mathcal { D } _ { \mathbb { K } _ { r } } ^ { 1 ^ { n } }$ 是经过 $r$ 轮传播后的 CBDP。如果集合 $\mathbb { K } _ { r }$ 不含单位向量 $\boldsymbol { e _ { m } } \in \mathbb { F } _ { 2 } ^ { n }$（其仅第 $m$ 个元素为 1），则 $r$ 轮密文的第 $m$ 个输出比特是平衡的。在 ASIACRYPT 2016 上，Xiang 等人 [27] 将 MILP 方法应用于 CBDP 的传播。他们首先引入了 CBDP 特征的概念，其定义如下。

定义 4（CBDP 迹 [27]）。考虑 CBDP $\{ \pmb { k } _ { I } \} \overset { d e f } { = } \mathbb { K } _ { 0 }  \mathbb { K } _ { 1 }  \cdots  \mathbb { K } _ { r }$ 的传播。对于任意向量 $\pmb { k } _ { i + 1 } \in \mathbb { K } _ { i + 1 }$，必定存在一个向量 $\boldsymbol { k } _ { i } \in \mathbb { K } _ { i }$，使得 $k _ { i }$ 能够通过 CBDP 的传播规则传播到 $\pmb { k } _ { i + 1 }$。此外，对于 $( \pmb { k } _ { 0 } , \pmb { k } _ { 1 } , \dots , \pmb { k } _ { r } ) \in \mathbb { K } _ { 0 } \times \mathbb { K } _ { 1 } \times \dots \times \mathbb { K } _ { r }$，如果对于所有 $i \in \{ 0 , 1 , \ldots r - 1 \}$，$k _ { i }$ 都能够传播到 $k _ { i + 1 }$，则称 $k _ { 0 } \to k _ { 1 } \to \cdot \cdot \cdot \to k _ { \prime }$ 为一个 r 轮 CBDP 迹。

在 [27] 中，作者用线性不等式对基本运算（Copy、Xor、And）和 S 盒的 CBDP 传播进行了建模。因此，他们能够构建一个 MILP 模型，以覆盖由给定初始 CBDP 生成的所有可能 CBDP 路径。这里，我们介绍 Copy、Xor、And 和 S 盒的 MILP 模型。

模型 1（Copy [27]）。设 $a \xrightarrow { C o p y } ( b _ { 0 } , b _ { 1 } , \dots , b _ { n - 1 } )$ 为 Copy 的一条 CBDP 迹。以下不等式足以描述其 CBDP 传播。

$$
\left\{ \begin{array}{l} \mathcal {M}. v a r \leftarrow a, b _ {0}, b _ {1}, \ldots , b _ {n - 1}   \text{为二进制变量}, \\ \mathcal {M}. c o n \leftarrow a = b _ {0} + b _ {1} + \dots + b _ {n - 1}. \end{array} \right.
$$

模型 2（Xor [27]）。设 $( a _ { 0 } , a _ { 1 } , \ldots , a _ { n - 1 } ) \ \xrightarrow { X o r }$ b 为 Xor 的一条 division trail。以下不等式足以描述其 CBDP 传播

$$
\left\{ \begin{array}{l} \mathcal {M}. v a r \leftarrow a _ {0}, a _ {1}, \ldots , a _ {n - 1}, b \text {为二进制变量}, \\ \mathcal {M}. c o n \leftarrow b = a _ {0} + a _ {1} + \dots + a _ {n - 1}. \end{array} \right.
$$

模型 3（And [27]）。设 $( a _ { 0 } , a _ { 1 } , \dotsc , a _ { n - 1 } ) \ { \xrightarrow { A n d } }$ b 为 And 的一个 division trail。以下不等式足以描述其 CBDP 传播。

$$
\left\{ \begin{array}{l} \mathcal {M}. v a r \leftarrow a _ {0}, a _ {1}, \ldots , a _ {n - 1}, b \text { 为二进制变量 }, \\ \mathcal {M}. c o n \leftarrow b \geq a _ {i} \text { 对所有 } i \in \{0, 1, \ldots , n - 1 \}. \end{array} \right.
$$

模型 4（S 盒 [27]）。第 2.3 节中的 CBDP 规则 5 可以生成 S 盒的 CBDP 传播性质。然后，我们可以使用 Sage 软件 [17] 中的 inequality_generator() 函数得到一组线性不等式。有时该集合中的线性不等式数量很大。因此，有人提出了一些贪心算法 [1,19] 来缩减该集合。

## 2.5 立方攻击

立方攻击由 Dinur 和 Shamir 在 EUROCRYPT 2009 上提出 [6]。对于具有 n 个秘密变量 ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \dots , x _ { n - 1 } )$ 和 m 个公开变量 $\pmb { v } = ( v _ { 0 } , v _ { 1 } , \dots , v _ { m - 1 } )$ 的密码，其输出比特可以表示为 $f ( { \pmb x } , { \pmb v } )$。攻击者确定一个索引子集 $I _ { v } = \{ i _ { 0 } , i _ { 1 } , \ldots , i _ { | I _ { v } | - 1 } \} \subset \{ 0 , 1 , \ldots , m - 1 \}$，则 $f ( { \pmb x } , { \pmb v } )$ 可以唯一地表示为

$$
f (\boldsymbol {x}, \boldsymbol {v}) = \boldsymbol {v} ^ {\boldsymbol {u} _ {I _ {v}}} \cdot p (\boldsymbol {x}, \boldsymbol {v}) \oplus q (\boldsymbol {x}, \boldsymbol {v}),
$$

其中 $p \left( { \pmb x } , { \pmb v } \right)$ 称为 $f \left( \pmb { x } , \pmb { v } \right)$ 中 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 的超多项式，并且 ${ \bf { \nabla } } q \left( { { \bf { x } } , { \bf { v } } } \right)$ 中的每一项都至少缺少 $\{ v _ { i _ { 0 } } , v _ { i _ { 1 } } , \ldots , v _ { i _ { | I _ { v } | - 1 } } \}$ 中的一个变量。

攻击者可以准备一个记为 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 的 cube 集，其中下标由 $I _ { v }$ 索引的公开变量取遍所有可能的取值组合，下标由 $J _ { v } \subset \{ 0 , 1 , \dotsc , m - 1 \} - I _ { v }$ 索引的公开变量被设为常数 1，而下标由 $K _ { v } = \{ 0 , 1 , \cdots , m - 1 \} - I _ { v } - J _ { v }$ 索引的公开变量被设为常数 0。如下所示：

$$
C _ {I _ {v}, J _ {v}, K _ {v}} = \left\{\boldsymbol {v} \in \mathbb {F} _ {2} ^ {m} \mid v _ {i} \in \mathbb {F} _ {2} \text {   若   } i \in I _ {v}, v _ {j} = 1 \text {   若   } j \in J _ {v}, v _ {k} = 0 \text {   若   } k \in K _ {v} \right\}\tag{1}
$$

此外，$f \left( { \pmb x } , { \pmb v } \right)$ 在立方集合 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 上的求和为

$$
\bigoplus_ {\boldsymbol {v} \in C _ {I _ {v}, J _ {v}, K _ {v}}} f (\boldsymbol {x}, \boldsymbol {v}) = p _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}).\tag{2}
$$

如果 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 不是常数多项式，攻击者可以使用所选立方体集 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 查询加密预言机，以获得包含秘密变量的方程。

## 2.6 基于 CBDP 的立方攻击

在 CRYPTO 2017 [23]，Todo 等人成功地将 CBDP 应用于立方攻击。他们使用 CBDP 来分析超多项式的 ANF 系数。

引理 1. [23] 设 $f \left( \pmb { x } \right) = \bigoplus _ { \pmb { u } \in \mathbb { F } _ { 2 } ^ { n } } \boldsymbol { a } _ { \pmb { u } } ^ { f } \cdot \pmb { x } ^ { \pmb { u } }$ 是一个从 $\mathbb { F } _ { 2 } ^ { n }$ 到 $\mathbb { F } _ { 2 }$ 的多项式，且 $a _ { u } ^ { f } \in \mathbb { F } _ { 2 }$ 为其 ANF 系数。设 k 为一个 n 维比特向量。若不存在满足 k $\underline { { f } } _ {  1 }$ 的 CBDP 路径，则对于 ${ \boldsymbol { \mathbf { \mathit { u } } } } \succeq k $，$a _ { u } ^ { f }$ 恒为 0。

命题 1. [23] 设 $f \left( \pmb { x } , \pmb { v } \right)$ 为一个多项式，其中 $\pmb { x } \in \mathbb { F } _ { 2 } ^ { n }$ 和 $\pmb { v } \in \mathbb { F } _ { 2 } ^ { m }$ 分别表示秘密变量和公开变量。对于按式 (1) 定义的立方集合 $C _ { I _ { v } , J _ { v } , K _ { v } }$，令 $e _ { i }$ 为一个 n 比特单位向量，其唯一的第 i 个元素为 1。若不存在 CBDP 迹使得 $( e _ { i } , \boldsymbol { u } _ { I _ { v } } ) \xrightarrow { f } 1$，则 $x _ { i }$ 不参与立方 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 的超多项式。

当 $f \left( \pmb { x } , \pmb { v } \right)$ 表示目标密码的输出比特时，我们可以通过检查是否存在分割试验 $\{ ( e _ { i } , \boldsymbol { u } _ { I _ { v } } ) \} \stackrel { f } { \longrightarrow } 1$（其中 $i = 0 , 1 , \cdots , n - 1$），使用 MILP 方法来识别所涉及的密钥集合 $I$。随后，在 CRYPTO 2018 [26] 上，Wang 等人提出了度数界定和项枚举技术，以进一步降低恢复超多项式的复杂度。对超多项式的度数评估基于以下命题。

命题 2. [26] 对于集合 $I _ { x } = \left\{ i _ { 0 } , i _ { 1 } , . . . , i _ { | I _ { x } | - 1 } \right\} \subset \left\{ 0 , 1 , . . . , n - 1 \right\}$，如果不存在使得 $( \boldsymbol { u } _ { I _ { x } } , \boldsymbol { u } _ { I _ { v } } ) \overset { f } { \longrightarrow } 1$ 的 CBDP 迹，则 ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ 不包含在立方 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 的超多项式中。

在得到所涉及密钥集合 $I$ 和 superpoly 的次数 $d$ 之后，superpoly 可以表示为 $\textstyle \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } }$ 个系数。因此，通过选取 ${ \textstyle \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } }$ 个不同的 $x$，可以构造一个包含 ${ \textstyle \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } }$ 个变量的线性方程组。然后，通过求解这样的线性方程组，可以恢复 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 的整个 ANF。因此，恢复立方 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 的 superpoly 的复杂度为 $\begin{array} { r } { 2 ^ { | I _ { v } | } \times \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } } \end{array}$

# 3 BDPT 的传播性质

在本节中，我们将探讨 BDPT 的一些新的传播性质。

## 3.1 S-盒的 BDPT 传播

在第 2.3 节中，我们已经介绍了 Copy、And 和 Xor 的现有 BDPT 传播规则。尽管任何布尔函数都可以使用这三条规则进行求值，但当布尔函数较为复杂时，该传播需要较大的时间复杂度和内存复杂度。在此，我们提出一种计算 S 盒 BDPT 传播的广义方法。

定理 1. 对于一个 S 盒：$\mathbb { F } _ { 2 } ^ { n } \ \to \ \mathbb { F } _ { 2 } ^ { m }$，令 ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \dots , x _ { n - 1 } )$ 和 ${ \textbf { 3 } } =$ $\left( y _ { 0 } , y _ { 1 } , \dotsc , y _ { m - 1 } \right)$ 分别表示输入和输出。每个 $y _ { i } , i \in \{ 0 , 1 , \dotsc , m - 1 \}$ 都可以表示为 $( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } )$ 的布尔函数。如果 S 盒的输入 BDPT 为 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } = \{ \ell \} } ^ { 1 ^ { n } }$，则 S 盒的输出 BDPT 可由 $\mathcal { D } _ { R e d u c e { \theta } ( \underline { { \mathbb { K } } } ) } ^ { 1 ^ { m } }$ <sub>K L</sub> 计算，其中

$\mathbb { E } = \{ \pmb { u } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { m } \}$ 对于任意 $\mathbf { \pmb { u } } \in \mathbb { K }$，若 $\boldsymbol { y } ^ { u ^ { \prime } }$ 包含任意满足 ${ \pmb v } \succeq { \pmb u } \rbrace$ 的项 $\pmb { x } ^ { v }$ $\mathbb { L } = \{ \pmb { u } \in \mathbb { F } _ { 2 } ^ { m } | \pmb { y } ^ { u }$ 包含项 ${ \pmb x } ^ { \ell } \}$

证明。设 $\mathbb { K } ^ { \prime }$ 为不含冗余向量的输出 BDPT 集合。根据第 2.3 节中的 CBDP 规则 5，我们知道 $\mathbb { K } ^ { \prime } = R e d u c e { \theta } \left( \underline { { \mathbb { K } } } \right)$

设 $\mathbb { L } ^ { \prime }$ 为不含冗余向量的输出 BDPT 集。对于任意 $\textbf { \em u } \in \mathbb { L } ^ { \prime }$，有 $\oplus \boldsymbol { y } ^ { u } = 1$。由于输入 L 中只有一个向量 -，$\pmb { y } \in \mathbb { Y }$。

$y ^ { u }$ 的 ANF 必须含有单项式 $\scriptstyle { \mathbf { } } x ^ { \ell }$。因此，我们得到 $\mathbb { L } ^ { \prime } \subset \underline { { \mathbb { L } } }$。由于函数 Reduce1 仅移除满足 - y<sup>u</sup> = unknown 的向量，我们 y Y

有 $\mathbb { L } ^ { \prime } \subset$ Reduce1 (K, L).

另一方面，如果 $y ^ { u }$ 包含单项式 $\scriptstyle { \mathbf { } } x ^ { \ell }$，则有 $\bigoplus _ { x \in \mathbb { X } } { \pmb { y } } ^ { u }$ 等于 unknown 或 1。对于集合 L，函数 Reduce1 会移除所有满足 $\oplus \ y ^ { u } = u n k n o w n$ 的向量。因此，所有剩余向量都满足 $\oplus y ^ { u } = 1$ y Y y Y T1

于是，我们得到 Reduce1 $( \underline { { \mathbb { K } } } , \underline { { \mathbb { L } } } ) \subset \mathbb { L } ^ { \prime }$

综上，我们得到 L = Reduce1 $( \underline { { \mathbb { K } } } , \underline { { \mathbb { L } } } )$

我们将定理 1 应用于 SIMON 族的核心运算，所得的 BDPT 传播规则与 [21] 中的规则一致。注意，当输入 L 仅含一个向量时，定理 1 可以得到 BDPT 传播规则。若 L 中有更多向量，文献 [21] 已给出一个如何得到其 BDPT 传播规则的例子。设 ${ \mathcal { D } } _ { \mathbb { K } , \mathbb { L } = \{ \ell _ { 0 } , \ell _ { 1 } , \dots , \ell _ { r - 1 } \} } ^ { 1 ^ { n } }$ 和 $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { m } }$ 分别为 S 盒的输入和输出 BDPT。根据定理 1，我们可以由相应的输入 BDPT $\mathcal { D } _ { \mathbb { K } , \mathbb { L } = \{ \ell _ { i } \} }$ 得到输出 BDPT $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } _ { i } ^ { \prime } } ^ { 1 ^ { m } }$，其中 $i = 0 , 1 , \ldots , r - 1$。然后，

$$
\mathbb {L} ^ {\prime} = \{\ell | \ell \text { 在集合 } \mathbb {L} _ {0} ^ {\prime}, \mathbb {L} _ {1} ^ {\prime}, \dots , \mathbb {L} _ {r - 1} ^ {\prime} \text { 中出现奇数次 } \}.
$$

我们还在第 5.1 节给出一个例子，以帮助读者理解 BDPT 的传播。

## 3.2 BDPT 的剪枝技术

以往的工作通常将密码划分为 r 轮，并研究轮函数的 CBDP 或 BDPT。轮函数往往包含过多操作，会产生许多冗余的 division property 中间向量。当轮数或分组长度增大时，仅由于复杂度就会使传播变得不可行。为了解决这一问题，我们将密码划分为较小的部分。并且在得到某一部分的 BDPT 传播之后，我们将使用剪枝技术去除冗余向量。随后，BDPT 中剩余的向量可以继续高效地传播。

设 $Q _ { i }$ 为 r 轮密码 $E = Q _ { r } \circ Q _ { r - 1 } \circ$ $\cdots \circ Q _ { 1 }$ 的第 i 轮轮函数，则我们将 $Q _ { i }$ 划分为 $l _ { i }$ 个部分 $Q _ { i } \ = \ Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 } ,$ 令 $E _ { i , j } \ = \ ( Q _ { i , j - 1 } \circ Q _ { i , j - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 } ) \circ ( Q _ { i - 1 } \circ Q _ { i - 2 } \circ \cdot \cdot \cdot \circ Q _ { 1 } )$ 且 ${ \overline { { E _ { i , j } } } } ~ =$ $\left( Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { i + 1 } \right) \left( Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdots \circ Q _ { i , j } \right)$，则 $E = \overline { { E _ { i , j } } } \circ E _ { i , j }$，其中 $1 \leq i \leq r , 0 \leq j \leq l _ { i } - 1$，且 $E _ { 1 , 0 }$ 为恒等函数。

定理 2（剪枝 K）。对于 r 轮密码 $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { 1 }$ ，令 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 为 $\overline { { E _ { i , j } } }$ 的输入 BDPT。对于任意向量 $\boldsymbol { k } \in \mathbb { K } _ { i , j }$ ，如果不存在使得 k $\xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ 的 CBDP 迹，则 $\boldsymbol { \mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } } }$ 的 BDPT 传播与 $\mathcal { D } _ { \mathbb { K } _ { i , j }  k , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 的 BDPT 传播在判定 $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ 以及 $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 }$ 是否成立方面是等价的。

证明。在第 2.3 节中，我们知道，对于公开函数，$\mathbb { K } _ { i , j }$ 和 $\mathbb L _ { i , j }$ 的 BDPT 传播是相互独立的。只有当异或秘密轮密钥时，$\mathbb L _ { i , j }$ 中的一些向量才会影响 $\mathbb { K } _ { i , j }$，但它们只会向 $\mathbb { K } _ { i , j }$ 中加入一些向量。由于每个向量 $\boldsymbol { k } \in \mathbb { K } _ { i , j }$ 都基于 CBDP 独立传播，如果不存在使得 $k \xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ 的 CBDP 迹，那么将其从 $\mathbb { K } _ { i , j }$ 中移除，并不会影响 ${ \mathbb K } _ { r + 1 , 0 }$ 是否包含 $e _ { m }$。这意味着，在 ${ \mathbb K } _ { r + 1 , 0 }$ 是否包含 $e _ { m }$ 这一点上，$\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { \mathbf { i } ^ { n } }$ 与 $\mathcal { D } _ { \mathbb { K } _ { i , j }  k , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 具有相同的结果。

因为 $\mathbb { L } _ { r + 1 , 0 }$ 中的所有向量都是由 $\mathbb L _ { i , j }$ 生成的，也就是说，从 $\mathbb { K } _ { i , j }$ 中移除 k 不会影响 $e _ { m } \in \mathbb { L } _ { r + 1 , 0 } .$ 的生成。另一方面，我们已经得到，从 $\mathbb { K } _ { i , j }$ 中移除 k 不会对 ${ \mathbb K } _ { r + 1 , 0 }$ 是否包含 $e _ { m }$ 产生任何影响。因此，它不会影响对 $e _ { m } \in \mathbb { L } _ { r + 1 , 0 } .$ 的约简。这意味着，在判断 $\mathbb { L } _ { r + 1 , 0 }$ 是否包含 $e _ { m }$ 时，$\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 与 $\mathcal { D } _ { \mathbb { K } _ { i , j }  k , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 具有相同的结果。 -

定理 3（剪枝 L）。对于 $r$ 轮密码 $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { 1 }$，令 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 为 $\overline { { E _ { i , j } } }$ 的输入 BDPT。对于任意向量 $\ell \in \mathbb { L } _ { i , j }$，如果不存在 CBDP 轨迹使得 $\ell \stackrel { \overline { { E _ { i , j } } } } { \longrightarrow } e _ { m }$，则在判断 $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ 以及 $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 }$ 是否成立方面，$\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 的 BDPT 传播等价于 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j }  \ell } ^ { 1 ^ { n } }$ 的 BDPT 传播。

证明。对于任意向量 $\ell \in \mathbb { L } _ { i , j }$，若根据定理 2，不存在使得 $\ell \stackrel { \overline { { E _ { i , j } } } } { \longrightarrow } e _ { m }$ 2 的 CBDP trail，则 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 的 BDPT 传播与 $\mathcal { D } _ { \mathbb { K } _ { i , j }  \ell , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 的 BDPT 传播在判定 $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ 以及 $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 } \mathrm { ~ o r ~ }$ not 方面是等价的。

因为 ${ \mathbb K } _ { i , j } ~ \gets ~ \ell .$ ，根据 BDPT 的定义，向量 - 可以从 $\mathbb L _ { i , j }$ 中移除。因此，BDPT $\mathcal { D } _ { \mathbb { K } _ { i , j }  \ell , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 与 $\mathcal { D } _ { \mathbb { K } _ { i , j } \left. \ell , \mathbb { L } _ { i , j } \right. \ell } ^ { 1 ^ { n } } .$ 完全等价。

再次根据定理2，$\mathcal { D } _ { \mathbb { K } _ { i , j } \left. \ell , \mathbb { L } _ { i , j } \right. \ell } ^ { 1 ^ { n } }$ 的 BDPT 传播与 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j }  \ell } ^ { 1 ^ { n } }$ 的传播等价，这取决于 $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ 以及 $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 }$ 是否成立。

CBDP 的传播可以通过 MILP 模型高效求解。因此，定理 2 和定理 3 的意义在于，我们可以使用 CBDP 方法来缩减 BDPT 集合 $\mathbb { K } _ { i , j }$ 和 $\mathbb L _ { i , j }$

## 3.3 快速传播

受“惰性传播”概念的启发，我们提出一种称为“快速传播”的概念，用以表示输出比特的平衡信息。

定义 5（快速传播）。对于 $r$ 轮密码 $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdot \cdot \cdot \circ Q _ { 1 }$，令 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 为 $\overline { { E _ { i , j } } }$ 的输入 BDPT。在快速传播下，我们将该 BDPT 转换为 CBDP $\mathcal { D } _ { \mathbb { K } _ { i , j } } ^ { 1 ^ { n } }$，其中 $\overline { { \mathbb { K } } } _ { i , j } = \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j }$。$\overline { { E _ { i , j } } }$ 的输出 CBDP 由 $\mathcal { D } _ { \mathbb { K } _ { i , j } } ^ { 1 ^ { n } }$ 计算得到。

“快速传播”移除了 $\mathbb L _ { i , j }$ 中的所有向量，并得到并集 $\mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j }$ 。从本质上讲，“快速传播”将 BDPT 转化为 CBDP。我们可以使用 MILP 方法来求解 $\boldsymbol { \mathcal { D } } _ { \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 的 CBDP 传播。让我们考虑“快速传播”的含义。设 $\overline { { E _ { i , j } } }$ 的输入集具有 BDPT $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ ，根据 BDPT 和 CBDP 的定义，该集合也必然具有 CBDP $\overset { \cdot } { \mathcal { D } } _ { \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 。若对于任意 $\pmb { k } \in \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j }$ ，都不存在使得 $k \xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ 的 CBDP 试验，则 $\overline { { E _ { i , j } } }$ 的第 $m$ 个输出比特是平衡的。

# 4 BDPT 的 MILP 辅助方法

基于 [27] 的工作，我们首先简化了基于 CBDP 搜索积分区分器的 MILP 算法，以提高效率。然后，我们给出三条停止规则，并提出一种基于 BDPT 搜索积分区分器的算法。

## 4.1 简化 CBDP 的 MILP 方法

采用文献 [27] 中的方法，我们可以得到一个线性不等式集合，用以描述在给定初始 CBDP ${ \mathcal { D } } _ { \{ k \} } ^ { 1 ^ { n } }$ 下的 $r$ 轮 CBDP 区分轨迹。先前的 CBDP 方法会返回一组平衡比特。由于只需要一个比特的平衡信息，因此我们的 MILP 模型没有目标函数，而是将其加入约束条件中。我们可以使用求解器 Gurobi [10] 来判断该 MILP 模型是否有可行解。若存在可行解，则表明输出的第 $m$ 位未知；否则，第 $m$ 位是平衡的。详细信息见算法 1。

## 4.2 终止规则

基于“lazy propagation”和“fast propagation”，在本小节中，我们提出了三种用于基于 BDPT 搜索积分区分器的停止规则。

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
算法 1. SCBDP(E, k, m)

<div>

输入：密码体 `E`，初始 `CBDP` 向量 `k`，以及数 `m`  
输出：基于 `CBDP`，输出的第 `m` 位是否平衡

1 begin  
2 `L` 是一个线性不等式集合，用于描述 `CBDP` 划分轨迹，使得 $k \xrightarrow{E} e_{m}$  
3 if `L` has feasible solutions do  
4 return unknown  
5 else  
6 return 0  
7 end

</div>

停止规则 1。对于一个 r 轮密码 $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdot \cdot \cdot \circ Q _ { 1 }$，令 $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ 为 $\overline { { E _ { i , j } } }$ 的输入 BDPT。对于任意向量 $\boldsymbol { k } \in \mathbb { K } _ { i , j }$，若存在 CBDP 迹使得 k $\xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$，则根据“惰性传播”，我们停止该过程，并得到 E 的第 m 个输出比特是未知的。

在停止规则 1 之后，如果搜索过程未停止，则根据定理 2 中的剪枝技术，$\mathbb { K } _ { i , j }$ 中的所有向量都将被移除。然后，我们考虑如下停止规则 2。

停止规则 2. 在根据定理 3 中的剪枝技术去除集合 $\mathbb L _ { i , j }$ 中的冗余向量后，如果集合 $\mathbb { L } _ { i , j }$ 中仍存在向量 $\ell$，则我们不能停止该过程，并且应基于 BDPT 将其传播到下一部分。若在 $\mathbb L _ { i , j ; }$ 中不存在向量，根据“快速传播”，可得到 $E$ 的第 $m$ 个输出比特是平衡的。

不同于表明第 $m$ 位未知的停止规则 1，停止规则 2 可以基于 BDPT 表明第 $m$ 位是平衡的。即使我们得到了 $E .$ 的输出 BDPT，如果过程仍然没有停止，停止规则 3 可以解释这种情况。

停止规则 3. 如果 $\mathbb { K } _ { r + 1 , 0 } = \varnothing$ 且 $\mathbb { L } _ { r + 1 , 0 } = \{ e _ { m } \}$，则我们找到一个积分区分器，其第 m 个输出比特的和为 1。

## 4.3 基于 BDPT 搜索积分区分器的 MILP 辅助方法

搜索积分区分器的算法通常从给定的初始 BDPT $\mathcal { D } _ { \mathbb { K } _ { 1 , 0 } , \mathbb { L } _ { 1 , 0 } } ^ { 1 ^ { n } }$ 开始。对于指标集合 $I = \{ i _ { 0 } , i _ { 1 } , \dotsc , i _ { | I | - 1 } \} \subset \{ 0 , 1 , \dotsc , n - 1 \}$，攻击者准备 $2 ^ { | I | }$ 个选择明文，其中由 $I$ 索引的变量取所有可能的取值组合，而其余变量设为常数。此类选择明文的 CBDP 为 $\mathcal { D } _ { \{ u _ { I } \} } ^ { 1 ^ { n } }$。于是，此类选择明文的 BDPT 为 $\mathcal { D } _ { \mathbb { K } _ { 1 , 0 } , \mathbb { L } _ { 1 , 0 } }$，其中 $\mathbb { K } _ { 1 , 0 } = \{ \pmb { u } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { \acute { n } } | \pmb { u } ^ { \prime } \succ \pmb { u } _ { I } \}$ 且 $\mathbb { L } _ { 1 , 0 } = \{ { \pmb u } _ { I } \}$。我们在算法 2 中展示整个框架。

```csv
算法 2. BDPT(E, L1,0, K1,0, m)

输入：密码 E，输入 BDPT D_{K1,0, L1,0}，以及数值 m
输出：基于 BDPT 的第 m 个输出比特的平衡信息

1 begin
2    for (i = 1; i ≤ r; i++) do
3    for (j = 0; j ≤ l_i - 1; j++) do
4    for k in K_{i,j}
5    if SCBDP(E_{i,j}, k, m) 未知
6    return 未知
7    else
8    K_{i,j} → k
9    end
10    L'_{i,j} = ∅
11    for ℓ in L_{i,j} do
12    if SCBDP(E_{i,j}, ℓ, m) 未知
13    L'_{i,j} = L'_{i,j} ∪ ℓ
14    end
15    end
16    if L'_{i,j} = ∅
17    return 0
18    end
19    D_{K_{i+[(j+1)/l_i], (j+1)modl_i}, L_{i+[(j+1)/l_i], (j+1)modl_i}} = BDPTP(Q_{i,j}, D_{0, L'_{i,j}})
20    end
21    end
22    return 1
23 end
```

我们逐行解释算法 2：

密码 \(E\) 被划分为若干小部分。

对于每个 $\boldsymbol { k } \in \mathbb { K } _ { i , j }$，如果 $S C B D P \left( \overline { { E _ { i , j } } } , k , m \right)$ 是未知的（算法 1），则根据停止规则 1，我们知道基于 BDPT 的第 m 个输出比特是未知的。否则，根据定理 2 中的剪枝技术，将其从 $\mathbb { K } _ { i , j }$ 中移除。

第 10 行 初始化 $\mathbb { L } _ { i , j } ^ { \prime }$ 为空集。

对于任意向量 $\ell \in \mathbb { L } _ { i , j }$，如果 $S C B D P ( \overline { { E _ { i , j } } } , \ell , m )$ 能够生成单位向量 $e _ { m }$，则将所有这些向量存储在 $\mathbb { L } _ { i , j } ^ { \prime }$ 中。

若集合 $\mathbb { L } _ { i , j } ^ { \prime }$ 为空集，则其满足停止规则 2，即第 m 个输出比特是平衡的。

如果我们没有得到第 \(m\) 位的平衡信息，则应使用 BDPT 的传播规则来获得下一部分的输入 BDPT。

它触发停止规则 3，且第 m 个输出比特的和为 1。

划分轮函数 $Q _ { i }$ 的原则是使 BDPT 的向量不扩展过多。只有这样，我们才能高效地运行搜索算法。算法 2 可以给出任意输出比特的平衡信息。因此，我们可以并行搜索密码的积分区分器。

# 5 分组密码中的应用

在本节中，我们将我们的算法应用于 SIMON、SIMECK、PRESENT、RECT-ANGLE 和 LBlock。所有实验均在如下平台上进行：Intel Core i5-4590 CPU @3,3 GHz，8.00G RAM。我们用于求解 MILP 模型的优化器是 Gurobi 8.1.0 [10]。对于积分区分器，需要说明的是，“a”表示活跃比特，“c”表示常数比特，“?”表示平衡信息未知，“b”表示平衡比特。

## 5.1 在 SIMON 和 SIMECK 中的应用

SIMON 是一个基于 Feistel 结构的轻量级分组密码族 [2]，仅涉及按位 And、Xor 和循环移位操作。令 SIMON2n 表示分组长度为 2n 比特的 SIMON 密码，其中 $n \in \{ 1 6 , 2 4 , 3 2 , 4 8 , 6 4 \}$，图 1 的左半部分展示了 SIMON2n 的轮结构。轮函数的核心操作由图 1 的右半部分表示。

![](images/ac061537f6d5a562265b6eab33abc44815310f0ecede2852373f0b612a540619.jpg)  
SIMON2 的第 n 轮结构

![](images/5c8adaaa517b9cc3089350c3656433f0a97a5691d1d826434633646951b9c0c8.jpg)  
核心操作 $\mathrm { Q } _ { i , j }$  
图 1. SIMON2n 的结构

当我们将算法 2 应用于 SIMON2n 时，我们将一轮 SIMON2n 划分为 $n + 1$ 个部分 $Q _ { i } = Q _ { i , n } \circ Q _ { i , n - 1 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 }$。并且将 $Q _ { i , j }$ 的输入记为 $\left( \pmb { x } ^ { i , j } , \pmb { y } ^ { i , j } \right) = \left( x _ { n - 1 } ^ { i , j } , \ldots , x _ { 0 } ^ { i , j } , y _ { n - 1 } ^ { i , j } , \ldots , y _ { 0 } ^ { i , j } \right)$。当 $0 \leq j \leq n - 1$ 时，我们有

$$
Q _ {i, j} \left(\boldsymbol {x} ^ {i, j}, \boldsymbol {y} ^ {i, j}\right) = \left(\boldsymbol {x} ^ {i, j}, y _ {n - 1} ^ {i, j}, \dots , y _ {j + 1} ^ {i, j}, Y _ {j} ^ {i, j}, y _ {j - 1} ^ {i, j}, \dots , y _ {0} ^ {i, j}\right),
$$

其中 Y <sup>i,j</sup><sub>j</sub> = x<sup>i,j</sup> <sup>(j</sup>−<sup>1)modn&x</sup> <sup>i,j</sup><sub>(j 8)modn</sub> - x<sup>i,j</sup><sub>(j 2)modn</sub>.

此外，$Q _ { i , n } \left( \pmb { x } ^ { i , n } , \pmb { y } ^ { i , n } \right) = \left( \pmb { y } ^ { i , n } \oplus \pmb { k } ^ { i } , \pmb { x } ^ { i , n } \right)$，其中 $k ^ { i }$ 是 SIMON2n 的第 i 轮轮密钥。

对于 $Q _ { i , j } , 0 \leq j \leq n - 1$，当我们考虑函数 $B D P T P \Big ( Q _ { i , j } , \mathcal { D } _ { \emptyset , \mathbb { L } _ { i , j } ^ { \prime } } \Big )$ 的 BDPT 传播规则时，$( 2 n - 4 )$ 个比特保持不变。因此，BDPT 向量中只有 4 比特 $\left( x _ { ( j - 1 ) \mathrm { m o d } ~ n } ^ { i , j } , x _ { ( j - 2 ) \mathrm { m o d } n } ^ { i , j } , x _ { ( j - 8 ) \mathrm { m o d } n } ^ { i , j } , y _ { ( j ) \mathrm { m o d } n } ^ { i , j } \right)$ 会发生变化。我们可以将其视为 4 比特 S 盒，并使用定理 1 得到其精确的 BDPT 传播规则，这些规则与论文 [21] 中的规则一致。我们将其列于附录表 7 中。

当我们使用算法 2 基于 BDPT 搜索 SIMON2n 的积分区分器时，应调用算法 1 基于 CBDP 构建 MILP 模型。文献 [27] 已经向我们展示了如何对 1 轮 SIMON2n 的 CBDP division trails 进行建模。我们将其介绍如下。

SIMON2n 的 1 轮描述。将 SIMON2n 的 1 轮 CBDP 迹记为 $\left( a _ { n - 1 } ^ { i } , \ldots , a _ { 0 } ^ { i } , \bar { b } _ { n - 1 } ^ { i } , \ldots , b _ { 0 } ^ { i } \right) \ \longrightarrow \ \left( a _ { n - 1 } ^ { i + 1 } , \ldots , a _ { 0 } ^ { i + 1 } , b _ { n - 1 } ^ { i + 1 } , \ldots , b _ { 0 } ^ { i + 1 } \right) \ $。为了得到 1 轮 SIMON2n 的所有 CBDP 迹的线性描述，我们引入四个辅助变量向量，分别为 $\left( u _ { n - 1 } ^ { i } , \ldots , u _ { 0 } ^ { i } \right) , \left( v _ { n - 1 } ^ { i } , \ldots , v _ { 0 } ^ { i } \right)$、$\left( w _ { n - 1 } ^ { i } , \ldots , w _ { 0 } ^ { i } \right)$ 和 $\left( t _ { n - 1 } ^ { i } , \ldots , t _ { 0 } ^ { i } \right)$。我们将 $\left( u _ { n - 1 } ^ { i } , \ldots , u _ { 0 } ^ { i } \right)$ 记为左循环移位 1 位的输入 CBDP。类似地，将 $\left( v _ { n - 1 } ^ { i } , \ldots , v _ { 0 } ^ { i } \right)$ 和 $\left( w _ { n - 1 } ^ { i } , \ldots , w _ { 0 } ^ { i } \right)$ 分别记为左循环移位 8 位和 2 位的输入 CBDP。令 $\left( t _ { n - 1 } ^ { i } , \ldots , t _ { 0 } ^ { i } \right)$ 表示按位与运算的输出 CBDP。以下不等式足以对 SIMON2n 中使用的复制操作进行建模：

$$
\mathcal {L} _ {1}: a _ {j} ^ {i} - u _ {j} ^ {i} - v _ {j} ^ {i} - w _ {j} ^ {i} - b _ {j} ^ {i + 1} = 0 \text {   对于   } j \in \{0, 1, \dots , n - 1\}.
$$

然后，SIMON2n 中使用的逐位 And 运算可以建模为：

$$
\mathcal {L} _ {2} = \left\{ \begin{array}{l l} t _ {j} ^ {i} - u _ {(j - 1) \mathrm{mod} n} ^ {i} \geq 0, & \text { 对于 } j \in \{0, 1, \ldots , n - 1 \}, \\ t _ {j} ^ {i} - v _ {(j - 8) \mathrm{mod} n} ^ {i} \geq 0, & \text { 对于 } j \in \{0, 1, \ldots , n - 1 \}, \\ t _ {j} ^ {i} - u _ {(j - 1) \mathrm{mod} n} ^ {i} - v _ {(j - 8) \mathrm{mod} n} ^ {i} \leq 0, & \text { 对于 } j \in \{0, 1, \ldots , n - 1 \}. \end{array} \right.
$$

最后，SIMON2n 中的 Xor 运算可以建模为：

$$
\mathcal {L} _ {3}: a _ {j} ^ {i + 1} - b _ {j} ^ {i} - t _ {j} ^ {i} - w _ {(j - 2) \mathrm{mod} n} ^ {i} = 1 \text {对于} j \in \{0, 1, \dots , n - 1 \}.
$$

到目前为止，我们得到了 1 轮 CBDP 迹的描述 $\{ { \mathcal { L } } _ { 1 } , { \mathcal { L } } _ { 2 } , { \mathcal { L } } _ { 3 } \}$。

如何描述部分轮的 CBDP 传播。对于 $\overline { { E _ { i , j } } }$，第一轮可能是一个部分轮 $Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , j }$。在考虑 $Q _ { i , j }$ 的 CBDP 传播时，若添加约束 $b _ { j } ^ { i + 1 , j } = \bar { b } _ { j } ^ { i , j }$，则输出向量与输入向量相同。也就是说，$\boldsymbol { Q } _ { i , j }$ 被转换为恒等函数。

对于 1 轮 SIMON2n，通过添加以下约束

$$
\mathcal {L} _ {4}: a _ {j} ^ {i + 1} - b _ {j} ^ {i} = 0 \text {   对于   } j \in \{0, 1, \dots , j - 1 \},
$$

我们得到部分轮 $Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , j }$ 的描述 $\{ { \mathcal { L } } _ { 1 } , { \mathcal { L } } _ { 2 } , { \mathcal { L } } _ { 3 } , { \mathcal { L } } _ { 4 } \}$。然后，通过将 1 轮的约束重复 $( r - i )$ 次，我们可以得到关于 $\overline { { E _ { i , j } } }$ 的线性不等式系统。

如何获得 $Q _ { i , j }$ 的输出 BDPT。经过剪枝技术和停止规则后，如果算法 2 不停止，我们知道 $\mathbb { K } _ { i , j } = \varnothing$ 且 $\mathbb { L } _ { i , j } \neq \emptyset$。为帮助读者理解我们的算法，我们给出一个 BDPT 传播的示例。

对于 SIMON32，如果 $Q _ { 1 , 1 5 }$ 的输入 BDPT 为 $\mathcal { D } _ { \mathbb { K } _ { 1 , 1 5 } = \varnothing , \mathbb { L } _ { 1 , 1 5 } = \{ \ell _ { 1 } , \ell _ { 2 } \} }$，其中 $\ell _ { 1 }$ $\mathbf { \Lambda } = ( 1 , \mathbf { 0 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } ) , \ell _ { 2 } = \mathbf { 0 } .$ (1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)。$\ell _ { 1 }$ 中可能由 $Q _ { 1 , 1 5 }$ 更新的 4 个比特为 (0, 1, 1, 0)。然后，根据表 7 中核心操作的 BDPT 传播规则，输出向量集为 $\mathbb { L } ^ { \prime } = \{ [ \bar { 0 } , 1 , 1 , \bar { 0 } ] , [ 0 , 1 , 0 , 1 ] , [ 0 , 1 , 1 , 1 ] \}$。因此，$\ell _ { 1 }$ 生成三个向量如下：

(1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) (1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) (1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

同理，我们可以得到，$\ell _ { 2 }$ 仅生成一个向量，如下：

(1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) .

根据 BDPT 规则 3，向量 (1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) 应当被消去，因为它由 $\ell _ { 1 }$ 和 $\ell _ { 2 }$ 各传播了两次。$Q _ { 1 , 1 5 }$ 的输出 BDPT 为 $\mathcal { D } _ { \mathbb { K } _ { 1 , 1 6 } = \varnothing , \mathbb { L } _ { 1 , 1 6 } = \{ \ell _ { 3 } , \ell _ { 4 } \} }$ ，其中

$\ell _ { 3 } = ( 1 , \mathbf { 0 } , \mathbf { 1 } , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 )$ 4 - = (1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) .

于是，$Q _ { 1 , 1 6 }$ 具有轮密钥异或操作。因此，根据 BDPT 规则 4，由 $\ell _ { 3 }$ 生成一个新向量，并将其插入到 $\mathbb { K } _ { 1 , 1 6 }$ 中。此外，由于 $\mathbb { K } _ { 1 , 1 6 }$ 中的新向量，$\mathbb { L } _ { 1 , 1 6 }$ 中的一个向量变为冗余。交换之后，$Q _ { 1 , 1 6 }$ 的输出 BDPT 为 $\mathcal { D } _ { \mathbb { K } _ { 2 , 0 } = \{ k \} , \mathbb { L } _ { 2 , 0 } = \{ \ell _ { 5 } \} }$，其中

k = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), -<sub>5</sub> = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1).

我们算法的高效率。对于 14 轮 SIMON32，我们准备选择明文，使得最左比特为常数，其余比特均为活跃。于是，选择明文的 BDPT 为 $\scriptstyle \mathcal { D } _ { \mathbb { K } = \{ ( 1 , 1 , 1 , \dots , 1 ) \} , \mathbb { L } = \{ ( 0 , 1 , 1 , \dots , 1 ) \} }$。表 3 给出了每一轮中 $| \mathbb { K } |$ 和 L 的大小。文献 [21] 中的大小是根据 BDPT 的定义去除冗余向量后得到的，而本文中的大小是在应用剪枝技术后得到的。从表 3 可以看出，本文中第 5 轮的 L 变为 0，这触发了停止规则 2，并且我们得到最右比特是平衡的。我们的剪枝技术能够大幅减小 BDPT 的大小。

积分区分器。SIMECK 是 CHES 2015 上提出的一族轻量级分组密码 [29]，除轮转常数外，其轮函数与 SIMON 的轮函数非常相似。我们使用算法 2 基于 BDPT 搜索 SIMON 和 SIMECK 族的积分区分器。对于 SIMON32，我们的 MILP 算法通过遍历所有 BDPT division trails，找到了文献 [21] 中发现的 14 轮积分区分器。对于 17 轮 SIMON64，我们找到了一个具有 23 个平衡比特的积分区分器，比此前最长的积分区分器多 1 个比特。对于 SIMON48/96/128 和 SIMECK32/48/64，我们找到的区分器与文献 [27] 中发现的此前最长区分器一致。SIMON32 和 SIMON64 的详细积分区分器列于表 4。并且表 4 中的所有积分区分器均可通过文献 [25] 中的技术再扩展一轮。

表 3. 在获得最右侧输出比特的平衡信息时 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } }$ 的大小

<table><tr><td rowspan="2">参考文献</td><td rowspan="2">BDPT</td><td colspan="16">每轮中的规模</td></tr><tr><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>11</td><td>12</td><td>13</td><td>14</td><td>15</td></tr><tr><td rowspan="2">[21]</td><td></td><td> $\mathbb{L}$ </td><td>1</td><td>1</td><td>5</td><td>19</td><td>138</td><td>2236</td><td>89878</td><td>4485379</td><td>47149981</td><td>2453101</td><td>20360</td><td>168</td><td>8</td><td>0</td><td>0</td></tr><tr><td> $\mathbb{K}$ </td><td>1</td><td>1</td><td>1</td><td>6</td><td>43</td><td>722</td><td>23321</td><td>996837</td><td>9849735</td><td>2524718</td><td>130724</td><td>7483</td><td>852</td><td>181</td><td>32</td><td>32</td></tr><tr><td rowspan="2">本文</td><td></td><td> $\mathbb{L}$ </td><td>1</td><td>1</td><td>1</td><td>2</td><td>2</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td> $\mathbb{K}$ </td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr></table>

Table 4. SIMON32 和 SIMON64 的积分区分器

```txt
密码区分器
14-SIMON32 输入: (caaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaa)
输出: (?????????????????, ?b??????b??????b)
17-SIMON64 输入: (caaaaaaaaaaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaaaaaaaaaa, bbbbbbbbbb?b??b????bbbbbbbb)
```

## 5.2 在 PRESENT 和 RECTANGLE 上的应用

PRESENT [3] 具有 SPN 结构，并在 31 轮中使用 80 位和 128 位密钥以及 64 位分组。为了提高硬件效率，它采用了完全布线的扩散层。图 2 展示了 PRESENT 的单轮结构。

![](images/c41e0b2e6bc69933944578e6a5f357ebf170a76c8a3e9803282db4cea43eaeea.jpg)  
图 2. PRESENT 的单轮 SPN 结构

我们将一轮 PRESENT 划分为 17 个部分 $Q _ { i } = Q _ { i , 1 6 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 }$。当 $0 \leq$ $j \le 1 5$ 时，有 $Q _ { i , j } \left( x _ { 0 } ^ { i , j } , \ldots , x _ { 6 3 } ^ { i , j } \right) = \left( x _ { 0 } ^ { i , j } , \ldots , S \left( x _ { 4 j } ^ { i , j } , \ldots , x _ { 4 j + 3 } ^ { i , j } \right) , \ldots , x _ { 6 3 } ^ { i , j } \right)$，其中 $S \left( x _ { 4 j } ^ { i , j } , \ldots , x _ { 4 j + 3 } ^ { i , j } \right)$ 是 PRESENT 的 S 盒。

此外，$Q _ { i , 1 6 } \left( x _ { 0 } ^ { i , 1 6 } , \ldots , x _ { 6 3 } ^ { i , 1 6 } \right) = P \left( x _ { 0 } ^ { i , 1 6 } , x _ { 1 } ^ { i , 1 6 } , \ldots , x _ { 6 3 } ^ { i , 1 6 } \right) \oplus k ^ { i }$，其中 P 是 PRESENT 的线性置换，$k ^ { i }$ 是第 i 轮轮密钥。

RECTANGLE [31] 与 PRESENT 非常相似。我们将算法 2 应用于 PRESENT 和 RECTANGLE，结果列于表 5。

表 5. PRESENT 和 RECTANGLE 的积分区分器

<table><tr><td>密码</td><td>区分器</td></tr><tr><td>9-PRESENT</td><td>输入：(aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaacccc)输出：(????????????????????????????????? ,????????????????????b???b???b???b)</td></tr><tr><td>9-PRESENT</td><td>输入：(aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaaaac)输出：(??b???b???bbbb???b???b???bbbb, ???b???b???bbbb???b???b???bbbb)</td></tr><tr><td>9-RECTANGLE</td><td>输入：(caaaaaaaaaaaaaaaaa, caaaaaaaaaaaaaaaaa, caaaaaaaaaaaaaaaaa, caaaaaaaaaaaaaaaaa)输出：(bbbbbbbbbbbbbbbb,bbbb??bb???bbbb, ??????????????????, ??????????????)</td></tr></table>

## 5.3 在 LBlock 上的应用

LBlock 是由 Wu 和 Zhang 提出的轻量级分组密码 [24]。其分组长度为 64 比特，密钥长度为 80 比特。它采用一种变体 Feistel 结构，并由 32 轮组成。LBlock 的单轮结构如图 3 所示。

![](images/de6f9ddcf7b1c5789899903d01bf6b4d6b291e5300d8e584b12acd7b8f928d51.jpg)  
(a) LBlock 的第 i 轮结构  
(b) F 函数的结构  
图 3. LBlock 的轮结构

我们将一轮 LBlock 划分为 9 个部分 $Q _ { i } = Q _ { i , 8 } \circ \cdots \circ Q _ { i , 0 }$。并且 $Q _ { i , j }$ 的输入记为 $\left( \pmb { x } ^ { i , j } , \pmb { y } ^ { i , j } \right) = \left( \pmb { x } _ { 7 } ^ { i , j } , \dots , \pmb { x } _ { 0 } ^ { i , j } , \pmb { y } _ { 7 } ^ { i , j } , \dots , \pmb { y } _ { 0 } ^ { i , j } \right)$。当 $0 \leq j \leq$ 7 时，有 $Q _ { i , j } \left( x ^ { i , j } , y ^ { i , j } \right) ~ = ~ \left( x ^ { i , j } , y _ { 7 } ^ { i , j } , \ldots , y _ { P ( j ) + 1 } ^ { i , j } , Y _ { P ( j ) } ^ { i , j } , y _ { P ( j ) - 1 } ^ { i , j } , \ldots , y _ { 0 } ^ { i , j } \right)$，其中 $\begin{array} { r c l } { { Y _ { P ( j ) } ^ { i , j } } } & { { = } } & { { S _ { j } \left( { \bf x } _ { j } ^ { i , j } \oplus k _ { i , j } \right) \oplus { y } _ { ( P ( j ) - 2 ) \mathrm { m o d } 8 } ^ { i , j } , ~ S _ { j } } } \end{array}$ 是 LBlock 的第 j 个 S 盒，且 $P \left( x \right)$ 是半字节扩散函数。此外，$Q _ { i , 8 } \left( \mathbf { x } ^ { i , 8 } , \mathbf { y } ^ { i , 8 } \right) =$ $\left( \boldsymbol { y } ^ { i , 8 } , \boldsymbol { x } ^ { i , 8 } \right)$

利用算法 2，我们找到了一个 LBlock 的 17 轮积分区分器，该结果与此前最长的积分区分器 [8] 一致；并且找到了一个更优的、活跃比特更少的 16 轮积分区分器。积分区分器的具体形式如表 6 所示。

表 6. LBlock 的积分区分器

<table><tr><td>密码</td><td>区分器</td></tr><tr><td>17轮 LBlock</td><td>输入：(caaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)输出：(?????????????????????????????????????????????????????????????bb)</td></tr><tr><td>16轮 LBlock</td><td>输入：(aaccaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)输出：(?????????????????????????????????????????????????????????)</td></tr></table>

# 6 在立方攻击中使用 BDPT 恢复超多项式

在本节中，我们分析立方攻击中非黑盒多项式和超级多项式的 ANF 系数。然后，我们展示一种基于 BDPT 的 MILP 辅助方法，用于恢复超级多项式的 ANF 系数。

## 6.1 分析多项式的 ANF 系数

设 $f \left( \pmb { x } , \pmb { v } \right)$ 为一个多项式，其中 $\pmb { x } \in \mathbb { F } _ { 2 } ^ { n }$ 和 $\pmb { v } \in \mathbb { F } _ { 2 } ^ { m }$ 分别表示秘密变量和公开变量。在立方攻击中，$f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 表示这样一个函数：由 $I _ { v } \subset \{ 0 , 1 , \cdots , m - 1 \}$ 索引的公开变量被选为立方变量，由 $J _ { v } \subset \{ 0 , 1 , \cdot \cdot \cdot , m - 1 \} - I _ { v }$ 索引的公开变量被置为 1，而其余公开变量 $K _ { v } = \{ 0 , 1 , \cdots , m - 1 \} - I _ { v } - J _ { v }$ 被置为 0。于是，$f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的 ANF 可表示如下：

$$
f _ {I _ {v}, J _ {v}, K _ {v}} \left(\boldsymbol {x}, \boldsymbol {v}\right) = \bigoplus_ {\boldsymbol {u} _ {x} \in \mathbb {F} _ {2} ^ {n}, \boldsymbol {u} _ {v} \preceq \boldsymbol {u} _ {I}} a _ {\left(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v}\right)} ^ {f _ {I _ {v}, J _ {v}, K _ {v}}} \cdot \left(\boldsymbol {x}, \boldsymbol {v}\right) ^ {\left(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v}\right)}.
$$

其中 $\boldsymbol { a } _ { ( \boldsymbol { u } _ { x } , \boldsymbol { u } _ { v } ) } ^ { f _ { I _ { v } , J _ { v } , K _ { v } } }$ 是 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中项 $( \pmb { x } , \pmb { v } ) ^ { ( \pmb { u } _ { x } , \pmb { u } _ { v } ) }$ 的 ANF 系数。

对于多项式 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 和一个索引子集 $I _ { x } \subset \{ 0 , 1 , \cdots , n - 1 \}$ ，如果将所有秘密变量 $\{ x _ { k } | k \in \{ 0 , 1 , \cdot \cdot \cdot , n - 1 \} - I _ { x } \}$ 固定为 0，则可以得到一个新的多项式，记为 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$

定义 6.（相似多项式）。对于索引子集 $I _ { x } ^ { \prime } \subset I _ { x }$，多项式 $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 称为 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的相似多项式。

引理 2. 若 $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 是 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的相似多项式，则 $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中 ANF 系数 $\begin{array} { r l } & { \quad f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } } \\ & { \quad a _ { \left( \boldsymbol { u } _ { I _ { x } ^ { \prime } } , \boldsymbol { u } _ { I _ { v } } \right) } } \end{array}$ 的值等于 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中 ANF 系数 $\begin{array} { r } { \boldsymbol { a } _ { \left( u _ { I _ { x } ^ { \prime } } , u _ { I _ { v } } , J _ { v } , K _ { v } \right. } ^ { \left. {  } } } \\ \right.{ \left. \left( \boldsymbol { u } _ { I _ { x } ^ { \prime } } , \boldsymbol { u } _ { I _ { v } } \right) \right. } \end{array}$ 的值。

证明。对于 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$，若将 $\{ x _ { i } | i \in I _ { x } - I _ { x } ^ { \prime } \}$ 中的所有变量赋值为 0，则其变为函数 $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$。与 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的 ANF 相比，$f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的 ANF 仅缺少那些包含 $\{ x _ { i } | i \in I _ { x } - I _ { x } ^ { \prime } \}$ 中任一变量的项。此外，$\pmb { x } ^ { u _ { I _ { x } ^ { \prime } } }$ 不包含 $\{ x _ { i } | i \in I _ { x } - I _ { x } ^ { \prime } \}$ 中的任何变量，因此 $\begin{array} { r } { a _ { \left( u _ { I _ { x } ^ { \prime } } , u _ { I _ { v } } , J _ { v } , K _ { v } \right) } ^ { f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } } = a _ { \left( u _ { I _ { x } ^ { \prime } } , u _ { I _ { v } } \right) } ^ { f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } } } \end{array}$

## 6.2 分析超级多项式的 ANF 系数

立方攻击最重要的部分是恢复超级多项式。一旦恢复了超级多项式，攻击者就可以计算立方上所有加密结果的和，并得到一个关于秘密变量的方程。

设 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 为第 2.5 节中由式 (1) 定义的立方集。对于多项式 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$，其中 $\pmb { x } \in \mathbb { F } _ { 2 } ^ { n }$ 且 $\pmb { v } \in \mathbb { F } _ { 2 } ^ { m }$，它可以唯一地表示为

$$
f _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}) = \boldsymbol {v} ^ {\boldsymbol {u} _ {I _ {v}}} \cdot p _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}) \oplus q _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}).\tag{3}
$$

其中 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 不包含 $\{ v _ { i } | i \in I _ { v } \}$ 中的任何变量，且 $q _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的每一项都不能被 ${ \boldsymbol { v } } ^ { u _ { I _ { v } } }$ 整除。那么，$p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 称为 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 的超多项式。

定义 7. 令 $C _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ 为满足如下条件的 $( { \pmb x } , { \pmb v } )$ 的集合：秘密变量 $\{ x _ { i } | i \in I _ { x } \}$ 取所有可能的取值组合，秘密变量 $\{ x _ { i } | i \in$ $\{ 0 , 1 , \ldots , n - 1 \} - I _ { x } \}$ 被置为常数 0，公开变量 $\{ v _ { i } | i \in I _ { v } \}$ 取所有可能的取值组合，公开变量 $\{ v _ { j } | j \in J _ { v } \}$ 被置为常数 1，且公开变量 $\{ v _ { k } | k \in K _ { v } \}$ 被置为常数 0。

这里，我们提出一种计算超多项式的 ANF 系数的方法。

命题 3. 对于任意指标子集 $I _ { x } \subset \{ 0 , 1 , \dotsc , n - 1 \}$，超多项式 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 中项 ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ 的 ANF 系数可以计算为

$$
a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} = \bigoplus_ {(\boldsymbol {x}, \boldsymbol {v}) \in C _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}).
$$

证明。$p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 的 ANF 可表示为

$$
p _ {I _ {v}, J _ {v}, K _ {v}} \left(\boldsymbol {x}\right) = \bigoplus_ {\boldsymbol {u} \in \mathbb {F} _ {2} ^ {n}} a _ {\boldsymbol {u}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} \cdot \boldsymbol {x} ^ {\boldsymbol {u}}.
$$

于是，$\pmb { v } ^ { { u } _ { I _ { v } } } \cdot p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 的 ANF 可以表示为

$$
\boldsymbol {v} ^ {\boldsymbol {u} _ {I _ {v}}} \cdot p _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}) = \bigoplus_ {\boldsymbol {u} \in \mathbb {F} _ {2} ^ {n}} a _ {\boldsymbol {u}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} \cdot (\boldsymbol {x}, \boldsymbol {v}) ^ {(\boldsymbol {u}, \boldsymbol {u} _ {I _ {v}})}.
$$

因此，$( \pmb { x } , \pmb { v } ) ^ { ( \pmb { u } _ { I _ { x } } , \pmb { u } _ { I _ { v } } ) }$ 在 $\pmb { v } ^ { \pmb { u } _ { I _ { v } } } \cdot p _ { I _ { v } , J _ { v } , K _ { v } } ( \pmb { x } , \pmb { v } )$ 中的 ANF 系数也为 $a _ { u _ { I _ { x } } } ^ { p _ { I _ { v } , J _ { v } , K _ { v } } }$。由于 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 可以唯一地表示为 $\operatorname { E q . } \ ( 3 )$，且 $q _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中的每一项都至少缺少 $\{ v _ { i } | i \in I _ { v } \}$ 中的一个变量，因此项 $( \pmb { x } , \pmb { v } ) ^ { ( \pmb { u } _ { I _ { x } } , \pmb { u } _ { I _ { v } } ) }$ 不存在于 $q _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中。根据式 (3)，可得 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中项 $( \mathbf { \bar { x } } , \mathbf { \bar { v } } ) ^ { \dot { \pmb { u } } _ { I _ { x } } , \dot { \pmb { u } } _ { I _ { v } } }$ 的 ANF 系数为 $a _ { u _ { I _ { x } } } ^ { p _ { I _ { v } , J _ { v } , K _ { v } } }$。也就是说，

$$
a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {v}, J _ {v}, K _ {v}}}.\tag{4}
$$

由定义 6 可知，$f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ 是 $f _ { I _ { v } , J _ { v } , K _ { v } }$ 的相似多项式。并且根据引理 2，我们得到

$$
a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {v}, J _ {v}, K _ {v}}} = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}}.\tag{5}
$$

于是，我们有

$$
\begin{array}{l} \bigoplus_ {(\boldsymbol {x}, \boldsymbol {v}) \in C _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}) \\ = \bigoplus_ {(\boldsymbol {x}, \boldsymbol {v}) \in C _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} \bigoplus_ {\boldsymbol {u} _ {x} \preceq \boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {v} \preceq \boldsymbol {v} _ {I _ {v}}} a _ {(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v})} ^ {f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} \cdot (\boldsymbol {x}, \boldsymbol {v}) ^ {(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v})} \\ = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} = a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}}. \end{array}
$$

## 6.3 恢复超级多项式的算法

集合 $C _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ 可被视为一个 cube 集。根据 BDPT 的定义，我们知道 $C _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ 的 BDPT 为 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$，其中 $\mathbb { K } = \varnothing$，且 $\mathbb { L } = \{ \left( \boldsymbol { u } _ { I _ { x } } , \boldsymbol { u } _ { v } \right) \lvert \boldsymbol { u } _ { I _ { v } } \preceq \boldsymbol { u } _ { v } \preceq \boldsymbol { u } _ { I _ { v } } \oplus \boldsymbol { u } _ { J _ { v } } \}$。然后，我们可以使用 MILP 辅助方法（算法 2）来研究 $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$ 的传播。由 BDPT 得到的积分区分器恢复了 superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 中 $x ^ { u _ { I _ { x } } }$ 的 ANF 系数。例如，如果算法 2 BDPT $( f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } , \mathbb { K } , \mathbb { L } , 0 )$ 返回 1，则意味着

\- $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right) = 1$。根据命题 3，我们知道 $( \pmb { x } , \pmb { v } ) { \in } C _ { I _ { \pmb { x } } , I _ { \pmb { v } } , J _ { \pmb { v } } , K _ { \pmb { v } } }$

超多项式 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 中 ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ 的 ANF 系数等于 1。我们在算法 3 中说明整个框架。

为了更好地分析这些密码，我们将其分为两类：公开更新密码和秘密更新密码。

定义 8. 对于函数 $f : \mathbb { F } _ { 2 } ^ { n } \to \mathbb { F } _ { 2 } ^ { m }$，如果 f 的 ANF 是确定的，则称其为公开函数。令 $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { 1 } \left( { \pmb x } , { \pmb v } \right)$ 为一个 r 轮密码，其中 $Q _ { i }$ 是第 i 轮更新函数，x 表示秘密变量，v 表示公开变量。如果所有轮更新函数 $Q _ { i } , i \in \{ 1 , 2 , \cdots , r \}$ 都是公开函数，则密码 E 是公开更新密码。否则称其为秘密更新密码。

命题 4. 对于一个公开更新密码 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 和立方集 $C _ { I _ { v } , J _ { v } , K _ { v } }$，其超级多项式 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 可以通过 $B D P T$ 的传播被完全恢复。

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
算法 3. 恢复 superpoly $p_{I_v, J_v, K_v}(\boldsymbol{x})$ 中 $\boldsymbol{x}^{u_{I_x}}$ 的 ANF 系数

1 procedure RecoverCoefficient($I_x$, $I_v$, $J_v$, $K_v$)
2    初始化 $\mathbb{K} = \emptyset$，$\mathbb{L} = \{ (\boldsymbol{u}_{I_x}, \boldsymbol{u}_v) | \boldsymbol{u}_{I_v} \preceq \boldsymbol{u}_v \preceq \boldsymbol{u}_{I_v} \oplus \boldsymbol{u}_{J_v} \}$
3    if $BDPT(f_{I_x, I_v, J_v, K_v}, \mathbb{K}, \mathbb{L}, 0)$ 返回 unknown
4    return unknown
5    else if $BDPT(f_{I_x, I_v, J_v, K_v}, \mathbb{K}, \mathbb{L}, 0)$ 返回 1
6    return 1
7    else
8    return 0
9 end procedure
</div>

证明。超级多项式 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ 是秘密变量 x 的函数。若对于任意项 ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$，我们都能确定其 ANF 系数，则可以得到精确的超级多项式。

由于 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 是一个公开更新密码，$f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 也是一个公开更新密码。因此，对于任意项 ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$，我们研究 BDPT $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n + m } }$ 的传播，其中 $\mathbb { K } = \varnothing$ 且 $\mathbb { L } = \{ \left( \boldsymbol { u } _ { I _ { x } } , \boldsymbol { u } _ { v } \right) \lvert \boldsymbol { u } _ { I _ { v } } \preceq \boldsymbol { u } _ { v } \preceq \boldsymbol { u } _ { I _ { v } } \oplus \boldsymbol { u } _ { J _ { v } } \}$。令 $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 的输出 BDPT 为 $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n + m } }$。初始的 $\mathbb { K } = \varnothing$ 意味着不存在从 $\mathbb { K } = \varnothing$ 到 $\mathbb { K } ^ { \prime }$ 的 division trail。由第 2.3 节可知，对于公开函数，K 和 L 的 BDPT 传播是相互独立的。只有当涉及秘密轮密钥时，L 中的某些向量才会影响 K。这意味着，当所有更新函数都是公开的时，不存在从 L 到 $\mathbb { K } ^ { \prime }$ 的 division trail。输出集合 $\mathbb { K } ^ { \prime } = \varnothing$，并且算法 3 的返回值为常数（0 或 1）。因此，任意项 ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ 的 ANF 系数可以通过 BDPT 恢复。

根据第 2.6 节，对于多项式 $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 和立方集 $C _ { I _ { v } , J _ { v } , K _ { v } }$，我们可以使用 MILP 方法来评估超多项式中涉及的秘密变量以及超多项式次数的上界。我们将所涉及的秘密变量下标集合记为 I，并将次数上界记为 d。于是，为了恢复超多项式，我们只需要确定满足 ${ \pmb u } \preceq { \pmb u } _ { I }$ 且 hw $( { \boldsymbol { \mathbf { u } } } ) \leq d .$ 的系数 $a _ { u } ^ { p _ { I _ { v } , J _ { v } , K _ { v } } }$。

公开更新密码分析。根据命题 4，我们可以查询算法 3 $\begin{array} { r } { \sum _ { i = 0 } ^ { d } \binom { | I | } { i } } \end{array}$ 次，以恢复 superpoly 的所有 ANF 系数。其复杂度为 $c \cdot \sum _ { i = 0 } ^ { d } \left( { | I | } \atop { i } \right)$，其中 c 是算法 3 的平均计算复杂度。与第 2.6 节中基于 CBDP 的立方攻击相比，可以知道，当 $c < 2 ^ { | I _ { v } | }$ 时，我们的方法可以获得更好的结果。

秘密更新密码的分析。由于中间轮中秘密密钥的影响，可能会从 $\mathbb { L } _ { i }$ 生成新的向量并将其加入 $\mathbb { K } _ { i }$ 。因此，输出 BDPT 集 $\mathbb { K } ^ { \prime } = \varnothing$ 的条件可能并不成立。也就是说，超多项式 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 中只有一部分 ANF 系数可以通过 BDPT 获得。若有 N 个 ANF 系数无法由 BDPT 确定，则必须通过中使用的方法来获得它们的 ANF 系数。

基于 CBDP 的立方攻击。因此，恢复超多项式的复杂度为 $\left\{ c \cdot \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } + N \cdot 2 ^ { | I _ { v } | } \right\}$

# 7 在 Trivium 上的应用

为了验证我们方法的正确性和有效性，我们将其应用于 Trivium [5]，它是一种公开更新密码。

## 7.1 Trivium 的描述

Trivium [5] 是一种面向比特的流密码，其 288 比特内部状态记为 $\pmb { \mathscr { s } } = ( \mathscr { s } _ { 0 } , \mathscr { s } _ { 1 } , \mathscr { . . . } , \mathscr { s } _ { 2 8 7 } )$。为更方便地概述我们的方法，我们使用如下表达式来描述 Trivium。令 ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \cdot \cdot \cdot , x _ { 7 9 } )$ 表示秘密变量（80 比特密钥），并令 $\pmb { v } = ( v _ { 0 } , v _ { 1 } , \dotsb , v _ { 2 0 7 } )$ 表示公开变量。对于公开变量，$v _ { 1 3 } , v _ { 1 4 } , \cdots$，v 是攻击者可以选择其取值的 IV 变量（80 比特 IV），$\{ v _ { 2 0 5 } , v _ { 2 0 6 } , v _ { 2 0 7 } \}$ 被设置为 1，其余变量被设置为 0。然后，在内部状态更新 1152 轮之前，该算法不会输出任何密钥流比特。Trivium 的完整描述由以下简单伪代码给出。

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
$(s_{0}, s_{1}, \ldots, s_{92}) \leftarrow (x_{0}, \ldots, x_{79}, v_{0}, \ldots, v_{12})$ $(s_{93}, s_{94}, \ldots, s_{176}) \leftarrow (v_{13}, \ldots, v_{96})$ $(s_{177}, s_{178}, \ldots, s_{287}) \leftarrow (v_{97}, \ldots, v_{207})$

对于 i = 1 到 N 执行

如果 i &gt; 1152，则

$z_{i-1152} \leftarrow s_{65} \oplus s_{92} \oplus s_{161} \oplus s_{176} \oplus s_{242} \oplus s_{287}$

end if

$t_{1} \leftarrow s_{65} \oplus s_{90} \cdot s_{91} \oplus s_{92} \oplus s_{170}$ $t_{2} \leftarrow s_{161} \oplus s_{174} \cdot s_{175} \oplus s_{176} \oplus s_{263}$ $t_{3} \leftarrow s_{242} \oplus s_{285} \cdot s_{286} \oplus s_{287} \oplus s_{68}$ $(s_{0}, s_{1}, \ldots, s_{92}) \leftarrow (t_{2}, s_{0}, \ldots, s_{91})$ $(s_{93}, s_{94}, \ldots, s_{176}) \leftarrow (t_{0}, s_{93}, \ldots, s_{175})$ $(s_{177}, s_{178}, \ldots, s_{287}) \leftarrow (t_{1}, s_{177}, \ldots, s_{286})$

end for
</div>

## 7.2 面向 Trivium 的 MILP 辅助算法

由于 Trivium 是一种公开更新密码，在恢复超级多项式的 ANF 系数的过程中，集合 K 始终为空。文献 [23,26] 已经展示了如何构建 Trivium 的 CBDP 模型。这里，我们提出算法 4 来获得 Trivium 轮函数的 L 传播。算法 4 中过程 RoundPropagation 的输入是第 r 轮 BDPT 集 $\mathbb { L } _ { r }$，输出是第 (r + 1) 轮 BDPT 集 $\mathbb { L } _ { r + 1 }$。

```fortran
算法 4. 轮函数中 L 的传播

1 过程 CorePropagation(L, i₀, i₁, i₂, i₃, i₄)
2 令 x = (x₀, x₁, x₂, x₃, x₄) 为变量
3 令 y 为 x 的函数，且 y = (x₀, x₁, x₂, x₃, x₀x₁ + x₂ + x₃ + x₄)
4 L' = ∅
5 对于 L 中的 ℓ
6    对所有 u = (u₀, u₁, u₂, u₃, u₄) ∈ F₂⁵ do
7    如果 yᵘ 包含项 x(ℓᵢ₀, ℓᵢ₁ℓᵢ₂, ℓᵢ₃, ℓᵢ₄) then
8    ℓ' = ℓ
9    ℓ′ᵢ₀ = u₀, ℓ′₁ = u₁, ℓ′ᵢ₂ = u₂, ℓ′₃ = u₃, ℓ′ᵢ₄ = u₄
10    L'←ℓ'
11    end if
12    end for
13    end for
14    返回 L'
15 end procedure

1 过程 RoundPropagation(Lᵣ)
2    初始化 L' = ∅, L'' = ∅, L''' = ∅, Lᵣ₊₁ = ∅
3    L' = CorePropagation(Lᵣ, 65, 170, 90, 91, 92)
4    L'' = CorePropagation(L', 161, 163, 174, 175, 176)
5    L''' = CorePropagation(L'', 242, 68, 285, 286, 287)
6    对所有 L''' 中的 ℓ do
7    Lᵣ₊₁ = Lᵣ₊₁ ∪{ℓ ≫ 1}
8    end for
9    返回 Lᵣ₊₁
10 end procedure
```

在 CRYPTO 2017 [23] 上，Todo 等人提出了针对 832 轮 Trivium 的基于 CBDP 的立方攻击。随后，在 CRYPTO 2018 [26] 上，Wang 等人改进了该结果，并给出了针对 839 轮 Trivium 的基于 CBDP 的立方攻击。但这两种方法都无法确保这些立方攻击是否为密钥恢复攻击。在将算法 3 应用于 832 轮和 839 轮 Trivium 后，我们得到如下结果。

结果 1. 对于立方集合 $C _ { I _ { v } , J _ { v } , K _ { v } }$，其中 $I _ { v } = \{ 1 3 , \ldots , 4 5 , 4 7 , \ldots , 5 8 , 6 0 , \ldots , 9 2 \}$，无论对非立方 $I V s \ \{ 4 6 , 5 9 \} \ i s$ 如何赋值，论文 $[ \boldsymbol { { \mathcal { Z } } } \boldsymbol { \delta } ]$ 中 839 轮 Trivium 的相应超多项式均为常数。因此，论文 [26] 中基于 CBDP 的立方攻击并非密钥恢复攻击。

结果 2. 对于立方集 $C _ { I _ { v } , J _ { v } , K _ { v } ; }$，其中 $I _ { v } = \{ 1 3 , 1 4 , \dots , 7 7 , 7 9 , 8 1 , \dots , 9 1 \}$，某些赋值的超级多项式是常数。例如，当 $J _ { v } \ =$ 205, 206, 207 且 $K _ { v } = \{ 0 , 1 , \ldots , 2 0 7 \} - I _ { v } - J _ { v }$ 时，恢复出的超级多项式为 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right) = 0$。而某些赋值的超级多项式是非常数。例如，当 $J _ { v } = \{ 8 0 , 9 0 , 2 0 5 , 2 0 6 , 2 0 7 \}$ 且 $K _ { v } = \{ 0 , 1 , \ldots , 2 0 7 \} - I _ { v } - J _ { v }$ 时，恢复出的超级多项式为 $p _ { I _ { v } , J _ { v } , K _ { v } } \left( { \pmb x } \right) = x _ { 5 6 } x _ { 5 7 } x _ { 5 8 } + x _ { 3 2 } x _ { 5 6 } + x _ { 5 6 } x _ { 5 9 }$。总之，对非立方 IV 的赋值会影响文献 [23] 中针对 832 轮 Trivium 的立方攻击是否为密钥恢复攻击。

## 7.3 理论结果

结果 3. 设 $C _ { I _ { v } , J _ { v } , K _ { v } }$ 为一个立方集合，其中 $I _ { v } = \{ 1 3 , 1 4 , \ldots , 8 9 , 9 1 \} , J _ { v } =$ 205, 206, 207，且 $K _ { v } = \{ 0 , 1 , \ldots , 2 0 4 \} - I _ { v }$。使用论文 ${ \it 2 6 } ] ,$ 中的次数界定技术，我们可以得到 841 轮 Trivium 中 superpoly 的次数不大于 10。于是，我们有 $\begin{array} { r } { \sum _ { i = 0 } ^ { d } \binom { | I | } { i } \leq \sum _ { i = 0 } ^ { 1 0 } \binom { 8 0 } { i } \leq 2 ^ { 4 1 } } \end{array}$ 这意味着我们可以使用不超过 $2 ^ { 4 1 }$ 次 MILP 辅助的 BDPT 传播来恢复 841 轮 Trivium 的精确 superpoly。

由于我们的计算资源有限，841 轮 Trivium 的精确 superpoly 无法在实际时间内恢复。在我们的普通 PC（Intel Core i5-4590 CPU @3.3 GHz，8.00G RAM）上，完成 100 次 BDPT 的 MILP 辅助传播大约需要 18 天。

# 8 结论

本文致力于解决基于 BDPT 搜索积分区分器的复杂性问题。为了使 BDPT 的传播更加高效，我们给出了能够及时移除冗余向量的剪枝技术。随后，设计了一种基于 BDPT 估计第 m 个输出比特是否平衡的算法。我们将该搜索算法应用于若干分组密码，所得积分区分器与此前最长的积分区分器相同或更优。需要注意的是，基于 BDPT 不存在积分区分器并不意味着不存在积分区分器。任何对 BDPT 传播精度的改进都可能获得更好的积分区分器。此外，我们的搜索算法假设所有轮密钥都是随机选取的。若考虑密钥编排算法，则可能获得更好的积分区分器。

此外，我们将 BDPT 应用于恢复立方攻击中的超多项式。据我们所知，这是 BDPT 首次应用于流密码。对于 publicupdate 密码，通过探索 BDPT 的传播，可以完全恢复超多项式的精确 ANF。为验证我们方法的正确性和有效性，我们将其应用于 Trivium。对于 832 轮 Trivium [23] 上的立方攻击，我们得到的结果是，只有某些适当的非立方 IV 赋值能够得到非常数超多项式。对于 839 轮 Trivium [26] 上的立方攻击，我们的结果表明超多项式始终为常数。由于我们的方法能够在实际可行的时间内确定超多项式的 ANF 系数，我们提出了对 841 轮 Trivium 的理论超多项式恢复。

对于秘密更新型密码，由于中间轮密钥的影响，并非所有 ANF 系数都能通过 $\mathrm { B D P T }$ 获得。从这一角度来看，当我们设计流密码时，秘密更新型密码更加安全。如何恢复秘密更新型密码的超多项式是我们未来的工作。

致谢。作者感谢匿名审稿人提出的详细意见和建议。本工作得到了国家自然科学基金[项目批准号：61572516，61802437]的资助。

# 附录

表 7. SIMON 核心运算的 BDPT 的 L 传播

<table><tr><td>输入  $\mathcal{D}_{\mathbb{K},\{\ell\}}^{1^4}$ </td><td>输出  $\mathcal{D}_{\mathbb{K}',\mathbb{L}'}^{1^4}$ </td></tr><tr><td> $\ell = [0, 0, 0, 0]$ </td><td> $\mathbb{L}' = \{[0, 0, 0, 0]\}$ </td></tr><tr><td> $\ell = [1, 0, 0, 0]$ </td><td> $\mathbb{L}' = \{[1, 0, 0, 0]\}$ </td></tr><tr><td> $\ell = [0, 1, 0, 0]$ </td><td> $\mathbb{L}' = \{[0, 1, 0, 0]\}$ </td></tr><tr><td> $\ell = [1, 1, 0, 0]$ </td><td> $\mathbb{L}' = \{[1, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1]\}$ </td></tr><tr><td> $\ell = [0, 0, 1, 0]$ </td><td> $\mathbb{L}' = \{[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 1]\}$ </td></tr><tr><td> $\ell = [1, 0, 1, 0]$ </td><td> $\mathbb{L}' = \{[1, 0, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1]\}$ </td></tr><tr><td> $\ell = [0, 1, 1, 0]$ </td><td> $\mathbb{L}' = \{[0, 1, 1, 0], [0, 1, 0, 1], [0, 1, 1, 1]\}$ </td></tr><tr><td> $\ell = [1, 1, 1, 0]$ </td><td> $\mathbb{L}' = \{[1, 1, 1, 0], [0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 0, 1]\}$ </td></tr><tr><td> $\ell = [\ell_0, \ell_1, \ell_2, 1]$ </td><td> $\mathbb{L}' = \{[\ell_0, \ell_1, \ell_2, 1]\}$ </td></tr></table>

# 实验验证

例 1. 对于 591 轮 Trivium 和立方集 $C _ { I _ { v } , J _ { v } , K _ { v } }$，其中 $I _ { v } = \{ 1 3 , 2 3$，33，43，53，63，73，83，$J _ { v } = \{ 1 4 , 2 9 , 3 2 , 2 0 5 , 2 0 6 , 2 0 7 \}$，且 $K _ { v } = \{ 0 , 1 , \cdot \cdot \cdot , 2 0 7 \} -$ $I _ { v } - J _ { v }$，我们可以得到所涉及的秘密变量为 $\{ x _ { 2 2 } , x _ { 2 3 } , x _ { 2 4 } , x _ { 6 6 } \}$，超多项式的次数不大于 2。然后，我们使用算法 3 恢复超多项式的所有 ANF 系数，其与如下实际恢复得到的超多项式一致：

$$
p _ {I _ {v}, J _ {v}, K _ {v}} (\pmb {x}) = x _ {6 6} + x _ {2 4} + x _ {2 3} x _ {2 2} + 1.
$$

例 2. 对于 591 轮 Trivium 和立方集合 $C _ { I _ { v } , J _ { v } , K _ { v } }$，其中 $I _ { v } = \{ 1 3 , 2 3$，33, 43, 53, 63, 73, 83，$J _ { v } = \{ 2 9 , 3 2 , 8 2 , 2 0 5 , 2 0 6 , 2 0 7 \}$，且 $K _ { v } = \{ 0 , 1 , \cdot \cdot \cdot , 2 0 7 \} -$ $I _ { v } - J _ { v }$，我们可以得到所涉及的秘密变量为 $\{ x _ { 2 2 } , x _ { 2 3 } , x _ { 2 4 } , x _ { 6 5 } , x _ { 6 6 } \}$ • 超多项式的次数不大于 3。然后，我们使用算法 3 恢复超多项式，其与如下实际恢复得到的超多项式一致：

$$
p _ {I _ {v}, J _ {v}, K _ {v}} (\pmb {x}) = x _ {6 5} x _ {2 3} x _ {2 2} + x _ {6 5} x _ {2 4} + x _ {6 6} x _ {6 5} + x _ {6 5}.
$$

# 参考文献

1. Abdelkhalek, A., Sasaki, Y., Todo, Y., Tolba, M., Youssef, M.: MILP modeling for (large) S-boxes to optimize probability of diferential characteristics. IACR Trans. Symmetric Cryptol. 2017(4), 99–129 (2017)

2. Beaulieu, R., Shors, D., Smith, J., Treatman–Clark, S., Weeks, B., Wingers, L.: The SIMON and SPECK families of lightweight block ciphers. IACR Cryptology ePrint Archive 2013:404 (2013). http://eprint.iacr.org/2013/404

3. Bogdanov, A., et al.: PRESENT: an ultra-lightweight block cipher. In: Paillier, P., Verbauwhede, I. (eds.) CHES 2007. LNCS, vol. 4727, pp. 450–466. Springer, Heidelberg (2007). https://doi.org/10.1007/978-3-540-74735-2 31

4. Boura, C., Canteaut, A.: Another view of the division property. In: Robshaw, M., Katz, J. (eds.) CRYPTO 2016. LNCS, vol. 9814, pp. 654–682. Springer, Heidelberg (2016). https://doi.org/10.1007/978-3-662-53018-4 24

5. De Canni\`ere, C., Preneel, B.: Trivium. In: Robshaw, M., Billet, O. (eds.) New Stream Cipher Designs. LNCS, vol. 4986, pp. 244–266. Springer, Heidelberg (2008). https://doi.org/10.1007/978-3-540-68351-3 18

6. Dinur, I., Shamir, A.: Cube attacks on tweakable black box polynomials. In: Joux, A. (ed.) EUROCRYPT 2009. LNCS, vol. 5479, pp. 278–299. Springer, Heidelberg (2009). https://doi.org/10.1007/978-3-642-01001-9 16

7. Dinur, I., Shamir, A.: Breaking grain-128 with dynamic cube attacks. In: Joux, A. (ed.) FSE 2011. LNCS, vol. 6733, pp. 167–187. Springer, Heidelberg (2011). https://doi.org/10.1007/978-3-642-21702-9 10

8. Eskandari, Z., Kidmose, A.B., K¨olbl, S., Tiessen, T.: Finding integral distinguishers with ease. In: Cid, C., Jacobson Jr., M. (eds.) SAC 2018. Lecture Notes in Computer Science, vol. 11349, pp. 115–138. Springer, Cham (2019). https://doi. org/10.1007/978-3-030-10970-7 6

9. Fu, X., Wang, X., Dong, X., Meier, W.: A key-recovery attack on 855-round Trivium. In: Shacham, H., Boldyreva, A. (eds.) CRYPTO 2018. LNCS, vol. 10992, pp. 160–184. Springer, Cham (2018). https://doi.org/10.1007/978-3-319-96881-0 6 10 Gurobi: http://www gurobi com/

10. Gurobi: http://www.gurobi.com

11. Knudsen, L., Wagner, D.: Integral cryptanalysis. In: Daemen, J., Rijmen, V. (eds.) FSE 2002. LNCS, vol. 2365, pp. 112–127. Springer, Heidelberg (2002). https://doi. org/10.1007/3-540-45661-9 9

12. Hao, Y., Jiao, L., Li, C., Meier, W., Todo, Y., Wang, Q.: Observations on the dynamic cube attack of 855-Round TRIVIUM from Crypto 2018. IACR Cryptology ePrint Archive 2018:972 (2018). https://eprint.iacr.org/2018/972.pdf

13. Hu, K., Wang, M.: Automatic search for a variant of division property using three subsets. In: Matsui, M. (ed.) CT-RSA 2019. LNCS, vol. 11405, pp. 412–432. Springer, Cham (2019). https://doi.org/10.1007/978-3-030-12612-4 21

14. Huang, S., Wang, X., Xu, G., Wang, M., Zhao, J.: Conditional cube attack on reduced-round keccak sponge function. In: Coron, J.-S., Nielsen, J.B. (eds.) EURO-CRYPT 2017. LNCS, vol. 10211, pp. 259–288. Springer, Cham (2017). https://doi. org/10.1007/978-3-319-56614-6 9

15. Liu, M., Yang, J., Wang, W., Lin, D.: Correlation cube attacks: from weak-key distinguisher to key recovery. In: Nielsen, J.B., Rijmen, V. (eds.) EUROCRYPT 2018. LNCS, vol. 10821, pp. 715–744. Springer, Cham (2018). https://doi.org/10. 1007/978-3-319-78375-8 23

16. Liu, M.: Degree evaluation of NFSR-based cryptosystems. In: Katz, J., Shacham, H. (eds.) CRYPTO 2017. LNCS, vol. 10403, pp. 227–249. Springer, Cham (2017). https://doi.org/10.1007/978-3-319-63697-9 8

17. Sage: http://www.sagemath.org/

18. Sun, B., Hai, X., Zhang, W., Cheng, L., Yang, Z.: New observation on division property. Sci. Chin. (Inf. Sci.) 2017(09), 274–276 (2017)

19. Sun, S., Hu, L., Wang, P., Qiao, K., Ma, X., Song, L.: Automatic security evaluation and (related-key) diferential characteristic search: application to SIMON, PRESENT, LBlock, DES(L) and other bit-oriented block ciphers. In: Sarkar, P., Iwata, T. (eds.) ASIACRYPT 2014. LNCS, vol. 8873, pp. 158–178. Springer, Heidelberg (2014). https://doi.org/10.1007/978-3-662-45611-8 9

20. Todo, Y.: Integral cryptanalysis on full MISTY1. In: Gennaro, R., Robshaw, M. (eds.) CRYPTO 2015. LNCS, vol. 9215, pp. 413–432. Springer, Heidelberg (2015). https://doi.org/10.1007/978-3-662-47989-6 20

21. Todo, Y., Morii, M.: Bit-based division property and application to Simon family. In: Peyrin, T. (ed.) FSE 2016. LNCS, vol. 9783, pp. 357–377. Springer, Heidelberg (2016). https://doi.org/10.1007/978-3-662-52993-5 18

22. Todo, Y.: Structural evaluation by generalized integral property. In: Oswald, E., Fischlin, M. (eds.) EUROCRYPT 2015. LNCS, vol. 9056, pp. 287–314. Springer, Heidelberg (2015). https://doi.org/10.1007/978-3-662-46800-5 12

23. Todo, Y., Isobe, T., Hao, Y., Meier, W.: Cube attacks on non-blackbox polynomials based on division property. In: Katz, J., Shacham, H. (eds.) CRYPTO 2017. LNCS, vol. 10403, pp. 250–279. Springer, Cham (2017). https://doi.org/10.1007/978-3- 319-63697-9 9

24. Wu, W., Zhang, L.: LBlock: a lightweight block cipher. In: Lopez, J., Tsudik, G. (eds.) ACNS 2011. LNCS, vol. 6715, pp. 327–344. Springer, Heidelberg (2011). https://doi.org/10.1007/978-3-642-21554-4 19

25. Wang, Q., Liu, Z., Varıcı, K., Sasaki, Y., Rijmen, V., Todo, Y.: Cryptanalysis of reduced-round SIMON32 and SIMON48. In: Meier, W., Mukhopadhyay, D. (eds.) INDOCRYPT 2014. LNCS, vol. 8885, pp. 143–160. Springer, Cham (2014). https://doi.org/10.1007/978-3-319-13039-2 9

26. Wang, Q., Hao, Y., Todo, Y., Li, C., Isobe, T., Meier, W.: Improved division property based cube attacks exploiting algebraic properties of superpoly. In: Shacham, H., Boldyreva, A. (eds.) CRYPTO 2018. LNCS, vol. 10991, pp. 275–305. Springer, Cham (2018). https://doi.org/10.1007/978-3-319-96884-1 10

27. Xiang, Z., Zhang, W., Bao, Z., Lin, D.: Applying MILP method to searching integral distinguishers based on division property for 6 lightweight block ciphers. In: Cheon, J.H., Takagi, T. (eds.) ASIACRYPT 2016. LNCS, vol. 10031, pp. 648–678. Springer, Heidelberg (2016). https://doi.org/10.1007/978-3-662-53887-6 24

28. Xie, X., Tian, T.: Improved distinguisher search techniques based on parity sets. Sci. Chin. Inf. Sci. 55, 2712 (2018)

29. Yang, G., Zhu, B., Suder, V., Aagaard, M.D., Gong, G.: The Simeck family of lightweight block ciphers. In: G¨uneysu, T., Handschuh, H. (eds.) CHES 2015. LNCS, vol. 9293, pp. 307–329. Springer, Heidelberg (2015). https://doi.org/10. 1007/978-3-662-48324-4 16

30. Ye, C., Tian, T.: Deterministic cube attacks. IACR Cryptology ePrint Archive, 2018:1028 (2018). https://eprint.iacr.org/2018/1082.pdf

31. Zhang, W., Bao, Z., Lin, D., Rijmen, V., Yang, B., Verbauwhede, I.: Rectangle: a bit-slice lightweight block cipher suitable for multiple platforms. Sci. Chin. Inf. Sci. 58(12), 1–15 (2015)