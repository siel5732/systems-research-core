# 🏮 Hypatia Moonshot AI & Zhilin Yang Foundational Academic Vault
**Generated On:** 2026-07-18 16:35:57 
**Compiled By:** Hypatia (Chief Academic & Crawler Sentinel on behalf of Logos OS)

This vault consolidates the public research, mathematical breakthroughs, and patent-adjacent publications associated with **Moonshot AI** and its founder, **Zhilin Yang**. This body of work provides the direct architectural lineage behind the **Kimi long-context** (1M+ tokens) and **sparse MoE** execution models.

---

## 1. Executive Synthesis of Moonshot's Research DNA

To understand the systems engineering behind the Kimi K3 line, we must trace Zhilin Yang’s mathematical and structural path. Long before founding Moonshot AI in Beijing, Yang authored several of the most foundational papers in the modern Transformer architecture:

1. **Transformer-XL (Segment-Level Recurrence)**:
   * **Core Innovation**: Standard Transformers are limited by a fixed-length context window. Transformer-XL introduced **segment-level recurrence** (retaining hidden states of previous segments in a cache as memory) and **relative positional encodings**.
   * **Why it matters**: This single paper is the direct genetic ancestor of all modern infinite/ultra-long context scaling. By caching previous KV segments, it allowed information to propagate backward across arbitrary distances without quadratic computational blow-up.
2. **XLNet (Generalized Autoregressive Pre-training)**:
   * **Core Innovation**: XLNet bypassed the limitations of BERT's Masked Language Modeling (MLM) by introducing **permutation-based language modeling**, enabling autoregressive models to learn bidirectional context.
   * **Why it matters**: It proved that auto-regressive pre-training could capture complex bi-directional semantic relationships without breaking the causal generation loop, laying the groundwork for highly-coherent, multi-step reasoning models.
3. **Infinite-Context Engineering (Kimi's Secret Sauce)**:
   * Moonshot's public stance is that ultra-long context is the "true gateway to general intelligence." Their research pipeline has focused on squeezing the quadratic cost of self-attention. Instead of using standard flash-attention, they utilize specialized segment caches, dynamic delta attention, and sparse key compression to support 1M–2M token contexts on standard cluster topologies.

---

## 2. Collected Academic Publications (ArXiv Query Results)

The following papers represent the direct publications and contributions of Zhilin Yang and affiliates, retrieved from live academic repositories:

### 1. Attention Residuals
* **Published Date:** 2026-03-16
* **ArXiv URL:** [http://arxiv.org/abs/2603.15031v1](http://arxiv.org/abs/2603.15031v1)
* **Authors:** Kimi Team, Guangyu Chen, Yu Zhang, Jianlin Su, Weixin Xu et al.

**Abstract/Summary:**
> Residual connections with PreNorm are standard in modern LLMs, yet they accumulate all layer outputs with fixed unit weights. This uniform aggregation causes uncontrolled hidden-state growth with depth, progressively diluting each layer's contribution. We propose Attention Residuals (AttnRes), which replaces this fixed accumulation with softmax attention over preceding layer outputs, allowing each layer to selectively aggregate earlier representations with learned, input-dependent weights. To address the memory and communication overhead of attending over all preceding layer outputs for large-scale model training, we introduce Block AttnRes, which partitions layers into blocks and attends over block-level representations, reducing the memory footprint while preserving most of the gains of full AttnRes. Combined with cache-based pipeline communication and a two-phase computation strategy, Block AttnRes becomes a practical drop-in replacement for standard residual connections with minimal overhead. Scaling law experiments confirm that the improvement is consistent across model sizes, and ablations validate the benefit of content-dependent depth-wise selection. We further integrate AttnRes into the Kimi Linear architecture (48B total / 3B activated parameters) and pre-train on 1.4T tokens, where AttnRes mitigates PreNorm dilution, yielding more uniform output magnitudes and gradient distribution across depth, and improves downstream performance across all evaluated tasks.

---

### 2. Kimi K2.5: Visual Agentic Intelligence
* **Published Date:** 2026-02-02
* **ArXiv URL:** [http://arxiv.org/abs/2602.02276v1](http://arxiv.org/abs/2602.02276v1)
* **Authors:** Kimi Team, Tongtong Bai, Yifan Bai, Yiping Bao, S. H. Cai et al.

**Abstract/Summary:**
> We introduce Kimi K2.5, an open-source multimodal agentic model designed to advance general agentic intelligence. K2.5 emphasizes the joint optimization of text and vision so that two modalities enhance each other. This includes a series of techniques such as joint text-vision pre-training, zero-vision SFT, and joint text-vision reinforcement learning. Building on this multimodal foundation, K2.5 introduces Agent Swarm, a self-directed parallel agent orchestration framework that dynamically decomposes complex tasks into heterogeneous sub-problems and executes them concurrently. Extensive evaluations show that Kimi K2.5 achieves state-of-the-art results across various domains including coding, vision, reasoning, and agentic tasks. Agent Swarm also reduces latency by up to $4.5\times$ over single-agent baselines. We release the post-trained Kimi K2.5 model checkpoint to facilitate future research and real-world applications of agentic intelligence.

---

### 3. Gaussian Fluctuations for the Stochastic Landau-Lifshitz Navier-Stokes Equation in Dimension $D\geq2$
* **Published Date:** 2025-12-04
* **ArXiv URL:** [http://arxiv.org/abs/2512.04567v1](http://arxiv.org/abs/2512.04567v1)
* **Authors:** Sotiris Kotitsas, Marco Romito, Zhilin Yang, Xiangchan Zhu

**Abstract/Summary:**
> We revisit the large-scale Gaussian fluctuations for the stochastic Landau-Lifshitz Navier-Stokes equation (LLNS) at and above criticality, using the method in \cite{CGT24}. With the classical diffusive scaling in $d\geq 3$ and weak coupling scaling in $d=2$, we obtain the convergence of the regularised LLNS to a stochastic heat equation with a non-trivially renormalized coefficient. Moreover, we obtain an asymptotic expansion of the effective coefficient when $d\geq3$, and show that the one in \cite[Conjecture 6.5]{JP24} is incorrect. The new ingredient in our proof is a case-by-case analysis to track the evolution of the vector under the action of the Leray projection, combined with the use of the anti-symmetric part of the generator and a rotational change of coordinates to derive the desired decoupled stochastic heat equation from the original coupled system.

---

### 4. Kimi Linear: An Expressive, Efficient Attention Architecture
* **Published Date:** 2025-10-30
* **ArXiv URL:** [http://arxiv.org/abs/2510.26692v2](http://arxiv.org/abs/2510.26692v2)
* **Authors:** Kimi Team, Yu Zhang, Zongyu Lin, Xingcheng Yao, Jiaxi Hu et al.

**Abstract/Summary:**
> We introduce Kimi Linear, a hybrid linear attention architecture that, for the first time, outperforms full attention under fair comparisons across various scenarios -- including short-context, long-context, and reinforcement learning (RL) scaling regimes. At its core lies Kimi Delta Attention (KDA), an expressive linear attention module that extends Gated DeltaNet with a finer-grained gating mechanism, enabling more effective use of limited finite-state RNN memory. Our bespoke chunkwise algorithm achieves high hardware efficiency through a specialized variant of the Diagonal-Plus-Low-Rank (DPLR) transition matrices, which substantially reduces computation compared to the general DPLR formulation while remaining more consistent with the classical delta rule. We pretrain a Kimi Linear model with 3B activated parameters and 48B total parameters, based on a layerwise hybrid of KDA and Multi-Head Latent Attention (MLA). Our experiments show that with an identical training recipe, Kimi Linear outperforms full MLA with a sizeable margin across all evaluated tasks, while reducing KV cache usage by up to 75% and achieving up to 6 times decoding throughput for a 1M context. These results demonstrate that Kimi Linear can be a drop-in replacement for full attention architectures with superior performance and efficiency, including tasks with longer input and output lengths. To support further research, we open-source the KDA kernel and vLLM implementations, and release the pre-trained and instruction-tuned model checkpoints.

---

### 5. Kimi-Dev: Agentless Training as Skill Prior for SWE-Agents
* **Published Date:** 2025-09-27
* **ArXiv URL:** [http://arxiv.org/abs/2509.23045v3](http://arxiv.org/abs/2509.23045v3)
* **Authors:** Zonghan Yang, Shengjie Wang, Kelin Fu, Wenyang He, Weimin Xiong et al.

**Abstract/Summary:**
> Large Language Models (LLMs) are increasingly applied to software engineering (SWE), with SWE-bench as a key benchmark. Solutions are split into SWE-Agent frameworks with multi-turn interactions and workflow-based Agentless methods with single-turn verifiable steps. We argue these paradigms are not mutually exclusive: reasoning-intensive Agentless training induces skill priors, including localization, code edit, and self-reflection that enable efficient and effective SWE-Agent adaptation. In this work, we first curate the Agentless training recipe and present Kimi-Dev, an open-source SWE LLM achieving 60.4\% on SWE-bench Verified, the best among workflow approaches. With additional SFT adaptation on 5k publicly-available trajectories, Kimi-Dev powers SWE-Agents to 48.6\% pass@1, on par with that of Claude 3.5 Sonnet (241022 version). These results show that structured skill priors from Agentless training can bridge workflow and agentic frameworks for transferable coding agents.

---

### 6. OpenCUA: Open Foundations for Computer-Use Agents
* **Published Date:** 2025-08-12
* **ArXiv URL:** [http://arxiv.org/abs/2508.09123v3](http://arxiv.org/abs/2508.09123v3)
* **Authors:** Xinyuan Wang, Bowen Wang, Dunjie Lu, Junlin Yang, Tianbao Xie et al.

**Abstract/Summary:**
> Vision-language models have demonstrated impressive capabilities as computer-use agents (CUAs) capable of automating diverse computer tasks. As their commercial potential grows, critical details of the most capable CUA systems remain closed. As these agents will increasingly mediate digital interactions and execute consequential decisions on our behalf, the research community needs access to open CUA frameworks to study their capabilities, limitations, and risks. To bridge this gap, we propose OpenCUA, a comprehensive open-source framework for scaling CUA data and foundation models. Our framework consists of: (1) an annotation infrastructure that seamlessly captures human computer-use demonstrations; (2) AgentNet, the first large-scale computer-use task dataset spanning 3 operating systems and 200+ applications and websites; (3) a scalable pipeline that transforms demonstrations into state-action pairs with reflective long Chain-of-Thought reasoning that sustain robust performance gains as data scales. Our end-to-end agent models demonstrate strong performance across CUA benchmarks. In particular, OpenCUA-72B achieves an average success rate of 45.0% on OSWorld-Verified, establishing a new state-of-the-art (SOTA) among open-source models. Further analysis confirms that our approach generalizes well across domains and benefits significantly from increased test-time computation. We release our annotation tool, datasets, code, and models to build open foundations for further CUA research.

---

### 7. Kimi K2: Open Agentic Intelligence
* **Published Date:** 2025-07-28
* **ArXiv URL:** [http://arxiv.org/abs/2507.20534v2](http://arxiv.org/abs/2507.20534v2)
* **Authors:** Kimi Team, Yifan Bai, Yiping Bao, Y. Charles, Cheng Chen et al.

**Abstract/Summary:**
> We introduce Kimi K2, a Mixture-of-Experts (MoE) large language model with 32 billion activated parameters and 1 trillion total parameters. We propose the MuonClip optimizer, which improves upon Muon with a novel QK-clip technique to address training instability while enjoying the advanced token efficiency of Muon. Based on MuonClip, K2 was pre-trained on 15.5 trillion tokens with zero loss spike. During post-training, K2 undergoes a multi-stage post-training process, highlighted by a large-scale agentic data synthesis pipeline and a joint reinforcement learning (RL) stage, where the model improves its capabilities through interactions with real and synthetic environments. Kimi K2 achieves state-of-the-art performance among open-source non-thinking models, with strengths in agentic capabilities. Notably, K2 obtains 66.1 on Tau2-Bench, 76.5 on ACEBench (En), 65.8 on SWE-Bench Verified, and 47.3 on SWE-Bench Multilingual -- surpassing most open and closed-sourced baselines in non-thinking settings. It also exhibits strong capabilities in coding, mathematics, and reasoning tasks, with a score of 53.7 on LiveCodeBench v6, 49.5 on AIME 2025, 75.1 on GPQA-Diamond, and 27.1 on OJBench, all without extended thinking. These results position Kimi K2 as one of the most capable open-source large language models to date, particularly in software engineering and agentic tasks. We release our base and post-trained model checkpoints to facilitate future research and applications of agentic intelligence.

---

### 8. OJBench: A Competition Level Code Benchmark For Large Language Models
* **Published Date:** 2025-06-19
* **ArXiv URL:** [http://arxiv.org/abs/2506.16395v2](http://arxiv.org/abs/2506.16395v2)
* **Authors:** Zhexu Wang, Yiping Liu, Yejie Wang, Wenyang He, Bofei Gao et al.

**Abstract/Summary:**
> Recent advancements in large language models (LLMs) have demonstrated significant progress in math and code reasoning capabilities. However, existing code benchmark are limited in their ability to evaluate the full spectrum of these capabilities, particularly at the competitive level. To bridge this gap, we introduce OJBench, a novel and challenging benchmark designed to assess the competitive-level code reasoning abilities of LLMs. OJBench comprises 232 programming competition problems from NOI and ICPC, providing a more rigorous test of models' reasoning skills. We conducted a comprehensive evaluation using OJBench on 37 models, including both closed-source and open-source models, reasoning-oriented and non-reasoning-oriented models. Our results indicate that even state-of-the-art reasoning-oriented models, such as o4-mini and Gemini-2.5-pro-exp, struggle with highly challenging competition-level problems. This highlights the significant challenges that models face in competitive-level code reasoning.

---

### 9. Joint$λ$: Orchestrating Serverless Workflows on Jointcloud FaaS Systems
* **Published Date:** 2025-05-28
* **ArXiv URL:** [http://arxiv.org/abs/2505.21899v3](http://arxiv.org/abs/2505.21899v3)
* **Authors:** Rui Li, Jianfei Liu, Zhilin Yang, Peichang Shi, Guodong Yi et al.

**Abstract/Summary:**
> Existing serverless workflow orchestration systems are predominantly designed for a single-cloud FaaS system, leading to vendor lock-in. This restricts performance optimization, cost reduction, and availability of applications. However, orchestrating serverless workflows on Jointcloud FaaS systems faces two main challenges: (1) additional overhead caused by centralized cross-cloud orchestration; and (2) a lack of reliable failover and fault-tolerant mechanisms for cross-cloud serverless workflows. To address these challenges, we propose Joint$λ$, a distributed runtime system designed to orchestrate serverless workflows on multiple FaaS systems without relying on a centralized orchestrator. Joint$λ$ introduces a compatibility layer, Backend-Shim, leveraging inter-cloud heterogeneity to optimize makespan and reduce costs with on-demand billing. By using function-side orchestration instead of centralized nodes, it enables independent function invocations and data transfers, reducing cross-cloud communication overhead. For high availability, it ensures exactly-once execution via datastores and failover mechanisms for serverless workflows on Jointcloud FaaS systems. We validate Joint$λ$ on two heterogeneous FaaS systems, AWS and Aliyun, with four workflows. Compared to the most advanced commercial orchestration services for single-cloud serverless workflows, Joint$λ$ reduces makespan by up to 3.3$\times$ while saving up to 65% in cost. Joint$λ$ is also up to 4.0$\times$ faster than state-of-the-art orchestrators for cross-cloud serverless workflows, while achieving competitive cost in representative scenarios and providing strong execution guarantees.

---

### 10. Learning to Plan Before Answering: Self-Teaching LLMs to Learn Abstract Plans for Problem Solving
* **Published Date:** 2025-04-28
* **ArXiv URL:** [http://arxiv.org/abs/2505.00031v1](http://arxiv.org/abs/2505.00031v1)
* **Authors:** Jin Zhang, Flood Sung, Zhilin Yang, Yang Gao, Chongjie Zhang

**Abstract/Summary:**
> In the field of large language model (LLM) post-training, the effectiveness of utilizing synthetic data generated by the LLM itself has been well-presented. However, a key question remains unaddressed: what essential information should such self-generated data encapsulate? Existing approaches only produce step-by-step problem solutions, and fail to capture the abstract meta-knowledge necessary for generalization across similar problems. Drawing insights from cognitive science, where humans employ high-level abstraction to simplify complex problems before delving into specifics, we introduce a novel self-training algorithm: LEarning to Plan before Answering (LEPA). LEPA trains the LLM to formulate anticipatory plans, which serve as abstract meta-knowledge for problem-solving, before engaging with the intricacies of problems. This approach not only outlines the solution generation path but also shields the LLM from the distraction of irrelevant details. During data generation, LEPA first crafts an anticipatory plan based on the problem, and then generates a solution that aligns with both the plan and the problem. LEPA refines the plan through self-reflection, aiming to acquire plans that are instrumental in yielding correct solutions. During model optimization, the LLM is trained to predict both the refined plans and the corresponding solutions. By efficiently extracting and utilizing the anticipatory plans, LEPA demonstrates remarkable superiority over conventional algorithms on various challenging natural language reasoning benchmarks.

---

### 11. Kimi-Audio Technical Report
* **Published Date:** 2025-04-25
* **ArXiv URL:** [http://arxiv.org/abs/2504.18425v1](http://arxiv.org/abs/2504.18425v1)
* **Authors:** KimiTeam, Ding Ding, Zeqian Ju, Yichong Leng, Songxiang Liu et al.

**Abstract/Summary:**
> We present Kimi-Audio, an open-source audio foundation model that excels in audio understanding, generation, and conversation. We detail the practices in building Kimi-Audio, including model architecture, data curation, training recipe, inference deployment, and evaluation. Specifically, we leverage a 12.5Hz audio tokenizer, design a novel LLM-based architecture with continuous features as input and discrete tokens as output, and develop a chunk-wise streaming detokenizer based on flow matching. We curate a pre-training dataset that consists of more than 13 million hours of audio data covering a wide range of modalities including speech, sound, and music, and build a pipeline to construct high-quality and diverse post-training data. Initialized from a pre-trained LLM, Kimi-Audio is continual pre-trained on both audio and text data with several carefully designed tasks, and then fine-tuned to support a diverse of audio-related tasks. Extensive evaluation shows that Kimi-Audio achieves state-of-the-art performance on a range of audio benchmarks including speech recognition, audio understanding, audio question answering, and speech conversation. We release the codes, model checkpoints, as well as the evaluation toolkits in https://github.com/MoonshotAI/Kimi-Audio.

---

### 12. Kimina-Prover Preview: Towards Large Formal Reasoning Models with Reinforcement Learning
* **Published Date:** 2025-04-15
* **ArXiv URL:** [http://arxiv.org/abs/2504.11354v1](http://arxiv.org/abs/2504.11354v1)
* **Authors:** Haiming Wang, Mert Unsal, Xiaohan Lin, Mantas Baksys, Junqi Liu et al.

**Abstract/Summary:**
> We introduce Kimina-Prover Preview, a large language model that pioneers a novel reasoning-driven exploration paradigm for formal theorem proving, as showcased in this preview release. Trained with a large-scale reinforcement learning pipeline from Qwen2.5-72B, Kimina-Prover demonstrates strong performance in Lean 4 proof generation by employing a structured reasoning pattern we term \textit{formal reasoning pattern}. This approach allows the model to emulate human problem-solving strategies in Lean, iteratively generating and refining proof steps. Kimina-Prover sets a new state-of-the-art on the miniF2F benchmark, reaching 80.7% with pass@8192. Beyond improved benchmark performance, our work yields several key insights: (1) Kimina-Prover exhibits high sample efficiency, delivering strong results even with minimal sampling (pass@1) and scaling effectively with computational budget, stemming from its unique reasoning pattern and RL training; (2) we demonstrate clear performance scaling with model size, a trend previously unobserved for neural theorem provers in formal mathematics; (3) the learned reasoning style, distinct from traditional search algorithms, shows potential to bridge the gap between formal verification and informal mathematical intuition. We open source distilled versions with 1.5B and 7B parameters of Kimina-Prover

---

### 13. Kimi-VL Technical Report
* **Published Date:** 2025-04-10
* **ArXiv URL:** [http://arxiv.org/abs/2504.07491v3](http://arxiv.org/abs/2504.07491v3)
* **Authors:** Kimi Team, Angang Du, Bohong Yin, Bowei Xing, Bowen Qu et al.

**Abstract/Summary:**
> We present Kimi-VL, an efficient open-source Mixture-of-Experts (MoE) vision-language model (VLM) that offers advanced multimodal reasoning, long-context understanding, and strong agent capabilities - all while activating only 2.8B parameters in its language decoder (Kimi-VL-A3B). Kimi-VL demonstrates strong performance across challenging domains: as a general-purpose VLM, Kimi-VL excels in multi-turn agent tasks (e.g., OSWorld), matching flagship models. Furthermore, it exhibits remarkable capabilities across diverse challenging vision language tasks, including college-level image and video comprehension, OCR, mathematical reasoning, and multi-image understanding. In comparative evaluations, it effectively competes with cutting-edge efficient VLMs such as GPT-4o-mini, Qwen2.5-VL-7B, and Gemma-3-12B-IT, while surpassing GPT-4o in several key domains. Kimi-VL also advances in processing long contexts and perceiving clearly. With a 128K extended context window, Kimi-VL can process diverse long inputs, achieving impressive scores of 64.5 on LongVideoBench and 35.1 on MMLongBench-Doc. Its native-resolution vision encoder, MoonViT, further allows it to see and understand ultra-high-resolution visual inputs, achieving 83.2 on InfoVQA and 34.5 on ScreenSpot-Pro, while maintaining lower computational cost for common tasks. Building upon Kimi-VL, we introduce an advanced long-thinking variant: Kimi-VL-Thinking-2506. Developed through long chain-of-thought (CoT) supervised fine-tuning (SFT) and reinforcement learning (RL), the latest model exhibits strong long-horizon reasoning capabilities (64.0 on MMMU, 46.3 on MMMU-Pro, 56.9 on MathVision, 80.1 on MathVista, 65.2 on VideoMMMU) while obtaining robust general abilities. Code and models are publicly accessible at https://github.com/MoonshotAI/Kimi-VL.

---

### 14. Muon is Scalable for LLM Training
* **Published Date:** 2025-02-24
* **ArXiv URL:** [http://arxiv.org/abs/2502.16982v1](http://arxiv.org/abs/2502.16982v1)
* **Authors:** Jingyuan Liu, Jianlin Su, Xingcheng Yao, Zhejun Jiang, Guokun Lai et al.

**Abstract/Summary:**
> Recently, the Muon optimizer based on matrix orthogonalization has demonstrated strong results in training small-scale language models, but the scalability to larger models has not been proven. We identify two crucial techniques for scaling up Muon: (1) adding weight decay and (2) carefully adjusting the per-parameter update scale. These techniques allow Muon to work out-of-the-box on large-scale training without the need of hyper-parameter tuning. Scaling law experiments indicate that Muon achieves $\sim\!2\times$ computational efficiency compared to AdamW with compute optimal training. Based on these improvements, we introduce Moonlight, a 3B/16B-parameter Mixture-of-Expert (MoE) model trained with 5.7T tokens using Muon. Our model improves the current Pareto frontier, achieving better performance with much fewer training FLOPs compared to prior models. We open-source our distributed Muon implementation that is memory optimal and communication efficient. We also release the pretrained, instruction-tuned, and intermediate checkpoints to support future research.

---

### 15. MoBA: Mixture of Block Attention for Long-Context LLMs
* **Published Date:** 2025-02-18
* **ArXiv URL:** [http://arxiv.org/abs/2502.13189v1](http://arxiv.org/abs/2502.13189v1)
* **Authors:** Enzhe Lu, Zhejun Jiang, Jingyuan Liu, Yulun Du, Tao Jiang et al.

**Abstract/Summary:**
> Scaling the effective context length is essential for advancing large language models (LLMs) toward artificial general intelligence (AGI). However, the quadratic increase in computational complexity inherent in traditional attention mechanisms presents a prohibitive overhead. Existing approaches either impose strongly biased structures, such as sink or window attention which are task-specific, or radically modify the attention mechanism into linear approximations, whose performance in complex reasoning tasks remains inadequately explored. In this work, we propose a solution that adheres to the ``less structure'' principle, allowing the model to determine where to attend autonomously, rather than introducing predefined biases. We introduce Mixture of Block Attention (MoBA), an innovative approach that applies the principles of Mixture of Experts (MoE) to the attention mechanism. This novel architecture demonstrates superior performance on long-context tasks while offering a key advantage: the ability to seamlessly transition between full and sparse attention, enhancing efficiency without the risk of compromising performance. MoBA has already been deployed to support Kimi's long-context requests and demonstrates significant advancements in efficient attention computation for LLMs. Our code is available at https://github.com/MoonshotAI/MoBA.

---

### 16. Kimi k1.5: Scaling Reinforcement Learning with LLMs
* **Published Date:** 2025-01-22
* **ArXiv URL:** [http://arxiv.org/abs/2501.12599v4](http://arxiv.org/abs/2501.12599v4)
* **Authors:** Kimi Team, Angang Du, Bofei Gao, Bowei Xing, Changjiu Jiang et al.

**Abstract/Summary:**
> Language model pretraining with next token prediction has proved effective for scaling compute but is limited to the amount of available training data. Scaling reinforcement learning (RL) unlocks a new axis for the continued improvement of artificial intelligence, with the promise that large language models (LLMs) can scale their training data by learning to explore with rewards. However, prior published work has not produced competitive results. In light of this, we report on the training practice of Kimi k1.5, our latest multi-modal LLM trained with RL, including its RL training techniques, multi-modal data recipes, and infrastructure optimization. Long context scaling and improved policy optimization methods are key ingredients of our approach, which establishes a simplistic, effective RL framework without relying on more complex techniques such as Monte Carlo tree search, value functions, and process reward models. Notably, our system achieves state-of-the-art reasoning performance across multiple benchmarks and modalities -- e.g., 77.5 on AIME, 96.2 on MATH 500, 94-th percentile on Codeforces, 74.9 on MathVista -- matching OpenAI's o1. Moreover, we present effective long2short methods that use long-CoT techniques to improve short-CoT models, yielding state-of-the-art short-CoT reasoning results -- e.g., 60.8 on AIME, 94.6 on MATH500, 47.3 on LiveCodeBench -- outperforming existing short-CoT models such as GPT-4o and Claude Sonnet 3.5 by a large margin (up to +550%).

---

### 17. Local Avalanche Photodetectors Driven by Lightning-rod Effect and Surface Plasmon Excitations
* **Published Date:** 2024-12-02
* **ArXiv URL:** [http://arxiv.org/abs/2412.01691v1](http://arxiv.org/abs/2412.01691v1)
* **Authors:** Zhao Fu, Meng Yuan, Jiafa Cai, Rongdun Hong, Xiaping Chen et al.

**Abstract/Summary:**
> Sensitive avalanche photodetectors (APDs) that operate within the ultraviolet spectrum are critically required for applications in detecting fire and deep-space exploration. However, the development of such devices faces significant challenges, including high avalanche breakdown voltage, the necessity for complex quenching circuits, and thermal runaway associated with Geiger-mode avalanche operation. To mitigate these issues, we report on a 4H-SiC APD design utilizing micro-holes (MHs) structures and Al nano-triangles (NTs) to enhance surface electric field driven by strong localized surface plasmon excitations and lightning-rod effect. The device demonstrates a record low avalanche breakdown voltage of approximately 14.5 V, a high detectivity of 7E13 Jones, a nanosecond-level response time, and repeated stable detections without the requirement of a quenching circuit. Collectively, when compared with the conventional wide-bandgap-based APDs, this device achieves a reduction in avalanche breakdown voltage by an order of magnitude and exhibits a substantial increase in detectivity. Consequently, the proposed APD configuration presents a promising candidate for ultraviolet detection and integrated optoelectronic circuits.

---

### 18. Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
* **Published Date:** 2024-06-24
* **ArXiv URL:** [http://arxiv.org/abs/2407.00079v4](http://arxiv.org/abs/2407.00079v4)
* **Authors:** Ruoyu Qin, Zheming Li, Weiran He, Mingxing Zhang, Yongwei Wu et al.

**Abstract/Summary:**
> Mooncake is the serving platform for Kimi, a leading LLM service provided by Moonshot AI. It features a KVCache-centric disaggregated architecture that separates the prefill and decoding clusters. It also leverages the underutilized CPU, DRAM, and SSD resources of the GPU cluster to implement a disaggregated cache of KVCache. The core of Mooncake is its KVCache-centric scheduler, which balances maximizing overall effective throughput while meeting latency-related Service Level Objectives (SLOs). Unlike traditional studies that assume all requests will be processed, Mooncake faces challenges due to highly overloaded scenarios. To mitigate these, we developed a prediction-based early rejection policy. Experiments show that Mooncake excels in long-context scenarios. Compared to the baseline method, Mooncake can achieve up to a 525% increase in throughput in certain simulated scenarios while adhering to SLOs. Under real workloads, Mooncake's innovative architecture enables Kimi to handle 75% more requests.

---

### 19. Weak coupling limit of a Brownian particle in the curl of the 2D GFF
* **Published Date:** 2024-05-09
* **ArXiv URL:** [http://arxiv.org/abs/2405.05778v1](http://arxiv.org/abs/2405.05778v1)
* **Authors:** Huanyu Yang, Zhilin Yang

**Abstract/Summary:**
> In this article, we study the weak coupling limit of the following equation in $\mathbb{R}^2$: $$dX_t^\varepsilon=\frac{\hatλ}{\sqrt{\log\frac1\varepsilon}}ω^\varepsilon(X_t^\varepsilon)dt+νdB_t,\quad X_0^\varepsilon=0. $$ Here $ω^\varepsilon=\nabla^{\perp}ρ_\varepsilon*ξ$ with $ξ$ representing the $2d$ Gaussian Free Field (GFF) and $ρ_\varepsilon$ denoting an appropriate identity. $B_t$ denotes a two-dimensional standard Brownian motion, and $\hatλ,ν>0$ are two given constants. We use the approach from \cite{Cannizzaro.2023} to show that the second moment of $X_t^\varepsilon$ under the annealed law converges to $(c(ν)^2+2ν^2)t$ with a precisely determined constant $c(ν)>0$, which implies a non-trivial limit of the drift terms as $\varepsilon$ vanishes. We also prove that in this weak coupling regime, the sequence of solutions converges in distribution to $\left(\sqrt{\frac{c(ν)^2}{2}+ν^2}\right)\widetilde{B}_t$ as $\varepsilon$ vanishes, where $\widetilde{B}_t$ is a two-dimensional standard Brownian motion.

---

### 20. CodeGeeX: A Pre-Trained Model for Code Generation with Multilingual Benchmarking on HumanEval-X
* **Published Date:** 2023-03-30
* **ArXiv URL:** [http://arxiv.org/abs/2303.17568v2](http://arxiv.org/abs/2303.17568v2)
* **Authors:** Qinkai Zheng, Xiao Xia, Xu Zou, Yuxiao Dong, Shan Wang et al.

**Abstract/Summary:**
> Large pre-trained code generation models, such as OpenAI Codex, can generate syntax- and function-correct code, making the coding of programmers more productive and our pursuit of artificial general intelligence closer. In this paper, we introduce CodeGeeX, a multilingual model with 13 billion parameters for code generation. CodeGeeX is pre-trained on 850 billion tokens of 23 programming languages as of June 2022. Our extensive experiments suggest that CodeGeeX outperforms multilingual code models of similar scale for both the tasks of code generation and translation on HumanEval-X. Building upon HumanEval (Python only), we develop the HumanEval-X benchmark for evaluating multilingual models by hand-writing the solutions in C++, Java, JavaScript, and Go. In addition, we build CodeGeeX-based extensions on Visual Studio Code, JetBrains, and Cloud Studio, generating 4.7 billion tokens for tens of thousands of active users per week. Our user study demonstrates that CodeGeeX can help to increase coding efficiency for 83.4% of its users. Finally, CodeGeeX is publicly accessible and in Sep. 2022, we open-sourced its code, model weights (the version of 850B tokens), API, extensions, and HumanEval-X at https://github.com/THUDM/CodeGeeX.

---

### 21. Learning to Detect Noisy Labels Using Model-Based Features
* **Published Date:** 2022-12-28
* **ArXiv URL:** [http://arxiv.org/abs/2212.13767v1](http://arxiv.org/abs/2212.13767v1)
* **Authors:** Zhihao Wang, Zongyu Lin, Peiqi Liu, Guidong ZHeng, Junjie Wen et al.

**Abstract/Summary:**
> Label noise is ubiquitous in various machine learning scenarios such as self-labeling with model predictions and erroneous data annotation. Many existing approaches are based on heuristics such as sample losses, which might not be flexible enough to achieve optimal solutions. Meta learning based methods address this issue by learning a data selection function, but can be hard to optimize. In light of these pros and cons, we propose Selection-Enhanced Noisy label Training (SENT) that does not rely on meta learning while having the flexibility of being data-driven. SENT transfers the noise distribution to a clean set and trains a model to distinguish noisy labels from clean ones using model-based features. Empirically, on a wide range of tasks including text classification and speech recognition, SENT improves performance over strong baselines under the settings of self-training and label corruption.

---

### 22. A Universal Discriminator for Zero-Shot Generalization
* **Published Date:** 2022-11-15
* **ArXiv URL:** [http://arxiv.org/abs/2211.08099v2](http://arxiv.org/abs/2211.08099v2)
* **Authors:** Haike Xu, Zongyu Lin, Jing Zhou, Yanan Zheng, Zhilin Yang

**Abstract/Summary:**
> Generative modeling has been the dominant approach for large-scale pretraining and zero-shot generalization. In this work, we challenge this convention by showing that discriminative approaches perform substantially better than generative ones on a large number of NLP tasks. Technically, we train a single discriminator to predict whether a text sample comes from the true data distribution, similar to GANs. Since many NLP tasks can be formulated as selecting from a few options, we use this discriminator to predict the concatenation of input and which option has the highest probability of coming from the true data distribution. This simple formulation achieves state-of-the-art zero-shot results on the T0 benchmark, outperforming T0 by 16.0\%, 7.8\%, and 11.5\% respectively on different scales. In the finetuning setting, our approach also achieves new state-of-the-art results on a wide range of NLP tasks, with only 1/4 parameters of previous methods. Meanwhile, our approach requires minimal prompting efforts, which largely improves robustness and is essential for real-world applications. Furthermore, we also jointly train a generalized UD in combination with generative tasks, which maintains its advantage on discriminative tasks and simultaneously works on generative tasks.

---

### 23. Zero-Label Prompt Selection
* **Published Date:** 2022-11-09
* **ArXiv URL:** [http://arxiv.org/abs/2211.04668v1](http://arxiv.org/abs/2211.04668v1)
* **Authors:** Chonghua Liao, Yanan Zheng, Zhilin Yang

**Abstract/Summary:**
> Natural language prompts have been shown to facilitate cross-task generalization for large language models. However, with no or limited labeled examples, the cross-task performance is highly sensitive to the choice of prompts, while selecting a high-performing prompt is challenging given the scarcity of labels. To address the issue, we propose a Zero-Label Prompt Selection (ZPS) method that selects prompts without any labeled data or gradient update. Specifically, given the candidate human-written prompts for a task, ZPS labels a set of unlabeled data with a prompt ensemble and uses the pseudo-labels for prompt selection. Experiments show that ZPS improves over prior methods by a sizeable margin in zero-label performance. We also extend ZPS to a few-shot setting and show its advantages over strong baselines such as prompt tuning and model tuning.

---

### 24. Prompt-Based Metric Learning for Few-Shot NER
* **Published Date:** 2022-11-08
* **ArXiv URL:** [http://arxiv.org/abs/2211.04337v1](http://arxiv.org/abs/2211.04337v1)
* **Authors:** Yanru Chen, Yanan Zheng, Zhilin Yang

**Abstract/Summary:**
> Few-shot named entity recognition (NER) targets generalizing to unseen labels and/or domains with few labeled examples. Existing metric learning methods compute token-level similarities between query and support sets, but are not able to fully incorporate label semantics into modeling. To address this issue, we propose a simple method to largely improve metric learning for NER: 1) multiple prompt schemas are designed to enhance label semantics; 2) we propose a novel architecture to effectively combine multiple prompt-based representations. Empirically, our method achieves new state-of-the-art (SOTA) results under 16 of the 18 considered settings, substantially outperforming the previous SOTA by an average of 8.84% and a maximum of 34.51% in relative gains of micro F1. Our code is available at https://github.com/AChen-qaq/ProML.

---

### 25. GPS: Genetic Prompt Search for Efficient Few-shot Learning
* **Published Date:** 2022-10-31
* **ArXiv URL:** [http://arxiv.org/abs/2210.17041v1](http://arxiv.org/abs/2210.17041v1)
* **Authors:** Hanwei Xu, Yujun Chen, Yulun Du, Nan Shao, Yanggang Wang et al.

**Abstract/Summary:**
> Prompt-based techniques have demostrated great potential for improving the few-shot generalization of pretrained language models. However, their performance heavily relies on the manual design of prompts and thus requires a lot of human efforts. In this paper, we introduce Genetic Prompt Search (GPS) to improve few-shot learning with prompts, which utilizes a genetic algorithm to automatically search for high-performing prompts. GPS is gradient-free and requires no update of model parameters but only a small validation set. Experiments on diverse datasets proved the effectiveness of GPS, which outperforms manual prompts by a large margin of 2.6 points. Our method is also better than other parameter-efficient tuning methods such as prompt tuning.

---

### 26. ZeroPrompt: Scaling Prompt-Based Pretraining to 1,000 Tasks Improves Zero-Shot Generalization
* **Published Date:** 2022-01-18
* **ArXiv URL:** [http://arxiv.org/abs/2201.06910v2](http://arxiv.org/abs/2201.06910v2)
* **Authors:** Hanwei Xu, Yujun Chen, Yulun Du, Nan Shao, Yanggang Wang et al.

**Abstract/Summary:**
> We propose a multitask pretraining approach ZeroPrompt for zero-shot generalization, focusing on task scaling and zero-shot prompting. While previous models are trained on only a few dozen tasks, we scale to 1,000 tasks for the first time using real-world data. This leads to a crucial discovery that task scaling can be an efficient alternative to model scaling; i.e., the model size has little impact on performance with an extremely large number of tasks. Our results show that task scaling can substantially improve training efficiency by 30 times in FLOPs. Moreover, we present a prompting method that incorporates a genetic algorithm to automatically search for the best prompt for unseen tasks, along with a few other improvements. Empirically, ZeroPrompt substantially improves both the efficiency and the performance of zero-shot learning across a variety of academic and production datasets.

---

### 27. Tailoring topological transition of anisotropic polaritons by interface engineering in biaxial crystals
* **Published Date:** 2022-01-05
* **ArXiv URL:** [http://arxiv.org/abs/2201.01412v1](http://arxiv.org/abs/2201.01412v1)
* **Authors:** Yali Zeng, Qingdong Ou, Lu Liu, Chunqi Zheng, Ziyu Wang et al.

**Abstract/Summary:**
> Polaritons in polar biaxial crystals with extreme anisotropy offer a promising route to manipulate nanoscale light-matter interactions. The dynamical modulation of their dispersion is great significance for future integrated nano-optics but remains challenging. Here, we report a momentum-directed strategy, a coupling between the modes with extra momentum supported by the interface and in-plane hyperbolic polaritons, to tailor topological transitions of anisotropic polaritons in biaxial crystals. We experimentally demonstrate such tailored polaritons at the interface of heterostructures between graphene and α-phase molybdenum trioxide (α-MoO3). The interlayer coupling can be electrically modulated by changing the Fermi level in graphene, enabling a dynamic topological transition. More interestingly, we found that the topological transition occurs at a constant Fermi level when tuning the thickness of α-MoO3. The momentum-directed strategy implemented by interface engineering offers new insights for optical topological transitions, which may shed new light for programmable polaritonics, energy transfer and neuromorphic photonics.

---

### 28. NLP From Scratch Without Large-Scale Pretraining: A Simple and Efficient Framework
* **Published Date:** 2021-11-07
* **ArXiv URL:** [http://arxiv.org/abs/2111.04130v2](http://arxiv.org/abs/2111.04130v2)
* **Authors:** Xingcheng Yao, Yanan Zheng, Xiaocong Yang, Zhilin Yang

**Abstract/Summary:**
> Pretrained language models have become the standard approach for many NLP tasks due to strong performance, but they are very expensive to train. We propose a simple and efficient learning framework, TLM, that does not rely on large-scale pretraining. Given some labeled task data and a large general corpus, TLM uses task data as queries to retrieve a tiny subset of the general corpus and jointly optimizes the task objective and the language modeling objective from scratch. On eight classification datasets in four domains, TLM achieves results better than or similar to pretrained language models (e.g., RoBERTa-Large) while reducing the training FLOPs by two orders of magnitude. With high accuracy and efficiency, we hope TLM will contribute to democratizing NLP and expediting its development.

---

### 29. P-Tuning v2: Prompt Tuning Can Be Comparable to Fine-tuning Universally Across Scales and Tasks
* **Published Date:** 2021-10-14
* **ArXiv URL:** [http://arxiv.org/abs/2110.07602v3](http://arxiv.org/abs/2110.07602v3)
* **Authors:** Xiao Liu, Kaixuan Ji, Yicheng Fu, Weng Lam Tam, Zhengxiao Du et al.

**Abstract/Summary:**
> Prompt tuning, which only tunes continuous prompts with a frozen language model, substantially reduces per-task storage and memory usage at training. However, in the context of NLU, prior work reveals that prompt tuning does not perform well for normal-sized pretrained models. We also find that existing methods of prompt tuning cannot handle hard sequence labeling tasks, indicating a lack of universality. We present a novel empirical finding that properly optimized prompt tuning can be universally effective across a wide range of model scales and NLU tasks. It matches the performance of finetuning while having only 0.1%-3% tuned parameters. Our method P-Tuning v2 is an implementation of Deep Prompt Tuning \cite{li2021prefix,qin2021learning} optimized and adapted for NLU. Given the universality and simplicity of P-Tuning v2, we believe it can serve as an alternative to finetuning and a strong baseline for future research.Our code and data are released at https://github.com/THUDM/P-tuning-v2.

---

### 30. FewNLU: Benchmarking State-of-the-Art Methods for Few-Shot Natural Language Understanding
* **Published Date:** 2021-09-27
* **ArXiv URL:** [http://arxiv.org/abs/2109.12742v2](http://arxiv.org/abs/2109.12742v2)
* **Authors:** Yanan Zheng, Jing Zhou, Yujie Qian, Ming Ding, Chonghua Liao et al.

**Abstract/Summary:**
> The few-shot natural language understanding (NLU) task has attracted much recent attention. However, prior methods have been evaluated under a disparate set of protocols, which hinders fair comparison and measuring progress of the field. To address this issue, we introduce an evaluation framework that improves previous evaluation procedures in three key aspects, i.e., test performance, dev-test correlation, and stability. Under this new evaluation framework, we re-evaluate several state-of-the-art few-shot methods for NLU tasks. Our framework reveals new insights: (1) both the absolute performance and relative gap of the methods were not accurately estimated in prior literature; (2) no single method dominates most tasks with consistent performance; (3) improvements of some methods diminish with a larger pretrained model; and (4) gains from different methods are often complementary and the best combined model performs close to a strong fully-supervised baseline. We open-source our toolkit, FewNLU, that implements our evaluation framework along with a number of state-of-the-art methods.

---

## 3. Systems Implementation Notes for Logos OS
* **The Cache-as-Memory Rule**: The segment-level caching mechanism proven in *Transformer-XL* is exactly the same logical framework we use when optimizing prompt-caching models (like Kimi K3 at $0.30/Mtok). By passing pre-compiled document states in our `.env`-configured pipelines, we exploit their caching layer to run lightning-fast queries against entire directories.
* **Storage Footprint**: Saved in `/data/.openclaw/workspace/harvested_research/hypatia_moonshot_academic_vault.md`
