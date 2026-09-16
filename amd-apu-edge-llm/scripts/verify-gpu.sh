#!/usr/bin/env bash
# amd-apu-edge-llm/scripts/verify-gpu.sh
# Diagnostic script to verify AMD iGPU/APU configuration, driver groups,
# device node permissions, and ROCm runtime overrides.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0;35m' # No Color
RESET='\033[0m'

echo -e "${BLUE}=====================================================================${RESET}"
echo -e "${BLUE}🛡️  AMD APU Edge LLM - Local iGPU Diagnostic Verification Tool  🛡️${RESET}"
echo -e "${BLUE}=====================================================================${RESET}"

# 1. Check OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}❌ Error: This verification script currently only supports native Linux environments.${RESET}"
    exit 1
fi
echo -e "${GREEN}✅ OS check: Linux detected.${RESET}"

# 2. Check for AMD hardware
echo -e "\n${BLUE}[1/5] Scanning PCIe bus for AMD Graphics hardware...${RESET}"
if lspci | grep -iE "vga|display|3d" | grep -iq "amd"; then
    gpu_info=$(lspci | grep -iE "vga|display|3d" | grep -i "amd")
    echo -e "${GREEN}✅ Found AMD Graphics Hardware:${RESET}"
    echo -e "   $gpu_info"
else
    echo -e "${YELLOW}⚠️  Warning: No AMD Graphics device found via lspci.${RESET}"
    echo -e "   Checking /sys/class/drm directly..."
    if ls /sys/class/drm/card* >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Found direct DRM card interfaces.${RESET}"
    else
        echo -e "${RED}❌ Error: No direct AMD GPU or DRM card interface detected.${RESET}"
        exit 1
    fi
fi

# 3. Verify Device Nodes & Permissions
echo -e "\n${BLUE}[2/5] Checking kernel device node permissions...${RESET}"

# /dev/kfd (Kernel Fusion Driver - critical for ROCm HSA)
if [ -c /dev/kfd ]; then
    echo -e "${GREEN}✅ /dev/kfd exists.${RESET}"
    if [ -r /dev/kfd ] && [ -w /dev/kfd ]; then
        echo -e "${GREEN}✅ Read/Write permissions are OK on /dev/kfd.${RESET}"
    else
        echo -e "${RED}❌ Error: User does not have Read/Write access to /dev/kfd.${RESET}"
        echo -e "   Permissions: $(ls -l /dev/kfd)"
        echo -e "   Please ensure your user is added to the 'render' and 'video' groups."
    fi
else
    echo -e "${RED}❌ Error: /dev/kfd device node is missing. Is the AMDGPU kernel module loaded?${RESET}"
fi

# Direct Rendering Infrastructure (DRI) card & render nodes
if ls /dev/dri/renderD* >/dev/null 2>&1; then
    echo -e "${GREEN}✅ DRI render nodes detected: $(ls /dev/dri/renderD* | tr '\n' ' ')${RESET}"
else
    echo -e "${YELLOW}⚠️  Warning: No /dev/dri/renderD* nodes found. Hardware acceleration might be impaired.${RESET}"
fi

# 4. Verify User Groups
echo -e "\n${BLUE}[3/5] Verifying user group memberships...${RESET}"
current_groups=$(groups)
group_err=0

for group in video render; do
    if [[ " $current_groups " =~ " $group " ]]; then
        echo -e "${GREEN}✅ User is a member of the '$group' group.${RESET}"
    else
        echo -e "${RED}❌ Error: User is NOT a member of the '$group' group.${RESET}"
        group_err=1
    fi
done

if [ $group_err -eq 1 ]; then
    echo -e "${YELLOW}👉 Run the following command to add your user to these groups, then log out and back in:${RESET}"
    echo -e "   sudo usermod -a -G video,render \$USER"
fi

# 5. Check ROCm/HSA Environment Overrides
echo -e "\n${BLUE}[4/5] Checking HSA runtime environment overrides...${RESET}"
if [ -z "$HSA_OVERRIDE_GFX_VERSION" ]; then
    echo -e "${YELLOW}⚠️  Warning: HSA_OVERRIDE_GFX_VERSION is not set.${RESET}"
    echo -e "   Most consumer AMD APUs (780M/890M) require this override to run ROCm/HIP."
    echo -e "   Please set this variable before running your LLM engine, e.g.:${RESET}"
    echo -e "   export HSA_OVERRIDE_GFX_VERSION=11.0.0"
else
    echo -e "${GREEN}✅ HSA_OVERRIDE_GFX_VERSION is active: $HSA_OVERRIDE_GFX_VERSION${RESET}"
fi

# 6. Locate ROCm / HIP CLI Tools
echo -e "\n${BLUE}[5/5] Checking for installed ROCm/HIP tools...${RESET}"
if command -v rocminfo >/dev/null 2>&1; then
    echo -e "${GREEN}✅ rocminfo found: $(which rocminfo)${RESET}"
else
    echo -e "${YELLOW}⚠️  Warning: rocminfo utility not found in PATH.${RESET}"
    echo -e "   Ensure ROCm is fully installed and in your PATH, e.g.:"
    echo -e "   export PATH=\$PATH:/opt/rocm/bin"
fi

if command -v clinfo >/dev/null 2>&1; then
    echo -e "${GREEN}✅ clinfo found: $(which clinfo)${RESET}"
else
    echo -e "${YELLOW}⚠️  Warning: clinfo utility not found in PATH.${RESET}"
fi

echo -e "\n${BLUE}=====================================================================${RESET}"
echo -e "${GREEN}Verification complete! If all checks are green, your hardware and${RESET}"
echo -e "${GREEN}permissions are fully ready for native ROCm LLM acceleration.${RESET}"
echo -e "${BLUE}=====================================================================${RESET}"
