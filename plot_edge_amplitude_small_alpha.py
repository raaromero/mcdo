"""
Plot edge amplitude vs alpha, showing full range with key points annotated.
Shows when Gaussian approaches uniform (edge amplitude → 1).
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("data/alpha_sweep")

# Alpha values - key points
alphas = np.array([0.001, 0.01, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0])

# Edge amplitude = exp(-alpha)
edge_amplitude = np.exp(-alphas)

# Continuous line for reference
alpha_fine = np.linspace(0.001, 8.0, 500)
edge_fine = np.exp(-alpha_fine)

fig, ax = plt.subplots(figsize=(12, 6))

# Plot
ax.plot(alpha_fine, edge_fine, 'b-', lw=2, label=r'$A_{\mathrm{edge}} = \exp(-\alpha)$')
ax.plot(alphas, edge_amplitude, 'ko', markersize=10)

# Annotate key points
annotations = {
    0.001: (0.15, 0.95),
    0.01: (0.2, 0.85),
    0.1: (0.4, 0.75),
    0.25: (0.6, 0.65),
    1.0: (1.4, 0.45),
    4.0: (4.5, 0.15),
    8.0: (6.5, 0.08),
}
for a, e in zip(alphas, edge_amplitude):
    if a in annotations:
        tx, ty = annotations[a]
        ax.annotate(f'α={a}\n({e:.3f})', xy=(a, e), xytext=(tx, ty),
                    fontsize=10, ha='left',
                    arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))

# Reference lines and regions
ax.axhline(1.0, color='green', ls='--', lw=1.5, alpha=0.7, label='Uniform (edge = 1)')
ax.axhline(0.018, color='red', ls='--', lw=1.5, alpha=0.7, label=r'α=4 threshold (2%)')

# Shade regions
ax.axvspan(0, 0.25, alpha=0.15, color='green', label='α ≤ 0.25: ≈ Uniform')
ax.axvspan(4, 8, alpha=0.15, color='red', label='α ≥ 4: "Untruncated"')

ax.set_xlabel(r'$\alpha$ (truncation coefficient)', fontsize=14)
ax.set_ylabel(r'Edge Amplitude $A_{\mathrm{edge}} = \exp(-\alpha)$', fontsize=14)
ax.set_title('Edge Amplitude vs Truncation Coefficient α', fontsize=14)
ax.set_xlim(0, 8.5)
ax.set_ylim(0, 1.05)
ax.legend(fontsize=10, loc='upper right')
ax.grid(True, alpha=0.3)
ax.tick_params(labelsize=12)

plt.tight_layout()
save_path = OUTPUT_DIR / "edge_amplitude_vs_alpha_annotated.png"
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {save_path}")
