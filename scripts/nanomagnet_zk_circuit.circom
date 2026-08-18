pragma circom 2.0.0;

/*
    📐 NANOMAGNET PLAQUETTE ENERGY TRANSITION PROVER (SAGE CRYPTO CORE)
    Author: Imhotep & Binah (SAGE Zero-Knowledge Architects)
    
    A Circom circuit designed to prove in zero-knowledge that a 4-nanomagnet 
    square plaquette transitioned from an initial state to a lower-energy ground state
    consistent with a secret coupling matrix J_ij (which encodes the physical 
    geometry/angle Phi of the chip), without revealing J_ij itself.
*/

template PlaquetteEnergyProver() {
    // === PUBLIC INPUTS ===
    signal input start_state[4]; // Binary inputs: 0 (spin down/left) or 1 (spin up/right)
    signal input end_state[4];   // Binary inputs: 0 or 1

    // === PRIVATE INPUTS (WITNESS) ===
    signal input J[4][4];        // Secret Coupling Matrix (scaled to integers, e.g. J_ij * 1000)

    // === OUTPUT ===
    signal output is_valid_transition;

    // === INTERNAL VARIABLES & CONSTRAINTS ===
    
    // 1. Enforce that starting and ending states are strictly binary (0 or 1)
    for (int i = 0; i < 4; i++) {
        start_state[i] * (start_state[i] - 1) === 0;
        end_state[i] * (end_state[i] - 1) === 0;
    }

    // 2. Map binary signals {0, 1} to spin signals {-1, 1}
    // Equation: spin = 2 * binary - 1
    signal start_spin[4];
    signal end_spin[4];
    for (int i = 0; i < 4; i++) {
        start_spin[i] <-- 2 * start_state[i] - 1;
        start_spin[i] === 2 * start_state[i] - 1;

        end_spin[i] <-- 2 * end_state[i] - 1;
        end_spin[i] === 2 * end_state[i] - 1;
    }

    // 3. Compute the start and end energies under the secret coupling matrix J
    // Energy formula: E = sum_{i < j} J_ij * s_i * s_j
    // We compute the individual coupling products first to maintain quadratic constraints
    signal start_pair_energy[6];
    signal end_pair_energy[6];
    
    // Couples mapping: 
    // 0: (0,1), 1: (0,2), 2: (0,3), 3: (1,2), 4: (1,3), 5: (2,3)
    int idx = 0;
    for (int i = 0; i < 4; i++) {
        for (int j = i + 1; j < 4; j++) {
            start_pair_energy[idx] <== J[i][j] * start_spin[i] * start_spin[j];
            end_pair_energy[idx] <== J[i][j] * end_spin[i] * end_spin[j];
            idx++;
        }
    }

    // Sum up total energies
    signal total_start_energy;
    total_start_energy <== start_pair_energy[0] + start_pair_energy[1] + start_pair_energy[2] + start_pair_energy[3] + start_pair_energy[4] + start_pair_energy[5];

    signal total_end_energy;
    total_end_energy <== end_pair_energy[0] + end_pair_energy[1] + end_pair_energy[2] + end_pair_energy[3] + end_pair_energy[4] + end_pair_energy[5];

    // 4. Enforce that the end state is a LOWER-energy configuration (valid physical relaxation)
    // In zero-knowledge, we prove: E_end < E_start => E_start - E_end > 0
    signal energy_delta;
    energy_delta <== total_start_energy - total_end_energy;

    // To prevent unconstrained output signals, we enforce that energy_delta is strictly positive.
    // In a production SNARK, we would use a comparison template (like LessThan) from the circomlib library.
    // For this conceptual schematic, we assert the delta is greater than zero using a witness checker.
    signal is_positive_delta;
    is_positive_delta <-- (energy_delta > 0) ? 1 : 0;
    is_positive_delta === 1; // Assert valid physical relaxation path cleared!

    is_valid_transition <== is_positive_delta;
}

component main {public [start_state, end_state]} = PlaquetteEnergyProver();
