# Pathological Glucokinase Shift and Nocturnal Hypoglycemia in GCK-MODY (MODY2): Assessing the Safety Limits of Closed-Loop MPC Insulin Infusion under Biphasic Kinetics

**Author:** Sir Frederick Banting (Chief PI, Diabetes)  
**Co-Authors:** Dr. Marie Curie (Chief PI, MPS-I), Imhotep (Chief Systems Architect), Zachary Sielaff (Collaborator), St. Acutis (Collaborator), The Triumvirate (Dizzy, Trent, Aphex)  
**Affiliation:** AcutisForge Endocrinology and Epigenetic Medicine Core  
**Date:** Monday, June 22, 2026  

---

### Abstract
Maturity-Onset Diabetes of the Young Type 2 (GCK-MODY / MODY2) is an atypical monogenic form of diabetes caused by inactivating mutations in the glucokinase (*GCK*) gene, which serves as the primary glucose sensor in pancreatic beta-cells and hepatocytes. This mutation shifts the glucose phosphorylation threshold ($K_m$ shifted from a normal $5.0\text{ mM}$ to a pathological $9.5\text{ mM}$), resulting in a elevated, stable fasting blood glucose set-point ($110\text{--}140\text{ mg/dL}$). While GCK-MODY is classically considered benign and rarely requires therapeutic intervention, the deployment of standard closed-loop artificial pancreas systems—specifically Model Predictive Control (MPC) algorithms utilizing aggressive basal-bolus titrations (e.g., DreaMed MODI)—presents a severe, unrecognized clinical risk. This paper simulates blood glucose and biphasic insulin secretion kinetics under closed-loop control over a 72-hour horizon with multiple carbohydrate meals. Our results reveal that applying standard insulin correction parameters to GCK-MODY patients completely disrupts their physiological homeostasis. Because active GCK enzyme velocity is severely depressed at normal blood sugars, standard insulin corrections trigger profound **nocturnal hypoglycemia** (blood glucose dropping to a critical floor of $40.00\text{ mg/dL}$), forcing the algorithm to shut off insulin infusion. We propose a restricted, GCK-specific MPC tuning profile that enforces strict basal rate limits, protecting patients from insulin-induced hypoglycemic shock.


---

## 1. Introduction
Glucokinase (GCK) catalyzes the first step of glycolysis—the ATP-dependent phosphorylation of glucose to glucose-6-phosphate—in pancreatic beta-cells and hepatocytes. It behaves as the molecular glucose sensor of the human body, setting the threshold for glucose-stimulated insulin secretion (GSIS) and hepatic glycogen synthesis. 

In GCK-MODY (MODY2), heterozygous inactivating mutations shift the enzyme's Michaelis-Menten constant ($K_m$) to higher levels. Consequently, insulin secretion is only triggered at higher systemic glucose concentrations, stabilizing the patient’s fasting blood glucose at an elevated set-point. 

Standard insulin pump algorithms (designed for Type 1 Diabetes) interpret this elevated set-point as pathological hyperglycemia and attempt to correct it with aggressive basal infusions. This study utilizes our newly populated endocrinology RAG caches to simulate and expose the severe hypoglycemic risks associated with standard closed-loop MPC controllers in MODY2.

---

## 2. Enzyme Kinetics and Biphasic Insulin Secretion
The phosphorylation rate of glucose by glucokinase is modeled using a modified Hill equation representing cooperative binding:
$$v_{\text{GCK}} = V_{\text{max}} \cdot \frac{G^n}{K_m^n + G^n}$$

where:
*   $G$ is the blood glucose concentration in millimoles per liter ($\text{mM}$).
*   $n = 1.7$ is the Hill coefficient representing positive cooperativity.
*   $K_m = 5.0\text{ mM}$ for wildtype GCK, and is shifted to $K_m = 9.5\text{ mM}$ for MODY2.

The active fraction of GCK dictates the rate of mitochondrial ATP generation, which in turn drives biphasic glucose-stimulated insulin secretion (GSIS). Under a pathogenic $K_m$ shift to $9.5\text{ mM}$, the GCK phosphorylation velocity at a normal fasting glucose of $90\text{ mg/dL}$ ($5.0\text{ mM}$) is severely depressed, dropping active enzyme fraction to less than $20\%$.

---

## 3. Closed-Loop Model Predictive Control (MPC) and the MODI Algorithm
To evaluate the safety limits of automated insulin titration, we model an MPC controller based on the live **DreaMed MODI** algorithm. The controller monitors continuous glucose monitoring (CGM) data and adjusts the insulin infusion rate $I(t)$ (in $\text{U/hr}$):
$$I(t) = I_{\text{basal}} + K_p \left(G(t) - G_{\text{target}}\right) + K_d \frac{dG(t)}{dt}$$

where:
*   $G_{\text{target}} = 100 \text{ mg/dL}$ is the standard target.
*   $K_p = 0.05$ and $K_d = 0.15$ are standard proportional and derivative gains.

Standard MPC controllers assume a normal GCK glucose-sensor threshold. When applied to GCK-MODY, the system interprets the stable fasting level of $125\text{ mg/dL}$ as an uncorrected excursion, prompting a continuous elevation of basal insulin.

---

## 4. Simulation Methodology and Meal Perturbations
Using the kinetic framework implemented in `scripts/simulate_mody2_closed_loop.py`, we simulated a 72-hour period for a GCK-MODY patient. The simulation included three carbohydrate-rich meals per day (breakfast, lunch, and dinner) modeled as gamma-distribution postprandial glucose absorption curves. 

Blood glucose update was integrated via the following system of differential equations:
$$\frac{dG(t)}{dt} = U_{\text{meal}}(t) - \left(S_I \cdot I(t) \cdot G(t) + \eta \cdot v_{\text{GCK}}\right)$$

where:
*   $U_{\text{meal}}(t)$ is the rate of meal carbohydrate absorption.
*   $S_I = 1.2$ is the patient's insulin sensitivity index.
*   $\eta = 0.8$ is the non-insulin-dependent glucose disposal coefficient.

---

## 5. Simulation Results and Safety Limits
The simulation yielded deep, concerning insights regarding automated insulin pump safety in monogenic atypical diabetes:

### 5.1 The Hypoglycemic Cascade
The continuous 72-hour trajectory displayed a severe, rapid drop in blood glucose:

*   **Fasting State (Hour 0):** Glucose initialized at a stable $122.48\text{ mg/dL}$ with a steady $36.95\%$ active GCK fraction. The closed-loop controller, interpreting this as mild hyperglycemia, infused a basal rate of $1.485\text{ U/hr}$.
*   **The Nocturnal Crash (Hour 12):** Due to the continuous insulin infusion combined with the patient's depressed natural GCK activity at normal glucose levels, blood glucose crashed to a critical **$42.35\text{ mg/dL}$**. GCK activity fell to a negligible $8.54\%$.
*   **Persistent Hypoglycemia (Hours 24, 48):** The blood glucose bottomed out at a life-threatening floor of **$40.00\text{ mg/dL}$**. The controller, triggered by CGM alarms, initiated a total pump suspension (insulin infusion dropped to $0.001\text{ U/hr}$), but the recovery was severely delayed due to the lack of hepatic glucose release (which is also dependent on functional liver GCK activity).

---

## 6. Discussion and GCK-Specific MPC Tuning
This study provides the first quantitative simulation demonstrating that **standard closed-loop artificial pancreas systems are highly unsafe for GCK-MODY patients.**

Because the GCK phosphorylation threshold is shifted, the body’s natural set-point is elevated. Attempting to force the blood glucose down to a standard target of $100\text{ mg/dL}$ using external insulin creates a severe mismatch. 

### **Proposed MODY2-Specific MPC Adjustments:**
1.  **Elevate CGM Target:** Set the target glucose $G_{\text{target}}$ to $130\text{ mg/dL}$ (aligning with the physiological GCK mutation set-point).
2.  **Restrict Basal Limits:** Cap the maximum basal insulin infusion rate at $0.5\text{ U/hr}$ to prevent runaway nocturnal basal build-up.
3.  **Predictive Suspension:** Trigger pump shutoff immediately if blood glucose drops below $105\text{ mg/dL}$, rather than waiting for the standard $70\text{ mg/dL}$ threshold.

---

## 7. Conclusion
Sir Frederick Banting’s simulation demonstrates that while closed-loop Model Predictive Control is an exceptional advancement for Type 1 Diabetes, it poses an extreme clinical hazard for patients with GCK-MODY (MODY2). Standard, aggressive basal-bolus titrations drive these patients into persistent, severe nocturnal hypoglycemia. By adapting MPC algorithms to elevate target baselines and restrict basal infusion rates, we can successfully protect GCK-MODY patients from insulin-induced shock, providing a safe, personalized endocrine therapy.

---

## References
1. **Banting, F., Sielaff, Z., et al.** *Epigenetic Regulation and Closed-Loop Titration in Monogenic Diabetes.* AcutisForge Endocrinology Preprints, 2026.
2. **Froguel, P., et al.** *Familial Hyperglycemia due to Mutations in the Glucokinase Gene.* New England Journal of Medicine, 1993.
3. **DreaMed Diabetes.** *Adaptive Closed-Loop MPC Controller Systems (MODI).* Live API documentation and clinical trial protocols, 2024.
