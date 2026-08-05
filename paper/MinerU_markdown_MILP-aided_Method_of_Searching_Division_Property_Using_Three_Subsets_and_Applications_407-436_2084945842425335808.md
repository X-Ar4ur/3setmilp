# MILP-aided Method of Searching Division Property Using Three Subsets and Applications

Senpeng Wang<sup>(B)</sup>, Bin Hu, Jie Guan, Kai Zhang, and Tairong Shi 

PLA SSF Information Engineering University, Zhengzhou, China wsp2110@126.com 

Abstract. Division property is a generalized integral property proposed by Todo at EUROCRYPT 2015, and then conventional bit-based division property (CBDP) and bit-based division property using three subsets (BDPT) were proposed by Todo and Morii at FSE 2016. At the very beginning, the two kinds of bit-based division properties once couldn’t be applied to ciphers with large block size just because of the huge time and memory complexity. At ASIACRYPT 2016, Xiang et al. extended Mixed Integer Linear Programming (MILP) method to search integral distinguishers based on CBDP. BDPT can find more accurate integral distinguishers than CBDP, but it couldn’t be modeled eficiently. 

This paper focuses on the feasibility of searching integral distinguishers based on BDPT. We propose the pruning techniques and fast propagation of BDPT for the first time. Based on these, an MILP-aided method for the propagation of BDPT is proposed. Then, we apply this method to some block ciphers. For SIMON64, PRESENT, and RECT-ANGLE, we find more balanced bits than the previous longest distinguishers. For LBlock, we find a better 16-round integral distinguisher with less active bits. For other block ciphers, our results are in accordance with the previous longest distinguishers. 

Cube attack is an important cryptanalytic technique against symmetric cryptosystems, especially for stream ciphers. And the most important step in cube attack is superpoly recovery. Inspired by the CBDP based cube attack proposed by Todo at CRYPTO 2017, we propose a method which uses BDPT to recover the superpoly in cube attack. We apply this new method to round-reduced Trivium. To be specific, the time complexity of recovering the superpoly of 832-round Trivium at CRYPTO 2017 is reduced from $2 ^ { 7 7 }$ to practical, and the time complexity of recovering the superpoly of 839-round Trivium at CRYPTO 2018 is reduced from $2 ^ { 7 9 }$ to practical. Then, we propose a theoretical attack which can recover the superpoly of Trivium up to 841 round. 

Keywords: Integral distinguisher Division property MILP Block cipher Cube attack Stream cipher 

## 1 Introduction

Division property, a generalization of integral property [11], was proposed by Todo at EUROCRYPT 2015 [22]. It can exploit the algebraic structure of block ciphers to construct integral distinguishers even if the block ciphers have nonbijective, bit-oriented, or low-degree structures. Then, at CRYPTO 2015 [20], Todo applied this new technique to MISTY1 and achieved the first theoretical cryptanalysis of the full-round MISTY1. Sun et al. [18], revisited division property, and they studied the property of a set (multiset) satisfying certain division property. At CRYPTO 2016 [4], Boura and Canteaut introduced a new notion called parity set to exploit division property. They formulated and characterized the division property of S-box and found better integral distinguisher of PRESENT [3]. But it required large time and memory complexity. To solve this problem, Xie and Tian [28] proposed another concept called term set, based on which they found a 9-round distinguisher of PRESENT with 22 balanced bits. 

In order to exploit the concrete structure of round function, Todo and Morii [21] proposed bit-based division property at FSE 2016. There are two kinds of bit-based division property: conventional bit-based division property (CBDP) and bit-based division property using three subsets (BDPT). CBDP focuses on that the parity $\bigoplus _ { x \in \mathbb { X } } x ^ { u }$ is 0 or unknown, while BDPT focuses on that the parity $\oplus { \pmb x } ^ { \pmb { u } }$ is 0, 1, or unknown. Therefore, BDPT can find more accurate integral x X 

characteristics than CBDP. For example, CBDP proved the existence of the 14-round integral distinguisher of SIMON32 while BDPT found the 15-round integral distinguisher of SIMON32 [21]. 

Although CBDP and BDPT could find accurate integral distinguishers, the huge complexity once restricted their wide applications. At ASIACRYPT 2016, Xiang et al. [27] applied MILP method to search integral distinguishers based on CBDP, which allowed them to analyze block ciphers with large sizes. But there was still no MILP method to model the propagation of BDPT. 

Cube attack, proposed by Dinur and Shamir [6] at EUROCRYPT 2009, is one of the general cryptanalytic techniques against symmetric cryptosystems. For a cipher with n secret variables ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \dots , x _ { n - 1 } )$ and m public variables $\pmb { v } = ( v _ { 0 } , v _ { 1 } , \dots , v _ { m - 1 } )$ , the output bit can be denoted as a polynomial $f \left( \pmb { x } , \pmb { v } \right)$ . The core idea of cube attack is to simplify $f \left( { \pmb x } , { \pmb v } \right)$ by summing the output of cryptosystem over a subset of public variables, called cube. And the target of cube attack is to recover secret variables from the simplified polynomial called superpoly. In the original paper of cube attack [6], the authors regarded stream cipher as a blackbox polynomial and introduced a linearity test to recover superpoly. Recently, many variants of cube attacks were put forward such as dynamic cube attacks [7], conditional cube attacks [14], correlation cube attacks [15], CBDP based cube attacks [23,26], and deterministic cube attacks [30]. 

At EUROCRYPT 2018 [15], Liu et al. proposed correlation cube attack, which could mount to 835-round Trivium using small dimensional cubes. Then, in [30], Ye et al. proposed a new variant of cube attack, named deterministic cube attacks. Their attacks were developed based on degree evaluation method proposed by Liu et al. at CRYPTO 2017 [16]. They proposed a special type of cube that the numeric degree of every term was always less than or equal to the cube size, called useful cube. With a 37-dimensional useful cube, they recovered the corresponding exact superpoly for up to 838-round Trivium. However, as the authors wrote in their paper, it seemed hard to increase the number of attacking round when the cube size increased. Namely, their methods didn’t work well for large cube size. Moreover, at CRYPTO 2018 [9], Fu et al. proposed a key recovery attack on 855-round Trivium which somewhat resembled dynamic cube attacks. For the attack in [9], the paper [12] pointed out that there was possibility that the correct key guesses and the wrong ones shared the same zero-sum property. It means that the key recovery attack may degenerate to distinguish attack. 

It is noticeable that, at CRYPTO 2017 [23], Todo et al. treated the polynomial as non-blackbox and applied CBDP to the cube attack on stream ciphers. Due to the MILP-aided CBDP, they could evaluate the algebraic normal form (ANF) of the superpoly with large cube size. By using a 72-dimensional cube, they proposed a theoretical cube attack on 832-round Trivium. Then, at CRYPTO 2018 [26], Wang et al. improve the CBDP based cube attack and gave a key recovery attack on 839-round Trivium. For CBDP based cube attacks, the superpolies of large cubes can be recovered by theoretical method. But the theory of CBDP cannot ensure that the superpoly of a cube is non-constant. Hence the key recovery attack may be just a distinguish attack. BDPT can exploit the integral distinguisher whose sum is 1, which means BDPT may show a determined key recovery attack. However, compared with the propagation of CBDP, the propagation of BDPT is more complicated and cannot be modeled by MILP method directly. An automatically searching for a variant three-subset division property with STP solver was proposed in [13], but the variant is weaker than the original BDPT. How to trace the propagation of BDPT is an open problem. 

## 1.1 Our Contributions

In this paper, we propose an MILP-aided method for BDPT. Then, we apply it to search integral distinguishers of block ciphers and recover superpolies of stream ciphers. 

## 1.1.1 MILP-aided Method for BDPT

Pruning Properties of BDPT. When we evaluate the propagation of BDPT, there may be some vectors that have no impact on the BDPT of output bit. So we show the pruning properties when the vectors of BDPT can be removed. 

Fast Propagation and Stopping Rules. Inspired by the “lazy propagation” in [21], we propose the notion of “fast propagation” which can translate BDPT into CBDP and show some bits are balanced. Then, based on “lazy propagation” and “fast propagation”, we obtain three stopping rules. Finally, an MILP-aided method for the propagation of BDPT is proposed. 

## 1.1.2 Searching Integral Distinguishers of Block Ciphers

We apply our MILP-aided method to search integral distinguishers of some block ciphers. The main results are shown in Table 1. 

ARX Ciphers. For SIMON32, we find the 15-round integral distinguisher that cannot be found by CBDP. For 18-round SIMON64, we find 23 balanced bits which has one more bit than the previous longest integral distinguisher. 

SPN Ciphers. For PRESENT, when the input data is $2 ^ { 6 0 }$ , our method can find 3 more balanced bits than the previous longest integral distinguisher. Moreover, when the input data is $2 ^ { 6 3 }$ , the integral distinguisher we got has 6 more balanced bits than that got by term set in the paper [28]. For RECTANGLE, when the input data is $2 ^ { 6 0 }$ , our method can also obtain 11 more balanced bits than the previous longest 9-round integral distinguisher. 

Generalized Feistel Cipher. For LBlock, we obtain a 17-round integral distinguisher which is the same with the previous longest integral distinguisher. Moreover, a better 16-round integral distinguisher with less active bits can also be obtained. 

## 1.1.3 Recovering Superpoly of Stream Cipher

Using BDPT to Recover the ANF Coeficient of Superpoly. Inspired by the CBDP based cube attack in [23,26], our new method is based on the propagation of BDPT which can find integral distinguisher whose sum is 0 or 1. But $\mathrm { i t } ^ { \prime } \mathrm { s }$ nontrivial to recover the superpoly by integral distinguishers based on BDPT. Therefore, we proposed the notion of similar polynomial. We can recover the ANF coeficient of superpoly by researching the BDPT propagation of corresponding similar polynomial. In order to analyze the security of ciphers better, we divide ciphers into two categories: public-update ciphers and secretupdate ciphers. For public-update ciphers, we proved that the exact ANF of superpoly can be fully recovered by BDPT. 

Application to Trivium. In order to verify the correctness and efectiveness of our method, we apply BDPT to recover the superpoly of round-reduced Trivium which is a public cipher. To be specific, the time complexity of recovering the superpoly of 832-round Trivium at CRYPTO 2017 is reduced from $2 ^ { 7 7 }$ to practical, and the time complexity of recovering the superpoly of 839-round Trivium at CRYPTO 2018 is reduced from $2 ^ { 7 9 }$ to practical. Then, we propose a theoretical attack which can recover the superpoly of Trivium up to 841 round. The detailed information is shown in Table 2. And the time complexity in the table means the time complexity of recovering superpoly. And c is the average computational complexity of tracing the propagation of BDPT using MILP-aided method. 


Table 1. Summarization of integral distinguishers


<table><tr><td>Cipher</td><td>Data</td><td>Round</td><td>Number of balanced bits</td><td>Time</td><td>Reference</td></tr><tr><td rowspan="2">SIMON32</td><td rowspan="2"><eq>2^{31}</eq></td><td>15</td><td>3</td><td></td><td>[21]</td></tr><tr><td>15</td><td>3</td><td>2m</td><td>Sect. 5.1</td></tr><tr><td rowspan="2">SIMON64</td><td rowspan="2"><eq>2^{63}</eq></td><td>18</td><td>22</td><td>6.7m</td><td>[27]</td></tr><tr><td>18</td><td>23</td><td>1h41m</td><td>Sect. 5.1</td></tr><tr><td rowspan="4">PRESENT</td><td rowspan="2"><eq>2^{60}</eq></td><td>9</td><td>1</td><td>3.4m</td><td>[27]</td></tr><tr><td>9</td><td>4</td><td>56m</td><td>Sect. 5.2</td></tr><tr><td rowspan="2"><eq>2^{63}</eq></td><td>9</td><td>22</td><td></td><td>[28]</td></tr><tr><td>9</td><td>28</td><td>10m</td><td>Sect. 5.2</td></tr><tr><td rowspan="2">RECTANGLE</td><td rowspan="2"><eq>2^{60}</eq></td><td>9</td><td>16</td><td>4.1m</td><td>[27]</td></tr><tr><td>9</td><td>27</td><td>10m</td><td>Sect. 5.2</td></tr><tr><td rowspan="4">LBlock</td><td rowspan="3"><eq>2^{63}</eq></td><td>16</td><td>32</td><td>4.9m</td><td>[27]</td></tr><tr><td>17</td><td>4</td><td></td><td>[8]</td></tr><tr><td>17</td><td>4</td><td>10h25m</td><td>Sect. 5.3</td></tr><tr><td><eq>2^{62}</eq></td><td>16</td><td>18</td><td>6h49m</td><td>Sect. 5.3</td></tr></table>


Table 2. Superpoly recovery of Trivium


<table><tr><td>Rounds</td><td>Cube size</td><td>Exact superpoly</td><td>Complexity</td><td>Reference</td></tr><tr><td rowspan="3">832</td><td rowspan="3">72</td><td rowspan="3">yes</td><td><eq>2^{77}</eq></td><td>[23]</td></tr><tr><td><eq>2^{76.7}</eq></td><td>[26]</td></tr><tr><td>practical</td><td>Sect. 7.3</td></tr><tr><td>835</td><td>36/37</td><td>no</td><td></td><td>[15]</td></tr><tr><td>838</td><td>37</td><td>yes</td><td>practical</td><td>[30]</td></tr><tr><td rowspan="2">839</td><td rowspan="2">78</td><td rowspan="2">yes</td><td><eq>2^{79}</eq></td><td>[26]</td></tr><tr><td>practical</td><td>Sect. 7.3</td></tr><tr><td>841</td><td>78</td><td>yes</td><td><eq>2^{41} \cdot c</eq></td><td>Sect. 7.4</td></tr></table>

## 1.2 Outline of the Paper

This paper is organized as follows: Sect. 2 provides the background of MILP, division property, and cube attacks etc. In Sect. 3, some new propagation properties of BDPT are given. In Sect. 4, we propose an MILP-aided method for BDPT. Section 5 shows applications to block ciphers. In Sect. 6, we use BDPT to recover the superpoly in cube attack. Section 7 shows the application to Trivium. Section 8 concludes the paper. Some auxiliary materials are supplied in Appendix. 

## 2 Preliminaries

## 2.1 Notations

Let $\mathbb { F } _ { 2 }$ denote the finite field 0, 1 and $\textbf { \em a } = ~ ( a _ { 0 } , a _ { 1 } , \ldots , a _ { n - 1 } ) ~ \in ~ \mathbb { F } _ { 2 } ^ { n }$ be an n-bit vector, where $a _ { i }$ denotes the i-th bit of a. For n-bit vectors x and u, define $\begin{array} { r } { \pmb { x } ^ { u } = \prod _ { i = 0 } ^ { n - 1 } x _ { i } ^ { u _ { i } } } \end{array}$ . Then, for any $\boldsymbol { k } \in \mathbb { F } _ { 2 } ^ { n }$ and $\boldsymbol { k } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { n }$ , define $k \succeq k ^ { \prime }$ if $k _ { i } \geq k _ { i } ^ { \prime }$ holds for all $i = 0 , 1 , \ldots , n - 1$ and define $k \succ k ^ { \prime }$ if $k _ { i } > k _ { i } ^ { \prime }$ holds for all $i = 0 , 1 , \ldots , n - 1$ . For a subset $I \subset \{ 0 , 1 , \ldots , n - 1 \}$ , u denotes an n-dimensional bit vector $\left( u _ { 0 } , u _ { 1 } , \ldots , u _ { n - 1 } \right)$ satisfying $u _ { i } = 1 { \mathrm { ~ i f ~ } } i \in I$ and $u _ { i } = 0$ otherwise. We simply write $\mathbb { K } \gets k$ when $\mathbb { K } : = \mathbb { K } \cup \{ k \}$ and $\mathbb { K } \to k$ when $\mathbb { K } : = \mathbb { K } \setminus \{ k \}$ . And <sup>K</sup> denotes the number of elements in the set <sup>K</sup> . 

## 2.2 Mixed Integer Linear Programming

MILP is a kind of optimization or feasibility program whose objective function and constraints are linear, and the variables are restricted to be integers. Generally, an MILP model consists of variables .var, constrains .con, and the objective function .obj. MILP models can be solved by solver like Gurob [10]. If there is no feasible solution, the solver will returns infeasible. When there is no objective function in , the MILP solver will only return whether is feasible or not. 

## 2.3 Bit-Based Division Property

Two kinds of bit-based division property (CBDP and BDPT) were introduced by Todo and Morii at FSE 2016 [21]. In this subsection, we will briefly introduce them and their propagation rules. 

Definition 1 (CBDP [21]). Let <sup>X</sup> be a multiset whose elements take a value of $\mathbb { F } _ { 2 } ^ { n }$ . When the multiset <sup>X</sup> has the CBDP $\mathcal { D } _ { \mathbb { K } } ^ { 1 ^ { n } }$ , where <sup>K</sup> denotes a set of ndimensional vectors whose i-th element takes a value between 0 and 1, it fulfills the following conditions: 

$$
\bigoplus_ {\boldsymbol {x} \in \mathbb {X}} \boldsymbol {x} ^ {\boldsymbol {u}} = \left\{ \begin{array}{l l} \text { unknown,   if   there   exists   } \boldsymbol {k} \in \mathbb {K} \text {   satisfying   } \boldsymbol {u} \succeq \boldsymbol {k}, \\ 0, \text { otherwise. } \end{array} \right.
$$

Definition 2 (BDPT [21]). Let <sup>X</sup> be a multiset whose elements take a value of $\mathbb { F } _ { 2 } ^ { n }$ . Let <sup>K</sup> and <sup>L</sup> be two sets whose elements take n-dimensional bit vectors. When the multiset <sup>X</sup> has the BDPT $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$ , it fulfills the following conditions: 

$$
\bigoplus_ {\boldsymbol {x} \in \mathbb {X}} \boldsymbol {x} ^ {\boldsymbol {u}} = \left\{ \begin{array}{l l} \text { unknown,   if   there   is   } \boldsymbol {k} \in \mathbb {K} \text {   satisfying   } \boldsymbol {u} \succeq \boldsymbol {k}, \\ 1, \text { else   if   there   is   } \boldsymbol {\ell} \in \mathbb {L} \text {   satisfying   } \boldsymbol {u} = \boldsymbol {\ell}, \\ 0, \text { otherwise. } \end{array} \right.
$$

According to [21], if there are $k \in \mathbb { K }$ and $\pmb { k } ^ { \prime } \in \mathbb { K }$ satisfying $k \succeq k ^ { \prime }$ , k can be removed from <sup>K</sup> because the vector k is redundant. We denote this progress as Reduce0 (<sup>K</sup>). If there are $\ell \in \mathbb { L }$ and $k \in \mathbb { K }$ satisfying $\ell \succeq k$ , the vector - can also be removed from <sup>L</sup>. We denote this progress as Reduce1 (<sup>K</sup>, <sup>L</sup>). For any u, the redundant vectors in <sup>K</sup> and <sup>L</sup> will not afect the value of - $\pmb { x } ^ { u }$ 

The propagation rules of <sup>K</sup> in CBDP are the same with BDPT. So here we only show the propagation rules of BDPT. For more details, please refer to [21]. 

BDPT Rule 1 (Copy [21]). Let $\begin{array} { r } { \begin{array} { r c l } { { \pmb { y } } } & { { = } } & { { \pmb { f } \left( { \pmb x } \right) } } \end{array} } \end{array}$ be a copy function, where $\begin{array} { r c l } { { \pmb x } } & { { = } } & { { \left( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } \right) \quad \in \quad { \mathbb { F } } _ { 2 } ^ { n } } } \end{array}$ , and the output is calculated as $\begin{array} { r l } { \pmb { y } } & { { } = } \end{array}$ $( x _ { 0 } , x _ { 0 } , x _ { 1 } , \dotsc , x _ { n - 1 } )$ . Assuming the input multiset <sup>X</sup> has $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$ , then the output multiset <sup>Y</sup> has $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n + 1 } }$ , where 

$$
\mathbb {K} ^ {\prime} \leftarrow \left\{ \begin{array}{l l} (0, 0, k _ {1}, \ldots , k _ {n - 1})  , & \text { if   } k _ {0} = 0 \\ (1, 0, k _ {1}, \ldots , k _ {n - 1})  , (0, 1, k _ {1}, \ldots , k _ {n - 1})  , & \text { if   } k _ {0} = 1 \end{array} \right.,
$$

$$
\mathbb {L} ^ {\prime} \leftarrow \left\{ \begin{array}{l l} (0, 0, \ell_ {1}, \ldots , \ell_ {n - 1})  , & i f   \ell_ {0} = 0 \\ (1, 0, \ell_ {1}, \ldots , \ell_ {n - 1})  , (0, 1, \ell_ {1}, \ldots , \ell_ {n - 1})  , (1, 1, \ell_ {1}, \ldots , \ell_ {n - 1})  , & i f   \ell_ {0} = 1 \end{array} \right.,
$$

are computed from all $k \in \mathbb { K }$ and all $\ell \in \mathbb { L }$ , respectively. 

BDPT Rule 2 (And [21]). Let $\begin{array} { r } { \mathbf { \boldsymbol { y } } = \mathbf { \boldsymbol { f } } \left( \mathbf { \boldsymbol { x } } \right) } \end{array}$ be a function compressed by an And, where the input $\pmb { x } = ( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n }$ , and the output is calculated as $\pmb { y } = ( x _ { 0 } \wedge x _ { 1 } , x _ { 2 } , \dots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n - 1 }$ . Assuming the input multiset <sup>X</sup> has $\boldsymbol { \mathcal { D } } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } } ,$ then the output multiset <sup>Y</sup> has $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n - 1 } }$ , where $\mathbb { K } ^ { \prime }$ is computed from all $k \in \mathbb { K }$ as 

$$
\mathbb {K} ^ {\prime} \leftarrow \left(\left\lceil \frac {k _ {0} + k _ {1}}{2} \right\rceil , k _ {2}, \dots , k _ {n - 1}\right),
$$

and $\mathbb { L } ^ { \prime }$ is computed from all $\ell \in \mathbb { L }$ satisfying $( \ell _ { 0 } , \ell _ { 1 } ) = ( 0 , 0 ) \ o r \ ( 1 , 1 )$ as 

$$
\mathbb {L} ^ {\prime} \leftarrow \left(\left\lceil \frac {\ell_ {0} + \ell_ {1}}{2} \right\rceil , \ell_ {2}, \dots , \ell_ {n - 1}\right).
$$

BDPT Rule 3 (Xor [21]). Let ${ \pmb y } = f \left( { \pmb x } \right)$ be a function compressed by an $X o r ,$ where the input $\pmb { x } = ( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n }$ , and the output is calculated as $\pmb { y } = ( x _ { 0 } \oplus x _ { 1 } , x _ { 2 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n - 1 }$ . Assuming the input multiset <sup>X</sup> has $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } } ,$ then the output multiset <sup>Y</sup> has $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n - 1 } }$ , where $\mathbb { K } ^ { \prime }$ is computed from all $k \in \mathbb { K }$ satisfying $\left( k _ { 0 } , k _ { 1 } \right) = \left( 0 , 0 \right) , \left( 1 , 0 \right) , o r \left( 0 , 1 \right)$ as 

$$
\mathbb {K} ^ {\prime} \leftarrow (k _ {0} + k _ {1}, k _ {2}, \dots , k _ {n - 1}),
$$

$\mathbb { L } ^ { \prime }$ is computed from all $\ell \in \mathbb { L }$ satisfying $( \ell _ { 0 } , \ell _ { 1 } ) = ( 0 , 0 ) , ( 1 , 0 ) , o r ( 0 , 1 )$ as 

$$
\mathbb {L} ^ {\prime} \stackrel {{x}} {{\leftarrow}} \left(\ell_ {0} + \ell_ {1}, \ell_ {2}, \dots , \ell_ {n - 1}\right).
$$

And $\mathbb { L }  \ell$ means 

$$
\mathbb {L} := \left\{ \begin{array}{l} \mathbb {L} \cup \{\boldsymbol {\ell} \} \text {   if   the   original   } \mathbb {L} \text {   does   not   include   } \boldsymbol {\ell}, \\ \mathbb {L} \setminus \{\boldsymbol {\ell} \} \text {   if   the   original   } \mathbb {L} \text {   includes   } \boldsymbol {\ell}. \end{array} \right.
$$

BDPT Rule 4 (Xor with Secret Key [21]). Let <sup>X</sup> be the input multiset satisfying $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { \hat { n } } }$ . For the input $\textbf { \em x } \in \mathrm { ~ \mathbb ~ X ~ }$ , the output $y \in \mathbb { Y }$ is computed as $\pmb { y } = ( x _ { 0 } , \ldots , x _ { i - 1 } , x _ { i } \oplus r _ { k } , x _ { i + 1 } , \ldots , x _ { n - 1 } )$ , where $r _ { k }$ is the secret key. Then, the output multiset <sup>Y</sup> has $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } ; } ^ { 1 ^ { n } }$ , where <sup>K</sup> and $\mathbb { L } ^ { \prime }$ are computed as 

$$
\mathbb {L} ^ {\prime} \leftarrow \ell , f o r \ell \in \mathbb {L},
$$

$$
\mathbb {K} ^ {\prime} \leftarrow \boldsymbol {k}, f o r \boldsymbol {k} \in \mathbb {K},
$$

$$
\mathbb {K} ^ {\prime} \leftarrow (\ell_ {0}, \ell_ {1}, \dots , \ell_ {i} \vee 1, \dots , \ell_ {n - 1}), f o r \ell \in \mathbb {L} s a t i s f y i n g \ell_ {i} = 0.
$$

CBDP Rule 5 (S-box [4,27]). Let $\pmb { y } = f \left( \pmb { x } \right)$ be a function of S-box, where the input $\pmb { x } = ( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } ) \in \mathbb { F } _ { 2 } ^ { n }$ , and the output $\pmb { y } = ( y _ { 0 } , y _ { 1 } , \dots , y _ { m - 1 } ) \in \mathbb { F } _ { 2 } ^ { m }$ Then, every $y _ { i } , i \in \{ 0 , 1 , \dotsc , m - 1 \}$ can be expressed as a Boolean function of $( x _ { 0 } , \ldots , x _ { n - 1 } )$ . For the input CBDP <sup>K</sup>, the output CBDP $\mathbb { K } ^ { \prime }$ is a set of vectors as follows: 

$\mathbb { K } ^ { \prime } = \{ \pmb { u } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { m } |$ for any $\pmb { u } \in \mathbb { K } , \ i f \ y ^ { \pmb { u } ^ { \prime } }$ contains any term $\pmb { x } ^ { v }$ satisfying $v \succeq u \rbrace$ 

When there was no efective way to model the propagation of BDPT, Todo and Morii [21] proposed the notion of ‘lazy propagation” to give the provable security of SIMON family against BDPT. 

Definition 3 (Lazy Propagation [21]). Let $D _ { \mathbb { K } _ { i } , \mathbb { L } _ { i } } ^ { 1 ^ { n } }$ be the input BDPT of the i-th round function and $D _ { \mathbb { K } _ { i + 1 } , \mathbb { L } _ { i + 1 } } ^ { 1 ^ { n } }$ be the BDPT from the lazy propagation. Then, $\overline { { \mathbb { K } } } _ { i + 1 }$ is computed from only a part of vectors in $\mathbb { K } _ { i }$ , and $\overline { { \mathbb { L } } } _ { i + 1 }$ always becomes the empty set $\varnothing .$ . Therefore, if the lazy propagation creates $\mathcal { D } _ { \mathbb { K } _ { r } , \varnothing } ^ { 1 ^ { n } }$ , where $\overline { { \mathbb { K } } } _ { r }$ has n distinct vectors whose Hamming weight is one, the accurate propagation also creates the same n distinct vectors in the same round. 

## 2.4 The MILP Representation of CBDP

For an r-round iterative cipher of size $n ,$ attackers determine indices set $I =$ $\left\{ i _ { 0 } , i _ { 1 } , \dotsc , i _ { | I | - 1 } , \right\} \subset \left\{ 0 , 1 , \dotsc , n - 1 \right\}$ and prepare $2 ^ { | I | }$ chosen plaintexts where variables indexed by I are taking all possible combinations of values and the other variables are set to constants. The CBDP of such chosen plaintexts is $\mathscr { D } _ { \mathbb { K } _ { 0 } = \{ k _ { I } \} } ^ { 1 ^ { n } }$ . Based on the propagation rules, the propagation of CBDP from $\boldsymbol { \mathcal { D } _ { \{ k _ { I } \} } ^ { 1 } } _ { } ^ { n }$ can be evaluated as $\{ \pmb { k } _ { I } \} \overset { d e f } { = } \mathbb { K } _ { 0 }  \mathbb { K } _ { 1 }  \cdots  \mathbb { K } _ { r }$ , where $\mathcal { D } _ { \mathbb { K } _ { r } } ^ { 1 ^ { n } }$ is the CBDP after r-round propagation. If the set $\mathbb { K } _ { r }$ doesn’t have the unit vector $\boldsymbol { e _ { m } } \in \mathbb { F } _ { 2 } ^ { n }$ whose only m-th element is 1, the m-th output bit of r-round ciphertexts is balanced. At ASIACRYPT 2016, Xiang et al. [27] applied MILP method to the propagation of CBDP. They first introduced the concept of CBDP trail, which is defined as follows. 

Definition 4 (CBDP Trail [27]). Let us consider the propagation of the CBDP $\{ \pmb { k } _ { I } \} \overset { d e f } { = } \mathbb { K } _ { 0 }  \mathbb { K } _ { 1 }  \cdots  \mathbb { K } _ { r }$ . For any vector $\pmb { k } _ { i + 1 } \in \mathbb { K } _ { i + 1 }$ , there must exist a vector $\boldsymbol { k } _ { i } \in \mathbb { K } _ { i }$ such that $\boldsymbol { k } _ { i }$ can propagate to $\pmb { k } _ { i + 1 }$ by the propagation rules of CBDP. Furthermore, for $( \pmb { k } _ { 0 } , \pmb { k } _ { 1 } , \dots , \pmb { k } _ { r } ) \in \mathbb { K } _ { 0 } \times \mathbb { K } _ { 1 } \times \dots \times \mathbb { K } _ { r }$ , if $k _ { i }$ can propagate to $k _ { i + 1 }$ for all $i \in \{ 0 , 1 , \ldots r - 1 \}$ , we call $k _ { 0 } \to k _ { 1 } \to \cdot \cdot \cdot \to k _ { \prime }$ an r-round CBDP trail. 

In [27], the authors modeled CBDP propagations of basic operations (Copy, Xor, And) and S-box by linear inequalities. Therefore, they could build an MILP model to cover all the possible CBDP trails generated from a given initial CBDP. Here, we introduce the MILP models for Copy, Xor, And and S-box. 

Model 1 (Copy [27]). Let $a \xrightarrow { C o p y } ( b _ { 0 } , b _ { 1 } , \dots , b _ { n - 1 } )$ be a CBDP trail of Copy. The following inequalities are suficient to describe its CBDP propagation 

$$
\left\{ \begin{array}{l} \mathcal {M}. v a r \leftarrow a, b _ {0}, b _ {1}, \ldots , b _ {n - 1}   a s   b i n a r y, \\ \mathcal {M}. c o n \leftarrow a = b _ {0} + b _ {1} + \dots + b _ {n - 1}. \end{array} \right.
$$

Model 2 (Xor [27]). Let $( a _ { 0 } , a _ { 1 } , \ldots , a _ { n - 1 } ) \ \xrightarrow { X o r }$ b be a division trail of Xor. The following inequalities are suficient to describe its CBDP propagation 

$$
\left\{ \begin{array}{l} \mathcal {M}. v a r \leftarrow a _ {0}, a _ {1}, \ldots , a _ {n - 1}, b \text {as binary}, \\ \mathcal {M}. c o n \leftarrow b = a _ {0} + a _ {1} + \dots + a _ {n - 1}. \end{array} \right.
$$

Model 3 (And [27]). Let $( a _ { 0 } , a _ { 1 } , \dotsc , a _ { n - 1 } ) \ { \xrightarrow { A n d } }$ b be a division trail of And. The following inequalities are suficient to describe its CBDP propagation 

$$
\left\{ \begin{array}{l} \mathcal {M}. v a r \leftarrow a _ {0}, a _ {1}, \ldots , a _ {n - 1}, b \text { as   binary }, \\ \mathcal {M}. c o n \leftarrow b \geq a _ {i} \text { for   all } i \in \{0, 1, \ldots , n - 1 \}. \end{array} \right.
$$

Model 4 (S-box [27]). The CBDP Rule 5 in Sect. 2.3 can generate the CBDP propagation property of S-box. Then, we can using the inequality generator() function in Sage software [17] to get a set of linear inequalities. Sometimes the number of linear inequalities in the set is large. Thus, some Greedy Algorithms [1,19] were proposed to reduced this set. 

## 2.5 Cube Attack

Cube attack was proposed by Dinur and Shamir at EUROCRYPT 2009 [6]. For a cipher with n secret variables ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \dots , x _ { n - 1 } )$ and m public variables $\pmb { v } = ( v _ { 0 } , v _ { 1 } , \dots , v _ { m - 1 } )$ , the output bit can be represented as $f ( { \pmb x } , { \pmb v } )$ . Attackers determine an indices subset $I _ { v } = \{ i _ { 0 } , i _ { 1 } , \ldots , i _ { | I _ { v } | - 1 } \} \subset \{ 0 , 1 , \ldots , m - 1 \}$ , then $f ( { \pmb x } , { \pmb v } )$ can be uniquely represented as 

$$
f (\boldsymbol {x}, \boldsymbol {v}) = \boldsymbol {v} ^ {\boldsymbol {u} _ {I _ {v}}} \cdot p (\boldsymbol {x}, \boldsymbol {v}) \oplus q (\boldsymbol {x}, \boldsymbol {v}),
$$

where $p \left( { \pmb x } , { \pmb v } \right)$ is called the superpoly of $C _ { I _ { v } , J _ { v } , K _ { v } }$ in $f \left( \pmb { x } , \pmb { v } \right)$ , and every term in ${ \bf { \nabla } } q \left( { { \bf { x } } , { \bf { v } } } \right)$ misses at least one variable from $\{ v _ { i _ { 0 } } , v _ { i _ { 1 } } , \ldots , v _ { i _ { | I _ { v } | - 1 } } \}$ 

Attackers can prepare a cube set denoted as $C _ { I _ { v } , J _ { v } , K _ { v } }$ , where public variables indexed by $I _ { v }$ are taking all possible combinations of values, public variables indexed by $J _ { v } \subset \{ 0 , 1 , \dotsc , m - 1 \} - I _ { v }$ are set to constant 1, and public variables indexed by $K _ { v } = \{ 0 , 1 , \cdots , m - 1 \} - I _ { v } - J _ { v }$ are set to constant 0. Just as follows 

$$
C _ {I _ {v}, J _ {v}, K _ {v}} = \left\{\boldsymbol {v} \in \mathbb {F} _ {2} ^ {m} | v _ {i} \in \mathbb {F} _ {2} \text {   if   } i \in I _ {v}, v _ {j} = 1 \text {   if   } j \in J _ {v}, v _ {k} = 0 \text {   if   } k \in K _ {v} \right\}\tag{1}
$$

What’s more, the sum of $f \left( { \pmb x } , { \pmb v } \right)$ over the cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ is 

$$
\bigoplus_ {\boldsymbol {v} \in C _ {I _ {v}, J _ {v}, K _ {v}}} f (\boldsymbol {x}, \boldsymbol {v}) = p _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}).\tag{2}
$$

If $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ is not a constant polynomial, attackers can query the encryption oracle with the chosen cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ to get the equation with secret variables. 

## 2.6 The Cube Attack Based on CBDP

At CRYPTO 2017 [23], Todo et al. successfully applied CBDP to cube attack. They use CBDP to analyze the ANF coeficients of superpoly. 

Lemma 1. [23] Let $f \left( \pmb { x } \right) = \bigoplus _ { \pmb { u } \in \mathbb { F } _ { 2 } ^ { n } } \boldsymbol { a } _ { \pmb { u } } ^ { f } \cdot \pmb { x } ^ { \pmb { u } }$ be a polynomial from $\mathbb { F } _ { 2 } ^ { n }$ to $\mathbb { F } _ { 2 }$ and $a _ { u } ^ { f } \in \mathbb { F } _ { 2 }$ be the ANF coeficients. Let k be an n-dimensional bit vector. If there is no CBDP trail such that k $\underline { { f } } _ {  1 }$ , then $a _ { u } ^ { f }$ is always 0 for ${ \boldsymbol { \mathbf { \mathit { u } } } } \succeq k $ 

Proposition 1. [23] Let $f \left( \pmb { x } , \pmb { v } \right)$ be a polynomial, where $\pmb { x } \in \mathbb { F } _ { 2 } ^ { n }$ and $\pmb { v } \in \mathbb { F } _ { 2 } ^ { m }$ denote the secret and public variables, respectively. For a cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ defined as Eq. (1), let $e _ { i }$ be an n-bit unit vector whose only i-th element is 1. If there is no CBDP trail such that $( e _ { i } , \boldsymbol { u } _ { I _ { v } } ) \xrightarrow { f } 1$ , then $x _ { i }$ is not involved in the superpoly of the cube $C _ { I _ { v } , J _ { v } , K _ { v } }$ 

When $f \left( \pmb { x } , \pmb { v } \right)$ represents the output bit of target cipher, we can use MILP method to identify the involved keys set I by checking whether there is division trial $\{ ( e _ { i } , \boldsymbol { u } _ { I _ { v } } ) \} \stackrel { f } { \longrightarrow } 1$ for $i = 0 , 1 , \cdots , n - 1$ . Then, at CRYPTO 2018 [26], Wang et al. proposed the degree bounding and term enumeration techniques to further reduce the complexity of recovering superpoly. The degree evaluation of superpoly is based on the following proposition. 

Proposition 2. [26] For a set $I _ { x } = \left\{ i _ { 0 } , i _ { 1 } , . . . , i _ { | I _ { x } | - 1 } \right\} \subset \left\{ 0 , 1 , . . . , n - 1 \right\}$ , if there is no CBDP trail such that $( \boldsymbol { u } _ { I _ { x } } , \boldsymbol { u } _ { I _ { v } } ) \overset { f } { \longrightarrow } 1$ , then ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ is not involved in the superpoly of cube $C _ { I _ { v } , J _ { v } , K _ { v } }$ 

After getting the involved keys set I and the degree d of superpoly, the superpoly can be represented with $\textstyle \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } }$ coeficients. Therefore, by selecting ${ \textstyle \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } }$ diferent x, a linear system with ${ \textstyle \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } }$ variables can be constructed. Then, the whole ANF of $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ can be recovered by solving such a linear system. So the complexity of recovering the superpoly of cube $C _ { I _ { v } , J _ { v } , K _ { v } }$ is $\begin{array} { r } { 2 ^ { | I _ { v } | } \times \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } } \end{array}$ 

## 3 The Propagation Properties of BDPT

In this section, we will explore some new propagation properties of BDPT. 

## 3.1 The BDPT Propagation of S-Box

In the Sect. 2.3, we have introduced the existing BDPT propagation rules of Copy, And, and Xor. Although any Boolean function can be evaluated by using these three rules, the propagation requires large time and memory complexity when the Boolean function is complex. Here, we propose a generalized method to calculate the BDPT propagation of S-box. 

Theorem 1. For an S-box: $\mathbb { F } _ { 2 } ^ { n } \ \to \ \mathbb { F } _ { 2 } ^ { m }$ , let ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \dots , x _ { n - 1 } )$ and ${ \textbf { 3 } } =$ $\left( y _ { 0 } , y _ { 1 } , \dotsc , y _ { m - 1 } \right)$ denote the input and output. Every $y _ { i } , i \in \{ 0 , 1 , \dotsc , m - 1 \}$ can be expressed as a boolean function of $( x _ { 0 } , x _ { 1 } , \ldots , x _ { n - 1 } )$ . If the input BDPT of S-box is $\mathcal { D } _ { \mathbb { K } , \mathbb { L } = \{ \ell \} } ^ { 1 ^ { n } }$ , then the output BDPT of S-box can be calculated by $\mathcal { D } _ { R e d u c e { \theta } ( \underline { { \mathbb { K } } } ) } ^ { 1 ^ { m } }$ <sub>K L</sub> , where 

$\mathbb { E } = \{ \pmb { u } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { m } \}$ for any $\mathbf { \pmb { u } } \in \mathbb { K }$ , if $\boldsymbol { y } ^ { u ^ { \prime } }$ contain any term $\pmb { x } ^ { v }$ satisfying ${ \pmb v } \succeq { \pmb u } \rbrace$ $\mathbb { L } = \{ \pmb { u } \in \mathbb { F } _ { 2 } ^ { m } | \pmb { y } ^ { u }$ contains the term ${ \pmb x } ^ { \ell } \}$ 

Proof. Let $\mathbb { K } ^ { \prime }$ be the set of output BDPT that has no redundant vectors. According to the CBDP rules 5 in Sect. 2.3, we know that $\mathbb { K } ^ { \prime } = R e d u c e { \theta } \left( \underline { { \mathbb { K } } } \right)$ 

Let <sup>L</sup> be the set of output BDPT that has no redundant vectors. For any $\textbf { \em u } \in \mathbb { L } ^ { \prime }$ , we have $\oplus \boldsymbol { y } ^ { u } = 1$ . Since there is only one vector - in the input <sup>L</sup>, $\pmb { y } \in \mathbb { Y }$ 

the ANF of $y ^ { u }$ must has the monomial $\scriptstyle { \mathbf { } } x ^ { \ell }$ . Thus, we get $\mathbb { L } ^ { \prime } \subset \underline { { \mathbb { L } } }$ . Because the function Reduce1 only removes the vectors satisfying - y<sup>u</sup> = unknown, we y Y 

have $\mathbb { L } ^ { \prime } \subset$ Reduce1 (<sup>K</sup>, <sup>L</sup>). 

On the other hand, if $y ^ { u }$ contains the monomial $\scriptstyle { \mathbf { } } x ^ { \ell }$ , we have $\bigoplus _ { x \in \mathbb { X } } { \pmb { y } } ^ { u }$ equals unknown or 1. For the set <sup>L</sup>, the function Reduce1 will remove all the vectors satisfying $\oplus \ y ^ { u } = u n k n o w n$ . So all the remaining vectors satisfying $\oplus y ^ { u } = 1$ y Y y Y Ti 

Then, we get Reduce1 $( \underline { { \mathbb { K } } } , \underline { { \mathbb { L } } } ) \subset \mathbb { L } ^ { \prime }$ 

Altogether, we obtain <sup>L</sup> = Reduce1 $( \underline { { \mathbb { K } } } , \underline { { \mathbb { L } } } )$ 

We apply Theorem 1 to the core operation of SIMON family, the obtained BDPT propagation rules are in accordance with that in [21]. Note that Theorem 1 can get the BDPT propagation rules when the input <sup>L</sup> has only one vector. If there are more vectors in <sup>L</sup>, the paper [21] has showed an example on how to get its BDPT propagation rules. Let ${ \mathcal { D } } _ { \mathbb { K } , \mathbb { L } = \{ \ell _ { 0 } , \ell _ { 1 } , \dots , \ell _ { r - 1 } \} } ^ { 1 ^ { n } }$ and $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { m } }$ be the input and output BDPT of S-box, respectively. According to Theorem 1, we can get the output BDPT $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } _ { i } ^ { \prime } } ^ { 1 ^ { m } }$ from the corresponding input BDPT $\mathcal { D } _ { \mathbb { K } , \mathbb { L } = \{ \ell _ { i } \} }$ , where $i = 0 , 1 , \ldots , r - 1$ . Then, 

$$
\mathbb {L} ^ {\prime} = \{\ell | \ell \text { appears   odd   times   in   sets } \mathbb {L} _ {0} ^ {\prime}, \mathbb {L} _ {1} ^ {\prime}, \dots , \mathbb {L} _ {r - 1} ^ {\prime} \}.
$$

And we also give an example in Sect. 5.1 to help readers understand the propagation of BDPT. 

## 3.2 Pruning Techniques of BDPT

The previous works often divide ciphers into r rounds, and investigate the CBDP or BDPT of round functions. Round functions often have too many operations which will generate many redundant intermediate vectors of division property. When the round number or block size grows, it will make propagation impossible just because of complexity. In order to solve this problem, we divide the ciphers into small parts. And after getting the BDPT propagation of a part, we will use the pruning techniques to remove the redundant vectors. Then, the remaining vectors in BDPT can continue to propagate eficiently. 

Let $Q _ { i }$ be the i-th round function of an r-round cipher $E = Q _ { r } \circ Q _ { r - 1 } \circ$ $\cdots \circ Q _ { 1 }$ , then we divide $Q _ { i }$ into $l _ { i }$ parts $Q _ { i } \ = \ Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 } ,$ Let $E _ { i , j } \ = \ ( Q _ { i , j - 1 } \circ Q _ { i , j - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 } ) \circ ( Q _ { i - 1 } \circ Q _ { i - 2 } \circ \cdot \cdot \cdot \circ Q _ { 1 } )$ and ${ \overline { { E _ { i , j } } } } ~ =$ $\left( Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { i + 1 } \right) \left( Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdots \circ Q _ { i , j } \right)$ , then $E = \overline { { E _ { i , j } } } \circ E _ { i , j }$ , where $1 \leq i \leq r , 0 \leq j \leq l _ { i } - 1$ and $E _ { 1 , 0 }$ is identity function. 

Theorem 2 (Prune <sup>K</sup>). For r-round cipher $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { 1 }$ , let $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ be the input BDPT of $\overline { { E _ { i , j } } }$ . For any vector $\boldsymbol { k } \in \mathbb { K } _ { i , j }$ , if there is no CBDP trail such that k $\xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ , the BDPT propagation of $\boldsymbol { \mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } } }$ is equivalent to that of $\mathcal { D } _ { \mathbb { K } _ { i , j }  k , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ on whether $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ and $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 }$ or not. 

Proof. In Sect. 2.3, we know that for public function, the BDPT propagation of $\mathbb { K } _ { i , j }$ and $\mathbb L _ { i , j }$ is independent. Only when the secret round key is Xored, some vectors of $\mathbb L _ { i , j }$ will afect $\mathbb { K } _ { i , j }$ , but they only adds some vectors into $\mathbb { K } _ { i , j }$ . Because every vector $\boldsymbol { k } \in \mathbb { K } _ { i , j }$ is propagated independently based on CBDP, if there is no CBDP trail such that $k \xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ , then removing it from $\mathbb { K } _ { i , j }$ doesn’t have any impact on whether ${ \mathbb K } _ { r + 1 , 0 }$ includes $e _ { m }$ or not. That means $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { \mathbf { i } ^ { n } }$ has the same result with $\mathcal { D } _ { \mathbb { K } _ { i , j }  k , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ on whether ${ \mathbb K } _ { r + 1 , 0 }$ includes $e _ { m }$ or not. 

Because all the vectors of $\mathbb { L } _ { r + 1 , 0 }$ are generated from $\mathbb L _ { i , j }$ , that is, removing k from $\mathbb { K } _ { i , j }$ has no impact on the generation of $e _ { m } \in \mathbb { L } _ { r + 1 , 0 } .$ . On the other hand, we have got that removing k from $\mathbb { K } _ { i , j }$ doesn’t have any impact on whether ${ \mathbb K } _ { r + 1 , 0 }$ includes $e _ { m }$ or not. So it has no impact on the reduction of $e _ { m } \in \mathbb { L } _ { r + 1 , 0 } .$ That means $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ has the same result with $\mathcal { D } _ { \mathbb { K } _ { i , j }  k , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ on whether $\mathbb { L } _ { r + 1 , 0 }$ includes $e _ { m }$ or not. □ 

Theorem 3 (Prune <sup>L</sup>). For r-round cipher $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { 1 }$ , let $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ be the input BDPT of $\overline { { E _ { i , j } } }$ . For any vector $\ell \in \mathbb { L } _ { i , j }$ , if there is no CBDP trail such that $\ell \stackrel { \overline { { E _ { i , j } } } } { \longrightarrow } e _ { m }$ , the BDPT propagation of $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ is equivalent to that of $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j }  \ell } ^ { 1 ^ { n } }$ on whether $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ and $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 }$ or not. 

Proof. For any vector $\ell \in \mathbb { L } _ { i , j }$ , if there is no CBDP trail such that $\ell \stackrel { \overline { { E _ { i , j } } } } { \longrightarrow } e _ { m }$ 2 according to Theorem 2, the BDPT propagation of $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ is equivalent to that of $\mathcal { D } _ { \mathbb { K } _ { i , j }  \ell , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ on whether $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ and $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 } \mathrm { ~ o r ~ }$ not. 

Because ${ \mathbb K } _ { i , j } ~ \gets ~ \ell .$ , the vector - can be removed from $\mathbb L _ { i , j }$ according to the definition of BDPT. So the BDPT $\mathcal { D } _ { \mathbb { K } _ { i , j }  \ell , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ is completely equivalent to $\mathcal { D } _ { \mathbb { K } _ { i , j } \left. \ell , \mathbb { L } _ { i , j } \right. \ell } ^ { 1 ^ { n } } .$ 

According to Theorem 2 again, the BDPT propagation of $\mathcal { D } _ { \mathbb { K } _ { i , j } \left. \ell , \mathbb { L } _ { i , j } \right. \ell } ^ { 1 ^ { n } }$ is equivalent to that of $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j }  \ell } ^ { 1 ^ { n } }$ on whether $\boldsymbol { e } _ { m } \in \mathbb { K } _ { r + 1 , 0 }$ and $\boldsymbol { e } _ { m } \in \mathbb { L } _ { r + 1 , 0 }$ or not. - 

The propagation of CBDP can be eficiently solved by MILP model. Therefore, the meaning of Theorems 2 and 3 is that we can use CBDP method to reduce the BDPT sets $\mathbb { K } _ { i , j }$ and $\mathbb L _ { i , j }$ 

## 3.3 Fast Propagation

Inspired by the notion of “lazy propagation”, we propose a notion called “fast propagation” to show the balanced information of output bits. 

Definition 5 (Fast Propagation). For r-round cipher $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdot \cdot \cdot \circ Q _ { 1 }$ let $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ be the input BDPT of $\overline { { E _ { i , j } } }$ . Under fast propagation, we translate the BDPT into CBDP $\mathcal { D } _ { \mathbb { K } _ { i , j } } ^ { 1 ^ { n } }$ , where $\overline { { \mathbb { K } } } _ { i , j } = \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j }$ . The output CBDP of $\overline { { E _ { i , j } } }$ is computed from $\mathcal { D } _ { \mathbb { K } _ { i , j } } ^ { 1 ^ { n } }$ 

The “fast propagation” removes all vectors from $\mathbb L _ { i , j }$ , and get the union set $\mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j }$ . By its nature, “fast propagation” translate BDPT into CBDP. We can use the MILP method to solve the CBDP propagation of $\boldsymbol { \mathcal { D } } _ { \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j } } ^ { 1 ^ { n } } ,$ . Let us consider the meaning of “fast propagation”. Assuming the input set of $\overline { { E _ { i , j } } }$ has BDPT $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ , according to the definition of BDPT and CBDP, this set must also has CBDP $\overset { \cdot } { \mathcal { D } } _ { \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j } } ^ { 1 ^ { n } } ,$ . If for any $\pmb { k } \in \mathbb { K } _ { i , j } \cup \mathbb { L } _ { i , j }$ , there is no CBDP trial such that $k \xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ , then the m-th output bit of $\overline { { E _ { i , j } } }$ is balanced. 

## 4 The MILP-aided Method for BDPT

Based on the work of [27], we first simplify the MILP algorithm of searching integral distinguishers based on CBDP to improve eficiency. Then, we show three stopping rules and propose an algorithm to search integral distinguishers based on BDPT. 

## 4.1 Simplify the MILP Method of CBDP

Using the method in the paper [27], we can get a linear inequality set which describes the r-round CBDP division trails with the given initial CBDP ${ \mathcal { D } } _ { \{ k \} } ^ { 1 ^ { n } }$ The former CBDP method will return a set of balanced bits. Because only one bit’s balanced information is needed, our MILP model has no objective function which is added into the constrains. We can use the solver Gurobi [10] to determine whether the MILP model has feasible solutions or not. If it has feasible solutions, it shows that the m-th bit of the output is unknown. Otherwise, the m-th bit is balanced. The detail information is shown in Algorithm 1. 

## 4.2 Stopping Rules

Based on “lazy propagation” and “fast propagation”, in this subsection, we propose three stopping rules in searching integral distinguishers based on BDPT. 

Algorithm 1. SCBDP(E, k, m)

Input: The cipher E, the initial CBDP vector k, and the number m
Output: Whether the m-th bit of the output is balanced or not based on CBDP 1 begin
2 L is a linear inequality set which describe the CBDP division trails such that $k \xrightarrow{E} e_{m}$ 3 if L has feasible solutions do
4 return unknown
5 else
6 return 0
7 end 

Stopping Rule 1. For an r-round cipher $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdot \cdot \cdot \circ Q _ { 1 }$ , let $\mathcal { D } _ { \mathbb { K } _ { i , j } , \mathbb { L } _ { i , j } } ^ { 1 ^ { n } }$ be the input BDPT of $\overline { { E _ { i , j } } }$ . For any vector $\boldsymbol { k } \in \mathbb { K } _ { i , j }$ , if there is CBDP trail such that k $\xrightarrow { \overline { { E _ { i , j } } } } e _ { m }$ , according to “lazy propagation”, we stop the process and obtain that the m-th output bit of E is unknown. 

After Stopping Rule 1, if the searching procedure doesn’t stop, all the vectors in $\mathbb { K } _ { i , j }$ will be removed according to the pruning technique in Theorem 2. Then, we consider the following Stopping Rule 2. 

Stopping Rule 2. After removing the redundant vectors in the set $\mathbb L _ { i , j }$ by the pruning technique in Theorem 3, if there is still vector $\ell \in \mathbb { L } _ { i , j }$ , we cannot stop the procedure and - should be propagated to next part based on BDPT. If there is no vector in $\mathbb L _ { i , j ; }$ , according to “fast propagation”, we can get that the m-th output bit of E is balanced. 

Diferent from Stopping Rule 1 which shows the m-th bit is unknown, Stopping Rule 2 can show the m-th bit is balanced based on BDPT. If the process doesn’t stop even we get the output BDPT of $E .$ , Stopping Rule 3 can explain this situation. 

Stopping Rule 3. If $\mathbb { K } _ { r + 1 , 0 } = \varnothing$ and $\mathbb { L } _ { r + 1 , 0 } = \{ e _ { m } \}$ , then we find an integral distinguisher whose sum of the m-th output bit is 1. 

## 4.3 The MILP-aided Method of Searching Integral Distinguishers Based on BDPT

The algorithm of searching integral distinguishers often has a given initial BDPT $\mathcal { D } _ { \mathbb { K } _ { 1 , 0 } , \mathbb { L } _ { 1 , 0 } } ^ { 1 ^ { n } }$ . For an indices set $I = \{ i _ { 0 } , i _ { 1 } , \dotsc , i _ { | I | - 1 } \} \subset \{ 0 , 1 , \dotsc , n - 1 \}$ , attackers prepare $2 ^ { | I | }$ chosen plaintexts where variables indexed by I are taking all possible combinations of values and the other variables are set to constants. The CBDP of such chosen plaintexts is $\mathcal { D } _ { \{ u _ { I } \} } ^ { 1 ^ { n } }$ . Then, the BDPT of such chosen plaintexts is $\mathcal { D } _ { \mathbb { K } _ { 1 , 0 } , \mathbb { L } _ { 1 , 0 } }$ , where $\mathbb { K } _ { 1 , 0 } = \{ \pmb { u } ^ { \prime } \in \mathbb { F } _ { 2 } ^ { \acute { n } } | \pmb { u } ^ { \prime } \succ \pmb { u } _ { I } \}$ and $\mathbb { L } _ { 1 , 0 } = \{ { \pmb u } _ { I } \}$ . We illustrate the whole framework in Algorithm 2. 

```csv
Algorithm 2. BDPT(E, L1,0, K1,0, m)

Input: The cipher E, the input BDPT D_{K1,0, L1,0}, and the number m
Output: The balanced information of the m-th output bit based on BDPT

1 begin
2 for (i = 1; i ≤ r; i++) do
3 for (j = 0; j ≤ l_i - 1; j++) do
4 for k in K_{i,j}
5 if SCBDP(E_{i,j}, k, m) is unknown
6 return unknown
7 else
8 K_{i,j} → k
9 end
10 L'_{i,j} = ∅
11 for ℓ in L_{i,j} do
12 if SCBDP(E_{i,j}, ℓ, m) is unknown
13 L'_{i,j} = L'_{i,j} ∪ ℓ
14 end
15 end
16 if L'_{i,j} = ∅
17 return 0
18 end
19 D_{K_{i+[(j+1)/l_i], (j+1)modl_i}, L_{i+[(j+1)/l_i], (j+1)modl_i}} = BDPTP(Q_{i,j}, D_{0, L'_{i,j}})
20 end
21 end
22 return 1
23 end 
```

We explain Algorithm 2 line by line: 

Line 2–3 The cipher E is divided into small parts. 

Line 4–9 For every $\boldsymbol { k } \in \mathbb { K } _ { i , j }$ , if $S C B D P \left( \overline { { E _ { i , j } } } , k , m \right)$ is unknown (Algorithm 1), according to Stopping Rule 1, we know that the m-th output bit is unknown based on BDPT. Otherwise, we remove it from $\mathbb { K } _ { i , j }$ according to the pruning technique in Theorem 2. 

Line 10 Initialize $\mathbb { L } _ { i , j } ^ { \prime }$ to be an empty set. 

Line 11–15 For any vector $\ell \in \mathbb { L } _ { i , j }$ , if $S C B D P ( \overline { { E _ { i , j } } } , \ell , m )$ can generate the unit vector $e _ { m }$ , we store all these vectors in $\mathbb { L } _ { i , j } ^ { \prime }$ 

Line 16–18 If the set $\mathbb { L } _ { i , j } ^ { \prime }$ is empty set, it satisfies Stopping Rule 2, that is, the m-th output bit is balanced. 

Line 19 If we don’t get the balanced information of the m-th bit, we should use the propagation rules of BDPT to get the input BDPT of the next part. 

Line 22 It triggers Stopping Rules 3, and the sum of the m-th output bit is 1. 

The principle of dividing the round function $Q _ { i }$ is that the vectors of BDPT don’t expand too much. Only in this way can we run the searching algorithm eficiently. Algorithm 2 can show the balanced information of any output bit. Therefore, we can search the integral distinguishers of cipher in parallel. 

## 5 Applications to Block Ciphers

In this section, we apply our algorithm to SIMON, SIMECK, PRESENT, RECT-ANGLE, and LBlock. All the experiments are conducted on the platform: Intel Core i5-4590 CPU @3,3 GHz, 8.00G RAM. And the optimizer we used to solve MILP models is Gurobi 8.1.0 [10]. For the integral distinguishers, what needs to be explained is that “a” denotes active bit, “c” denotes constant bit, “?” denotes the balanced information is unknown, and “b” denotes the balanced bit. 

## 5.1 Applications to SIMON and SIMECK

SIMON is a lightweight block cipher family [2] based on Feistel structure which only involves bit-wise And, Xor, and Circular shift operations. Let SIMON2n be the SIMON cipher with 2n-bit block length, where $n \in \{ 1 6 , 2 4 , 3 2 , 4 8 , 6 4 \}$ And the left part of Fig. 1 shows the round structure of SIMON2n. The core operation of round function is represented by the right part of Fig. 1. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-07-10/fc103d2e-553f-422f-95d9-dea73aded7ea/e89ca66f7a329c54483a213195033bc574f7dc67f2ca2f584e08163c8fd3bcee.jpg)



a i n-th round structure of SIMON2


![image](https://cdn-mineru.openxlab.org.cn/result/2026-07-10/fc103d2e-553f-422f-95d9-dea73aded7ea/7b98b69891bdff63c3b587d35e506aca814e3ebacf8c00e7ac2c504ed020af92.jpg)



The core operationb $\mathrm { Q } _ { i , j }$



Fig. 1. The structure of SIMON2n


When we apply Algorithm 2 to SIMON2n, we divide one-round SIMON2n into $n + 1$ parts $Q _ { i } = Q _ { i , n } \circ Q _ { i , n - 1 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 }$ . And the input of $Q _ { i , j }$ is denoted as $\left( \pmb { x } ^ { i , j } , \pmb { y } ^ { i , j } \right) = \left( x _ { n - 1 } ^ { i , j } , \ldots , x _ { 0 } ^ { i , j } , y _ { n - 1 } ^ { i , j } , \ldots , y _ { 0 } ^ { i , j } \right)$ . When $0 \leq j \leq n - 1$ , we have 

$$
Q _ {i, j} \left(\boldsymbol {x} ^ {i, j}, \boldsymbol {y} ^ {i, j}\right) = \left(\boldsymbol {x} ^ {i, j}, y _ {n - 1} ^ {i, j}, \dots , y _ {j + 1} ^ {i, j}, Y _ {j} ^ {i, j}, y _ {j - 1} ^ {i, j}, \dots , y _ {0} ^ {i, j}\right),
$$

where Y <sup>i,j</sup><sub>j</sub> = x<sup>i,j</sup> <sub>(j−1)modn</sub>&x <sup>i,j</sup><sub>(j 8)modn</sub><sup></sup> - x<sup>i,j</sup><sub>(j 2)modn</sub>. 

Moreover, $Q _ { i , n } \left( \pmb { x } ^ { i , n } , \pmb { y } ^ { i , n } \right) = \left( \pmb { y } ^ { i , n } \oplus \pmb { k } ^ { i } , \pmb { x } ^ { i , n } \right)$ , where $k ^ { i }$ is the i-th round key of SIMON2n. 

For $Q _ { i , j } , 0 \leq j \leq n - 1$ , when we consider the BDPT propagation rules of the function $B D P T P \Big ( Q _ { i , j } , \mathcal { D } _ { \emptyset , \mathbb { L } _ { i , j } ^ { \prime } } \Big ) , ( 2 n - 4 )$ bits remain unchanged. Thus, only 4- bit $\left( x _ { ( j - 1 ) \mathrm { m o d } ~ n } ^ { i , j } , x _ { ( j - 2 ) \mathrm { m o d } n } ^ { i , j } , x _ { ( j - 8 ) \mathrm { m o d } n } ^ { i , j } , y _ { ( j ) \mathrm { m o d } n } ^ { i , j } \right)$ of the BDPT vectors will be changed. We can view it as 4-bit S-box and use Theorem 1 to get its accurate BDPT propagation rules which are in accordance with that in the paper [21]. We show it in Appendix Table 7. 

When we use Algorithm 2 to search the integral distinguishers of SIMON2n based on BDPT, we should call Algorithm 1 to build the MILP model based on CBDP. The paper [27] has showed us how to model CBDP division trails of 1-round SIMON2n. We introduce it as follows. 

1-round Description of SIMON2n. Denote 1-round CBDP trail of SIMON2n by $\left( a _ { n - 1 } ^ { i } , \ldots , a _ { 0 } ^ { i } , \bar { b } _ { n - 1 } ^ { i } , \ldots , b _ { 0 } ^ { i } \right) \ \longrightarrow \ \left( a _ { n - 1 } ^ { i + 1 } , \ldots , a _ { 0 } ^ { i + 1 } , b _ { n - 1 } ^ { i + 1 } , \ldots , b _ { 0 } ^ { i + 1 } \right) \ $ . In order to get a linear description of all CBDP trails of 1-round SIMON2n, we introduce four vectors of auxiliary variables which are $\left( u _ { n - 1 } ^ { i } , \ldots , u _ { 0 } ^ { i } \right) , \left( v _ { n - 1 } ^ { i } , \ldots , v _ { 0 } ^ { i } \right)$ , $\left( w _ { n - 1 } ^ { i } , \ldots , w _ { 0 } ^ { i } \right)$ and $\left( t _ { n - 1 } ^ { i } , \ldots , t _ { 0 } ^ { i } \right)$ . We denote $\left( u _ { n - 1 } ^ { i } , \ldots , u _ { 0 } ^ { i } \right)$ the input CBDP of the left circular shift by 1 bit. Similarly, denote $\left( v _ { n - 1 } ^ { i } , \ldots , v _ { 0 } ^ { i } \right)$ and $\left( w _ { n - 1 } ^ { i } , \ldots , w _ { 0 } ^ { i } \right)$ the input CBDP of the left circular shift by 8 bits and 2 bits, respectively. Let $\left( t _ { n - 1 } ^ { i } , \ldots , t _ { 0 } ^ { i } \right)$ denote the output CBDP of bit-wise And operation. The following inequalities are suficient to model the Copy operation used in SIMON2n: 

$$
\mathcal {L} _ {1}: a _ {j} ^ {i} - u _ {j} ^ {i} - v _ {j} ^ {i} - w _ {j} ^ {i} - b _ {j} ^ {i + 1} = 0 \text {   for   } j \in \{0, 1, \dots , n - 1 \}.
$$

Then, the bit-wise And operation used in SIMON2n can be modeled by: 

$$
\mathcal {L} _ {2} = \left\{ \begin{array}{l l} t _ {j} ^ {i} - u _ {(j - 1) \mathrm{mod} n} ^ {i} \geq 0, & \text { for } j \in \{0, 1, \ldots , n - 1 \}, \\ t _ {j} ^ {i} - v _ {(j - 8) \mathrm{mod} n} ^ {i} \geq 0, & \text { for } j \in \{0, 1, \ldots , n - 1 \}, \\ t _ {j} ^ {i} - u _ {(j - 1) \mathrm{mod} n} ^ {i} - v _ {(j - 8) \mathrm{mod} n} ^ {i} \leq 0, & \text { for } j \in \{0, 1, \ldots , n - 1 \}. \end{array} \right.
$$

At last, the Xor operation in SIMON2n can be modeled by: 

$$
\mathcal {L} _ {3}: a _ {j} ^ {i + 1} - b _ {j} ^ {i} - t _ {j} ^ {i} - w _ {(j - 2) \mathrm{mod} n} ^ {i} = 1 \text {for} j \in \{0, 1, \dots , n - 1 \}.
$$

So far, we get a description $\{ { \mathcal { L } } _ { 1 } , { \mathcal { L } } _ { 2 } , { \mathcal { L } } _ { 3 } \}$ of 1-round CBDP trails. 

How to Describe the CBDP Propagation of Partial Round. For $\overline { { E _ { i , j } } }$ , the first round maybe a partial round $Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , j }$ . When considering the CBDP propagation of $Q _ { i , j }$ , if add constrain $b _ { j } ^ { i + 1 , j } = \bar { b } _ { j } ^ { i , j }$ , the output vector is the same with the input vector. Namely, $\boldsymbol { Q } _ { i , j }$ is transformed into identity function. 

For 1-round SIMON2n, by adding the following constrains 

$$
\mathcal {L} _ {4}: a _ {j} ^ {i + 1} - b _ {j} ^ {i} = 0 \text {   for   } j \in \{0, 1, \dots , j - 1 \},
$$

we obtain a description $\{ { \mathcal { L } } _ { 1 } , { \mathcal { L } } _ { 2 } , { \mathcal { L } } _ { 3 } , { \mathcal { L } } _ { 4 } \}$ of partial round $Q _ { i , l _ { i } - 1 } \circ Q _ { i , l _ { i } - 2 } \circ \cdot \cdot \cdot \circ Q _ { i , j }$ Then, by repeating the constrains of 1-round $( r - i )$ times, we can get a linear inequality system for $\overline { { E _ { i , j } } }$ 

How to Obtain the Output BDPT of $Q _ { i , j }$ . After the pruning techniques and stopping rules, if Algorithm 2 doesn’t stop, we know that $\mathbb { K } _ { i , j } = \varnothing$ and $\mathbb { L } _ { i , j } \neq \emptyset$ In order to help readers understand our algorithm, we show an example of the propagation of BDPT. 

For SIMON32, if the input BDPT of $Q _ { 1 , 1 5 }$ is $\mathcal { D } _ { \mathbb { K } _ { 1 , 1 5 } = \varnothing , \mathbb { L } _ { 1 , 1 5 } = \{ \ell _ { 1 } , \ell _ { 2 } \} }$ , where $\ell _ { 1 }$ $\mathbf { \Lambda } = ( 1 , \mathbf { 0 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } , \mathbf { 1 } ) , \ell _ { 2 } = \mathbf { 0 } .$ (1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1). The 4 bits of $\ell _ { 1 }$ that may be updated by $Q _ { 1 , 1 5 }$ is (0, 1, 1, 0). Then, according to the BDPT propagation rules of core operation in Table 7. The output vector set is $\mathbb { L } ^ { \prime } = \{ [ \bar { 0 } , 1 , 1 , \bar { 0 } ] , [ 0 , 1 , 0 , 1 ] , [ 0 , 1 , 1 , 1 ] \}$ . So $\ell _ { 1 }$ generates three vectors as: 

(1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) (1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) (1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) 

In the same way, we can obtain that $\ell _ { 2 }$ generates only one vector as 

(1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) . 

According to BDPT Rule 3, the vector (1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) should be canceled because it is propagated from $\ell _ { 1 }$ and $\ell _ { 2 }$ twice. The output BDPT of $Q _ { 1 , 1 5 }$ is $\mathcal { D } _ { \mathbb { K } _ { 1 , 1 6 } = \varnothing , \mathbb { L } _ { 1 , 1 6 } = \{ \ell _ { 3 } , \ell _ { 4 } \} }$ , where 

$\ell _ { 3 } = ( 1 , \mathbf { 0 } , \mathbf { 1 } , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 )$ - = (1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) . 

Then, $Q _ { 1 , 1 6 }$ has round keys Xored operation. So a new vector is generated from $\ell _ { 3 }$ and inserted into $\mathbb { K } _ { 1 , 1 6 }$ according to the BDPT Rule 4. Moreover, a vector in $\mathbb { L } _ { 1 , 1 6 }$ becomes redundant because of the new vector of $\mathbb { K } _ { 1 , 1 6 }$ . After the swapping, the output BDPT of $Q _ { 1 , 1 6 }$ is $\mathcal { D } _ { \mathbb { K } _ { 2 , 0 } = \{ k \} , \mathbb { L } _ { 2 , 0 } = \{ \ell _ { 5 } \} }$ , where 

k = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), -<sub>5</sub> = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1). 

The High Eficiency of Our Algorithm. For 14-round SIMON32, we prepare chosen plaintexts such that the leftmost bit is constant and the others are active. Then, the BDPT of chosen plaintexts is $\scriptstyle \mathcal { D } _ { \mathbb { K } = \{ ( 1 , 1 , 1 , \dots , 1 ) \} , \mathbb { L } = \{ ( 0 , 1 , 1 , \dots , 1 ) \} }$ . Table 3 shows the sizes of $| \mathbb { K } |$ and <sup>L</sup> in every round. The sizes in the paper [21] are obtained after removing redundant vectors according to the definition of BDPT, while the sizes in this paper are obtained after the pruning techniques. From Table 3, we find that <sup>L</sup> of the 5-th round in this paper becomes 0, it triggers Stopping Rule 2, and we obtain that the rightmost bit is balanced. Our pruning techniques can reduce the size of BDPT greatly. 

Integral Distinguishers. SIMECK is a family of lightweight block cipher proposed at CHES 2015 [29], and its round function is very similar to that of SIMON except the rotation constants. We use Algorithm 2 to search the integral distinguishers of SIMON and SIMECK family based on BDPT. For SIMON32, our MILP algorithm finds the 14-round integral distinguisher that found in [21] by going through all the BDPT division trails. For 17-round SIMON64, we find an integral distinguisher with 23 balanced bits which has one more bit than the previous longest integral distinguisher. For SIMON48/96/128 and SIMECK32/48/64, the distinguishers we find are in accordance with the previous longest distinguishers that found in [27]. The detailed integral distinguishers of SIMON32 and SIMON64 are listed in Table 4. And all the integral distinguishers in Table 4 can be extended one more round by the technique in [25]. 


Table 3. Sizes of $\mathcal { D } _ { \mathbb { K } , \mathbb { L } }$ in obtaining balanced information of the rightmost output bit


<table><tr><td rowspan="2">Reference</td><td rowspan="2">BDPT</td><td colspan="16">Size in every round</td></tr><tr><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>11</td><td>12</td><td>13</td><td>14</td><td>15</td></tr><tr><td rowspan="2">[21]</td><td></td><td><eq>\mathbb{L}</eq></td><td>1</td><td>1</td><td>5</td><td>19</td><td>138</td><td>2236</td><td>89878</td><td>4485379</td><td>47149981</td><td>2453101</td><td>20360</td><td>168</td><td>8</td><td>0</td><td>0</td></tr><tr><td><eq>\mathbb{K}</eq></td><td>1</td><td>1</td><td>1</td><td>6</td><td>43</td><td>722</td><td>23321</td><td>996837</td><td>9849735</td><td>2524718</td><td>130724</td><td>7483</td><td>852</td><td>181</td><td>32</td><td>32</td></tr><tr><td rowspan="2">This paper</td><td></td><td><eq>\mathbb{L}</eq></td><td>1</td><td>1</td><td>1</td><td>2</td><td>2</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td><eq>\mathbb{K}</eq></td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr></table>


Table 4. Integral distinguishers of SIMON32 and SIMON64


```txt
Cipher Distinguisher
14-SIMON32 In: (caaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaa)
Out: (?????????????????, ?b??????b??????b)
17-SIMON64 In: (caaaaaaaaaaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaaaaaaaaaa, bbbbbbbbbb?b??b????bbbbbbbb) 
```

## 5.2 Applications to PRESENT and RECTANGLE

PRESENT [3] has an SPN structure and uses 80- and 128-bit keys with 64-bit blocks through 31 rounds. In order to improve the hardware eficiency, it use a fully wired difusion layer. Figure 2 illustrates one-round structure of PRESENT. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-07-10/fc103d2e-553f-422f-95d9-dea73aded7ea/008f44d123e40ddf248b97bcf5b126a3b9771ef95748c0cfd2d2033e9ddb3b9e.jpg)



Fig. 2. One-round SPN structure of PRESENT


We divide one-round PRESENT into 17 parts $Q _ { i } = Q _ { i , 1 6 } \circ \cdot \cdot \cdot \circ Q _ { i , 0 }$ . When $0 \leq$ $j \le 1 5$ , we have $Q _ { i , j } \left( x _ { 0 } ^ { i , j } , \ldots , x _ { 6 3 } ^ { i , j } \right) = \left( x _ { 0 } ^ { i , j } , \ldots , S \left( x _ { 4 j } ^ { i , j } , \ldots , x _ { 4 j + 3 } ^ { i , j } \right) , \ldots , x _ { 6 3 } ^ { i , j } \right)$ where $S \left( x _ { 4 j } ^ { i , j } , \ldots , x _ { 4 j + 3 } ^ { i , j } \right)$ is the S-box of PRESENT. 

Moreover, $Q _ { i , 1 6 } \left( x _ { 0 } ^ { i , 1 6 } , \ldots , x _ { 6 3 } ^ { i , 1 6 } \right) = P \left( x _ { 0 } ^ { i , 1 6 } , x _ { 1 } ^ { i , 1 6 } , \ldots , x _ { 6 3 } ^ { i , 1 6 } \right) \oplus k ^ { i }$ , where P is the linear permutation of PRESENT and $k ^ { i }$ is the i-th round key. 

RECTANGLE [31] is very like PRESENT. We apply Algorithm 2 to PRESENT and RECTANGLE, and the results are listed in Table 5. 


Table 5. Integral distinguishers of PRESENT and RECTANGLE


<table><tr><td>Cipher</td><td>Distinguisher</td></tr><tr><td>9-PRESENT</td><td>In: (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaacccc)Out: (????????????????????????????????? ,????????????????????b???b???b???b)</td></tr><tr><td>9-PRESENT</td><td>In: (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaaaac)Out: (??b???b???bbbb???b???b???bbbb, ???b???b???bbbb???b???b???bbbb)</td></tr><tr><td>9-RECTANGLE</td><td>In: (caaaaaaaaaaaaaaaaa, caaaaaaaaaaaaaaaaa, caaaaaaaaaaaaaaaaa, caaaaaaaaaaaaaaaaa)Out: (bbbbbbbbbbbbbbbb,bbbb??bb???bbbb, ??????????????????, ??????????????????)</td></tr></table>

## 5.3 Applications to LBlock

LBlock is a lightweitht block cipher proposed by Wu and Zhang [24]. The block size is 64 bits and the key size is 80 bits. It employs a variant Feistel structure and consists of 32 rounds. One-round structure of LBlock is given in Fig. 3. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-07-10/fc103d2e-553f-422f-95d9-dea73aded7ea/f8964e7971956f4cafa8e717575f31f364b7795100d0169210c10d6c91bc14b7.jpg)



( ) -th round structure of LBlocka i



(b) The structure of F-function



Fig. 3. Round structure of LBlock


We divide one-round LBlock into 9 parts $Q _ { i } = Q _ { i , 8 } \circ \cdots \circ Q _ { i , 0 }$ . And the input of $Q _ { i , j }$ is denoted as $\left( \pmb { x } ^ { i , j } , \pmb { y } ^ { i , j } \right) = \left( \pmb { x } _ { 7 } ^ { i , j } , \dots , \pmb { x } _ { 0 } ^ { i , j } , \pmb { y } _ { 7 } ^ { i , j } , \dots , \pmb { y } _ { 0 } ^ { i , j } \right)$ . When $0 \leq j \leq$ 7, we have $Q _ { i , j } \left( x ^ { i , j } , y ^ { i , j } \right) ~ = ~ \left( x ^ { i , j } , y _ { 7 } ^ { i , j } , \ldots , y _ { P ( j ) + 1 } ^ { i , j } , Y _ { P ( j ) } ^ { i , j } , y _ { P ( j ) - 1 } ^ { i , j } , \ldots , y _ { 0 } ^ { i , j } \right)$ where $\begin{array} { r c l } { { Y _ { P ( j ) } ^ { i , j } } } & { { = } } & { { S _ { j } \left( { \bf x } _ { j } ^ { i , j } \oplus k _ { i , j } \right) \oplus { y } _ { ( P ( j ) - 2 ) \mathrm { m o d } 8 } ^ { i , j } , ~ S _ { j } } } \end{array}$ is the j-th S-box of LBlock, and $P \left( x \right)$ is the nibble difusion function. Moreover, $Q _ { i , 8 } \left( \mathbf { x } ^ { i , 8 } , \mathbf { y } ^ { i , 8 } \right) =$ $\left( \boldsymbol { y } ^ { i , 8 } , \boldsymbol { x } ^ { i , 8 } \right)$ 

Using Algorithm 2, we find a 17-round integral distinguisher of LBlock which is in accordance with the previous longest integral distinguisher [8], and a better 16-round integral distinguisher with less active bits. The detail forms of the integral distinguishers are shown in Table 6. 


Table 6. Integral distinguishers of LBlock


<table><tr><td>Cipher</td><td>Distinguisher</td></tr><tr><td>17-LBlock</td><td>In: (caaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)Out: (??????????????????????????????????,??bb?????????????????????????bb)</td></tr><tr><td>16-LBlock</td><td>In: (aaccaaaaaaaaaaaaaaaaaaaaaaaaaa,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)Out: (??????????????????????????????????,??bbbbbbbbb?b?bb?b?bbb???????)</td></tr></table>

## 6 Using BDPT to Recover the Superpoly in Cube Attack

In this section, we analyze the ANF coeficients of non-blackbox polynomial and superpoly in cube attack. Then, we show an MILP-aided method based on BDPT to recover the ANF coeficients of superpoly. 

## 6.1 Analyze the ANF Coeficients of Polynomial

Let $f \left( \pmb { x } , \pmb { v } \right)$ be a polynomial, where $\pmb { x } \in \mathbb { F } _ { 2 } ^ { n }$ and $\pmb { v } \in \mathbb { F } _ { 2 } ^ { m }$ denote the secret and public variables, respectively. In cube attack, $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ denotes a function that the public variables indexed by $I _ { v } \subset \{ 0 , 1 , \cdots , m - 1 \}$ are chosen as cube variables, the public variables indexed by $J _ { v } \subset \{ 0 , 1 , \cdot \cdot \cdot , m - 1 \} - I _ { v }$ are set to 1, and the remaining public variables $K _ { v } = \{ 0 , 1 , \cdots , m - 1 \} - I _ { v } - J _ { v }$ are set to 0. Then, the ANF of $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ can be represented as follows 

$$
f _ {I _ {v}, J _ {v}, K _ {v}} \left(\boldsymbol {x}, \boldsymbol {v}\right) = \bigoplus_ {\boldsymbol {u} _ {x} \in \mathbb {F} _ {2} ^ {n}, \boldsymbol {u} _ {v} \preceq \boldsymbol {u} _ {I}} a _ {\left(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v}\right)} ^ {f _ {I _ {v}, J _ {v}, K _ {v}}} \cdot \left(\boldsymbol {x}, \boldsymbol {v}\right) ^ {\left(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v}\right)}.
$$

where $\boldsymbol { a } _ { ( \boldsymbol { u } _ { x } , \boldsymbol { u } _ { v } ) } ^ { f _ { I _ { v } , J _ { v } , K _ { v } } }$ is the ANF coeficient of term $( \pmb { x } , \pmb { v } ) ^ { ( \pmb { u } _ { x } , \pmb { u } _ { v } ) }$ in $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 

For polynomial $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ and an index subset $I _ { x } \subset \{ 0 , 1 , \cdots , n - 1 \}$ , if fixing all the secret variables $\{ x _ { k } | k \in \{ 0 , 1 , \cdot \cdot \cdot , n - 1 \} - I _ { x } \}$ to 0, we can get a new polynomial denoted as $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 

Definition 6. (Similar Polynomial). For subsets of indices $I _ { x } ^ { \prime } \subset I _ { x }$ , the polynomial $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is called the similar polynomial of $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 

Lemma 2. If $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is the similar polynomial of $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ , then the value of ANF coeficient $\begin{array} { r l } & { \quad f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } } \\ & { \quad a _ { \left( \boldsymbol { u } _ { I _ { x } ^ { \prime } } , \boldsymbol { u } _ { I _ { v } } \right) } } \end{array}$ in $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is equal to the value of ANF coeficients $\begin{array} { r } { \boldsymbol { a } _ { \left( u _ { I _ { x } ^ { \prime } } , u _ { I _ { v } } , J _ { v } , K _ { v } \right. } ^ { \left. {  } } } \\ \right.{ \left. \left( \boldsymbol { u } _ { I _ { x } ^ { \prime } } , \boldsymbol { u } _ { I _ { v } } \right) \right. } \end{array}$ in $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 

Proof. For $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ , if all the variables of $\{ x _ { i } | i \in I _ { x } - I _ { x } ^ { \prime } \}$ are assigned 0, it becomes the function $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ . Compared with the ANF of $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ , the ANF of $f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ only misses terms that contain any variables of $\{ x _ { i } | i \in I _ { x } - I _ { x } ^ { \prime } \}$ . Moreover, $\pmb { x } ^ { u _ { I _ { x } ^ { \prime } } }$ doesn’t contain any variables of $\{ x _ { i } | i \in I _ { x } - I _ { x } ^ { \prime } \}$ , so $\begin{array} { r } { a _ { \left( u _ { I _ { x } ^ { \prime } } , u _ { I _ { v } } , J _ { v } , K _ { v } \right) } ^ { f _ { I _ { x } ^ { \prime } , I _ { v } , J _ { v } , K _ { v } } } = a _ { \left( u _ { I _ { x } ^ { \prime } } , u _ { I _ { v } } \right) } ^ { f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } } } \end{array}$ 

## 6.2 Analyze the ANF Coeficients of Superpoly

The most important part of cube attack is recovering the superpoly. Once the superpoly is recovered, attackers can compute the sum of encryptions over the cube and get one equation about secret variables. 

Let $C _ { I _ { v } , J _ { v } , K _ { v } }$ be a cube set defined as Eq. (1) in Sect. 2.5. For polynomia $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ , where $\pmb { x } \in \mathbb { F } _ { 2 } ^ { n }$ and $\pmb { v } \in \mathbb { F } _ { 2 } ^ { m }$ , it can be unique represented as 

$$
f _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}) = \boldsymbol {v} ^ {\boldsymbol {u} _ {I _ {v}}} \cdot p _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}) \oplus q _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}).\tag{3}
$$

where $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ does not contain any variable in $\{ v _ { i } | i \in I _ { v } \}$ , and each term of $q _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is not divisible by ${ \boldsymbol { v } } ^ { u _ { I _ { v } } }$ . Then, $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ is called the superpoly of $C _ { I _ { v } , J _ { v } , K _ { v } }$ in $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ 

Definition 7. Let $C _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ be the set of $( { \pmb x } , { \pmb v } )$ satisfying secret variables $\{ x _ { i } | i \in I _ { x } \}$ are taking all possible combinations of values, secret variables $\{ x _ { i } | i \in$ $\{ 0 , 1 , \ldots , n - 1 \} - I _ { x } \}$ are set to constant 0, public variables $\{ v _ { i } | i \in I _ { v } \}$ are taking all possible combinations of values, public variables $\{ v _ { j } | j \in J _ { v } \}$ are set to constant 1, and public variables $\{ v _ { k } | k \in K _ { v } \}$ are set to constant 0. 

Here, we propose a method to calculate the ANF coeficient of superpoly. 

Proposition 3. For any index subset $I _ { x } \subset \{ 0 , 1 , \dotsc , n - 1 \}$ , the ANF coeficient of term ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ in the superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ can be calculated as 

$$
a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} = \bigoplus_ {(\boldsymbol {x}, \boldsymbol {v}) \in C _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}).
$$

Proof. The ANF of $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ can be presented as 

$$
p _ {I _ {v}, J _ {v}, K _ {v}} \left(\boldsymbol {x}\right) = \bigoplus_ {\boldsymbol {u} \in \mathbb {F} _ {2} ^ {n}} a _ {\boldsymbol {u}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} \cdot \boldsymbol {x} ^ {\boldsymbol {u}}.
$$

Then, the ANF of $\pmb { v } ^ { { u } _ { I _ { v } } } \cdot p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ can be presented as 

$$
\boldsymbol {v} ^ {\boldsymbol {u} _ {I _ {v}}} \cdot p _ {I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}) = \bigoplus_ {\boldsymbol {u} \in \mathbb {F} _ {2} ^ {n}} a _ {\boldsymbol {u}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} \cdot (\boldsymbol {x}, \boldsymbol {v}) ^ {(\boldsymbol {u}, \boldsymbol {u} _ {I _ {v}})}.
$$

So, the ANF coeficient of $( \pmb { x } , \pmb { v } ) ^ { ( \pmb { u } _ { I _ { x } } , \pmb { u } _ { I _ { v } } ) } \mathrm { i n } \pmb { v } ^ { \pmb { u } _ { I _ { v } } } \cdot p _ { I _ { v } , J _ { v } , K _ { v } } ( \pmb { x } , \pmb { v } )$ is also $a _ { u _ { I _ { x } } } ^ { p _ { I _ { v } , J _ { v } , K _ { v } } }$ Because $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ can be unique represented as $\operatorname { E q . } \ ( 3 )$ and every term in $q _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ misses at least one variable from $\{ v _ { i } | i \in I _ { v } \}$ , the term $( \pmb { x } , \pmb { v } ) ^ { ( \pmb { u } _ { I _ { x } } , \pmb { u } _ { I _ { v } } ) }$ doesn’t exist in $q _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ . According to Eq. (3), we obtain that the ANF coeficient of term $( \mathbf { \bar { x } } , \mathbf { \bar { v } } ) ^ { \dot { \pmb { u } } _ { I _ { x } } , \dot { \pmb { u } } _ { I _ { v } } }$ in $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is $a _ { u _ { I _ { x } } } ^ { p _ { I _ { v } , J _ { v } , K _ { v } } }$ Namely, 

$$
a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {v}, J _ {v}, K _ {v}}}.\tag{4}
$$

From the Definition 6, we know that $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ is the similar polynomial of $f _ { I _ { v } , J _ { v } , K _ { v } }$ . And according to Lemma 2, we obtain that 

$$
a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}} = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {v}, J _ {v}, K _ {v}}} = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}}.\tag{5}
$$

Then, we have 

$$
\begin{array}{l} \bigoplus_ {(\boldsymbol {x}, \boldsymbol {v}) \in C _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}} (\boldsymbol {x}, \boldsymbol {v}) \\ = \bigoplus_ {(\boldsymbol {x}, \boldsymbol {v}) \in C _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} \bigoplus_ {\boldsymbol {u} _ {x} \preceq \boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {v} \preceq \boldsymbol {v} _ {I _ {v}}} a _ {(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v})} ^ {f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} \cdot (\boldsymbol {x}, \boldsymbol {v}) ^ {(\boldsymbol {u} _ {x}, \boldsymbol {u} _ {v})} \\ = a _ {(\boldsymbol {u} _ {I _ {x}}, \boldsymbol {u} _ {I _ {v}})} ^ {f _ {I _ {x}, I _ {v}, J _ {v}, K _ {v}}} = a _ {\boldsymbol {u} _ {I _ {x}}} ^ {p _ {I _ {v}, J _ {v}, K _ {v}}}. \end{array}
$$

## 6.3 The Algorithm to Recover Superpoly

The set $C _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ can be viewed as a cube set, according to the definition of BDPT, we know that the BDPT of $C _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } }$ is $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$ , where $\mathbb { K } = \varnothing$ , and $\mathbb { L } = \{ \left( \boldsymbol { u } _ { I _ { x } } , \boldsymbol { u } _ { v } \right) \lvert \boldsymbol { u } _ { I _ { v } } \preceq \boldsymbol { u } _ { v } \preceq \boldsymbol { u } _ { I _ { v } } \oplus \boldsymbol { u } _ { J _ { v } } \}$ . Then, we can use MILP-aided method (Algorithm 2) to research the propagation of $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n } }$ . The integral distinguisher got by BDPT recover the ANF coeficient of $x ^ { u _ { I _ { x } } }$ in superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ For example, if Algorithm 2 BDP T $( f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } , \mathbb { K } , \mathbb { L } , 0 )$ return 1, it means that 

- $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right) = 1$ . According to Proposition 3, we know that $( \pmb { x } , \pmb { v } ) { \in } C _ { I _ { \pmb { x } } , I _ { \pmb { v } } , J _ { \pmb { v } } , K _ { \pmb { v } } }$ 

the ANF coeficient of ${ \pmb x } ^ { u _ { I _ { x } } }$ in superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ equals 1. We illustrate the whole framework in Algorithm 3. 

In order to analyze the ciphers better, we divide them into two categories: public-update ciphers and secret-update ciphers. 

Definition 8. For a function $f : \mathbb { F } _ { 2 } ^ { n } \to \mathbb { F } _ { 2 } ^ { m }$ , if the ANF of f is definite, we call it public function. Let $E = Q _ { r } \circ Q _ { r - 1 } \circ \cdots \circ Q _ { 1 } \left( { \pmb x } , { \pmb v } \right)$ be an r-round cipher, where $Q _ { i }$ is the i-th round update function, x denotes the secret variables, and v denotes the public variables. If all the round update functions $Q _ { i } , i \in \{ 1 , 2 , \cdots , r \}$ are public functions, the cipher E is public-update cipher. Otherwise we call it secret-update cipher. 

Proposition 4. For a public-update cipher $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ and cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ , the superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ can be fully recovered by the propagation of $B D P T$ 

Algorithm 3. Recover the ANF coefficient of $\boldsymbol{x}^{u_{I_x}}$ in superpoly $p_{I_v, J_v, K_v}(\boldsymbol{x})$ 1 procedure RecoverCoefficient( $I_x$ , $I_v$ , $J_v$ , $K_v$ )
2    Initial $\mathbb{K} = \emptyset$ , $\mathbb{L} = \{ (\boldsymbol{u}_{I_x}, \boldsymbol{u}_v) | \boldsymbol{u}_{I_v} \preceq \boldsymbol{u}_v \preceq \boldsymbol{u}_{I_v} \oplus \boldsymbol{u}_{J_v} \}$ 3    if $BDPT(f_{I_x, I_v, J_v, K_v}, \mathbb{K}, \mathbb{L}, 0)$ return unknown
4    return unknown
5    else if $BDPT(f_{I_x, I_v, J_v, K_v}, \mathbb{K}, \mathbb{L}, 0)$ return 1
6    return 1
7    else
8    return 0
9 end procedure 

Proof. The superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right)$ is a function of secret variables x. If for arbitrary term ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ , we can determine its ANF coeficient. Then, the exact superpoly can be obtained. 

Because $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is a public-update cipher, $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ is also a public-update cipher. Then, for arbitrary term ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ , we research the propagation of BDPT $\mathcal { D } _ { \mathbb { K } , \mathbb { L } } ^ { 1 ^ { n + m } }$ , where $\mathbb { K } = \varnothing$ and $\mathbb { L } = \{ \left( \boldsymbol { u } _ { I _ { x } } , \boldsymbol { u } _ { v } \right) \lvert \boldsymbol { u } _ { I _ { v } } \preceq \boldsymbol { u } _ { v } \preceq \boldsymbol { u } _ { I _ { v } } \oplus \boldsymbol { u } _ { J _ { v } } \}$ . Let the output BDPT of $f _ { I _ { x } , I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ be $\mathcal { D } _ { \mathbb { K } ^ { \prime } , \mathbb { L } ^ { \prime } } ^ { 1 ^ { n + m } }$ . The initial $\mathbb { K } = \varnothing$ means that there is no division trail from $\mathbb { K } = \varnothing$ to $\mathbb { K } ^ { \prime }$ . From Sect. 2.3, we know that for public function, the BDPT propagation of <sup>K</sup> and <sup>L</sup> is independent. Only when the secret round key is involved, some vectors of <sup>L</sup> will afect <sup>K</sup>. That means, there is no division trail from <sup>L</sup> to $\mathbb { K } ^ { \prime }$ when all the update functions are public. The output set $\mathbb { K } ^ { \prime } = \varnothing$ and the return value of Algorithm 3 is constant (0 or 1). So the ANF coeficient of arbitrary term ${ \pmb x } ^ { { \pmb u } _ { I _ { x } } }$ can be recovered by BDPT. 

According to Sect. 2.6, for polynomial $f _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ and cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ we can use MILP method to evaluate the secret variables involved in the superpoly and the upper bounding degree of superpoly. We denote the involved secret variables indices set as I and the upper bounding degree as d. Then, in order to recover the superpoly, we only need to determine the coeficients $a _ { u } ^ { p _ { I _ { v } , J _ { v } , K _ { v } } }$ satisfying ${ \pmb u } \preceq { \pmb u } _ { I }$ and hw $( { \boldsymbol { \mathbf { u } } } ) \leq d .$ 

Analysis of Public-Update Cipher. According to Proposition 4, we can query the Algorithm 3 $\begin{array} { r } { \sum _ { i = 0 } ^ { d } \binom { | I | } { i } } \end{array}$ times to recover all the ANF coeficients of superpoly. The complexity is $c \cdot \sum _ { i = 0 } ^ { d } \left( { | I | } \atop { i } \right)$ , where c is the average computational complexity of Algorithm 3. Compared with CBDP based cube attack in Sect. 2.6, we can know that when $c < 2 ^ { | I _ { v } | }$ , our method can obtain better results. 

Analysis of Secret-Update Cipher. Due to the influence of secret keys in the intermediate rounds, new vectors may be generated from $\mathbb { L } _ { i }$ and added to $\mathbb { K } _ { i }$ . Therefore, the condition that the output BDPT set $\mathbb { K } ^ { \prime } = \varnothing$ may not hold. Namely, only a part of the ANF coeficients in superpoly $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } , \pmb { v } \right)$ can be obtained by BDPT. If there are N ANF coeficients that cannot be determined by BDPT, we have to get their ANF coeficients by the method used in the 

CBDP based cube attack. Therefore, the complexity of recovering superpoly is $\left\{ c \cdot \sum _ { i = 0 } ^ { d } { \binom { | I | } { i } } + N \cdot 2 ^ { | I _ { v } | } \right\}$ 

## 7 Application to Trivium

In order to verify the correctness and efectiveness of our method, we apply it to Trivium [5] which is a public-update cipher. 

## 7.1 Descriptions of Trivium

Trivium [5] is a bit-oriented stream cipher with 288-bit internal state denoted by $\pmb { \mathscr { s } } = ( \mathscr { s } _ { 0 } , \mathscr { s } _ { 1 } , \mathscr { . . . } , \mathscr { s } _ { 2 8 7 } )$ . To outline our technique more conveniently, we describe Trivium using the following expression. Let ${ \pmb x } = ( x _ { 0 } , x _ { 1 } , \cdot \cdot \cdot , x _ { 7 9 } )$ denote the secret variables (80-bit Key), and $\pmb { v } = ( v _ { 0 } , v _ { 1 } , \dotsb , v _ { 2 0 7 } )$ denote the public variables. For public variables, $v _ { 1 3 } , v _ { 1 4 } , \cdots$ , v are the IV variables whose values can be chosen by attackers (80-bit IV), $\{ v _ { 2 0 5 } , v _ { 2 0 6 } , v _ { 2 0 7 } \}$ are set to 1, and others are set to 0. Then, the algorithm would not output any keystream bit until the internal state is updated 1152 rounds. A complete description of Trivium is given by the following simple pseudo-code. 

$(s_{0}, s_{1}, \ldots, s_{92}) \leftarrow (x_{0}, \ldots, x_{79}, v_{0}, \ldots, v_{12})$ $(s_{93}, s_{94}, \ldots, s_{176}) \leftarrow (v_{13}, \ldots, v_{96})$ $(s_{177}, s_{178}, \ldots, s_{287}) \leftarrow (v_{97}, \ldots, v_{207})$ for i = 1 to N do

    if i > 1152 then $z_{i-1152} \leftarrow s_{65} \oplus s_{92} \oplus s_{161} \oplus s_{176} \oplus s_{242} \oplus s_{287}$ end if $t_{1} \leftarrow s_{65} \oplus s_{90} \cdot s_{91} \oplus s_{92} \oplus s_{170}$ $t_{2} \leftarrow s_{161} \oplus s_{174} \cdot s_{175} \oplus s_{176} \oplus s_{263}$ $t_{3} \leftarrow s_{242} \oplus s_{285} \cdot s_{286} \oplus s_{287} \oplus s_{68}$ $(s_{0}, s_{1}, \ldots, s_{92}) \leftarrow (t_{2}, s_{0}, \ldots, s_{91})$ $(s_{93}, s_{94}, \ldots, s_{176}) \leftarrow (t_{0}, s_{93}, \ldots, s_{175})$ $(s_{177}, s_{178}, \ldots, s_{287}) \leftarrow (t_{1}, s_{177}, \ldots, s_{286})$ end for 

## 7.2 The MILP-aided Algorithm for Trivium

Because Trivium is a public-update cipher, during the progress of recovering the ANF coeficients of superpoly, the set <sup>K</sup> is always empty. The papers [23,26] have showed the method on how to build the CBDP model of Trivium. Here, we propose Algorithm 4 to get the <sup>L</sup>’s propagation of Trivium’s round function. The input of procedure RoundPropagation in Algorithm 4 is the r-th round BDPT set $\mathbb { L } _ { r }$ , and the outputs is the (r + 1)-th round BDPT set $\mathbb { L } _ { r + 1 }$ 

```fortran
Algorithm 4. The propagation of L for the round function

1 procedure CorePropagation(L, i₀, i₁, i₂, i₃, i₄)
2 Let x = (x₀, x₁, x₂, x₃, x₄) be the variables
3 Let y be the function of x, and y = (x₀, x₁, x₂, x₃, x₀x₁ + x₂ + x₃ + x₄)
4 L' = ∅
5 for ℓ in L
6    for all u = (u₀, u₁, u₂, u₃, u₄) ∈ F₂⁵ do
7    if yᵘ contains the term x(ℓᵢ₀, ℓᵢ₁ℓᵢ₂, ℓᵢ₃, ℓᵢ₄) then
8    ℓ' = ℓ
9    ℓ′ᵢ₀ = u₀, ℓ′₁ = u₁, ℓ′ᵢ₂ = u₂, ℓ′₃ = u₃, ℓ′ᵢ₄ = u₄
10    L'←ℓ'
11    end if
12    end for
13    end for
14    return L'
15 end procedure

1 procedure RoundPropagation(Lᵣ)
2    initial L' = ∅, L'' = ∅, L''' = ∅, Lᵣ₊₁ = ∅
3    L' = CorePropagation(Lᵣ, 65, 170, 90, 91, 92)
4    L'' = CorePropagation(L', 161, 163, 174, 175, 176)
5    L''' = CorePropagation(L'', 242, 68, 285, 286, 287)
6    for all ℓ in L''' do
7    Lᵣ₊₁ = Lᵣ₊₁ ∪{ℓ ≫ 1}
8    end for
9    return Lᵣ₊₁
10 end procedure 
```

At CRYPTO 2017 [23], Todo et al. proposed a CBDP based cube attack on the 832-round Trivium. Then, at CRYPTO 2018 [26], Wang et al. improved the result and presented a CBDP based cube attack on 839-round Trivium. But both methods cannot ensure whether the cube attacks are key recovery attacks or not. After applying Algorithm 3 to the 832-round and 839-round Trivium, we have the following results. 

Result 1. For cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ , where $I _ { v } = \{ 1 3 , \ldots , 4 5 , 4 7 , \ldots , 5 8 , 6 0 , \ldots , 9 2 \}$ , no matter what the assignment to the non-cube IVs 46, 59 is, the corresponding superpoly of 839-round Trivium in the paper $[ \boldsymbol { { \mathcal { Z } } } \boldsymbol { \delta } ]$ is constant. So the cube attack based on CBDP in the paper [26] is not key recovery attack. 

Result 2. For the cube set $C _ { I _ { v } , J _ { v } , K _ { v } ; }$ , where $I _ { v } = \{ 1 3 , 1 4 , \dots , 7 7 , 7 9 , 8 1 , \dots , 9 1 \}$ the superpolies of some assignments are constant. For example, when $J _ { v } \ =$ 205, 206, 207 and $K _ { v } = \{ 0 , 1 , \ldots , 2 0 7 \} - I _ { v } - J _ { v }$ , the superpoly recovered is $p _ { I _ { v } , J _ { v } , K _ { v } } \left( \pmb { x } \right) = 0$ . And the superpolies of some assignments are non-constant. For example, when $J _ { v } = \{ 8 0 , 9 0 , 2 0 5 , 2 0 6 , 2 0 7 \}$ and $K _ { v } = \{ 0 , 1 , \ldots , 2 0 7 \} - I _ { v } - J _ { v }$ , the superpoly recovered is $p _ { I _ { v } , J _ { v } , K _ { v } } \left( { \pmb x } \right) = x _ { 5 6 } x _ { 5 7 } x _ { 5 8 } + x _ { 3 2 } x _ { 5 6 } + x _ { 5 6 } x _ { 5 9 }$ . In a word, the assignment to the non-cube IVs will afect whether the cube attack on 832-round Trivium in the paper [23] is key recovery attack or not. 

## 7.3 Theoretical Result

Result 3. Let $C _ { I _ { v } , J _ { v } , K _ { v } }$ be a cube set, where $I _ { v } = \{ 1 3 , 1 4 , \ldots , 8 9 , 9 1 \} , J _ { v } =$ 205, 206, 207 , and $K _ { v } = \{ 0 , 1 , \ldots , 2 0 4 \} - I _ { v }$ . Using the degree bounding technique in the paper ${ \it 2 6 } ] ,$ , we can get that the degree of superpoly in 841-round Trivium is not larger than 10. Then, we have $\begin{array} { r } { \sum _ { i = 0 } ^ { d } \binom { | I | } { i } \leq \sum _ { i = 0 } ^ { 1 0 } \binom { 8 0 } { i } \leq 2 ^ { 4 1 } } \end{array}$ That means we can use no more than $2 ^ { 4 1 }$ MILP-aided propagation of BDPT to recover the exact superpoly of 841-round Trivium. 

Because our computing resources are limited, the exact superpoly of 841- round Trivium cannot be recovered in practical time. On our common PC (Intel Core i5-4590 CPU @3.3 GHz, 8.00G RAM), it takes about 18 days to complete the MILP-aided propagation of BDPT 100 times. 

## 8 Conclusions

This paper is committed to solve the complexity problem of searching integral distinguishers based on BDPT. In order to make the propagation of BDPT eficient, we show the pruning techniques which can removing redundant vectors in time. Then, an algorithm is designed to estimate whether the m-th output bit is balanced or not based on BDPT. We apply the searching algorithm to some blocks, and the obtained integral distinguishers are the same or better than the previous longest integral distinguishers. It should be noted that the absence of integral distinguishers based on BDPT doesn’t imply the absence of integral distinguishers. Any improvement on the accuracy of BDPT propagation may obtain better integral distinguishers. Moreover, our searching algorithm supposes that all round keys are chosen randomly. If consider the key scheduling algorithm, we may obtain better integral distinguishers. 

Moreover, we apply BDPT to recover the superpoly in cube attack. As far as we know, this is the first application of BDPT to stream ciphers. For publicupdate ciphers, the exact ANF of superpoly can be fully recovered by exploring the propagation of BDPT. To verify the correctness and efectiveness of our method, we apply it to Trivium. For the cube attack on the 832-round Trivium [23], we obtain that only some proper non-cube IV assignments can obtain nonconstant superpolies. For the cube attack on 839-round Trivium [26], our result shows that the superpoly is always constant. Because our method can determine the ANF coeficients of superpoly in practical time, we propose a theoretical superpoly recovery of 841-round Trivium. 

For secret-update ciphers, due to the influence of intermediate round keys, not all the ANF coeficients can be obtained by $\mathrm { B D P T }$ . From this perspective, when we design stream ciphers, the secret-update ciphers are more secure. How to recover the superpoly of secret-update ciphers is our future work. 

Acknowledgement. The authors would like to thank the anonymous reviewers for their detailed comments and suggestions. This work was supported by the National Natural Science Foundation of China [Grant No. 61572516, 61802437]. 

## Appendix


Table 7. The <sup>L</sup> propagation of BDPT for the core operation of SIMON


<table><tr><td>Input <eq>\mathcal{D}_{\mathbb{K},\{\ell\}}^{1^4}</eq></td><td>Output <eq>\mathcal{D}_{\mathbb{K}&#x27;,\mathbb{L}&#x27;}^{1^4}</eq></td></tr><tr><td><eq>\ell = [0, 0, 0, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[0, 0, 0, 0]\}</eq></td></tr><tr><td><eq>\ell = [1, 0, 0, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[1, 0, 0, 0]\}</eq></td></tr><tr><td><eq>\ell = [0, 1, 0, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[0, 1, 0, 0]\}</eq></td></tr><tr><td><eq>\ell = [1, 1, 0, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[1, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1]\}</eq></td></tr><tr><td><eq>\ell = [0, 0, 1, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 1]\}</eq></td></tr><tr><td><eq>\ell = [1, 0, 1, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[1, 0, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1]\}</eq></td></tr><tr><td><eq>\ell = [0, 1, 1, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[0, 1, 1, 0], [0, 1, 0, 1], [0, 1, 1, 1]\}</eq></td></tr><tr><td><eq>\ell = [1, 1, 1, 0]</eq></td><td><eq>\mathbb{L}&#x27; = \{[1, 1, 1, 0], [0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 0, 1]\}</eq></td></tr><tr><td><eq>\ell = [\ell_0, \ell_1, \ell_2, 1]</eq></td><td><eq>\mathbb{L}&#x27; = \{[\ell_0, \ell_1, \ell_2, 1]\}</eq></td></tr></table>

## Experimental Verification

Example 1. For 591-round Trivium and cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ , where $I _ { v } = \{ 1 3 , 2 3$ , 33, 43, 53, 63, 73, 83 , $J _ { v } = \{ 1 4 , 2 9 , 3 2 , 2 0 5 , 2 0 6 , 2 0 7 \}$ and $K _ { v } = \{ 0 , 1 , \cdot \cdot \cdot , 2 0 7 \} -$ $I _ { v } - J _ { v }$ , we can get that the involved secret variables are $\{ x _ { 2 2 } , x _ { 2 3 } , x _ { 2 4 } , x _ { 6 6 } \}$ , the degree of superpoly is not larger than 2. Then, we use Algorithm 3 to recover all the ANF coeficients of the superpoly, which is in accordance with the practically recovered superpoly as follows: 

$$
p _ {I _ {v}, J _ {v}, K _ {v}} (\pmb {x}) = x _ {6 6} + x _ {2 4} + x _ {2 3} x _ {2 2} + 1.
$$

Example 2. For 591-round Trivium and cube set $C _ { I _ { v } , J _ { v } , K _ { v } }$ , where $I _ { v } = \{ 1 3 , 2 3$ , 33, 43, 53, 63, 73, 83 , $J _ { v } = \{ 2 9 , 3 2 , 8 2 , 2 0 5 , 2 0 6 , 2 0 7 \}$ , and $K _ { v } = \{ 0 , 1 , \cdot \cdot \cdot , 2 0 7 \} -$ $I _ { v } - J _ { v }$ , we can get that the involved secret variables are $\{ x _ { 2 2 } , x _ { 2 3 } , x _ { 2 4 } , x _ { 6 5 } , x _ { 6 6 } \}$ • the degree of superpoly is not larger than 3. Then, we use Algorithm 3 to recover the superpoly, which is in accordance with the practically recovered superpoly as follows: 

$$
p _ {I _ {v}, J _ {v}, K _ {v}} (\pmb {x}) = x _ {6 5} x _ {2 3} x _ {2 2} + x _ {6 5} x _ {2 4} + x _ {6 6} x _ {6 5} + x _ {6 5}.
$$

## References



1. Abdelkhalek, A., Sasaki, Y., Todo, Y., Tolba, M., Youssef, M.: MILP modeling for (large) S-boxes to optimize probability of diferential characteristics. IACR Trans. Symmetric Cryptol. 2017(4), 99–129 (2017) 





2. Beaulieu, R., Shors, D., Smith, J., Treatman–Clark, S., Weeks, B., Wingers, L.: The SIMON and SPECK families of lightweight block ciphers. IACR Cryptology ePrint Archive 2013:404 (2013). http://eprint.iacr.org/2013/404 





3. Bogdanov, A., et al.: PRESENT: an ultra-lightweight block cipher. In: Paillier, P., Verbauwhede, I. (eds.) CHES 2007. LNCS, vol. 4727, pp. 450–466. Springer, Heidelberg (2007). https://doi.org/10.1007/978-3-540-74735-2 31 





4. Boura, C., Canteaut, A.: Another view of the division property. In: Robshaw, M., Katz, J. (eds.) CRYPTO 2016. LNCS, vol. 9814, pp. 654–682. Springer, Heidelberg (2016). https://doi.org/10.1007/978-3-662-53018-4 24 





5. De Canni`ere, C., Preneel, B.: Trivium. In: Robshaw, M., Billet, O. (eds.) New Stream Cipher Designs. LNCS, vol. 4986, pp. 244–266. Springer, Heidelberg (2008). https://doi.org/10.1007/978-3-540-68351-3 18 





6. Dinur, I., Shamir, A.: Cube attacks on tweakable black box polynomials. In: Joux, A. (ed.) EUROCRYPT 2009. LNCS, vol. 5479, pp. 278–299. Springer, Heidelberg (2009). https://doi.org/10.1007/978-3-642-01001-9 16 





7. Dinur, I., Shamir, A.: Breaking grain-128 with dynamic cube attacks. In: Joux, A. (ed.) FSE 2011. LNCS, vol. 6733, pp. 167–187. Springer, Heidelberg (2011). https://doi.org/10.1007/978-3-642-21702-9 10 





8. Eskandari, Z., Kidmose, A.B., K¨olbl, S., Tiessen, T.: Finding integral distinguishers with ease. In: Cid, C., Jacobson Jr., M. (eds.) SAC 2018. Lecture Notes in Computer Science, vol. 11349, pp. 115–138. Springer, Cham (2019). https://doi. org/10.1007/978-3-030-10970-7 6 





9. Fu, X., Wang, X., Dong, X., Meier, W.: A key-recovery attack on 855-round Trivium. In: Shacham, H., Boldyreva, A. (eds.) CRYPTO 2018. LNCS, vol. 10992, pp. 160–184. Springer, Cham (2018). https://doi.org/10.1007/978-3-319-96881-0 6 10 Cwnobi.h++p 





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

