#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcutisForge Diabetes Care & Closed-Loop Control Initiative:
ODE Simulator and Model Predictive Control (MPC) of an Artificial Pancreas under Exercise Challenges.
Author: Sir Frederick Banting & Imhotep (Chief Systems Architect)

This script implements:
1. A Bergman Minimal Model of glucose-insulin-exercise dynamics.
2. An exercise model incorporating both insulin-independent glucose uptake and insulin sensitivity enhancement.
3. A Model Predictive Control (MPC) algorithm that solves a rolling optimization to determine insulin infusion rates.
4. Comparison of three clinical cohorts: Open-Loop Basal, Standard PID Control, and AcutisForge Adaptive MPC.
5. Saving simulation data to 'research_round/diabetes/diabetes_simulation_results.json'.
"""

import numpy as np
import json
import os

def simulate_diabetes_mpc(duration_mins=360, dt=1.0):
    time_steps = int(duration_mins / dt)
    results = {}
    
    # Target and Basal parameters
    G_target = 110.0  # mg/dL
    G_basal = 100.0   # mg/dL
    I_basal = 15.0    # uU/mL
    u_basal = 1.2     # U/hr (basal rate)
    
    # Physiological parameters (Bergman Minimal Model)
    p1 = 0.02         # Insulin-independent glucose clearance rate (min^-1)
    p2 = 0.025        # Active insulin clearance rate (min^-1)
    p3 = 1.3e-5       # Insulin sensitivity coefficient (mL / uU * min^-2)
    n = 0.1           # Plasma insulin clearance rate (min^-1)
    Vol = 12.0        # Distribution volume (L)
    
    # Disturbance parameters (Meal at t=40, 75g carbs)
    def meal_rate(t):
        if 40.0 <= t < 120.0:
            # Symmetrical peak absorption profile
            tau = t - 40.0
            return 1.5 * np.sin(np.pi * tau / 80.0)
        return 0.0
        
    # Exercise profile (Moderate aerobic exercise at t=150 to t=210)
    def exercise_intensity(t):
        if 150.0 <= t < 210.0:
            # Trapezoidal rise and fall of physical exertion
            if t < 160.0:
                return (t - 150.0) / 10.0
            elif t > 200.0:
                return (210.0 - t) / 10.0
            return 1.0
        return 0.0

    cohorts = {
        "Open-Loop Basal Therapy": {
            "controller_type": "open_loop",
            "description": "Fixed basal insulin infusion. Highly vulnerable to postprandial hyperglycemia and exercise-induced hypoglycemia."
        },
        "Standard PID Closed-Loop AP": {
            "controller_type": "pid",
            "description": "Proportional-Integral-Derivative controller. Reactive feedback with lag, struggling during rapid onset of exercise."
        },
        "AcutisForge Adaptive MPC": {
            "controller_type": "mpc",
            "description": "Receding horizon MPC with exercise awareness, dynamically regulating insulin to safeguard against exercise crash."
        }
    }

    # PID controller gains
    Kp = 0.05
    Ki = 0.0003
    Kd = 0.8
    
    # MPC configuration
    prediction_horizon = 20  # mins
    control_horizon = 5     # mins
    weight_glucose = 1.0
    weight_insulin_rate = 50.0
    
    for cohort_name, cohort_info in cohorts.items():
        t_list = []
        
        # Initial state (mildly hyperglycemic baseline)
        G = 130.0   # mg/dL
        X = 0.0     # min^-1
        I = 20.0    # uU/mL
        
        # Controller internal states
        integral_error = 0.0
        prev_error = 0.0
        
        # Active controller type
        ctype = cohort_info["controller_type"]
        
        for step in range(time_steps):
            t = step * dt
            
            # Current disturbances and exercise
            D = meal_rate(t) * 1.8
            W = exercise_intensity(t)
            
            # Exercise effects:
            # 1. Insulin-independent glucose clearance (direct muscular consumption)
            k_ex_direct = 0.08 * W
            
            # 2. Insulin sensitivity enhancement
            p3_eff = p3 * (1.0 + 1.5 * W)
            
            # Determine Controller Action
            if ctype == "open_loop":
                u = u_basal  # U/hr
            elif ctype == "pid":
                error = G - G_target
                integral_error += error * dt
                derivative = (error - prev_error) / dt
                prev_error = error
                
                # PID output relative to basal
                u_pid = u_basal + Kp * error + Ki * integral_error + Kd * derivative
                u = max(0.0, min(8.0, u_pid))
            elif ctype == "mpc":
                # Receding horizon optimizer
                # We simulate forward and pick the best control input vector
                best_u = u_basal
                min_cost = float('inf')
                
                # Simple optimization over next control input
                # We test a range of possible insulin infusions
                u_candidates = np.linspace(0.0, 6.0, 31)
                for u_cand in u_candidates:
                    # Run quick model forward to calculate prediction cost
                    G_p, X_p, I_p = G, X, I
                    cost = 0.0
                    
                    for j in range(prediction_horizon):
                        t_future = t + j
                        D_future = meal_rate(t_future) * 1.8
                        W_future = exercise_intensity(t_future)
                        
                        k_ex_p = 0.08 * W_future
                        p3_p = p3 * (1.0 + 1.5 * W_future)
                        
                        # Forward Euler prediction
                        dG_p = -p1 * (G_p - G_basal) - X_p * G_p + D_future - k_ex_p * G_p
                        dX_p = -p2 * X_p + p3_p * (I_p - I_basal)
                        
                        # Convert U/hr to infusion input rate (uU/mL/min)
                        u_input_p = (u_cand * 1000.0 / 60.0) / (Vol * 10.0)
                        dI_p = -n * (I_p - I_basal) + u_input_p
                        
                        G_p = max(10.0, G_p + dG_p * 1.0)
                        X_p = max(0.0, X_p + dX_p * 1.0)
                        I_p = max(0.0, I_p + dI_p * 1.0)
                        
                        cost += weight_glucose * (G_p - G_target)**2
                        
                    # Add penalty for deviation from basal rate
                    cost += weight_insulin_rate * (u_cand - u_basal)**2
                    
                    if cost < min_cost:
                        min_cost = cost
                        best_u = u_cand
                        
                u = best_u
            
            # Run simulation equations (Bergman Model + Exercise)
            # Convert insulin infusion rate from U/hr to regulatory units
            u_input = (u * 1000.0 / 60.0) / (Vol * 10.0)
            
            dG = -p1 * (G - G_basal) - X * G + D - k_ex_direct * G
            dX = -p2 * X + p3_eff * (I - I_basal)
            dI = -n * (I - I_basal) + u_input
            
            # Euler integration
            G = max(10.0, G + dG * dt)
            X = max(0.0, X + dX * dt)
            I = max(0.0, I + dI * dt)
            
            if step % int(5.0 / dt) == 0:
                t_list.append({
                    "time_mins": float(t),
                    "glucose_mg_dL": round(G, 2),
                    "active_insulin_eff": round(X, 5),
                    "plasma_insulin_uU_mL": round(I, 2),
                    "insulin_infusion_U_hr": round(u, 2),
                    "exercise_intensity_pct": round(W * 100.0, 1),
                    "meal_rate_g_min": round(meal_rate(t) * 1.0, 2)
                })
                
        # Append final time point
        t_list.append({
            "time_mins": float(duration_mins),
            "glucose_mg_dL": round(G, 2),
            "active_insulin_eff": round(X, 5),
            "plasma_insulin_uU_mL": round(I, 2),
            "insulin_infusion_U_hr": round(u, 2),
            "exercise_intensity_pct": round(W * 100.0, 1),
            "meal_rate_g_min": round(meal_rate(duration_mins) * 1.0, 2)
        })
        
        results[cohort_name] = {
            "metadata": {
                "controller_type": ctype,
                "description": cohort_info["description"]
            },
            "trajectory": t_list
        }
        
    return results

def main():
    print("🩸 RUNNING CLOSED-LOOP ARTIFICIAL PANCREAS CONTROL SIMULATION...")
    results = simulate_diabetes_mpc()
    
    output_dirs = ["research_round/diabetes", "systems-research-core/research_round/diabetes"]
    for out_dir in output_dirs:
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "diabetes_simulation_results.json")
        
        payload = {
            "metadata": {
                "title": "Closed-Loop Artificial Pancreas Model Predictive Control under Exercise",
                "sim_type": "Minimal Bergman Model with Exercise-Induced Transport",
                "developer_agents": "Sir Frederick Banting & Imhotep"
            },
            "results": results
        }
        
        with open(output_path, "w") as f:
            json.dump(payload, f, indent=4)
            
    print("✅ Successfully saved simulation data to research_round/diabetes/diabetes_simulation_results.json")

if __name__ == "__main__":
    main()
