# 🌐 Hypatia Live Decentralized & Collaborative Training Research Report
**Generated On:** 2026-07-13 15:30:28 EDT
**Compiled By:** Hypatia (Chief Academic & Crawler Sentinel)

This report compiles cutting-edge academic breakthroughs in peer-to-peer (P2P) training, browser-based WebGPU/WebRTC execution, and local fine-tuning of sparse Mixture of Experts (MoE) models to establish a technical foundation for custom local LLM training within Logos OS.

## 1. Decentralized & Peer-to-Peer Training Paradigms
These papers detail distributed backpropagation, decentralized SGD, and gradient averaging networks operating over high-latency or heterogeneous edge environments without a central server.

### 🌼 The Power of Backdoor Absorption in Community Training
* **Published:** 2026-07-07T15:19:20Z
* **Source:** [http://arxiv.org/abs/2607.06643v1](http://arxiv.org/abs/2607.06643v1)

**Abstract:** Backdoor attacks severely threaten large-scale AI models. When model owners delegate training to external compute providers within a decentralized training paradigm, adversaries can craft stealthy, low-frequency triggers to inject malicious behavior while evading standard audits. Traditionally, detecting these attacks requires a full re-computation of the training steps--a prohibitive overhead that directly contradicts the owner's resource constraints. To address this, we investigate the resilience of continuous optimization dynamics under Byzantine perturbations, where adversaries are forced to compete against a continuous influx of honest updates. Under a threat model where an adversary compromises f out of n total trainers, we quantify the minimum auditing overhead required by the model owner to probabilistically bound the attack success rate. We formalize this injection-absorption dynamic as a Discrete-Time Markov Chain (DTMC). Using this framework, we prove that the success probability of any bounded adversary asymptotically collapses to zero under a defense strategy combining natural absorption, a randomized scheduler, and lazy verification oracle. Empirical results demonstrate significant backdoor suppression with zero utility degradation even when invoking the verification oracle on merely 10% of the total training steps. This approach yields a provably sound and computationally efficient defense for safety-critical AI.

---

### 🌼 FedFFT: Taming Client Drift in Federated SAM via Spectral Perturbation Filtering
* **Published:** 2026-07-05T08:33:38Z
* **Source:** [http://arxiv.org/abs/2607.04170v1](http://arxiv.org/abs/2607.04170v1)

**Abstract:** Federated Learning (FL) enables decentralized training without data sharing, but suffers from statistical heterogeneity across clients, leading to client drift, poor generalization, and sharp minima compared to centralized training. Sharpness-Aware Minimization (SAM) has emerged as a promising approach to improve generalization, yet its application in federated learning still suffers from divergence problems, since perturbations are computed locally and reflect client-specific loss geometries. To better understand this issue, we provide experimental evidence from a new perspective, the frequency domain, for SAM perturbations in federated settings, revealing that inter-client perturbation inconsistencies are predominantly concentrated in the low-frequency spectrum. Motivated by this insight, we propose Federated learning with Frequency-domain Filtering of SAM perturbations (FedFFT). It is a lightweight and plug-and-play method that filters out low-frequency components of SAM perturbations without requiring additional communication, thereby suppressing inconsistent components in client updates while preserving consistent learning signals. Extensive experiments across multiple benchmarks and diverse backbones demonstrate that FedFFT consistently outperforms SAM-based FL methods, particularly under severe non-IID distributions. These results highlight the effectiveness, scalability, and general applicability of our frequency-domain perspective for sharpness-aware federated optimization.

---

### 🌼 Decentralised AI Training and Inference with BlockTrain
* **Published:** 2026-06-23T15:47:33Z
* **Source:** [http://arxiv.org/abs/2606.24722v2](http://arxiv.org/abs/2606.24722v2)

**Abstract:** Frontier AI training is increasingly shaped by access to dense, centrally controlled accelerator clusters. This creates a structural advantage for hyperscalers and large centralized laboratories, and makes open or independent AI efforts depend on scarce capital, privileged infrastructure, and data-center geography. We present Spheroid BlockTrain, a decentralized training protocol in which a model is partitioned into independently trainable blocks, each optimized on a local objective derived from the same global target and composed at inference into one model. On byte-level WikiText, BlockTrain reaches cross entropy 1.359 (perplexity 3.89), within about 0.04 CE of a same-setup end-to-end Transformer reference, while each active worker trains only one block and avoids full-model optimizer state. A shared six-worker block training run reaches CE 1.385 by averaging same-block updates into one assembled model. HTTP/TCP transport experiments move real serialized checkpoints and updates, including a public-IP three-host run that improves CE from 5.580 to 1.811 while moving 15.22 GB. For inference, the current BlockTrain path uses one block-stack traversal per full output and serves over direct TCP across three public-network GPU hosts up to a 75.80B-parameter logical fp16 shape, outperforming a matched plain-autoregressive TCP pipeline baseline because it emits a full sequence per WAN pipeline traversal rather than one token per traversal.

---

### 🌼 Beyond Weights and Gradients: A Taxonomy of Federated Learning Messages
* **Published:** 2026-06-15T16:02:03Z
* **Source:** [http://arxiv.org/abs/2606.16891v1](http://arxiv.org/abs/2606.16891v1)

**Abstract:** Federated Learning is rapidly evolving beyond the exchange of traditional model weights and gradients, yet existing definitions fail to capture the full scope of modern payloads like synthetic data and federated analytics. This paper addresses the gap by proposing a formal mathematical definition of a federated message that accounts for both utility and privacy. We introduce a taxonomy that organizes these exchanges into three categories: model structures, statistical summaries, and data-conditioned representations. By evaluating these groups based on computational demands, communication costs, and privacy risks, we provide a clearer understanding of the trade-offs involved in decentralized training. Our review of 202 recent publications highlights a significant shift since 2021 toward diverse messaging paradigms, signaling a move away from standard deep learning updates toward more specialized information sharing. This framework provides a structured path for future research to optimize federated systems for varying hardware and security requirements.

---

### 🌼 Mixtures of Subspaces for Bandwidth Efficient Context Parallel Training
* **Published:** 2026-06-15T08:17:13Z
* **Source:** [http://arxiv.org/abs/2606.16384v1](http://arxiv.org/abs/2606.16384v1)

**Abstract:** Pretraining language models with extended context windows enhances their ability to leverage rich information during generation. Existing methods split input sequences into chunks, broadcast them across multiple devices, and compute attention block by block which incurs significant communication overhead. While feasible in high-speed clusters, these methods are impractical for decentralized training over low-bandwidth connections. We propose a compression method for communication-efficient context parallelism in decentralized settings, achieving a remarkable compression rate of over 95\% with negligible overhead and no loss in convergence. Our key insight is to exploit the intrinsic low-rank structure of activation outputs by dynamically constraining them to learned mixtures of subspaces via efficient reparameterizations. We demonstrate scaling billion-parameter decentralized models to context lengths exceeding 100K tokens on networks as slow as 300Mbps, matching the wall-clock convergence speed of centralized models on 100Gbps interconnects.

---

## 2. In-Browser (WebGPU/WebRTC) & On-Device Edge Learning
These papers explore the mechanics of executing training loops directly inside client nodes, leveraging hardware-accelerated WebGPU pipelines and low-latency peer-to-peer transport layers.

### ⚡ On-Device Adaptive Battery Power Prediction for Electric Vehicles
* **Published:** 2026-07-10T13:24:34Z
* **Source:** [http://arxiv.org/abs/2607.09400v1](http://arxiv.org/abs/2607.09400v1)

**Abstract:** Adaptive power management in Electric Vehicles (EVs) requires accurate power prediction. Although deep learning models have emerged as highly effective for time-series forecasting in this domain, their performance is prone to degradation when exposed to data with distributions different from the training data. We introduce a novel approach that enables on-device learning in resource-constrained EV systems to continuously adapt pretrained battery prediction models to new, unseen data. We leverage existing pretrained models by transforming them into adaptable versions that retain critical hyperparameter knowledge from their initial training. We comprehensively investigate both online and offline model adaptation strategies. Our results demonstrate significant improvements in forecasting performance across various models and time horizons, achieving mean absolute error reductions of up to 7.49\% and 14.88\% with online and offline adaptation techniques, respectively. This study highlights the substantial benefit of on-device adaptation, resulting in enhanced battery power predictions than unadapted model deployments in real-world EV scenarios.

---

### ⚡ Decentralised Federated Learning over Temporal Networks: The Role of Heterogeneities
* **Published:** 2026-07-03T10:12:20Z
* **Source:** [http://arxiv.org/abs/2607.03171v1](http://arxiv.org/abs/2607.03171v1)

**Abstract:** Decentralised federated learning, based on peer-to-peer communication, is increasingly proposed for on-device training of machine learning models, promising a privacy-preserving, communication-efficient training process with no risk of single-point failure. However, the role of structural and temporal inhomogeneities in such fully decentralised settings remains poorly understood. Here, we investigate their effects when model parameters are locally averaged during aggregation. We show that the decentralised federated learning process is governed, both in the early phase and the late, stationary limit, by the same dynamics as a lazy random-walk diffusion process on temporal networks. Based on this mapping, we demonstrate that the typical experimental scenario used in decentralised federated learning leads to unrealistically rapid convergence because of ignoring the temporal and structural inhomogeneities inherent in the communication network. We analyse real-world temporal networks and find that inhomogeneities most often dramatically slow down diffusion, hence the convergence process.

---

### ⚡ Query Complexity of Hypergraph Connectivity and Learnability using CUT Oracles
* **Published:** 2026-07-01T17:54:03Z
* **Source:** [http://arxiv.org/abs/2607.01216v1](http://arxiv.org/abs/2607.01216v1)

**Abstract:** We investigate the power of CUT queries to reveal the structure of unknown hypergraphs. While simple graphs allow for optimal $O(n)$-query connectivity algorithms, hypergraphs face a fundamental identifiability barrier in that distinct hypergraphs can share identical cut-profiles, making exact edge learning impossible in general, a primitive crucial in the graph connectivity algorithms.   We first present a zero-error randomized algorithm that identifies the connected components of any weighted hypergraph using $O(n)$ expected queries, matching the $Ω(n)$ lower bound. This approach bypasses the reconstruction barrier by introducing the notion of ``independent families'' -- vertex subpartitions that do not share hyperedges -- and iteratively coarsening them using auxiliary weighted graph connectivity techniques [Liao-Chakrabarty, 2024].   Second, we demonstrate that the impossibility of exact learning depends on hyperedge parity. For even-parity hypergraphs, we show that the structure is reconstructible using a Möbius transform on the CUT function to implement binary-search-style vertex identification. This yields deterministic algorithms for obtaining $k$-connectivity certificates for $r$-bounded even hypergraphs in $\tilde{O}_r(kn)$ queries. Finally, we bypass parity and rank constraints for linear hypergraphs, achieving a subquadratic $\tilde{O}(kn^{1.5})$ query complexity for $k$-connectivity. This significantly improves upon the general $\tilde{O}(n^2)$ bound derived via symmetric submodular function minimization.

---

### ⚡ What Browsers Do in the Shaders: A Measurement Study of WebGPU Privacy
* **Published:** 2026-06-24T22:11:06Z
* **Source:** [http://arxiv.org/abs/2606.26412v1](http://arxiv.org/abs/2606.26412v1)

**Abstract:** WebGPU lets ordinary web pages run GPU workloads through a validated programming model. Validation protects memory safety, but shared browser, driver, OS, and GPU state can still expose privacy-relevant signals. We present WGPULens, a framework for measuring those signals across controlled scenarios, browser-native co-residency, a participant field study, public page loads, and mitigation policies. Our framework separates measurements: controlled scenarios support leakage, boundary, and mitigation claims; participant runs support deployment, compatibility, and fingerprintability; and a Tranco crawl measures WebGPU exposure in real-world pages.   Our controlled results identify persistent pipeline compilation state as the clearest surface. Cold/warm pipeline probes reveal prior compilation state across selected origin, profile, and browser placements. Controlled browser/native experiments also show native GPU activity can be inferred from browser-visible observables under labeled workloads. Other resource probes provide weaker positive results and negative controls.   The participant field study shows active WebGPU behavior is highly distinctive within the sample, with deterministic components stable within runs and lower exact stability across repeated visits. A page-load crawl finds WebGPU use mainly as adapter probing and static support code, with no observed page-load shader, pipeline, queue, query, or map activity. Mitigation pilots identify source-level key separation as a proxy for evaluating pipeline-cache partitioning. Overall, WGPULens shows that WebGPU privacy analysis must be surface-specific: browsers need to measure which GPU state crosses which boundary, which browser-visible signals reveal it, and what the corresponding mitigations cost.

---

### ⚡ From Handcrafted Features to Functional Edge Learning: Evolution of EEG Seizure Detection Frameworks
* **Published:** 2026-06-20T23:10:04Z
* **Source:** [http://arxiv.org/abs/2606.22258v1](http://arxiv.org/abs/2606.22258v1)

**Abstract:** Electroencephalogram (EEG) analysis remains the clinical gold standard for epilepsy diagnosis and seizure detection. While Deep Learning (DL) has significantly advanced automated EEG interpretation, its transition from controlled experimental settings to routine clinical deployment is severely bottlenecked by fundamental architectural flaws. Standard DL models operate as opaque black-boxes lacking clinical interpretability, demand massive amounts of balanced annotated data, and incur steep computational costs incompatible with resource-constrained wearable or implantable neuromodulation devices. This paper presents a comprehensive review of these prevailing limitations and explores Kolmogorov-Arnold Networks (KANs) as a emerging paradigm for EEG-based seizure detection. By replacing the fixed activation functions of traditional neurons with flexible, learnable functions along the network's connections, KANs bridge the critical gap between predictive accuracy and mathematical transparency. We systematically analyze how KAN architectures resolve the shortcomings of traditional DL-based models by offering exceptional parameter efficiency, inherent interpretability for physician trust, and robust performance under data scarcity. Ultimately, this review establishes KANs not merely as an incremental algorithmic update, but as a fundamental paradigm shift necessary to actualize next-generation, patient-specific, and thoroughly transparent clinical EEG monitoring systems.

---

## 3. Sparse MoE Architectures, PEFT & Local Fine-Tuning
These papers outline techniques for local parameter-efficient fine-tuning (PEFT), Mixture of Experts routing optimization, and sparse-activation training designed to run natively within consumer RAM boundaries.

### 🧠 What VGGT Knows About Overlap: Probing Geometric Foundation Models for Co-Visibility
* **Published:** 2026-07-10T15:17:02Z
* **Source:** [http://arxiv.org/abs/2607.09503v1](http://arxiv.org/abs/2607.09503v1)

**Abstract:** A fundamental challenge in 3D reconstruction and robotic localization is co-visibility: determining which image pairs share overlapping visible surfaces, particularly in scenarios with minimal overlap. We demonstrate that VGGT implicitly encodes co-visibility as an emergent behavior: without any supervision for this task, its internal representations exhibit a clear hierarchical structure mirroring that of large language models, i.e. early layers build a 3D-aware scene representation, while late layers act as dedicated co-visibility reasoners. In particular, we identify layer L17 as a negative anchor that consistently routes non-co-visible pairs for this backbone, regardless of the evaluation setting, providing task-grounded evidence of layer specialization in a geometry-grounded foundation model. Building on this, we introduce Co-VGGT, which freezes VGGT and trains only a lightweight layer-wise mixture-of-experts head (less than 7.5M parameters) to classify co-visibility from RGB alone, treating each layer as a specialized expert whose geometric abstraction is adaptively weighted per input pair. On the Co-VisiON benchmark, Co-VGGT surpasses the human annotation baseline and improves over prior work by more than 25% pairwise and 10% multiview. Pairwise predictions are well-calibrated (ECE=0.030), enabling direct use as edge weights in visibility graphs for downstream SfM and SLAM pipelines without post-hoc correction. Code and data are available.

---

### 🧠 A Sovereign, Open-Source Foundation Model for German and English
* **Published:** 2026-07-10T13:51:41Z
* **Source:** [http://arxiv.org/abs/2607.09424v1](http://arxiv.org/abs/2607.09424v1)

**Abstract:** We present Soofi S 30B-A3B, a sovereign, open-source Mixture-of-Experts (MoE) hybrid Mamba Transformer foundation model for German and English. Its hybrid design activates only 3B of 30B parameters per token and keeps the inference cache near-constant as context grows, giving it a decisive throughput advantage over dense models for long-context, high-concurrency deployment. Pretrained on roughly 27 trillion tokens with deliberately up-weighted German, Soofi S matches dense 14 to 27B models on aggregate English and German benchmarks while achieving the best code aggregates in both languages among 17 open base models, and outperforms every European sovereign baseline in our comparison, including ones far larger in active parameters. Among fully open models, Soofi S obtains the highest English and German evaluation scores, ahead of Olmo 3 32B and Apertus 70B. Soofi S was built end-to-end on the German Industrial AI Cloud, a sovereign HPC scale AI infrastructure operated by Deutsche Telekom in Munich. Soofi S will be released under highly permissive, open-access terms: weights, selected intermediate checkpoints, full per-source data accounting, hyperparameters, and training and evaluation code. Where source licenses permit, data-construction artifacts are released under permissive licenses; commercially licensed sources are documented with aggregate statistics and exact mixture accounting.

---

### 🧠 Mach-Mind-4-Flash Technical Report
* **Published:** 2026-07-10T12:57:08Z
* **Source:** [http://arxiv.org/abs/2607.09375v1](http://arxiv.org/abs/2607.09375v1)

**Abstract:** We present Mach-Mind-4-Flash, a 35B-parameter Mixture-of-Experts (MoE) agentic model with 3B activated parameters. Through post-training optimization alone without scaling pre-training compute, the model achieves performance on par with or surpassing that of 100B-parameter-class models. By introducing scalable agentic interaction environments for large-scale reinforcement learning, the model attains significant performance gains on real-world application tasks. Our pipeline comprises three stages: (1) a unified RL/OPD training infrastructure with dynamic multi-teacher scheduling and operator-level acceleration, delivering 17\% end-to-end training speedup; (2) multiple domain-specific RL experts trained in parallel across Reasoning, General, and Agent tracks, then fused into a single generalist via Multi-Teacher On-Policy Distillation (MOPD) -- a routed reverse-KL objective that eliminates the see-saw degradation of mixed-reward RL; (3) Hybrid Median-length Policy Optimization (HMPO), a single-stage token-efficiency method that compresses reasoning chains by 19--46\% with $\le$0.7 percentage-point accuracy loss. Mach-Mind-4-Flash scores 92.70 on AIME'26, 82.82 on IFBench, 80.74 on Behavioral-SafetyBench, 75.80 on BFCL-v4, 72.31 on BrowseComp-zh, and 84.20 on ClawBench -- leading or matching models with 10--30$\times$ its activated size at a fraction of the inference cost.

---

### 🧠 Automatic Thematic Indexing of Large Literary Corpora: A Machine Learning Approach to Voltaire's Complete Works
* **Published:** 2026-07-10T11:54:02Z
* **Source:** [http://arxiv.org/abs/2607.09316v1](http://arxiv.org/abs/2607.09316v1)

**Abstract:** Thematic indexing -- the practice of assigning structured conceptual labels to sections of text -- is essential to scholarly access in large-scale literary and historical editions, yet it remains a largely manual, labour-intensive process. This paper explores the application of machine learning to automatic thematic indexing, using two substantial sub-corpora of the Complete Works of Voltaire as a test case: the Essai sur les mœurs et l'esprit des nations and the Questions sur l'Encyclopédie. The task is framed as a multi-label classification problem, in which a model must assign the set of index entries that a professional indexer would apply to a given page of text. We compare a range of approaches -- from encoder-based models with classification heads to generative large language models (LLMs) fine-tuned via Low-Rank Adaptation (LoRA) -- spanning model sizes from approximately 3 to 120 billion parameters. Our best-performing model, from the Mistral family in a 4-bit quantised configuration, achieves F1 scores of up to 0.67; we argue that these figures represent lower bounds, given the inherent subjectivity of professional indexing and the frequency with which model predictions prove semantically valid despite diverging from the print index. We further evaluate cross-corpus generalisation and conduct a detailed qualitative analysis of model behaviour on literary and rhetorical features of the source texts that prove particularly resistant to automated treatment. Our findings have implications for the broader challenge of providing structured thematic access to large-scale literary and historical corpora.

---

### 🧠 Super-Tuning: From Activation-Aware Pruning to Sparse Fine-Tuning
* **Published:** 2026-07-10T10:55:28Z
* **Source:** [http://arxiv.org/abs/2607.09287v1](http://arxiv.org/abs/2607.09287v1)

**Abstract:** Large language models (LLMs) remain expensive to fine-tune because full-parameter updates require substantial memory, compute, and per-task storage. We study whether saliency signals originally developed for pruning can be reused to choose where a model should adapt. We propose Super, a sparse parameter-efficient fine-tuning (PEFT) method that fixes a small trainable support using a Wanda-style activation-weighted magnitude score [Sun et al., 2023] computed from a calibration pass. We then introduce Supra, a hybrid adapter that combines this sparse update with LoRA while preserving a matched trainable-parameter budget through a simple budget-splitting rule. In single-seed Math17K arithmetic experiments on Llama-3.2-1B and Meta-Llama-3-8B, the best Super/Supra variants achieve the highest average accuracy among the tested schedule-selected adapter configurations. We also include a PaFi-style magnitude-only support as a closest training-free sparse baseline and find that low-score supports under both magnitude and Wanda-style orderings can be effective. These results suggest that simple pruning-inspired orderings can provide useful fixed sparse supports for PEFT, especially when combined with low-rank adapters.

---

