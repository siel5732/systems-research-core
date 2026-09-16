# Running LLMs on AMD APUs under Windows (Vulkan & llama.cpp Path)

This guide provides a step-by-step walkthrough for configuring and running hardware-accelerated LLM inference on AMD Ryzen APUs (such as the Radeon 780M and 890M) within a native Windows environment using the **Vulkan API**.

While Linux with ROCm is the standard choice for enterprise servers, Windows with Vulkan offers a massive advantage for local workstations, mini-PCs, and laptops: **it requires zero complex driver toolchains or overrides and works out-of-the-box on standard consumer drivers.**

---

## 🚀 Why Vulkan on Windows?

1.  **Driver Simplicity:** No need to install development-stage ROCm packages or bypass hardware signature checks. The official consumer **AMD Software: Adrenalin Edition** drivers ship with full, high-performance Vulkan support pre-installed.
2.  **Stability:** Vulkan is a highly mature, cross-platform graphics and compute API. It is incredibly stable on Windows and does not suffer from kernel/dkms package breakages during Windows updates.
3.  **Performance parity:** For LLM text generation (generation phase), Vulkan on Windows achieves virtually identical tokens-per-second performance compared to native ROCm on Linux, as both are ultimately bound by the exact same physical DDR5 system memory bandwidth limit (~89.6 GB/s).

---

## 🛠️ Prerequisites

Before starting, ensure your system is configured to expose enough physical memory to the iGPU.

### 1. BIOS UMA Frame Buffer Size (VRAM Carve-out)
By default, Windows APUs dynamically share system RAM but often only report a small amount (512MB or 2GB) as "dedicated" VRAM. To ensure heavy models do not silently crash or fall back to slow system paging:
1.  Reboot your PC and enter your UEFI/BIOS utility (usually by tapping `Del` or `F2` during startup).
2.  Navigate to **Advanced** -> **AMD CBS** -> **NBIO Common Options** -> **GFX Configuration**.
3.  Set **UMA Mode** to **`Specified`**.
4.  Set **UMA Frame Buffer Size** to at least **`4G`**, **`8G`**, or **`16G`** (16G is highly recommended if your system has 32GB or 64GB of total system RAM).
5.  Save and reboot.

### 2. Verify in Windows Task Manager
1.  Open Task Manager (`Ctrl + Shift + Esc`).
2.  Go to the **Performance** tab and select **GPU 0** (AMD Radeon Graphics).
3.  Verify that **Dedicated GPU memory** displays the size you allocated in the BIOS (e.g., `16.0 GB`).

---

## 📦 Method 1: Native Windows via llama.cpp (Vulkan Backend)

This is the most highly recommended method for raw performance and granular control. `llama.cpp` features an exceptionally optimized, native Vulkan backend.

### 1. Download pre-compiled Binaries
1.  Navigate to the official [llama.cpp Releases page on GitHub](https://github.com/ggerganov/llama.cpp/releases).
2.  Download the latest zip package containing the Vulkan binaries. Look for a file named like:
    `llama-<version>-bin-win-vulkan-x64.zip`
3.  Extract the zip file to a clean folder on your local drive (e.g., `C:\llama-vulkan\`).

### 2. Download a GGUF Model
We recommend starting with **Qwen-2.5-7B-Instruct** (Q4_K_M quantization), which represents the current gold-standard balance of intelligence, speed, and size for 16GB APU systems.
1.  Download the `.gguf` file from Hugging Face (e.g., Qwen/Qwen2.5-7B-Instruct-GGUF).
2.  Place the model file in your `C:\llama-vulkan\` folder.

### 3. Run Inference with GPU Offloading
Open PowerShell or Command Prompt, navigate to your folder, and run the following command. The critical flag is `-ngl 99` (Number of GPU Layers to offload) and `--gpu-api vulkan` (if not automatically selected):

```powershell
cd C:\llama-vulkan\

# Run interactive chat offloading all layers to the Radeon iGPU
.\llama-cli.exe -m qwen2.5-7b-instruct-q4_k_m.gguf -ngl 99 -p "You are a helpful assistant." -cnv
```

### 🔍 Reading the Output logs:
During startup, `llama.cpp` will print the detected hardware. Look for lines resembling:
```text
ggml_vulkan: Found 1 compatible device(s):
device 0: AMD Radeon 780M Graphics (discrete: 0)
```
If you see the `780M` listed, and your generation speeds are averaging **18 - 22 tokens/sec**, your hardware acceleration is fully operational!

---

## 📦 Method 2: Ollama for Windows (DirectML / Vulkan support)

Ollama provides a highly convenient, native Windows installer that manages background services and model downloads automatically.

1.  Download and run the installer from the [Official Ollama Website](https://ollama.com/download/windows).
2.  Once installed, Ollama runs as a background tray icon.
3.  Open PowerShell and trigger a run. Ollama automatically scans your system drivers and offloads model layers to your Radeon graphics utilizing Microsoft's DirectML/Vulkan backend under the hood:
    ```powershell
    ollama run qwen2.5:7b
    ```
4.  To verify if the model is running on the GPU, run this command in a separate PowerShell window while generating text:
    ```powershell
    ollama ps
    ```
    It should display the active model and indicate that it is utilizing GPU resources.

---

## 💡 Troubleshooting & Performance Tips

### 1. "HIP out of memory" or Crash on Startup
*   **Cause:** Your model size + context window exceeds the dedicated UMA buffer allocated in the BIOS, or Windows is refusing to allocate shared memory dynamically.
*   **Fix:** Reduce your context window (using the `-c` flag in llama.cpp, e.g., `-c 2048`), use a smaller model/tighter quantization (like `Q3_K_S` or `Q4_K_S`), or ensure your BIOS GFX configuration is set to a higher dedicated threshold.

### 2. Slow Generation Speeds (< 5 tokens/sec)
*   **Cause:** The model layers did not successfully offload to the GPU, causing the system to run the model on the CPU.
*   **Fix:** Ensure you passed the `-ngl 99` flag. If some layers are still on the CPU, check the terminal logs on startup to see if llama.cpp rejected the Vulkan device due to driver mismatches. Ensure you are running the latest official AMD Adrenalin drivers.
