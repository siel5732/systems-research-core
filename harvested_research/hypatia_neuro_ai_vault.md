# 🧠 Hypatia Computational Neuroscience & Neuro-Inspired AI Vault
**Compiled On:** 2026-07-18 00:40:41  
**Core Target**: Biologically plausible learning, predictive coding, spiking networks, and cognitive brain simulations.

---

## I. Leading Global Institutions & Laboratories (Standout Centers)
These departments are leading the translation of pure neurobiology and cognitive psychology into computational architectures:

1. **Gatsby Computational Neuroscience Unit (University College London - UCL)**
   * *Core Focus*: Active Inference, predictive coding, and the mathematical foundations of biological intelligence (pioneered by Karl Friston and Peter Dayan).
2. **Kempner Institute for Natural & Artificial Intelligence (Harvard University)**
   * *Core Focus*: Mathematical models that unify biological and artificial neural computation, studying how synaptic plasticity and cortical circuit wiring produce high-order reasoning.
3. **Centre for Theoretical Neuroscience (University of Waterloo)**
   * *Core Focus*: Large-scale brain models (Spaun - Semantic Pointer Architecture Unified Network) that utilize the Neural Engineering Framework (NEF) to simulate biological neurons executing functional tasks.
4. **McGovern Institute for Brain Research & DiCarlo Lab (MIT)**
   * *Core Focus*: Utilizing deep convolutional networks to model the visual ventral stream; developers of the "Brain-Score" benchmarks comparing artificial weights to primate cortical firing data.
5. **Yamins Lab (Stanford University)**
   * *Core Focus*: Sensory computational neuroscience, training deep neural models to mirror auditory and visual sensory processing structures in biological systems.
6. **Mila / University of Montreal (Yoshua Bengio's Cognitive AI Lab)**
   * *Core Focus*: Bridging biological synaptic plasticity with artificial backpropagation alternatives (e.g., Equilibrium Propagation, target propagation, and credit assignment in the brain).

---

## II. Harvested Academic Literature

### 1. A Study of Biologically Plausible Neural Network: The Role and Interactions of Brain-Inspired Mechanisms in Continual Learning
* **Authors:** Fahad Sarfraz, Elahe Arani, Bahram Zonooz  
* **Published Date:** 2023-04-13  
* **Document URL:** [https://arxiv.org/pdf/2304.06738v1](https://arxiv.org/pdf/2304.06738v1)  

**Abstract:**
Humans excel at continually acquiring, consolidating, and retaining information from an ever-changing environment, whereas artificial neural networks (ANNs) exhibit catastrophic forgetting. There are considerable differences in the complexity of synapses, the processing of information, and the learning mechanisms in biological neural networks and their artificial counterparts, which may explain the mismatch in performance. We consider a biologically plausible framework that constitutes separate populations of exclusively excitatory and inhibitory neurons that adhere to Dale's principle, and the excitatory pyramidal neurons are augmented with dendritic-like structures for context-dependent processing of stimuli. We then conduct a comprehensive study on the role and interactions of different mechanisms inspired by the brain, including sparse non-overlapping representations, Hebbian learning, synaptic consolidation, and replay of past activations that accompanied the learning event. Our study suggests that the employing of multiple complementary mechanisms in a biologically plausible architecture, similar to the brain, may be effective in enabling continual learning in ANNs.

---

### 2. The Influence of Initial Connectivity on Biologically Plausible Learning
* **Authors:** Weixuan Liu, Xinyue Zhang, Yuhan Helena Liu  
* **Published Date:** 2024-10-15  
* **Document URL:** [https://arxiv.org/pdf/2410.11164v3](https://arxiv.org/pdf/2410.11164v3)  

**Abstract:**
Understanding how the brain learns can be advanced by investigating biologically plausible learning rules -- those that obey known biological constraints, such as locality, to serve as valid brain learning models. Yet, many studies overlook the role of architecture and initial synaptic connectivity in such models. Building on insights from deep learning, where initialization profoundly affects learning dynamics, we ask a key but underexplored neuroscience question: how does initial synaptic connectivity shape learning in neural circuits? To investigate this, we train recurrent neural networks (RNNs), which are widely used for brain modeling, with biologically plausible learning rules. Our findings reveal that initial weight magnitude significantly influences the learning performance of such rules, mirroring effects previously observed in training with backpropagation through time (BPTT). By examining the maximum Lyapunov exponent before and after training, we uncovered the greater demands that certain initialization schemes place on training to achieve desired information propagation properties. Consequently, we extended the recently proposed gradient flossing method, which regularizes the Lyapunov exponents, to biologically plausible learning and observed an improvement in learning performance. To our knowledge, we are the first to examine the impact of initialization on biologically plausible learning rules for RNNs and to subsequently propose a biologically plausible remedy. Such an investigation can lead to neuroscientific predictions about the influence of initial connectivity on learning dynamics and performance, as well as guide neuromorphic design.

---

### 3. Counter-Current Learning: A Biologically Plausible Dual Network Approach for Deep Learning
* **Authors:** Chia-Hsiang Kao, Bharath Hariharan  
* **Published Date:** 2024-09-30  
* **Document URL:** [https://arxiv.org/pdf/2409.19841v2](https://arxiv.org/pdf/2409.19841v2)  

**Abstract:**
Despite its widespread use in neural networks, error backpropagation has faced criticism for its lack of biological plausibility, suffering from issues such as the backward locking problem and the weight transport problem. These limitations have motivated researchers to explore more biologically plausible learning algorithms that could potentially shed light on how biological neural systems adapt and learn. Inspired by the counter-current exchange mechanisms observed in biological systems, we propose counter-current learning (CCL), a biologically plausible framework for credit assignment in neural networks. This framework employs a feedforward network to process input data and a feedback network to process targets, with each network enhancing the other through anti-parallel signal propagation. By leveraging the more informative signals from the bottom layer of the feedback network to guide the updates of the top layer of the feedforward network and vice versa, CCL enables the simultaneous transformation of source inputs to target outputs and the dynamic mutual influence of these transformations. Experimental results on MNIST, FashionMNIST, CIFAR10, and CIFAR100 datasets using multi-layer perceptrons and convolutional neural networks demonstrate that CCL achieves comparable performance to other biologically plausible algorithms while offering a more biologically realistic learning mechanism. Furthermore, we showcase the applicability of our approach to an autoencoder task, underscoring its potential for unsupervised representation learning. Our work presents a direction for biologically inspired and plausible learning algorithms, offering an alternative mechanism of learning and adaptation in neural networks.

---

### 4. Biologically-plausible learning algorithms can scale to large datasets
* **Authors:** Will Xiao, Honglin Chen, Qianli Liao, Tomaso Poggio  
* **Published Date:** 2018-11-08  
* **Document URL:** [https://arxiv.org/pdf/1811.03567v3](https://arxiv.org/pdf/1811.03567v3)  

**Abstract:**
The backpropagation (BP) algorithm is often thought to be biologically implausible in the brain. One of the main reasons is that BP requires symmetric weight matrices in the feedforward and feedback pathways. To address this "weight transport problem" (Grossberg, 1987), two more biologically plausible algorithms, proposed by Liao et al. (2016) and Lillicrap et al. (2016), relax BP's weight symmetry requirements and demonstrate comparable learning capabilities to that of BP on small datasets. However, a recent study by Bartunov et al. (2018) evaluate variants of target-propagation (TP) and feedback alignment (FA) on MINIST, CIFAR, and ImageNet datasets, and find that although many of the proposed algorithms perform well on MNIST and CIFAR, they perform significantly worse than BP on ImageNet. Here, we additionally evaluate the sign-symmetry algorithm (Liao et al., 2016), which differs from both BP and FA in that the feedback and feedforward weights share signs but not magnitudes. We examine the performance of sign-symmetry and feedback alignment on ImageNet and MS COCO datasets using different network architectures (ResNet-18 and AlexNet for ImageNet, RetinaNet for MS COCO). Surprisingly, networks trained with sign-symmetry can attain classification performance approaching that of BP-trained networks. These results complement the study by Bartunov et al. (2018), and establish a new benchmark for future biologically plausible learning algorithms on more difficult datasets and more complex architectures.

---

### 5. Biologically plausible deep learning -- but how far can we go with shallow networks?
* **Authors:** Bernd Illing, Wulfram Gerstner, Johanni Brea  
* **Published Date:** 2019-02-27  
* **Document URL:** [https://arxiv.org/pdf/1905.04101v2](https://arxiv.org/pdf/1905.04101v2)  

**Abstract:**
Training deep neural networks with the error backpropagation algorithm is considered implausible from a biological perspective. Numerous recent publications suggest elaborate models for biologically plausible variants of deep learning, typically defining success as reaching around 98% test accuracy on the MNIST data set. Here, we investigate how far we can go on digit (MNIST) and object (CIFAR10) classification with biologically plausible, local learning rules in a network with one hidden layer and a single readout layer. The hidden layer weights are either fixed (random or random Gabor filters) or trained with unsupervised methods (PCA, ICA or Sparse Coding) that can be implemented by local learning rules. The readout layer is trained with a supervised, local learning rule. We first implement these models with rate neurons. This comparison reveals, first, that unsupervised learning does not lead to better performance than fixed random projections or Gabor filters for large hidden layers. Second, networks with localized receptive fields perform significantly better than networks with all-to-all connectivity and can reach backpropagation performance on MNIST. We then implement two of the networks - fixed, localized, random & random Gabor filters in the hidden layer - with spiking leaky integrate-and-fire neurons and spike timing dependent plasticity to train the readout layer. These spiking models achieve > 98.2% test accuracy on MNIST, which is close to the performance of rate networks with one hidden layer trained with backpropagation. The performance of our shallow network models is comparable to most current biologically plausible models of deep learning. Furthermore, our results with a shallow spiking network provide an important reference and suggest the use of datasets other than MNIST for testing the performance of future models of biologically plausible deep learning.

---

### 6. Memory Networks: Towards Fully Biologically Plausible Learning
* **Authors:** Jacobo Ruiz, Manas Gupta  
* **Published Date:** 2024-09-18  
* **Document URL:** [https://arxiv.org/pdf/2409.17282v1](https://arxiv.org/pdf/2409.17282v1)  

**Abstract:**
The field of artificial intelligence faces significant challenges in achieving both biological plausibility and computational efficiency, particularly in visual learning tasks. Current artificial neural networks, such as convolutional neural networks, rely on techniques like backpropagation and weight sharing, which do not align with the brain's natural information processing methods. To address these issues, we propose the Memory Network, a model inspired by biological principles that avoids backpropagation and convolutions, and operates in a single pass. This approach enables rapid and efficient learning, mimicking the brain's ability to adapt quickly with minimal exposure to data. Our experiments demonstrate that the Memory Network achieves efficient and biologically plausible learning, showing strong performance on simpler datasets like MNIST. However, further refinement is needed for the model to handle more complex datasets such as CIFAR10, highlighting the need to develop new algorithms and techniques that closely align with biological processes while maintaining computational efficiency.

---

### 7. Kernelized information bottleneck leads to biologically plausible 3-factor Hebbian learning in deep networks
* **Authors:** Roman Pogodin, Peter E. Latham  
* **Published Date:** 2020-06-12  
* **Document URL:** [https://arxiv.org/pdf/2006.07123v2](https://arxiv.org/pdf/2006.07123v2)  

**Abstract:**
The state-of-the art machine learning approach to training deep neural networks, backpropagation, is implausible for real neural networks: neurons need to know their outgoing weights; training alternates between a bottom-up forward pass (computation) and a top-down backward pass (learning); and the algorithm often needs precise labels of many data points. Biologically plausible approximations to backpropagation, such as feedback alignment, solve the weight transport problem, but not the other two. Thus, fully biologically plausible learning rules have so far remained elusive. Here we present a family of learning rules that does not suffer from any of these problems. It is motivated by the information bottleneck principle (extended with kernel methods), in which networks learn to compress the input as much as possible without sacrificing prediction of the output. The resulting rules have a 3-factor Hebbian structure: they require pre- and post-synaptic firing rates and an error signal - the third factor - consisting of a global teaching signal and a layer-specific term, both available without a top-down pass. They do not require precise labels; instead, they rely on the similarity between pairs of desired outputs. Moreover, to obtain good performance on hard problems and retain biological plausibility, our rules need divisive normalization - a known feature of biological networks. Finally, simulations show that our rules perform nearly as well as backpropagation on image classification tasks.

---

### 8. Dendritic Localized Learning: Toward Biologically Plausible Algorithm
* **Authors:** Changze Lv, Jingwen Xu, Yiyang Lu, Xiaohua Wang, Zhenghua Wang, Zhibo Xu, Di Yu, Xin Du, Xiaoqing Zheng, Xuanjing Huang  
* **Published Date:** 2025-01-17  
* **Document URL:** [https://arxiv.org/pdf/2501.09976v2](https://arxiv.org/pdf/2501.09976v2)  

**Abstract:**
Backpropagation is the foundational algorithm for training neural networks and a key driver of deep learning's success. However, its biological plausibility has been challenged due to three primary limitations: weight symmetry, reliance on global error signals, and the dual-phase nature of training, as highlighted by the existing literature. Although various alternative learning approaches have been proposed to address these issues, most either fail to satisfy all three criteria simultaneously or yield suboptimal results. Inspired by the dynamics and plasticity of pyramidal neurons, we propose Dendritic Localized Learning (DLL), a novel learning algorithm designed to overcome these challenges. Extensive empirical experiments demonstrate that DLL satisfies all three criteria of biological plausibility while achieving state-of-the-art performance among algorithms that meet these requirements. Furthermore, DLL exhibits strong generalization across a range of architectures, including MLPs, CNNs, and RNNs. These results, benchmarked against existing biologically plausible learning algorithms, offer valuable empirical insights for future research. We hope this study can inspire the development of new biologically plausible algorithms for training multilayer networks and advancing progress in both neuroscience and machine learning. Our code is available at https://github.com/Lvchangze/Dendritic-Localized-Learning.

---

### 9. Predictive Coding as Stimulus Avoidance in Spiking Neural Networks
* **Authors:** Atsushi Masumori, Lana Sinapayen, Takashi Ikegami  
* **Published Date:** 2019-11-21  
* **Document URL:** [https://arxiv.org/pdf/1911.09230v1](https://arxiv.org/pdf/1911.09230v1)  

**Abstract:**
Predictive coding can be regarded as a function which reduces the error between an input signal and a top-down prediction. If reducing the error is equivalent to reducing the influence of stimuli from the environment, predictive coding can be regarded as stimulation avoidance by prediction. Our previous studies showed that action and selection for stimulation avoidance emerge in spiking neural networks through spike-timing dependent plasticity (STDP). In this study, we demonstrate that spiking neural networks with random structure spontaneously learn to predict temporal sequences of stimuli based solely on STDP.

---

### 10. Predictive Coding Graphs are a Superset of Feedforward Neural Networks
* **Authors:** Björn van Zwol  
* **Published Date:** 2026-03-06  
* **Document URL:** [https://arxiv.org/pdf/2603.06142v1](https://arxiv.org/pdf/2603.06142v1)  

**Abstract:**
Predictive coding graphs (PCGs) are a recently introduced generalization to predictive coding networks, a neuroscience-inspired probabilistic latent variable model. Here, we prove how PCGs define a mathematical superset of feedforward artificial neural networks (multilayer perceptrons). This positions PCNs more strongly within contemporary machine learning (ML), and reinforces earlier proposals to study the use of non-hierarchical neural networks for ML tasks, and more generally the notion of topology in neural networks.

---

### 11. Predictive Coding-based Deep Neural Network Fine-tuning for Computationally Efficient Domain Adaptation
* **Authors:** Matteo Cardoni, Sam Leroux  
* **Published Date:** 2025-09-24  
* **Document URL:** [https://arxiv.org/pdf/2509.20269v2](https://arxiv.org/pdf/2509.20269v2)  

**Abstract:**
As deep neural networks are increasingly deployed in dynamic, real-world environments, relying on a single static model is often insufficient. Changes in input data distributions caused by sensor drift or lighting variations necessitate continual model adaptation. In this paper, we propose a hybrid training methodology that enables efficient on-device domain adaptation by combining the strengths of Backpropagation and Predictive Coding. The method begins with a deep neural network trained offline using Backpropagation to achieve high initial performance. Subsequently, Predictive Coding is employed for online adaptation, allowing the model to recover accuracy lost due to shifts in the input data distribution. This approach leverages the robustness of Backpropagation for initial representation learning and the computational efficiency of Predictive Coding for continual learning, making it particularly well-suited for resource-constrained edge devices or future neuromorphic accelerators. Experimental results on the MNIST and CIFAR-10 datasets demonstrate that this hybrid strategy enables effective adaptation with a reduced computational overhead, offering a promising solution for maintaining model performance in dynamic environments.

---

### 12. Predictive Coding-based Deep Dynamic Neural Network for Visuomotor Learning
* **Authors:** Jungsik Hwang, Jinhyung Kim, Ahmadreza Ahmadi, Minkyu Choi, Jun Tani  
* **Published Date:** 2017-06-08  
* **Document URL:** [https://arxiv.org/pdf/1706.02444v1](https://arxiv.org/pdf/1706.02444v1)  

**Abstract:**
This study presents a dynamic neural network model based on the predictive coding framework for perceiving and predicting the dynamic visuo-proprioceptive patterns. In our previous study [1], we have shown that the deep dynamic neural network model was able to coordinate visual perception and action generation in a seamless manner. In the current study, we extended the previous model under the predictive coding framework to endow the model with a capability of perceiving and predicting dynamic visuo-proprioceptive patterns as well as a capability of inferring intention behind the perceived visuomotor information through minimizing prediction error. A set of synthetic experiments were conducted in which a robot learned to imitate the gestures of another robot in a simulation environment. The experimental results showed that with given intention states, the model was able to mentally simulate the possible incoming dynamic visuo-proprioceptive patterns in a top-down process without the inputs from the external environment. Moreover, the results highlighted the role of minimizing prediction error in inferring underlying intention of the perceived visuo-proprioceptive patterns, supporting the predictive coding account of the mirror neuron systems. The results also revealed that minimizing prediction error in one modality induced the recall of the corresponding representation of another modality acquired during the consolidative learning of raw-level visuo-proprioceptive patterns.

---

### 13. pyhgf: A neural network library for predictive coding
* **Authors:** Nicolas Legrand, Lilian Weber, Peter Thestrup Waade, Anna Hedvig Møller Daugaard, Mojtaba Khodadadi, Nace Mikuš, Chris Mathys  
* **Published Date:** 2024-10-11  
* **Document URL:** [https://arxiv.org/pdf/2410.09206v2](https://arxiv.org/pdf/2410.09206v2)  

**Abstract:**
Bayesian models of cognition have gained considerable traction in computational neuroscience and psychiatry. Their scopes are now expected to expand rapidly to artificial intelligence, providing general inference frameworks to support embodied, adaptable, and energy-efficient autonomous agents. A central theory in this domain is predictive coding, which posits that learning and behaviour are driven by hierarchical probabilistic inferences about the causes of sensory inputs. Biological realism constrains these networks to rely on simple local computations in the form of precision-weighted predictions and prediction errors. This can make this framework highly efficient, but its implementation comes with unique challenges on the software development side. Embedding such models in standard neural network libraries often becomes limiting, as these libraries' compilation and differentiation backends can force a conceptual separation between optimization algorithms and the systems being optimized. This critically departs from other biological principles such as self-monitoring, self-organisation, cellular growth and functional plasticity. In this paper, we introduce \texttt{pyhgf}: a Python package backed by JAX and Rust for creating, manipulating and sampling dynamic networks for predictive coding. We improve over other frameworks by enclosing the network components as transparent, modular and malleable variables in the message-passing steps. The resulting graphs can implement arbitrary computational complexities as beliefs propagation. But the transparency of core variables can also translate into inference processes that leverage self-organisation principles, and express structure learning, meta-learning or causal discovery as the consequence of network structural adaptation to surprising inputs. The code, tutorials and documentation are hosted at: https://github.com/ilabcode/pyhgf.

---

### 14. PC-SNN: Predictive Coding-based Local Hebbian Plasticity Learning in Spiking Neural Networks
* **Authors:** Haidong Wang, Xiaogang Xiong, Mengting Lan, Yinghao Chu, Zixuan Jiang, KC Santosh, Shimin Wang, Renxin Zhong  
* **Published Date:** 2022-11-24  
* **Document URL:** [https://arxiv.org/pdf/2211.15386v3](https://arxiv.org/pdf/2211.15386v3)  

**Abstract:**
Spiking Neural Networks (SNNs), regarded as the third generation of neural networks, emulate the brain's information processing with unparalleled biological plausibility compared to traditional neural networks. However, their non-linear, event-driven dynamics pose significant challenges for training, and existing methods often deviate from neuroscientific principles of cortical learning. Drawing inspiration from predictive coding theory-a leading model of brain information processing-we propose PC-SNN, a novel learning framework that integrates predictive coding with SNNs to enable biologically plausible, local Hebbian plasticity without reliance on backpropagation. Unlike conventional SNN training approaches, PC-SNN leverages only local computations, aligning with the brain's distributed processing and overcoming the biological implausibility of global error propagation. Our classification model achieves competitive performance on the benchmark datasets, including Caltech Face/Motorbike, MNIST, and CIFAR10, surpassing state-of-the-art multi-layer SNNs. Furthermore, our predictive coding-based regression model outperforms backpropagation-based methods while adhering to local plasticity constraints, offering a scalable and biologically grounded alternative for SNN training. PC-SNN drives progress in neuromorphic computing through validating the adaptability of bio-inspired algorithms within spiking neural architectures, but also unveils novel understandings of neurocognitive learning processes, presenting a conceptual framework distinguished by its theoretical originality and functional efficacy.

---

### 15. Integration of Contrastive Predictive Coding and Spiking Neural Networks
* **Authors:** Emirhan Bilgiç, Neslihan Serap Şengör, Namık Berk Yalabık, Yavuz Selim İşler, Aykut Görkem Gelen, Rahmi Elibol  
* **Published Date:** 2025-06-10  
* **Document URL:** [https://arxiv.org/pdf/2506.09194v1](https://arxiv.org/pdf/2506.09194v1)  

**Abstract:**
This study examines the integration of Contrastive Predictive Coding (CPC) with Spiking Neural Networks (SNN). While CPC learns the predictive structure of data to generate meaningful representations, SNN mimics the computational processes of biological neural systems over time. In this study, the goal is to develop a predictive coding model with greater biological plausibility by processing inputs and outputs in a spike-based system. The proposed model was tested on the MNIST dataset and achieved a high classification rate in distinguishing positive sequential samples from non-sequential negative samples. The study demonstrates that CPC can be effectively combined with SNN, showing that an SNN trained for classification tasks can also function as an encoding mechanism. Project codes and detailed results can be accessed on our GitHub page: https://github.com/vnd-ogrenme/ongorusel-kodlama/tree/main/CPC_SNN

---

### 16. Predify: Augmenting deep neural networks with brain-inspired predictive coding dynamics
* **Authors:** Bhavin Choksi, Milad Mozafari, Callum Biggs O'May, Benjamin Ador, Andrea Alamia, Rufin VanRullen  
* **Published Date:** 2021-06-04  
* **Document URL:** [https://arxiv.org/pdf/2106.02749v2](https://arxiv.org/pdf/2106.02749v2)  

**Abstract:**
Deep neural networks excel at image classification, but their performance is far less robust to input perturbations than human perception. In this work we explore whether this shortcoming may be partly addressed by incorporating brain-inspired recurrent dynamics in deep convolutional networks. We take inspiration from a popular framework in neuroscience: 'predictive coding'. At each layer of the hierarchical model, generative feedback 'predicts' (i.e., reconstructs) the pattern of activity in the previous layer. The reconstruction errors are used to iteratively update the network's representations across timesteps, and to optimize the network's feedback weights over the natural image dataset-a form of unsupervised training. We show that implementing this strategy into two popular networks, VGG16 and EfficientNetB0, improves their robustness against various corruptions and adversarial attacks. We hypothesize that other feedforward networks could similarly benefit from the proposed framework. To promote research in this direction, we provide an open-sourced PyTorch-based package called Predify, which can be used to implement and investigate the impacts of the predictive coding dynamics in any convolutional neural network.

---

### 17. Adaptive motor control and learning in a spiking neural network realised on a mixed-signal neuromorphic processor
* **Authors:** Sebastian Glatz, Julien N. P. Martel, Raphaela Kreiser, Ning Qiao, Yulia Sandamirskaya  
* **Published Date:** 2018-10-25  
* **Document URL:** [https://arxiv.org/pdf/1810.10801v1](https://arxiv.org/pdf/1810.10801v1)  

**Abstract:**
Neuromorphic computing is a new paradigm for design of both the computing hardware and algorithms inspired by biological neural networks. The event-based nature and the inherent parallelism make neuromorphic computing a promising paradigm for building efficient neural network based architectures for control of fast and agile robots. In this paper, we present a spiking neural network architecture that uses sensory feedback to control rotational velocity of a robotic vehicle. When the velocity reaches the target value, the mapping from the target velocity of the vehicle to the correct motor command, both represented in the spiking neural network on the neuromorphic device, is autonomously stored on the device using on-chip plastic synaptic weights. We validate the controller using a wheel motor of a miniature mobile vehicle and inertia measurement unit as the sensory feedback and demonstrate online learning of a simple 'inverse model' in a two-layer spiking neural network on the neuromorphic chip. The prototype neuromorphic device that features 256 spiking neurons allows us to realise a simple proof of concept architecture for the purely neuromorphic motor control and learning. The architecture can be easily scaled-up if a larger neuromorphic device is available.

---

### 18. Evaluating Spiking Neural Network On Neuromorphic Platform For Human Activity Recognition
* **Authors:** Sizhen Bian, Michele Magno  
* **Published Date:** 2023-08-01  
* **Document URL:** [https://arxiv.org/pdf/2308.00787v1](https://arxiv.org/pdf/2308.00787v1)  

**Abstract:**
Energy efficiency and low latency are crucial requirements for designing wearable AI-empowered human activity recognition systems, due to the hard constraints of battery operations and closed-loop feedback. While neural network models have been extensively compressed to match the stringent edge requirements, spiking neural networks and event-based sensing are recently emerging as promising solutions to further improve performance due to their inherent energy efficiency and capacity to process spatiotemporal data in very low latency. This work aims to evaluate the effectiveness of spiking neural networks on neuromorphic processors in human activity recognition for wearable applications. The case of workout recognition with wrist-worn wearable motion sensors is used as a study. A multi-threshold delta modulation approach is utilized for encoding the input sensor data into spike trains to move the pipeline into the event-based approach. The spikes trains are then fed to a spiking neural network with direct-event training, and the trained model is deployed on the research neuromorphic platform from Intel, Loihi, to evaluate energy and latency efficiency. Test results show that the spike-based workouts recognition system can achieve a comparable accuracy (87.5\%) comparable to the popular milliwatt RISC-V bases multi-core processor GAP8 with a traditional neural network ( 88.1\%) while achieving two times better energy-delay product (0.66 \si{\micro\joule\second} vs. 1.32 \si{\micro\joule\second}).

---

### 19. Watermarking Neuromorphic Brains: Intellectual Property Protection in Spiking Neural Networks
* **Authors:** Hamed Poursiami, Ihsen Alouani, Maryam Parsa  
* **Published Date:** 2024-05-07  
* **Document URL:** [https://arxiv.org/pdf/2405.04049v1](https://arxiv.org/pdf/2405.04049v1)  

**Abstract:**
As spiking neural networks (SNNs) gain traction in deploying neuromorphic computing solutions, protecting their intellectual property (IP) has become crucial. Without adequate safeguards, proprietary SNN architectures are at risk of theft, replication, or misuse, which could lead to significant financial losses for the owners. While IP protection techniques have been extensively explored for artificial neural networks (ANNs), their applicability and effectiveness for the unique characteristics of SNNs remain largely unexplored. In this work, we pioneer an investigation into adapting two prominent watermarking approaches, namely, fingerprint-based and backdoor-based mechanisms to secure proprietary SNN architectures. We conduct thorough experiments to evaluate the impact on fidelity, resilience against overwrite threats, and resistance to compression attacks when applying these watermarking techniques to SNNs, drawing comparisons with their ANN counterparts. This study lays the groundwork for developing neuromorphic-aware IP protection strategies tailored to the distinctive dynamics of SNNs.

---

### 20. Spiking Neural Network Equalization on Neuromorphic Hardware for IM/DD Optical Communication
* **Authors:** Elias Arnold, Georg Böcherer, Eric Müller, Philipp Spilger, Johannes Schemmel, Stefano Calabrò, Maxim Kuschnerov  
* **Published Date:** 2022-06-01  
* **Document URL:** [https://arxiv.org/pdf/2206.00401v1](https://arxiv.org/pdf/2206.00401v1)  

**Abstract:**
A spiking neural network (SNN) non-linear equalizer model is implemented on the mixed-signal neuromorphic hardware system BrainScaleS-2 and evaluated for an IM/DD link. The BER 2e-3 is achieved with a hardware penalty less than 1 dB, outperforming numeric linear equalization.

---

### 21. Spiking Neural Network based Region Proposal Networks for Neuromorphic Vision Sensors
* **Authors:** Jyotibdha Acharya, Vandana Padala, Arindam Basu  
* **Published Date:** 2019-02-26  
* **Document URL:** [https://arxiv.org/pdf/1902.09864v1](https://arxiv.org/pdf/1902.09864v1)  

**Abstract:**
This paper presents a three layer spiking neural network based region proposal network operating on data generated by neuromorphic vision sensors. The proposed architecture consists of refractory, convolution and clustering layers designed with bio-realistic leaky integrate and fire (LIF) neurons and synapses. The proposed algorithm is tested on traffic scene recordings from a DAVIS sensor setup. The performance of the region proposal network has been compared with event based mean shift algorithm and is found to be far superior (~50% better) in recall for similar precision (~85%). Computational and memory complexity of the proposed method are also shown to be similar to that of event based mean shift

---

### 22. Spiking Neural Network on Neuromorphic Hardware for Energy-Efficient Unidimensional SLAM
* **Authors:** Guangzhi Tang, Arpit Shah, Konstantinos P. Michmizos  
* **Published Date:** 2019-03-06  
* **Document URL:** [https://arxiv.org/pdf/1903.02504v2](https://arxiv.org/pdf/1903.02504v2)  

**Abstract:**
Energy-efficient simultaneous localization and mapping (SLAM) is crucial for mobile robots exploring unknown environments. The mammalian brain solves SLAM via a network of specialized neurons, exhibiting asynchronous computations and event-based communications, with very low energy consumption. We propose a brain-inspired spiking neural network (SNN) architecture that solves the unidimensional SLAM by introducing spike-based reference frame transformation, visual likelihood computation, and Bayesian inference. We integrated our neuromorphic algorithm to Intel's Loihi neuromorphic processor, a non-Von Neumann hardware that mimics the brain's computing paradigms. We performed comparative analyses for accuracy and energy-efficiency between our neuromorphic approach and the GMapping algorithm, which is widely used in small environments. Our Loihi-based SNN architecture consumes 100 times less energy than GMapping run on a CPU while having comparable accuracy in head direction localization and map-generation. These results pave the way for scaling our approach towards active-SLAM alternative solutions for Loihi-controlled autonomous robots.

---

### 23. Solving a steady-state PDE using spiking networks and neuromorphic hardware
* **Authors:** J. Darby Smith, William Severa, Aaron J. Hill, Leah Reeder, Brian Franke, Richard B. Lehoucq, Ojas D. Parekh, James B. Aimone  
* **Published Date:** 2020-05-21  
* **Document URL:** [https://arxiv.org/pdf/2005.10904v1](https://arxiv.org/pdf/2005.10904v1)  

**Abstract:**
The widely parallel, spiking neural networks of neuromorphic processors can enable computationally powerful formulations. While recent interest has focused on primarily machine learning tasks, the space of appropriate applications is wide and continually expanding. Here, we leverage the parallel and event-driven structure to solve a steady state heat equation using a random walk method. The random walk can be executed fully within a spiking neural network using stochastic neuron behavior, and we provide results from both IBM TrueNorth and Intel Loihi implementations. Additionally, we position this algorithm as a potential scalable benchmark for neuromorphic systems.

---

### 24. Bio-inspired computational memory model of the Hippocampus: an approach to a neuromorphic spike-based Content-Addressable Memory
* **Authors:** Daniel Casanueva-Morato, Alvaro Ayuso-Martinez, Juan P. Dominguez-Morales, Angel Jimenez-Fernandez, Gabriel Jimenez-Moreno  
* **Published Date:** 2023-10-09  
* **Document URL:** [https://arxiv.org/pdf/2310.05868v1](https://arxiv.org/pdf/2310.05868v1)  

**Abstract:**
The brain has computational capabilities that surpass those of modern systems, being able to solve complex problems efficiently in a simple way. Neuromorphic engineering aims to mimic biology in order to develop new systems capable of incorporating such capabilities. Bio-inspired learning systems continue to be a challenge that must be solved, and much work needs to be done in this regard. Among all brain regions, the hippocampus stands out as an autoassociative short-term memory with the capacity to learn and recall memories from any fragment of them. These characteristics make the hippocampus an ideal candidate for developing bio-inspired learning systems that, in addition, resemble content-addressable memories. Therefore, in this work we propose a bio-inspired spiking content-addressable memory model based on the CA3 region of the hippocampus with the ability to learn, forget and recall memories, both orthogonal and non-orthogonal, from any fragment of them. The model was implemented on the SpiNNaker hardware platform using Spiking Neural Networks. A set of experiments based on functional, stress and applicability tests were performed to demonstrate its correct functioning. This work presents the first hardware implementation of a fully-functional bio-inspired spiking hippocampal content-addressable memory model, paving the way for the development of future more complex neuromorphic systems.

---

### 25. WEBCA: Weakly-Electric-Fish Bioinspired Cognitive Architecture
* **Authors:** Amit Kumar Mishra  
* **Published Date:** 2018-06-29  
* **Document URL:** [https://arxiv.org/pdf/1806.11401v1](https://arxiv.org/pdf/1806.11401v1)  

**Abstract:**
Neuroethology has been an active field of study for more than a century now. Out of some of the most interesting species that has been studied so far, weakly electric fish is a fascinating one. It performs communication, echo-location and inter-species detection efficiently with an interesting configuration of sensors, neu-rons and a simple brain. In this paper we propose a cognitive architecture inspired by the way these fishes handle and process information. We believe that it is eas-ier to understand and mimic the neural architectures of a simpler species than that of human. Hence, the proposed architecture is expected to both help research in cognitive robotics and also help understand more complicated brains like that of human beings.

---

### 26. Cognitive Architecture for Decision-Making Based on Brain Principles Programming
* **Authors:** Anton Kolonin, Andrey Kurpatov, Artem Molchanov, Gennadiy Averyanov  
* **Published Date:** 2022-04-17  
* **Document URL:** [https://arxiv.org/pdf/2204.07919v3](https://arxiv.org/pdf/2204.07919v3)  

**Abstract:**
We describe a cognitive architecture intended to solve a wide range of problems based on the five identified principles of brain activity, with their implementation in three subsystems: logical-probabilistic inference, probabilistic formal concepts, and functional systems theory. Building an architecture involves the implementation of a task-driven approach that allows defining the target functions of applied applications as tasks formulated in terms of the operating environment corresponding to the task, expressed in the applied ontology. We provide a basic ontology for a number of practical applications as well as for the subject domain ontologies based upon it, describe the proposed architecture, and give possible examples of the execution of these applications in this architecture.

---

### 27. Design for a Darwinian Brain: Part 2. Cognitive Architecture
* **Authors:** Chrisantha Fernando, Vera Vasas  
* **Published Date:** 2013-03-28  
* **Document URL:** [https://arxiv.org/pdf/1303.7201v1](https://arxiv.org/pdf/1303.7201v1)  

**Abstract:**
The accumulation of adaptations in an open-ended manner during lifetime learning is a holy grail in reinforcement learning, intrinsic motivation, artificial curiosity, and developmental robotics. We present a specification for a cognitive architecture that is capable of specifying an unlimited range of behaviors. We then give examples of how it can stochastically explore an interesting space of adjacent possible behaviors. There are two main novelties; the first is a proper definition of the fitness of self-generated games such that interesting games are expected to evolve. The second is a modular and evolvable behavior language that has systematicity, productivity, and compositionality, i.e. it is a physical symbol system. A part of the architecture has already been implemented on a humanoid robot.

---

### 28. Cognitive Architecture for Decision-Making Based on Brain Principles Programming (in Russian)
* **Authors:** Anton Kolonin, Andrey Kurpatov, Artem Molchanov, Gennadiy Averyanov  
* **Published Date:** 2023-02-18  
* **Document URL:** [https://arxiv.org/pdf/2302.09377v1](https://arxiv.org/pdf/2302.09377v1)  

**Abstract:**
We describe a cognitive architecture intended to solve a wide range of problems based on the five identified principles of brain activity, with their implementation in three subsystems: logical-probabilistic inference, probabilistic formal concepts, and functional systems theory. Building an architecture involves the implementation of a task-driven approach that allows defining the target functions of applied applications as tasks formulated in terms of the operating environment corresponding to the task, expressed in the applied ontology. We provide a basic ontology for a number of practical applications as well as for the subject domain ontologies based upon it, describe the proposed architecture, and give possible examples of the execution of these applications in this architecture.

---

### 29. Brain-inspired Distributed Cognitive Architecture
* **Authors:** Leendert A Remmelzwaal, Amit K Mishra, George F R Ellis  
* **Published Date:** 2020-05-18  
* **Document URL:** [https://arxiv.org/pdf/2005.08603v1](https://arxiv.org/pdf/2005.08603v1)  

**Abstract:**
In this paper we present a brain-inspired cognitive architecture that incorporates sensory processing, classification, contextual prediction, and emotional tagging. The cognitive architecture is implemented as three modular web-servers, meaning that it can be deployed centrally or across a network for servers. The experiments reveal two distinct operations of behaviour, namely high- and low-salience modes of operations, which closely model attention in the brain. In addition to modelling the cortex, we have demonstrated that a bio-inspired architecture introduced processing efficiencies. The software has been published as an open source platform, and can be easily extended by future research teams. This research lays the foundations for bio-realistic attention direction and sensory selection, and we believe that it is a key step towards achieving a bio-realistic artificial intelligent system.

---

### 30. A Whole Brain Probabilistic Generative Model: Toward Realizing Cognitive Architectures for Developmental Robots
* **Authors:** Tadahiro Taniguchi, Hiroshi Yamakawa, Takayuki Nagai, Kenji Doya, Masamichi Sakagami, Masahiro Suzuki, Tomoaki Nakamura, Akira Taniguchi  
* **Published Date:** 2021-03-15  
* **Document URL:** [https://arxiv.org/pdf/2103.08183v2](https://arxiv.org/pdf/2103.08183v2)  

**Abstract:**
Building a humanlike integrative artificial cognitive system, that is, an artificial general intelligence (AGI), is the holy grail of the artificial intelligence (AI) field. Furthermore, a computational model that enables an artificial system to achieve cognitive development will be an excellent reference for brain and cognitive science. This paper describes an approach to develop a cognitive architecture by integrating elemental cognitive modules to enable the training of the modules as a whole. This approach is based on two ideas: (1) brain-inspired AI, learning human brain architecture to build human-level intelligence, and (2) a probabilistic generative model(PGM)-based cognitive system to develop a cognitive system for developmental robots by integrating PGMs. The development framework is called a whole brain PGM (WB-PGM), which differs fundamentally from existing cognitive architectures in that it can learn continuously through a system based on sensory-motor information. In this study, we describe the rationale of WB-PGM, the current status of PGM-based elemental cognitive modules, their relationship with the human brain, the approach to the integration of the cognitive modules, and future challenges. Our findings can serve as a reference for brain studies. As PGMs describe explicit informational relationships between variables, this description provides interpretable guidance from computational sciences to brain science. By providing such information, researchers in neuroscience can provide feedback to researchers in AI and robotics on what the current models lack with reference to the brain. Further, it can facilitate collaboration among researchers in neuro-cognitive sciences as well as AI and robotics.

---

### 31. Prefrontal Cortex Motivated Cognitive Architecture for Multiple Robots
* **Authors:** Amit Kumar Mishra, Abhishek Kumar, Dipankar Deb  
* **Published Date:** 2014-11-12  
* **Document URL:** [https://arxiv.org/pdf/1411.3111v1](https://arxiv.org/pdf/1411.3111v1)  

**Abstract:**
In this paper, we introduce a cerebral cortex inspired architecture for robots in which we have mapped hierarchical cortical representation of human brain to logic flow and decision making process. Our work focuses on the two major features of human cognitive process, viz. the perception action cycle and its hierarchical organization, and the decision making process. To prove the effectiveness of our proposed method, we incorporated this architecture in our robot which we named as Cognitive Insect Robot inspired by Brain Architecture (CIRBA). We have extended our research to the implementation of this cognitive architecture of CIRBA in multiple robots and have analyzed the level of cognition attained by them

---

### 32. Designing Artificial Cognitive Architectures: Brain Inspired or Biologically Inspired?
* **Authors:** Emanuel Diamant  
* **Published Date:** 2018-12-12  
* **Document URL:** [https://arxiv.org/pdf/1812.04769v1](https://arxiv.org/pdf/1812.04769v1)  

**Abstract:**
Artificial Neural Networks (ANNs) were devised as a tool for Artificial Intelligence design implementations. However, it was soon became obvious that they are unable to fulfill their duties. The fully autonomous way of ANNs working, precluded from any human intervention or supervision, deprived of any theoretical underpinning, leads to a strange state of affairs, when ANN designers cannot explain why and how they achieve their amazing and remarkable results. Therefore, contemporary Artificial Intelligence R&D looks more like a Modern Alchemy enterprise rather than a respected scientific or technological undertaking. On the other hand, modern biological science posits that intelligence can be distinguished not only in human brains. Intelligence today is considered as a fundamental property of each and every living being. Therefore, lower simplified forms of natural intelligence are more suitable for investigation and further replication in artificial cognitive architectures.

---

