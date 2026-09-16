# Memory Bandwidth Bottlenecks & BIOS UMA Carve-out Tuning for AMD APUs

Integrated GPUs (iGPUs), such as the AMD Radeon 780M and 890M, share the host system's DDR5 memory rather than possessing dedicated ultra-fast graphics memory (like GDDR6 or HBM3 found on discrete GPUs). 

Because LLM text generation is fundamentally bound by memory bandwidth, understanding how system memory speed, memory architecture, and BIOS-level memory carving impact performance is critical for achieving optimal generation speeds.

This guide provides the mathematical formulas, system architecture details, and tuning recommendations to eliminate memory bottlenecks on your local AMD APU edge-compute cluster.

---

## 🧮 The Mathematics of LLM Generation (The DDR5 Bottleneck)

During the **decode phase** (generating tokens one by one), LLM execution is strictly **memory-bandwidth bound**. To generate a single token, the processor must read every single parameter of the active model from VRAM into its compute cores.

We can calculate the absolute maximum theoretical generation speed of any hardware setup using this simple formula:

$$\text{Max Generation Speed (tokens/sec)} = \frac{\text{System Memory Bandwidth (GB/s)}}{\text{Active Model Size (GB)}}$$

### 1. Calculating Memory Bandwidth
For a dual-channel DDR5-5600 system (standard in Ryzen 7040/8040 mini-PCs):
*   **Bus Width:** 64-bit per channel $\times$ 2 channels = 128-bit (or more precisely, DDR5 runs four 32-bit subchannels, yielding 128-bit total).
*   **Effective Clock Rate:** 5600 MT/s (MegaTransfers per second).
*   **Bandwidth Formula:** 
    $$\text{Bandwidth} = \frac{128 \text{ bits} \times 5600 \text{ MT/s}}{8 \text{ bits/byte}} = 89,600 \text{ MB/s} = 89.6 \text{ GB/s}$$

### 2. Calculating the Theoretical Limit
If we load **Qwen-2.5-7B-Instruct (Q4_K_M GGUF)**, the file size is approximately **`4.25 GB`**:
*   **Theoretical Speed Limit:** 
    $$\text{Limit} = \frac{89.6 \text{ GB/s}}{4.25 \text{ GB}} \approx 21.08 \text{ tokens/sec}$$

This mathematical limit perfectly explains why your generation speeds on the 780M hover between **18 and 22 tokens/sec**. The compute units of the GPU are mostly idling, waiting for the system RAM to feed them model weights.

### 3. The Impact of RAM Speed
Because performance is linear with memory bandwidth, upgrading system RAM has a direct, measurable impact on LLM generation speed:

| Memory Speed | Channels | Total Bandwidth | Theoretical Max (Qwen-2.5-7B Q4) | Actual Measured |
| :--- | :---: | :---: | :---: | :---: |
| **DDR5-4800** | Dual | 76.8 GB/s | 18.0 tokens/sec | **~15 tokens/sec** |
| **DDR5-5600** | Dual | 89.6 GB/s | 21.1 tokens/sec | **~19 tokens/sec** |
| **LPDDR5X-6400** | Dual | 102.4 GB/s | 24.1 tokens/sec | **~21 tokens/sec** |
| **LPDDR5X-7500** | Dual | 120.0 GB/s | 28.2 tokens/sec | **~25 tokens/sec** |

*Crucial Hardware Note: **Single-channel memory completely halves your performance.** Ensure your mini-PC or laptop is running matched dual-channel SODIMMs.*

---

## 🧠 UMA Frame Buffer Size vs. GTT (Shared Memory)

On AMD systems, system RAM is split into two virtual pools for the graphics driver:

1.  **UMA (Unified Memory Architecture) Frame Buffer:** This is a dedicated partition of system RAM carved out at the BIOS level. The operating system hides this memory from the CPU and exposes it to the GPU as dedicated physical VRAM.
2.  **GTT (Graphics Translation Table) / Shared Memory:** This is system RAM that remains visible to the CPU, but the GPU can dynamically access or "borrow" it on demand over the PCIe bus interface.

### The Conflict of Dynamic Allocation
If you leave your BIOS "UMA Frame Buffer Size" at the default setting (often `512M` or `2G`), the operating system relies on GTT to dynamically allocate memory when you load an LLM.

This causes three major performance and stability issues:
*   **Context-Switching Latency:** Copying data back and forth between GTT space and the CPU cache introduces heavy latency penalties, causing **Prefill stalls** (the time it takes for the model to process your prompt before generating the first token).
*   **Allocation Failures:** Many runtimes (like ROCm/HIP on Linux) expect a flat, contiguous, static block of physical memory. If they do not see enough "Dedicated VRAM," they will fail to initialize or throw silent "Out of Memory" (OOM) errors, even if you have plenty of free "Shared Memory" available.
*   **System Thrashing:** If the OS dynamically swaps memory pages, performance collapses to less than 1 token/sec.

### The Solution: 16GB UMA Carve-out
By setting the **UMA Frame Buffer Size** to **`16G`** in your BIOS:
*   You physically lock 16GB of contiguous system RAM to the GPU's memory controller.
*   The ROCm and Vulkan runtimes see a stable, static 16GB of dedicated VRAM, ensuring they can load massive models (up to 14B or 16B parameter sizes) with zero runtime allocation overhead.
*   This completely bypasses the latency-heavy GTT mapping, slashing your Prefill latency and keeping generation speeds stable and un-throttled.

---

## 📈 Prefill vs. Decode Phase Dynamics on APUs

Understanding the two distinct phases of LLM inference is critical for profiling performance:

### 1. The Prefill Phase (Compute-Bound)
*   **What it is:** The model reads and processes your entire prompt.
*   **Limiting Factor:** Compute performance (FLOPs).
*   **On the APU:** This is where the Compute Units (CUs) of the iGPU are heavily utilized. The Radeon 780M has **12 CUs** (768 stream processors), which provide plenty of compute power to handle prompts of 1K - 2K tokens in milliseconds. Flash Attention and quantized KV caches should be enabled to prevent compute bottlenecks during deep prompt processing.

### 2. The Decode Phase (Bandwidth-Bound)
*   **What it is:** The model generates output text one token at a time.
*   **Limiting Factor:** Memory Bandwidth (GB/s).
*   **On the APU:** The compute units are idle ~90% of the time, waiting for the system RAM (DDR5) to stream the weights. To maximize this phase, ensure you are running the fastest RAM speed supported by your motherboard and have configured your dual-channel memory correctly.
