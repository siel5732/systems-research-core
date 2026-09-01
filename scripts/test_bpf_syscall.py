#!/usr/bin/env python3
"""
scripts/test_bpf_syscall.py

SAGE High-Performance Zero-Dependency eBPF Map Writer.
Loads GEEKOM's native libbpf shared library (/usr/lib/x86_64-linux-gnu/libbpf.so.1)
and invokes bpf_obj_get() to obtain a verified BPF map file descriptor, followed
by bpf_map_update_elem() directly from Python with sub-microsecond latency.
Completely abstracts raw system-call structure layouts and kernel size-checks!
"""

import sys
import os
import ctypes

# --- 1. LOAD NATIVE LIBBPF ---
LIBBPF_PATH = "/usr/lib/x86_64-linux-gnu/libbpf.so.1"
try:
    libbpf = ctypes.CDLL(LIBBPF_PATH, use_errno=True)
except Exception as e:
    print(f"[-] Failed to load libbpf at {LIBBPF_PATH}: {e}")
    sys.exit(1)

# --- 2. DEFINE LIBBPF FUNCTION SIGNATURES ---
# int bpf_obj_get(const char *pathname);
libbpf.bpf_obj_get.argtypes = [ctypes.c_char_p]
libbpf.bpf_obj_get.restype = ctypes.c_int

# int bpf_map_update_elem(int fd, const void *key, const void *value, __u64 flags);
libbpf.bpf_map_update_elem.argtypes = [
    ctypes.c_int,      # map_fd
    ctypes.c_void_p,   # const void *key
    ctypes.c_void_p,   # const void *value
    ctypes.c_uint64    # __u64 flags (BPF_ANY = 0)
]
libbpf.bpf_map_update_elem.restype = ctypes.c_int

def write_bpf_map_libbpf(pin_path, seq_id, delay_ns):
    # 1. Obtain a verified BPF file descriptor using libbpf's bpf_obj_get()
    # (Do not use raw os.open, as that returns a standard VFS FD instead of a BPF object FD!)
    fd = libbpf.bpf_obj_get(pin_path.encode('utf-8'))
    
    if fd < 0:
        err = ctypes.get_errno()
        print(f"[-] Failed to obtain BPF Map File Descriptor via bpf_obj_get()!")
        print(f"    - Path: {pin_path}")
        print(f"    - Error code: {fd}, Errno: {err} ({os.strerror(err)})")
        print("    Please ensure the map is pinned by running:")
        print("    sudo bpftool map pin id <your_map_id> /sys/fs/bpf/delay_map")
        sys.exit(1)
        
    # 2. Prepare Ctypes variables for key and value in GEEKOM RAM
    key_c = ctypes.c_uint32(seq_id)
    val_c = ctypes.c_uint64(delay_ns)
    
    # 3. Trigger native libbpf map update function
    import time
    start_time = time.perf_counter_ns()
    res = libbpf.bpf_map_update_elem(
        fd,
        ctypes.byref(key_c),
        ctypes.byref(val_c),
        0  # BPF_ANY
    )
    end_time = time.perf_counter_ns()
    
    # 4. Clean up file descriptor using standard close()
    try:
        os.close(fd)
    except Exception:
        pass
    
    if res < 0:
        err = ctypes.get_errno()
        print(f"[-] libbpf bpf_map_update_elem Failed! Return code: {res}, Errno: {err} ({os.strerror(err)})")
        return False
    
    print(f"[✓] libbpf Map Update SUCCESS!")
    print(f"    - Wrote seq={seq_id}, delay={delay_ns} ns to pinned map: {pin_path}")
    print(f"    - Execution Latency: {(end_time - start_time) / 1000.0:.3f} microseconds!")
    return True

if __name__ == "__main__":
    pin_path = "/sys/fs/bpf/delay_map"
    seq = 5
    delay = 123456789
    
    print(f"[*] Starting SAGE High-Speed libbpf Map Writer...")
    write_bpf_map_libbpf(pin_path, seq, delay)
