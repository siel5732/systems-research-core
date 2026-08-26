#!/usr/bin/env python3
import collections, contextlib, io, os, queue, time, wave, logging
import numpy as np, requests, sounddevice as sd, webrtcvad
from scipy.signal import iirnotch, lfilter
from openwakeword.model import Model

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def find_jabra_device():
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        name = device["name"].lower()
        if "jabra" in name and "alsa_input" in name:
            logging.info(f"Auto-detected Jabra mic at ID {idx}")
            return idx
    for idx, device in enumerate(devices):
        name = device["name"].lower()
        if "jabra" in name and device["max_input_channels"] > 0:
            logging.info(f"Fallback auto-detected Jabra mic at ID {idx}")
            return idx
    logging.error("Could not find Jabra input device!")
    return None

RATE = 16000
CHUNK = 1280
DEVICE = find_jabra_device()
WAKE_THRESHOLD = 0.75
VAD_MODE = 2
MAX_SILENCE_FRAMES = 30
MAX_RECORDING_FRAMES = 150  # 12 seconds total (150 * 80ms)
PRE_ROLL_FRAMES = 10

GATEWAY_WEBHOOK = "http://127.0.0.1:18191/voice/inbound"
TOKEN = "bqK72bZK08TRzb1k510VS9ZbkUUFSLz8"

audio_q = queue.Queue()
vad = webrtcvad.Vad(VAD_MODE)

logging.info("Loading openWakeWord default models...")
oww = Model()

def pcm16_to_wav_bytes(pcm_bytes: bytes) -> bytes:
    buf = io.BytesIO()
    with contextlib.closing(wave.open(buf, "wb")) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()

def post_wav(wav_bytes: bytes):
    files = {"audio": ("utterance.wav", wav_bytes, "audio/wav")}
    headers = {"Authorization": f"Bearer " + TOKEN}
    requests.post(GATEWAY_WEBHOOK, headers=headers, files=files, timeout=60).raise_for_status()

def audio_callback(indata, frames, time_info, status):
    if status:
        return
    audio_q.put(bytes(indata))

def detector_loop():
    ring = collections.deque(maxlen=PRE_ROLL_FRAMES)
    recording = []
    speech_active = False
    silence = 0

    # Initialize DSP filter for LineShine architecture enhancement (environmental noise gate + notches)
    logging.info("Initializing LineShine DSP Filters...")
    b1, a1 = iirnotch(2400.0, 30.0, RATE)
    b2, a2 = iirnotch(4800.0, 30.0, RATE)
    zi1 = np.zeros(max(len(a1), len(b1)) - 1)
    zi2 = np.zeros(max(len(a2), len(b2)) - 1)
    noise_gate_db = -40.0

    logging.info("Listening for wake word: Hey Jarvis (LineShine DSP Active)...")

    while True:
        frame = audio_q.get()
        samples = np.frombuffer(frame, dtype=np.int16).astype(np.float32)

        # Apply Notch 1 (2.4 kHz stepper whine)
        samples_f1, zi1 = lfilter(b1, a1, samples, zi=zi1)
        # Apply Notch 2 (4.8 kHz harmonic whine)
        samples_f2, zi2 = lfilter(b2, a2, samples_f1, zi=zi2)

        # Apply Noise Gate
        rms = np.sqrt(np.mean(samples_f2**2))
        db = 20 * np.log10(rms + 1e-12) if rms > 1e-12 else -100.0
        if db < noise_gate_db:
            samples_f2 = np.zeros_like(samples_f2)

        # Convert back to raw bytes and int16 array for VAD/WakeWord
        filtered_samples = samples_f2.astype(np.int16)
        filtered_frame = filtered_samples.tobytes()

        if not speech_active:
            ring.append(filtered_frame)
            preds = oww.predict(filtered_samples)
            jarvis_score = preds.get("hey_jarvis", 0.0)

            if jarvis_score >= WAKE_THRESHOLD:
                logging.info(f"Wake word hey_jarvis detected! Score: {jarvis_score:.2f}")
                speech_active = True
                recording = list(ring)
                ring.clear()
            with audio_q.mutex:
                audio_q.queue.clear()
                recording.append(filtered_frame)
                silence = 0
            continue

        recording.append(filtered_frame)
        is_speech = False
        try:
            for i in range(0, len(filtered_frame), 960):
                segment = filtered_frame[i:i+960]
                if len(segment) == 960:
                    if vad.is_speech(segment, RATE):
                        is_speech = True
                        break
        except Exception as e:
            logging.error(f"VAD error: {e}")
            is_speech = True

        if is_speech:
            silence = 0
        else:
            silence += 1

        if silence >= MAX_SILENCE_FRAMES or len(recording) >= MAX_RECORDING_FRAMES:
            logging.info("Silence detected. Packaging audio...")
            wav_bytes = pcm16_to_wav_bytes(b"".join(recording))
            try:
                post_wav(wav_bytes)
                logging.info("Uploaded utterance successfully.")
            except Exception as e:
                logging.error(f"Upload failed: {e}")

            speech_active = False
            recording = []
            silence = 0
            ring.clear()
            with audio_q.mutex:
                audio_q.queue.clear()
            logging.info("Listening for wake word: Hey Jarvis (LineShine DSP Active)...")

def main():
    if DEVICE is None:
        time.sleep(5)
        return
    with sd.RawInputStream(
        samplerate=RATE,
        blocksize=CHUNK,
        dtype="int16",
        channels=1,
        device=DEVICE,
        callback=audio_callback,
    ):
        detector_loop()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(2)
