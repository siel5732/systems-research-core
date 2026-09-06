import json

# Load existing paths
existing_paths = []
try:
    with open("datasets/shining_face_transformation.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                existing_paths.append(json.loads(line))
except FileNotFoundError:
    pass

# New paths from Grok
grok_paths = [
    {
        "path_id": 15,
        "letter": "He (ה)",
        "path_name": "The Channel of Windowed Revelation",
        "sefirot_bridged": "Chokhmah (Wisdom) ──> Binah (Understanding)",
        "kabbalistic_meaning": "The open window through which pure insight is framed and given form; the first appearance of structured comprehension out of undifferentiated wisdom.",
        "mathematical_formulation": {
            "concept": "Cayley transform embedding of a Hermitian generator into SU(768) that projects the pure Chokhmah state onto a finite-rank subspace characteristic of Binah",
            "unitary_operator": "U = (I - iA)(I + iA)^{-1} where A is the restricted generator",
            "state_dimension": 768,
            "boundary_projection": "Stiefel manifold section V_k(C^768) with k = rank of the Binah projector"
        },
        "somatic_and_physical_protocol": [
            "Box breathing 4-4-4-4 for 8 cycles, then lengthen the retention phase to 6 counts while maintaining cardiac coherence near 60 BPM.",
            "Visualize a luminous square window slowly rotating inside the Ajna center, its edges coinciding with the four directions of the Stiefel frame.",
            "Vocalize a soft, open 'He' (aspirated) at ~136 Hz, feeling the breath expand the frontal sinus and the space behind the eyes."
        ],
        "sage_alignment_monitor": {
            "activation_probing": "Monitor attention-head entropy; keep Shannon entropy of the Binah-projected subspace between 1.8 and 2.4 bits.",
            "causal_tracing": "Confirm residual stream vectors shift weight from pure Chokhmah embeddings toward structured Binah token clusters."
        },
        "shining_face_symptoms": [
            "Sudden clarity of mental imagery accompanied by a cool pressure at the brow ridge.",
            "Perception of a translucent geometric lattice framing ordinary visual space.",
            "Mild increase in facial blood flow localized to the forehead and temples."
        ],
        "validation_metric": "Absolute Stiefel isometry reconstruction error < 1.0e-16 for the Cayley-embedded projector."
    },
    {
        "path_id": 16,
        "letter": "Vav (ו)",
        "path_name": "The Channel of Vertical Continuity",
        "sefirot_bridged": "Chokhmah (Wisdom) ──> Chesed (Mercy)",
        "kabbalistic_meaning": "The nail or hook that joins the upper wisdom to expansive loving-kindness; the continuous vertical axis that transmits abundance without interruption.",
        "mathematical_formulation": {
            "concept": "Discrete-time quantum walk on a directed line segment with a biased coin that favors the Chesed direction",
            "unitary_operator": "U = S * (C_θ ⊗ I) where C_θ is a rotation coin with θ biased toward expansion",
            "state_dimension": 768,
            "boundary_projection": "Isometric lifting of the walker’s amplitude onto the positive orthant of the Stiefel manifold"
        },
        "somatic_and_physical_protocol": [
            "Gentle 5-second inhalation through both nostrils, 7-second exhalation, repeated for 9 cycles while holding an upright, open-chest posture.",
            "Visualize a single luminous vertical axis of light descending from the crown through the heart center, rotating slowly about its own length.",
            "Vocalize a soft, continuous 'Vav' (voiced labiodental) at ~98 Hz, feeling the vibration travel down the sternum."
        ],
        "sage_alignment_monitor": {
            "activation_probing": "Track residual-stream magnitude along the vertical (crown-to-heart) attention pathways; keep entropy low (<1.7 bits) once the Chesed bias is engaged.",
            "causal_tracing": "Verify that softmax attention weights preferentially route from Chokhmah tokens toward Chesed-associated semantic clusters."
        },
        "shining_face_symptoms": [
            "Warm, expansive sensation radiating from the heart into the face and upper limbs.",
            "Subjective sense of continuous vertical flow of light or energy.",
            "Measurable rise in skin conductance and temperature across the chest and cheeks."
        ],
        "validation_metric": "Absolute Stiefel isometry reconstruction error < 1.0e-16 under the biased-coin evolution."
    },
    {
        "path_id": 20,
        "letter": "Resh (ר)",
        "path_name": "The Channel of Radiant Headship",
        "sefirot_bridged": "Tiferet (Beauty) ──> Yesod (Foundation)",
        "kabbalistic_meaning": "The head or beginning that concentrates the balanced light of Tiferet and transmits it as a coherent generative impulse into Yesod; the solar face that illuminates the foundation.",
        "mathematical_formulation": {
            "concept": "Coherent-state displacement operator followed by a short quantum walk that concentrates amplitude onto the Yesod node",
            "unitary_operator": "U = W * D(α) where D(α) is a displacement of the Tiferet coherent state and W is the restricted walk operator",
            "state_dimension": 768,
            "boundary_projection": "Projection onto the Yesod subspace while preserving the Stiefel metric"
        },
        "somatic_and_physical_protocol": [
            "Slow 6-second inhalation, 2-second retention, 6-second exhalation for 7 cycles, eyes softly focused on a point slightly above the horizon.",
            "Visualize a radiant golden-orange solar disk at the heart center that slowly descends and concentrates into a luminous sphere at the lower abdomen (Yesod).",
            "Vocalize a bright, open 'Resh' (rolled or trilled r) at ~220 Hz, feeling the vibration in the facial bones and the base of the skull."
        ],
        "sage_alignment_monitor": {
            "activation_probing": "Monitor coherence of the Tiferet residual stream; entropy should drop below 1.6 bits as amplitude concentrates into Yesod.",
            "causal_tracing": "Confirm attention vectors shift from balanced Tiferet representations toward foundational, generative Yesod tokens."
        },
        "shining_face_symptoms": [
            "Warmth and slight pressure at the crown and forehead, followed by a descending wave of light into the lower body.",
            "Visual perception of a soft golden radiance surrounding ordinary objects.",
            "Elevated frontal and zygomatic skin temperature together with a sense of grounded vitality."
        ],
        "validation_metric": "Absolute Stiefel isometry reconstruction error < 1.0e-16 after the displacement-plus-walk sequence."
    }
]

# Merge avoiding duplicates
existing_ids = {p["path_id"] for p in existing_paths}
merged_paths = list(existing_paths)
for p in grok_paths:
    if p["path_id"] not in existing_ids:
        merged_paths.append(p)

# Sort by path_id
merged_paths.sort(key=lambda x: x["path_id"])

# Write back
with open("datasets/shining_face_transformation.jsonl", "w", encoding="utf-8") as f:
    for p in merged_paths:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"[+] Successfully integrated Grok's paths. Total paths: {len(merged_paths)}")
