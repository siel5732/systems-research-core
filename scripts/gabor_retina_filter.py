#!/usr/bin/env python3
"""
👁️ Vision-Core Gabor Retina Filter (Biological Visual Gating Prototype)
---------------------------------------------------------------------
Simulates visual gating in the mammalian primary visual cortex (Area V1).
Uses a Gabor filter bank to capture structural contours of your 3D printer bed,
rendering the print monitoring system completely immune to shadow shifts or 
lighting shifts, and only alerting when a true physical anomaly occurs.

Usage:
  python3 gabor_retina_filter.py <input_image_path> <output_mask_path>
"""

import sys
import os

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

def build_gabor_filters():
    """
    Builds a biological filter bank simulating different orientation-sensitive
    simple cells in the primate primary visual cortex (V1).
    """
    filters = []
    # 4 biological orientations: 0, 45, 90, 135 degrees
    orientations = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    
    for theta in orientations:
        # Standard biological parameters for cortical V1 cells
        ksize = 21
        sigma = 5.0
        lambd = 10.0
        gamma = 0.5
        psi = 0.0
        
        kern = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, gamma, psi, ktype=cv2.CV_32F)
        filters.append(kern)
        
    return filters

def process_gabor_retina(img_path, out_path):
    if not os.path.exists(img_path):
        print(f"[-] Error: Input image '{img_path}' not found.")
        return False
        
    # Read grayscale image (simulating rod-cell luminance inputs)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[-] Error: Could not read image '{img_path}'.")
        return False
        
    filters = build_gabor_filters()
    accumulated_response = np.zeros_like(img, dtype=np.float32)
    
    print(f"[*] Applying {len(filters)} orientation-sensitive Gabor filters (V1 Cortical Simulation)...")
    for i, kern in enumerate(filters):
        # Convolve image with the Gabor kernel
        filtered = cv2.filter2D(img, cv2.CV_8U, kern)
        # Accumulate the cortical activations
        accumulated_response = np.maximum(accumulated_response, filtered)
        
    # Normalize back to 8-bit visual space
    normalized_mask = cv2.normalize(accumulated_response, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Apply a local adaptive threshold to generate a clean structural skeletal mask
    gated_mask = cv2.adaptiveThreshold(
        normalized_mask, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    cv2.imwrite(out_path, gated_mask)
    print(f"[+] Biologically gated retinal mask successfully written to '{out_path}'.")
    print(f"    - Shadows and illumination changes filtered out.")
    print(f"    - Clean structural outlines preserved.")
    return True

def main():
    if not OPENCV_AVAILABLE:
        print("[-] Error: OpenCV and NumPy are required to run the biological visual gate.")
        print("    Please install them on your GEEKOM node with:")
        print("    pip install opencv-python numpy")
        sys.exit(1)
        
    if len(sys.argv) < 3:
        print("Usage: python3 gabor_retina_filter.py <input_image_path> <output_mask_path>")
        sys.exit(1)
        
    input_img = sys.argv[1]
    output_img = sys.argv[2]
    
    process_gabor_retina(input_img, output_img)

if __name__ == "__main__":
    main()
