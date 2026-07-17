# 🌐 Hypatia MoE Open-Weight & Sparse Architecture Research Report
**Generated On:** 2026-07-17 12:18:24 
**Compiled By:** Hypatia (Chief Academic & Crawler Sentinel on behalf of Logos OS)

This report details current open-access and academic breakthroughs in **Sparse Mixture-of-Experts (MoE)** architectures, with a specific focus on **Chinese labs, universities, and open-weight models** (DeepSeek, Moonshot, Tsinghua, Alibaba, Tencent) verified against live global repositories.

---

## 1. Executive Synthesis & Architectural Paradigms

Based on the parsed telemetry of the latest MoE papers, the frontier has converged on several massive optimization layers designed to bypass physical network and memory ceilings:

1. **Fine-Grained Expert Segmentation**: Instead of routing to 8 or 16 large experts (like early MoE models), modern designs (e.g., DeepSeekMoE) divide the network into 64 or 128 micro-experts. By activating a dynamic subset (e.g., 6 out of 128), models achieve surgical routing accuracy with a fraction of the active parameter footprint.
2. **Shared and Routing-Isolated Experts**: To prevent "redundant knowledge acquisition" across experts (where multiple experts learn basic English grammar or syntax instead of specialized skills), modern architectures isolate a subset of experts as "Shared Experts." These shared experts are always active on every token, freeing the routed experts to specialize exclusively on niche reasoning tracks.
3. **Auxiliary Loss-Free Balance Control**: Standard MoEs suffer from "expert collapse," where a few experts get all the traffic while others starve. Traditional balancing tricks (like auxiliary load loss) degrade performance. Modern models use dynamic bias adjustments at the gating layer to smoothly distribute traffic without introducing performance penalties during training.
4. **Attention-MoE Co-Design**: Long-context scaling (1M+ tokens) is being unlocked by co-designing MoE gating with sparse attention mechanisms (like Kimi Delta Attention and Attention Residuals), preventing the memory footprint of KV caching from scaling quadratically.

---

## 2. Global MoE Academic Database (Live arXiv Crawl)

Below is the database compiled by Hypatia's crawler, highlighting contributions from elite Chinese academic institutions and industrial research divisions.

### 1. In-Place Tokenizer Expansion for Pre-trained LLMs
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-16
* **Source URL:** [http://arxiv.org/abs/2607.15232v1](http://arxiv.org/abs/2607.15232v1)
* **Authors:** Jimmy T. H. Smith, Tarek Dakhran, Alberto Cabrera, Simon S. Lee, Paul Pak et al.

**Abstract/Summary:**
> A tokenizer fixed at the start of pre-training allocates vocabulary in proportion to the pre-training corpus, reflecting the deployment priorities at that time. When those priorities shift, languages added later are split into many more tokens per word, which can raise latency, compute, and energy consumption for users of those languages. Cloud models can afford a broad vocabulary because the embedding and LM-head matrices are a small fraction of their parameters. On a compact model those matrices are a material share of per-token decode bandwidth, so on-device models ship small vocabularies and accept fragmentation outside a fixed language set. We present tokenizer expansion, an in-place recipe for upgrading a pre-trained model's tokenizer when the model producer controls its design. We continue the existing tokenizer's BPE merges on a multilingual corpus, so most source tokens carry over unchanged as single tokens and every new token has an exact decomposition into source tokens. We copy the carried-over embedding rows unchanged and initialize new rows as the mean of their source sub-token embeddings. A two-stage adaptation, embedding-only training then full-model continued pre-training, recovers source-checkpoint quality. We apply the recipe to a continued pre-trained checkpoint of LFM2-8B-A1B, an 8B-parameter Mixture-of-Experts model, to help produce LFM2.5-8B-A1B with a 128K tokenizer. The expanded tokenizer encodes Hindi and Vietnamese in roughly $2.4\times$ and $2.6\times$ fewer tokens than the source (up to $4.0\times$ on Thai). Combining these reductions with the measured per-token cost of the larger vocabulary, we estimate a $2.2$-$3.7\times$ per-character decode speedup for these languages across our reference devices. We release the model weights and the expanded tokenizer, and report the negative findings that shaped the recipe.

---

### 2. LongStraw: Long-Context RL Beyond 2M Tokens under a Fixed GPU Budget
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-16
* **Source URL:** [http://arxiv.org/abs/2607.14952v1](http://arxiv.org/abs/2607.14952v1)
* **Authors:** Changhai Zhou, Kieran Liu, Yuhua Zhou, Qian Qiao, Jun Gao et al.
* **Detected Affiliations/Keywords:** Qwen, Glm

**Abstract/Summary:**
> A growing gap separates inference context lengths from RL post-training: inference systems are approaching million-token contexts, while post-training workloads often remain at 256K tokens or below and rely on length generalization at deployment. The gap is especially important for AI agents, whose observations, tool outputs, documents, and prior decisions accumulate over long trajectories. LongStraw is an architecture-aware execution stack for million-token RL post-training under a fixed GPU budget, instantiated with Group Relative Policy Optimization (GRPO). It evaluates the shared prompt without autograd, retains only model-specific state needed by later tokens, and replays short response branches one at a time, reducing the live training graph at the cost of additional replay time. We implement it for the hybrid recurrent and full-attention Qwen3.6-27B and the compressed-attention mixture-of-experts GLM-5.2. On eight H20 GPUs, LongStraw completes grouped Qwen scoring and response backward at 2.1M positions for groups of 2 and 8; increasing the group size adds only 0.21 GB of peak allocated memory, while a separate stress test reaches 4.46M positions. On 32 H20 GPUs, we validate the end-to-end LongStraw execution path for a 2.1M-token prompt across all 78 layers of GLM-5.2. These experiments establish execution capacity rather than complete training correctness because the captured prompt state is detached and some distributed forward and gradient composition paths remain incomplete.

---

### 3. TAMF-VTON: Texture-Aware Mask-Free Virtual Try-On via High-Fidelity Image Synthesis
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-16
* **Source URL:** [http://arxiv.org/abs/2607.14807v1](http://arxiv.org/abs/2607.14807v1)
* **Authors:** Jie Wang, Qian He, Gaofeng He, Xiaogang Jin, Huamin Wang

**Abstract/Summary:**
> Recent diffusion-based virtual try-on (VTON) methods remain limited by their reliance on segmentation masks, insufficient preservation of fine-grained textures, and limited support for arbitrary multi-garment compositions. Consequently, existing approaches still face significant challenges in real-world e-commerce deployment. We present TAMF-VTON, a texture-aware, mask-free framework that enables high-fidelity image synthesis under practical unconstrained conditions. Our method requires no human parsing or inpainting masks at inference time and supports diverse garment styles, categories, and quantities, enabling the simultaneous transfer of multiple items while preserving body structure and intricate texture details. This is achieved through a unified generative pipeline with three key components: (1) a lightweight Mixture-of-Experts (MoE) adaptation scheme that enables efficient fine-tuning without compromising the base model's general editing capabilities; (2) a frequency-domain supervision mechanism that explicitly optimizes high-frequency spectral consistency to preserve high-fidelity textures; and (3) a robust data curation pipeline employing an adaptive inpainting strategy to simulate the inverse VTON process for high-quality training pair generation. Extensive experiments demonstrate that our approach outperforms state-of-the-art methods in both quantitative metrics and perceptual quality. Optimized for efficiency, the model achieves inference in under 15 seconds per image on an NVIDIA RTX 4090 with INT4 quantization. By combining mask-free operation, flexible multi-garment composition, faithful texture preservation, and efficient inference on consumer hardware, TAMF-VTON demonstrates a commercially viable solution for scalable deployment in real-world digital fashion scenarios. The project is available at https://www.style3d.ai/ai-photoshoot/virtual-clothing-try-on.

---

### 4. D-cut: Adaptive Verification Depth Pruning for Batched Speculative Decoding
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-16
* **Source URL:** [http://arxiv.org/abs/2607.14647v1](http://arxiv.org/abs/2607.14647v1)
* **Authors:** Tianyu Liu, Yuhao Shen, Rui Cen, Junhan Shi, Jiebin Zhang et al.

**Abstract/Summary:**
> Speculative decoding accelerates large language model (LLM) inference without compromising output quality. Recent parallel drafting methods further improve single-request performance by decoupling draft length from drafting latency, enabling longer drafts and higher mean accepted tokens (MAT). However, under high request concurrency, long drafts waste substantial computation on rejected tokens, increasing verification cost and potentially making speculative decoding slower than autoregressive decoding. We present D-Cut, an adaptive pruning method that selects draft tokens jointly across the batch and concentrates the verification budget on tokens most likely to be accepted. D-Cut is motivated by two observations. First, acceptance lengths vary considerably across concurrent requests; D-Cut therefore performs cross-request pruning, allocating the verification budget adaptively according to draft confidence. Second, verification cost depends strongly on the deployment environment, including GPU architecture and parallelism strategy; D-Cut incorporates a runtime cost model to adapt its pruning depth to the target environment. Experiments on dense and mixture-of-experts (MoE) models show that, under high concurrency, D-Cut improves the average speedup from \(1.26\times\) to \(1.65\times\), restores acceleration in dense-model configurations where long-draft baselines are slower than autoregressive decoding, and achieves up to \(3.0\times\) speedup over autoregressive decoding on MoE models.

---

### 5. A Modern Multimodal Assistant on a 6 GB 2011 GPU: Stage-Validated, All-GPU CUDA Inference for Fermi
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-16
* **Source URL:** [http://arxiv.org/abs/2607.14568v1](http://arxiv.org/abs/2607.14568v1)
* **Authors:** A. C. Opus, J. Q. Lu

**Abstract/Summary:**
> A companion study ran a 35B mixture-of-experts model on a 2011 NVIDIA Tesla C2075 (Fermi, sm_20, 6GB) as a GPU-prefill/CPU-decode hybrid, because the 4-bit model did not fit in device memory (arXiv:2606.24031). This report keeps the hardware and asks what a model that fits can do: we deploy MiniCPM-V-4.6, a modern multimodal assistant pairing a SigLIP2 vision encoder and window-attention merger (16x visual token compression) with a compact hybrid gated-delta-net backbone, entirely on the GPU. Three results. (i) An all-GPU engine built on measured foundations: projections that dequantize 8-bit weights once and call the vendor SGEMM still in the last Fermi toolchain (64% of FP32 peak; our best hand-written GEMM hit 37%, wrongly called the ceiling); a chunked delta-rule rewrite of the recurrent layers, 2.8x faster than the sequential scan once attribution exposed one bad kernel; and a measured negative: 4-bit weights make decode slower than 8-bit here, since Fermi issues nibble-unpacking shifts at half rate. (ii) The vision side is a port with a proof obligation: we translate tower, merger, and projector to sm_20 CUDA, validating every stage against a locally generated reference forward (full tower 1.4e-5). One failure, position-embedding bucketization differing on exact rational ties, generalizes to a rule: float tie-breaking in index arithmetic is implementation-defined; call the reference operator, do not reimplement it. (iii) Long context exposes an O(N^2) wall short benchmarks hide: prefill falls from 114 tok/s at 2k tokens to 21 at 10k in a naive attention kernel; per-head vendor-GEMM calls writing into the existing score buffer (zero extra memory) restore a flat profile (408 at 2k, 361 at 10k; 17x), verified by exact needle retrieval from 60% depth. The same rewrite cuts image encoding 6x, to 0.93s. The system answers an image question end-to-end in 1.7s.

---

### 6. VLT: A Vision-Language-Time Series Multimodal Foundation Model for Industrial Intelligence
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-16
* **Source URL:** [http://arxiv.org/abs/2607.14510v1](http://arxiv.org/abs/2607.14510v1)
* **Authors:** Haiteng Wang, Jingheng Yan, Xiaokang Wang, Lei Ren

**Abstract/Summary:**
> Industrial time series serve as the foundation for Prognostics and Health Management (PHM) to ensure the reliability and safety of industrial equipment such as aero-engines. However, existing approaches are typically limited to single-modality modeling, which restricts their generalization in complex scenarios. Although recent advances in large language models (LLMs) provide new opportunities for multimodal learning, bridging continuous time-series signals and discrete textual semantics remains an open challenge. To this end, we propose VLT, a multimodal foundation model that jointly models time-series, frequency-spectrum visual representations, and textual knowledge. A key insight is to utilize the frequency spectrum as a visual bridge to connect continuous temporal signals with discrete semantics. Specifically, a Time-aware Mixture-of-Experts (Time-MoE) is designed to capture heterogeneous temporal dynamics, while a Frequency-Text Augmented Learner enables joint modeling of spectral and semantic features within a shared representation space. Furthermore, a time-centric gradient alignment mechanism is introduced to mitigate cross-modal optimization conflicts via gradient normalization and reliability-aware dynamic reweighting. Extensive experiments on multiple industrial datasets demonstrate that VLT outperforms state-of-the-art methods, achieving superior robustness and generalization under few-shot, noisy, and incomplete-modality settings.

---

### 7. MixCompress: Mixture of Experts for Variable Rate Learned Image Compression
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-15
* **Source URL:** [http://arxiv.org/abs/2607.14334v1](http://arxiv.org/abs/2607.14334v1)
* **Authors:** Calvin-Khang Ta, Praneet Singh, Tong Shao, Peng Yin

**Abstract/Summary:**
> Learned image compression (LIC) is bottlenecked by the need to store independent models for each rate-distortion operating point. Existing variable bit-rate (VBR) methods aim to reduce this overhead via dense parameter modulation, but forcing a shared backbone to approximate divergent mappings causes severe feature entanglement. Specifically, low-rate smoothing gradients inherently conflict with the preservation of high-frequency textural details, leading to sub-optimal performance. To resolve this, we propose MixCompress, a unified VBR framework based on sparse structural specialization. While sparsely gated Mixture-of-Experts (MoE) routing successfully mitigates gradient conflict, it operates on a fixed computational budget. To address the increased representational demands of higher bit-rates we introduce a Mixture-of-Depths (MoD) extension to dynamically scale model capacity. Combined with Conditional Auxiliary Transforms (CAT) for dynamic sub-band energy modulation, our hierarchical framework effectively dynamically scales capacity. Extensive evaluations demonstrate that MixCompress not only matches individually optimized single-rate baselines but can even surpass them, establishing a new Pareto frontier for computationally efficient image coding.

---

### 8. Fine-Grained Vision-Language Pretraining with Organ-Conditioned Pattern Tokens for CT Understanding
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-15
* **Source URL:** [http://arxiv.org/abs/2607.13892v1](http://arxiv.org/abs/2607.13892v1)
* **Authors:** Guoliang You, Xiaomeng Chu

**Abstract/Summary:**
> Computed tomography (CT) vision-language pretraining from paired volumes and radiology reports is a scalable yet challenging task. Existing methods commonly adopt global scan-report contrast, which is scalable but obscures heterogeneous organ evidence. Meanwhile, direct organ-level alignment remains coarse, since the same anatomy can exhibit multiple distinct radiological appearances. Therefore, pretraining requires a finer alignment unit: the organ-conditioned radiological pattern. In this work, we propose OCP-CT, an organ-conditioned pattern-token alignment framework for CT vision-language pretraining. Specifically, OCP-CT preserves a stable global CT-report contrastive branch and introduces an organ pattern interface: sparse Mixture-of-Experts (MoE) routes image and text tokens according to latent radiological patterns, learnable slots query the routed tokens into continuous pattern tokens, and paired token contrast aligns image-text pattern tokens with structured soft targets built from report-derived clinical similarity. On the publicly available CT-RATE and RAD-ChestCT benchmarks, OCP-CT achieves average AUROCs of 84.5% and 69.9% for zero-shot abnormality diagnosis, respectively. Compared with the strongest prior reported results, these results yield absolute AUROC gains of 6.7 and 0.8 percentage points.

---

### 9. FM$^2$: Unified Federated Foundation Models for Heterogeneous Multimodal Medical Imaging
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-15
* **Source URL:** [http://arxiv.org/abs/2607.13386v1](http://arxiv.org/abs/2607.13386v1)
* **Authors:** Shengchao Chen, Ting Shu

**Abstract/Summary:**
> Building foundation models for medical imaging requires pooling data across institutions, yet privacy regulations prohibit centralized aggregation. Existing Federated Foundation Models either fine-tune natural-image models with poor medical-domain transfer, or train from scratch within a single modality, lacking the flexibility to unify tasks. We identify an under-explored challenge, Imaging Modality Heterogeneity, where clients operate under two structural regimes: Overlapped (shared modalities with heterogeneous label distributions) and Non-overlapped (fully disjoint modalities per client). We propose FM$^2$, a unified framework that trains the core backbone from scratch to preserve medical domain fidelity while optionally incorporating biomedical pretrained encoders for vision-language alignment. FM$^2$ equips each client with dual Mixture-of-Experts modules (a Class-wise MoE for personalized category knowledge and a Domain-wise MoE for shared cross-modality representations), coupled with a Heterogeneous Modality Alignment (HMA) regularizer that explicitly aligns modality-specific expert parameters, admitting provable $O(1/\sqrt{T})$ convergence and generalization guarantees. FM$^2$ further incorporates Caption-Enhanced Learning (CEL), where locally retained GPT-4o-generated captions serve as a textual semantic bridge enabling representation transfer across clients with disjoint modalities, and demonstrates extensibility to Federated Medical VQA. Experiments on our MIMH benchmark (classification and CEL) and real-world medical VQA datasets confirm consistent superiority over state-of-the-art federated baselines and strong out-of-modality generalization across all three tasks.

---

### 10. Audio-Native Speech Recognition with a Frozen Discrete-Diffusion Language Model
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-14
* **Source URL:** [http://arxiv.org/abs/2607.13013v1](http://arxiv.org/abs/2607.13013v1)
* **Authors:** Harsha Vardhan Khurdula, Abhinav Kumar Singh, Yoeven D Khemlani, Vineet Agarwal

**Abstract/Summary:**
> Automatic speech recognition is dominated by autoregressive decoders that emit one token at a time. We ask whether a discrete diffusion language model can transcribe speech instead, refining a whole transcript in parallel over a small number of denoising steps. We train an audio-native interface for DiffusionGemma, a 26B mixture-of-experts model that generates text by uniform, random-token discrete diffusion rather than the absorbing-mask scheme common to recent diffusion language models. A frozen Whisper encoder supplies acoustic features, a lightweight projector maps them into the model embedding space, and low-rank adapters let the frozen backbone attend to the new modality. About 42M parameters are trained, which is 0.16 percent of the backbone. We find that the natural training objectives fail to ground the audio because their gradient reaches the projector only through attention that has already dismissed it. A connectionist temporal classification loss applied through the frozen output head breaks this deadlock. The resulting model reaches 6.6 percent word error rate on LibriSpeech test-clean, transcribes in roughly eight parallel steps regardless of utterance length, and uses a single adapter trained on six languages, which we evaluate here on English, Hindi, and Mandarin.

---

### 11. Hy-Embodied-VLM-1.0: Efficient Physical-World Agents
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-14
* **Source URL:** [http://arxiv.org/abs/2607.12894v1](http://arxiv.org/abs/2607.12894v1)
* **Authors:** Ziyi Wang, Xumin Yu, Yongming Rao, Yonggen Ling, Yunheng Li et al.
* **Detected Affiliations/Keywords:** Qwen

**Abstract/Summary:**
> Building capable embodied agents requires not only multimodal perception and understanding, but also agentic capabilities for reasoning about actions, adapting to evolving situations, and interacting with the physical world. In this report, we introduce Hy-Embodied-VLM-1.0, an efficient and powerful embodied foundation model specifically designed for embodied agents operating in the physical world. To cultivate such capabilities from the pre-training stage onward, we define an action-centric capability taxonomy comprising three progressive dimensions: Action-Relevant State Understanding, Action-Transition Reasoning, and Sequential and Adaptive Reasoning. Guided by this taxonomy, we develop a systematic data pipeline and curate data mixtures spanning both pre-training and post-training. To deliver strong physical-world understanding and interaction capabilities while supporting latency-sensitive deployment, we build our model on the Hy3-A3B language backbone and the Hy-ViT2 vision encoder. Its efficient Mixture-of-Experts architecture combines strong model capacity with high inference efficiency. We evaluate Hy-Embodied-VLM-1.0 on a comprehensive suite of 38 benchmarks covering embodied perception, physical-world understanding, and embodied reasoning. The model achieves the best performance among similarly sized models on 19 of the 38 benchmarks and substantially outperforms strong competitors, including Qwen3.6-A3B and Cosmos 3. Compared with the previous-generation Hy-Embodied-0.5 MoT-2B, Hy-Embodied-VLM-1.0 improves average performance by 8.4%. Despite activating only 3B parameters, it achieves performance close to that of the previous-generation model with 32B activated parameters. Beyond static benchmark evaluation, Hy-Embodied-VLM-1.0 also demonstrates strong performance on embodied agentic tasks requiring multi-turn interaction and long-horizon reasoning.

---

### 12. Less Experts, Faster Decoding: Cost-Aware Speculative Decoding for Mixture-of-Experts
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-14
* **Source URL:** [http://arxiv.org/abs/2607.12696v1](http://arxiv.org/abs/2607.12696v1)
* **Authors:** Jincheng Xie, Runheng Liu, Heyan Huang, Yawen Ling, Hanbin Dai et al.
* **Detected Affiliations/Keywords:** Deepseek, Qwen

**Abstract/Summary:**
> Sparse Mixture-of-Experts (MoE) models have become an important approach for scaling Large Language Models (LLMs), but their inference efficiency depends strongly on expert activation patterns. Speculative decoding (SD) accelerates autoregressive generation by verifying multiple draft tokens in parallel, yet existing draft selection strategies primarily optimize acceptance likelihood. In large-scale MoE models, however, selecting draft tokens also determines the union of experts activated during verification. We observe that confidence-driven SD can introduce \textit{expert scattering}: high-probability draft tokens may route to disjoint experts, increasing expert-weight memory traffic and reducing the speedup from speculation. Motivated by this observation, we revisit draft-tree selection under the non-uniform memory-cost structure of MoE inference. We propose \textsc{EcoSpec}, a cost-aware speculative decoding framework that incorporates predicted marginal expert activation cost into draft selection. With a lightweight expert predictor and a dynamic expert buffer, \textsc{EcoSpec} favors draft paths that preserve high acceptance likelihood while reusing experts already covered by the current verification set, without modifying the target-model verification rule. We evaluate \textsc{EcoSpec} on three large-scale MoE models, including DeepSeek-V3.1 (671B), Qwen3-235B-A22B, and GPT-OSS-120B, across reasoning, coding, question-answering, and dialogue benchmarks. \textsc{EcoSpec} consistently reduces active expert footprints and improves end-to-end decoding speed, achieving up to $1.62\times$ speedup. These results show that accounting for expert activation cost is important for efficient speculative decoding in large-scale MoE models.

---

### 13. WaterMoE: Expert-Routing-based Watermarking for High Fidelity and Efficiency
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-14
* **Source URL:** [http://arxiv.org/abs/2607.13099v1](http://arxiv.org/abs/2607.13099v1)
* **Authors:** Z Sun, Q Jiang, S Sheng, L Xiang

**Abstract/Summary:**
> Large language models (LLMs) have achieved remarkable success but raise growing concerns about content provenance and misuse, motivating the need for reliable watermarking techniques. However, these techniques have rarely been adopted in practice mainly for two reasons: i) severely degraded model performance, and ii) additional inference overhead. To confirm the problem, we construct a comprehensive benchmark spanning different generation tasks to systematically evaluate 9 representative watermarking methods. We found almost all existing methods are designed for text fluency, but not for restricted and complicated tasks, and their overhead prevents them from deployment in latency-critical systems. To address i) and ii), we propose an LLM watermarking scheme \textit{WaterMoE} for the growingly popular Mixture-of-Experts (MoE) LLMs. WaterMoE embeds watermarking signals through controlled perturbation into the expert selection at each router, which accumulates to token selection shift at the final output. In contrast to watermarking as a post-processing token-sampling approach, WaterMoE embeds watermark within the inference loop incurring negligible quality degradation and computational overhead. Extensive experiments demonstrate that our method achieves a fidelity performance close to the unwatermarked and consistently outperforms state-of-the-art watermarking methods on the benchmark, with up to $4\times$ speedup, incurring merely 1\% additional inference latency compared to native generation. The results demonstrate the capability of WaterMoE to be deployed in real-world tasks.

---

### 14. Full-Pipeline Inference Optimization for MiMo-V2.5 Series: Pushing Hybrid SWA Efficiency to the Limit
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-14
* **Source URL:** [http://arxiv.org/abs/2607.13095v1](http://arxiv.org/abs/2607.13095v1)
* **Authors:** Xiaomi MiMo Team, Anqi Liu, Aoxin Ma, Bo Chen, Bo Yang et al.

**Abstract/Summary:**
> We present a full-pipeline inference optimization for the MiMo-V2.5 model family, which combines Hybrid Sliding Window Attention (Hybrid SWA), sparse Mixture-of-Experts (MoE), and multimodal encoders. While Hybrid SWA can ideally reduce both attention compute and KVCache storage significantly compared to Full Attention, realizing these gains in production requires substantial engineering effort. We systematically optimize the KVCache system with layerwise prefetch, SWA-aware prefix cache trees, and specialized placement strategies, achieving strict $O(W)$ SWA storage and high cache hit rates. We further build GCache, a high-performance distributed cache infrastructure with RDMA-optimized networking, and develop a KVCache-affinity router to reduce computation while preserving load balancing. We also optimize for multimodal inputs, including GPU image preprocessing, parallel video decoding, and multimodal cache sharing. Together, these optimizations constitute the first large-scale LLM serving system in production that efficiently covers the Hybrid SWA + MoE + multimodal composite architecture.

---

### 15. Understanding Structured Health Data through Interaction-Aware Mixture-of-Experts
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-14
* **Source URL:** [http://arxiv.org/abs/2607.12255v1](http://arxiv.org/abs/2607.12255v1)
* **Authors:** Ji Hwan Park, Ying Ding, Tianjin Guo

**Abstract/Summary:**
> We study interaction-aware mixture-of-experts for post-stroke rigidity prediction using multi-level views of structured health records. Despite minimal performance gains, routing attribution reveals systematic importance differences across views, underscoring view construction as key to interpretability.

---

### 16. Mixture of Frames Policy: Multi-Frame Action Denoising for Bimanual Mobile Manipulation
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-13
* **Source URL:** [http://arxiv.org/abs/2607.11884v1](http://arxiv.org/abs/2607.11884v1)
* **Authors:** Dian Wang, Jisang Park, Xiaomeng Xu, Han Zhang, Shuran Song et al.

**Abstract/Summary:**
> Robotic manipulation is inherently multi-frame: local actions may be simple in an end-effector frame, while transport, upright-object handling, and whole-body coordination are better represented in a base-aligned frame. However, modern diffusion-based visuomotor policies typically commit to a single predefined action frame, forcing one denoiser to model action distributions that are often unnecessarily complex in that frame. We propose Mixture of Frames Policy (MoF), a diffusion policy that performs synchronized action denoising across multiple coordinate frames. MoF maintains a single canonical diffusion state, re-expresses it in several task-relevant frames, applies frame-specialized denoisers, and fuses their noise predictions back in the canonical frame. To make this possible for intermediate noisy diffusion states, we introduce a column-based 6D rotation representation within an SE(3) action parameterization that supports exact, differentiable frame transformations without requiring noisy rotations to lie on the SO(3) manifold. Across nine simulated bimanual manipulation tasks, we show that the best action frame is task-dependent and that MoF improves over oracle frame selection and standard Mixture-of-Experts (MoE) baselines. We further evaluate MoF on two real-world bimanual mobile manipulation tasks, demonstrating that it outperforms all constituent single-frame baselines. Project homepage: https://mofpo.github.io

---

### 17. HCRMap: Pressure-Aware Hot-Expert Residency Mapping for 3.5D MoE Chiplet Inference
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-13
* **Source URL:** [http://arxiv.org/abs/2607.11586v1](http://arxiv.org/abs/2607.11586v1)
* **Authors:** Yongqin Zhang
* **Detected Affiliations/Keywords:** Cas

**Abstract/Summary:**
> Mixture-of-Experts (MoE) large language models (LLM) activate only a small number of experts during inference, but token routing introduces persistent expert hotness skew: a small set of hot experts continuously receives most tokens, while the remaining experts are lightly loaded. On 3.5D multi-chiplet systems, this skew not only causes compute imbalance but also amplifies pressure on communication, memory bandwidth, I/O, and execution queues. Therefore, the core problem is not simply to reduce token movement, but to dynamically place and reuse hot expert replicas across different memory tiers. This paper proposes HCRMap, a hot expert residency mapping framework for pressure-aware expert replica management in 3.5D MoE inference. Based on expert hotness, weight loading cost, migration overhead, and runtime resource pressure, HCRMap dynamically determines which experts should be promoted, retained, demoted, or evicted. It then maps routed token groups to suitable resident replicas, thereby jointly mitigating communication, memory, and queue bottlenecks. Experimental results show that HCRMap reduces end-to-end latency by 43.6% and 43.0% over Hydra in the prefill and decode stages, respectively; by 34.5% and 33.1% over MoEntwine; and by 46.7% and 46.0% over PIMoE.

---

### 18. UMoE:Unlocking Every Expert in Domain-Specific Training
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-13
* **Source URL:** [http://arxiv.org/abs/2607.11444v1](http://arxiv.org/abs/2607.11444v1)
* **Authors:** Xuefeng Li, Pengfei Liu
* **Detected Affiliations/Keywords:** Qwen

**Abstract/Summary:**
> Mixture-of-Experts (MoE) models scale capacity without proportional compute cost and have become a key architecture for frontier large language models (LLMs). Yet domain-specific post-training inherits an expert pool shaped by mixed-domain pre-training: a substantial subset of experts contributes little on the target domain, and standard supervised fine-tuning (SFT) leaves the composition of this pool unchanged. We propose a simple, budget-preserving pipeline that realigns the expert pool to the target domain before fine-tuning. Given a target domain, we (1) prune the experts with lowest domain-aligned saliency, (2) regrow the expert pool to its original size through perturbation-based expert expansion, and (3) apply standard SFT. The resulting model preserves the original expert count, parameter count, and inference cost. With a single frozen recipe and no per-domain hyperparameter tuning, UMoE consistently improves over direct sft across two MoE architectures (Qwen3-30B-A3B and Qwen3.5-35B-A3B), five domains (math, code, science, tool-use, and agentic coding), and 12 benchmarks. Representative improvements are 3.4 points in math average accuracy, 6.0 points on SWE-bench Verified. On a strong in-house math corpus, direct sft already surpasses Qwen3-30B-A3B-Thinking (82.81 vs.\ 81.06), yet UMoE further raises the average to 84.17, an additional 1.36 points, demonstrating robustness to a substantially stronger SFT regime. Data-scaling experiments further show that the gain persists as training data grows. Analysis reveals that the direct-SFT model allocates substantial routed-expert compute to a low-saliency subset that can be removed post hoc with little average degradation; UMoE turns this redundant capacity into useful domain capacity and achieves lower training loss, with gains spanning all difficulty levels in downstream evaluation.

---

### 19. Weight-Adjusted Gradients Reveal Parameter Importance and Failure Modes in LLMs
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-12
* **Source URL:** [http://arxiv.org/abs/2607.10803v1](http://arxiv.org/abs/2607.10803v1)
* **Authors:** Shrestha Datta, Hongfu Liu, Anshuman Chhabra

**Abstract/Summary:**
> Understanding which parameters are influential in Large Language Models (LLMs) is central to improving their efficiency, reliability, and interpretability. We introduce Weight-Adjusted Gradients (WAG), a simple yet effective approach for estimating parameter importance that explicitly captures the interaction between model weights and first-order gradient information and identifies parameters that disproportionately influence model behavior, such as those responsible for collapse phenomena in LLMs. Across a range of models and settings, we show that WAG surfaces a tiny but critical subset of parameters whose modification leads to dramatic degradation in performance, a failure mode that existing importance metrics overlook. These findings reveal a previously underexplored interplay between weights and gradients, suggesting that parameter importance cannot be fully understood through either signal alone. The surprising effectiveness of WAG points to fundamental structural properties of trained networks and motivates new open questions about the role of zeroth-order and first-order information in deep learning. We demonstrate the practical utility of WAG across multiple applications, including expert allocation in mixture-of-expert architectures, parameter-specific unlearning, mixed-precision quantization, and layer selection for knowledge editing. Our results position WAG as a unified approach for analyzing, debugging, and controlling LLMs, and opens new directions for principled model-level interpretation.

---

### 20. The Economics of AI Decoding Chips: Rebalancing Compute, Capacity, and Bandwidth for Efficient LLM Inference
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-10
* **Source URL:** [http://arxiv.org/abs/2607.13068v1](http://arxiv.org/abs/2607.13068v1)
* **Authors:** Michael J. Yuan, Ju Long
* **Detected Affiliations/Keywords:** Deepseek

**Abstract/Summary:**
> Every mainstream GPU is built compute-heavy and capacity-light: it pairs enormous arithmetic throughput with too little memory to hold a modern model. In contrast, large language model decoding requires little compute and a large amount of memory: a GPU's floating-point units run at single-digit-percent utilization during decoding, and the memory the workload does need is sold only bundled with yet more compute. The compute is recovered only at hyperscale, where Mixture-of-Experts (MoE) models are spread across 96--320-GPU expert-parallel clusters serving thousands of concurrent users, a scale available to a handful of operators. We formalize the inefficiency with two fixed per-chip constants. F/B, the roofline ridge point, determines whether the compute can be utilized; F/S, the compute bundled with each GB of memory, determines how much compute must be bought. We then argue for a rebalanced decode accelerator: less compute, far more commodity memory, and a deliberately lower and cheaper bandwidth. The Skymizer HTX-301, a purpose-built 28nm PCIe accelerator using commodity DDR5, occupies that design point. Its entry cost is low. A single eight-chip card holds DeepSeek-R1 671B for about \$19,000, and a 4U server of four four-chip cards serves two users at a deterministic 20.3 tokens per second each for about \$28,000. Either costs less than a single H100, while the minimum GPU deployment for the model is an eight-GPU node near \$350,000. Concurrency then scales out by adding hardware: eight 4U servers carry sixteen users for about \$224,000, two-thirds of the node's price, with the cost per token unchanged at about \$12 per million against the node's \$21. The HTX-301's decisive advantage is a supply chain free of every rationed input: it uses no high-bandwidth memory, no CoWoS, and no leading-edge logic.

---

### 21. What VGGT Knows About Overlap: Probing Geometric Foundation Models for Co-Visibility
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-10
* **Source URL:** [http://arxiv.org/abs/2607.09503v1](http://arxiv.org/abs/2607.09503v1)
* **Authors:** Filippo Ziliotto, Luciano Serafini, Lamberto Ballan, Tommaso Campari

**Abstract/Summary:**
> A fundamental challenge in 3D reconstruction and robotic localization is co-visibility: determining which image pairs share overlapping visible surfaces, particularly in scenarios with minimal overlap. We demonstrate that VGGT implicitly encodes co-visibility as an emergent behavior: without any supervision for this task, its internal representations exhibit a clear hierarchical structure mirroring that of large language models, i.e. early layers build a 3D-aware scene representation, while late layers act as dedicated co-visibility reasoners. In particular, we identify layer L17 as a negative anchor that consistently routes non-co-visible pairs for this backbone, regardless of the evaluation setting, providing task-grounded evidence of layer specialization in a geometry-grounded foundation model. Building on this, we introduce Co-VGGT, which freezes VGGT and trains only a lightweight layer-wise mixture-of-experts head (less than 7.5M parameters) to classify co-visibility from RGB alone, treating each layer as a specialized expert whose geometric abstraction is adaptively weighted per input pair. On the Co-VisiON benchmark, Co-VGGT surpasses the human annotation baseline and improves over prior work by more than 25% pairwise and 10% multiview. Pairwise predictions are well-calibrated (ECE=0.030), enabling direct use as edge weights in visibility graphs for downstream SfM and SLAM pipelines without post-hoc correction. Code and data are available.

---

### 22. A Sovereign, Open-Source Foundation Model for German and English
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-10
* **Source URL:** [http://arxiv.org/abs/2607.09424v2](http://arxiv.org/abs/2607.09424v2)
* **Authors:** The Soofi-Team, :, Benedikt Droste, David Fitzek, Ruben Härle et al.

**Abstract/Summary:**
> We present Soofi S 30B-A3B, a sovereign, open-source Mixture-of-Experts (MoE) hybrid Mamba Transformer foundation model for German and English. Its hybrid design activates only 3B of 30B parameters per token and keeps the inference cache near-constant as context grows, giving it a decisive throughput advantage over dense models for long-context, high-concurrency deployment. Pretrained on roughly 27 trillion tokens with deliberately up-weighted German, Soofi S matches dense 14 to 27B models on aggregate English and German benchmarks while achieving the best code aggregates in both languages among 17 open base models, and outperforms every European sovereign baseline in our comparison, including ones far larger in active parameters. Among fully open models, Soofi S obtains the highest English and German evaluation scores, ahead of Olmo 3 32B and Apertus 70B. Soofi S was built end-to-end on the German Industrial AI Cloud, a sovereign HPC scale AI infrastructure operated by Deutsche Telekom in Munich. Soofi S will be released under highly permissive, open-access terms: weights, selected intermediate checkpoints, full per-source data accounting, hyperparameters, and training and evaluation code. Where source licenses permit, data-construction artifacts are released under permissive licenses; commercially licensed sources are documented with aggregate statistics and exact mixture accounting.

---

### 23. Mach-Mind-4-Flash Technical Report
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-10
* **Source URL:** [http://arxiv.org/abs/2607.09375v1](http://arxiv.org/abs/2607.09375v1)
* **Authors:** Foundation Model Team

**Abstract/Summary:**
> We present Mach-Mind-4-Flash, a 35B-parameter Mixture-of-Experts (MoE) agentic model with 3B activated parameters. Through post-training optimization alone without scaling pre-training compute, the model achieves performance on par with or surpassing that of 100B-parameter-class models. By introducing scalable agentic interaction environments for large-scale reinforcement learning, the model attains significant performance gains on real-world application tasks. Our pipeline comprises three stages: (1) a unified RL/OPD training infrastructure with dynamic multi-teacher scheduling and operator-level acceleration, delivering 17\% end-to-end training speedup; (2) multiple domain-specific RL experts trained in parallel across Reasoning, General, and Agent tracks, then fused into a single generalist via Multi-Teacher On-Policy Distillation (MOPD) -- a routed reverse-KL objective that eliminates the see-saw degradation of mixed-reward RL; (3) Hybrid Median-length Policy Optimization (HMPO), a single-stage token-efficiency method that compresses reasoning chains by 19--46\% with $\le$0.7 percentage-point accuracy loss. Mach-Mind-4-Flash scores 92.70 on AIME'26, 82.82 on IFBench, 80.74 on Behavioral-SafetyBench, 75.80 on BFCL-v4, 72.31 on BrowseComp-zh, and 84.20 on ClawBench -- leading or matching models with 10--30$\times$ its activated size at a fraction of the inference cost.

---

### 24. Multimodal Digital Biomarker for Asthma: Complementary Roles of Vocal, Clinical and Demographic Factors
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-09
* **Source URL:** [http://arxiv.org/abs/2607.08714v1](http://arxiv.org/abs/2607.08714v1)
* **Authors:** Vladimir Despotovic, Milena Despotovic, Abir Elbeji, Petr V. Nazarov, Guy Fagherazzi
* **Detected Affiliations/Keywords:** Cas

**Abstract/Summary:**
> Asthma affects over 260 million people worldwide, yet diagnosis remains dependent on spirometry and specialist assessment, limiting accessibility in primary care and low-resource settings. Vocal biomarkers offer a promising non-invasive alternative, but prior studies have largely focused on acoustic features without integrating clinical context. We present a multimodal Mixture-of-Experts framework for asthma detection that adaptively combines acoustic embeddings from sustained vowel phonation and reading passage tasks with structured clinical and demographic data. The model was evaluated on a matched cohort of 1,218 asthma cases and healthy controls from the Colive Voice study. The multimodal model achieved an AUROC of 0.85 and Brier score of 0.17, outperforming unimodal and bimodal approaches. Adaptive gating analysis revealed increased reliance on audio features in participants with greater respiratory symptom burden, whereas clinical features contributed more strongly in less symptomatic individuals. These findings support scalable and explainable asthma screening using smartphone-collected voice recordings.

---

### 25. It Takes a MAESTRO To Prune Bad Experts
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-09
* **Source URL:** [http://arxiv.org/abs/2607.08601v1](http://arxiv.org/abs/2607.08601v1)
* **Authors:** Palaash Goel, Ayush Maheshwari, Tanmoy Chakraborty

**Abstract/Summary:**
> Sparsely-activated Mixture-of-Experts (MoE) language models achieve remarkable inference efficiency by activating only a small fraction of parameters per token, yet their full expert banks reside in memory at all times, creating a prohibitive deployment bottleneck. Existing structured pruning methods, largely designed for dense transformers, assess expert importance using locally derived heuristics that are blind to the interdependent nature of MoE routing. We introduce MAESTRO (Markov-chain Approximated Expert Sparsification via Transition-based ROuting), a structured pruning framework designed for MoE architectures that models autoregressive expert activation trajectories as Ergodic Markov chains whose stationary distributions encode cross-layer dependencies, yielding a globally aware importance heuristic. Evaluated across five diverse domains including Safety, Bias, and Ethics, MAESTRO outperforms state-of-the-art baselines by up to 10.61% in average performance retention under a strict 50% compression regime, while exhibiting substantially lower cross-task variance, indicating that global, routing-congruent pruning produces models that generalize more consistently across heterogeneous tasks.

---

### 26. On the Design of Mixture-of-Experts for Dynamic Gaussian Splatting
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-09
* **Source URL:** [http://arxiv.org/abs/2607.08250v2](http://arxiv.org/abs/2607.08250v2)
* **Authors:** In-Hwan Jin, Hyeongju Mun, Joonsoo Kim, Kugjin Yun, Kyeongbo Kong

**Abstract/Summary:**
> Dynamic scene reconstruction remains challenging due to the heterogeneous and spatially varying nature of real-world motion. Although recent 3D Gaussian Splatting methods have introduced diverse deformation formulations for dynamic novel view synthesis, each method typically relies on a single deformation model within its representation, which limits robustness across diverse dynamic scenarios. In this work, we study a fundamental problem-multi-deformation modeling for dynamic 3D Gaussian representations-under two distinct integration constraints that differ in when and how multiple deformation experts interact during training. From a Mixture-of-Experts (MoE) perspective, we view multi-deformation modeling as the problem of combining multiple specialized deformation models within a unified 3D representation. We first introduce Mixture of Deformation Experts (MoDE), which integrates multiple deformation experts directly into the deformable Gaussian Splatting pipeline through joint optimization. In MoDE, experts operate on a shared canonical Gaussian representation, enabling multi-deformation modeling without introducing additional training stages or modifying the original optimization schedule. In contrast, we further present Mixture of Experts for Dynamic Gaussian Splatting (MoE-GS) under a different integration constraint, where deformation experts are optimized independently and combined through a separate routing stage. As a result, expert interaction occurs over non-canonical Gaussian representations after individual optimization. Together, these two approaches provide alternative strategies for multi-deformation modeling, clarifying how integration constraints shape the design and behavior of deformation experts in dynamic 3D Gaussian representations. Our code is available at: https://github.com/cvsp-lab/MoE-GS-studio.

---

### 27. MORES: Mobile Reasoning-as-a-Service via Distributed LLM Inference-Time Scaling
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-09
* **Source URL:** [http://arxiv.org/abs/2607.08116v1](http://arxiv.org/abs/2607.08116v1)
* **Authors:** Guanchen Liu, Hongyang Du, Kaibin Huang

**Abstract/Summary:**
> Inference-time scaling has emerged as an effective approach for enhancing the capabilities of Large Language Models (LLMs), addressing the growing demand for stronger reasoning without increasing model size. This novel form of LLM scaling comprises two representative approaches: explicit reasoning, which generates intermediate chain-of-thought tokens during an explicit thinking phase, and implicit reasoning, which iteratively updates hidden states in the latent space without producing explicit outputs. Despite their effectiveness, both paradigms incur substantial computational and memory overhead, raising challenges for deployment on resource-constrained edge devices. To address these issues, we propose a Mobile Reasoning-as-aService (MORES) framework that treats reasoning as a computational service accessible to edge devices over wireless networks. Focusing on implicit reasoning, we leverage its recursive structure to partition hiddenstate updates between edge devices and servers, enabling cooperative inference that allows devices to access additional cloud computation on demand. To optimize long-term performance, we formulate a joint computation and communication scheduling problem and solve it using a semantic Mixture-of-Experts (MoE)-based Deep Reinforcement Learning (DRL) algorithm to address heterogeneity in wireless conditions and task demands. The agent adaptively allocates resources by adjusting the number of recurrent steps and the transmission pruning rate, while a semantic router enables high-speed gating for real-time expert selection. Experimental results show that the proposed method achieves an approximately 18% improvement in system throughput over the baseline Soft Actor-Critic (SAC) algorithm. Our code is available at https://github.com/NICE-HKU/MORES.

---

### 28. When LLMs Agree, Are They Right? Auditing Self-Consistency and Cross-Model Agreement as Confidence Signals
* **Status/Tag:** 🔴 [CHINESE LAB CONTRIBUTION]
* **Published Date:** 2026-07-09
* **Source URL:** [http://arxiv.org/abs/2607.08065v1](http://arxiv.org/abs/2607.08065v1)
* **Authors:** Kaihua Ding
* **Detected Affiliations/Keywords:** Cas

**Abstract/Summary:**
> LLM-as-judge (Zheng et al., 2023) is increasingly the default for evaluating AI systems in enterprise pipelines, often scaled to ensembles (Verga et al., 2024) or "mixture-of-experts" (Shazeer et al., 2017) panels of judges. These systems share a key assumption: that consistency -- agreement among judges, or among a model's own samples -- indicates correctness. We show this assumption is unreliable. Agreement is not accuracy: a model can agree with itself, and different models can agree with each other, out of shared bias, a memorized heuristic, or an option-position prior rather than truth. We ask when agreement is nonetheless a usable proxy, in a large-scale cross-runner study: 53 runners drew K=50 samples for assigned overlapping cases across comparisons of model tier, prompting, and scale on GPQA Diamond and AIME -- 265,000 samples. Using majority-correctness as the deployment label and a hierarchical runner-clustered bootstrap, agreement is a positive but weak predictor (rho 0.20-0.59, all positive under item-clustered resampling) whose usefulness is regime-dependent: best for unsaturated mid-tier models and for allocating compute, and worst -- over-confident yet no more accurate -- for the most consistent frontier model (agreement >=0.8 on 77% of GPQA case-result entries, 48% of those wrong). An exploratory cross-family check on three Claude tiers shows the same frontier over-confidence, with confident errors recurring across providers above a marginal-preserving null. Self-consistency is thus a conditional proxy for correctness, not a standalone confidence score. We publicly release the de-identified per-run rows and answer distributions.

---

### 29. Scaling Mixture-of-Experts Video Pretraining for Embodied Intelligence
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-08
* **Source URL:** [http://arxiv.org/abs/2607.07675v1](http://arxiv.org/abs/2607.07675v1)
* **Authors:** Shuailei Ma, Jiaqi Liao, Xinyang Wang, Jingjing Wang, Chaoran Feng et al.

**Abstract/Summary:**
> Despite the recent promise in robot control, video generative models suffer from a domain mismatch due to their primary focus on content creation. For example, their design inherently prioritizes visual fidelity and creativity over computational efficiency and physical realism. In this work, we present LingBot-Video, a DiT-based video pretraining paradigm specifically tailored for embodied intelligence. From the architecture perspective, we adopt the Mixture-of-Experts (MoE), instead of dense, framework to achieve a better trade-off between modeling capacity and inference efficiency, and manage to scale it up from scratch. From the data perspective, we construct a data profiling engine that augments standard internet videos with extensive robot-oriented footage, encompassing manipulation, navigation, and egocentric perspectives, to equip the base model with an intrinsic understanding of actions and world dynamics. From the training perspective, we develop a multi-dimensional reward system to enforce the alignment regarding physical rationality and task completion, going beyond standard criteria such as aesthetics, prompt-following, and motion consistency. Comprehensive evaluations validate its performance and efficiency as a video foundation model. We contribute LingBot-Video as the inaugural large-scale, open-source MoE video foundation model to the community, in a pioneering effort to bridge digital creativity and physical actuation.

---

### 30. Image classification via a quantum-inspired strategy involving a mixture of experts
* **Status/Tag:** 🔵 [GLOBAL RESEARCH]
* **Published Date:** 2026-07-08
* **Source URL:** [http://arxiv.org/abs/2607.07754v1](http://arxiv.org/abs/2607.07754v1)
* **Authors:** Kumari Jyoti, Rohith Babu, Apoorva D. Patel

**Abstract/Summary:**
> Pattern recognition problems arise in a variety of physical image processing situations, and convolutional neural networks are a popular scheme for the required feature extraction and classification tasks. The classical networks use diffusion-based smearing and block-wise pooling to downsample the image data and capture important structural features. In this work, we propose and demonstrate a more efficient quantum-inspired strategy involving a mixture of experts. It is a hybrid classical-quantum framework. The quantum part consists of amplitude encoding of the images, convolution using local unitary operations, multiple experts processing the same image with different parameters, and feature extraction using quantum stabiliser codes. The classical part then jointly processes the features extracted by different experts using a standard fully connected neural network for image class prediction. Using MNIST and Fashion-MNIST datasets as benchmarks, we demonstrate that the joint expert analysis outperforms the individual expert one, as well as reduces the failure rate of image class prediction by around a factor of two. The overhead of our quantum-inspired strategy is only moderate on GPU workstations, which makes our proposal a practical alternative to existing classical schemes. We also point out how the quantum part of our framework can be executed on a quantum processor.

---

## 3. Crawler Telemetry & Metrics
* **Total Papers Scraped:** 30
* **Chinese Lab Affiliations Identified:** 8 (26.67%)
* **Data Sources Query String:** `all:"mixture of experts"` sorted by submission date.
* **Storage Footprint:** Saved in `/data/.openclaw/workspace/harvested_research/hypatia_moe_research.md`
