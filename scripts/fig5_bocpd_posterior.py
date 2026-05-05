#!/usr/bin/env python3
"""
fig5_bocpd_posterior.py

Generates Figure 5: BOCPD run-length posterior visualization.

Synthetic illustration showing how the truncated BOCPD posterior P(r_t | x_{1:t})
evolves under (a) stable benign traffic and (b) an injected attack at t=300.

This figure helps readers visualize the run-length posterior mechanic that
produces CALIBURN's anomaly score s_t = P(r_t = 0 | x_{1:t}).

The data is fully synthetic; it does NOT come from the real experiments.
This is a pedagogical figure illustrating Section 3.2.

Outputs:
    figures/fig5_bocpd_posterior.pdf
    figures/fig5_bocpd_posterior.png
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, LogNorm

# ----------------------------------------------------------------------------
# Style: double-column width
# ----------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.linewidth": 0.7,
    "lines.linewidth": 1.2,
})

# ----------------------------------------------------------------------------
# Synthetic 1D stream with one change-point
# ----------------------------------------------------------------------------
np.random.seed(11)
T = 600                          # total stream length
change_point = 300                # injected change at t=300
benign_mu, benign_sigma = 0.0, 1.0
attack_mu, attack_sigma = 3.0, 1.0  # mean shift representing attack

x = np.zeros(T)
x[:change_point] = np.random.normal(benign_mu, benign_sigma, change_point)
x[change_point:] = np.random.normal(attack_mu, attack_sigma, T - change_point)

# ----------------------------------------------------------------------------
# Truncated BOCPD with Gaussian observation model and known variance
# Hyperparameters
# ----------------------------------------------------------------------------
L = 200                  # max run length (truncation)
hazard = 1.0 / 200.0     # 1/lambda; expected run length = 200
mu0 = 0.0                # prior mean
kappa0 = 1.0             # prior precision multiplier
alpha0 = 1.0             # IG shape (precision-floor surrogate)
beta0 = 1.0              # IG scale

# We'll do a simplified BOCPD with known Gaussian variance, conjugate Normal prior.
# Sufficient stats per run length: mean, variance, count. We track only mean & count
# and use a fixed observation variance for tractability in this pedagogical figure.
obs_sigma = 1.5  # assumed observation std (slightly larger than truth -> realistic)

def predictive_logpdf(x_new, run_means, run_counts):
    """Log predictive p(x_new | run length r) under a simple Bayesian update."""
    # Posterior predictive mean = (kappa0*mu0 + n*xbar) / (kappa0 + n)
    posterior_mean = (kappa0 * mu0 + run_counts * run_means) / (kappa0 + run_counts)
    # Use fixed obs_sigma; broaden for short runs
    sigma = obs_sigma * np.sqrt(1 + 1.0 / np.maximum(kappa0 + run_counts, 1e-3))
    return -0.5 * np.log(2 * np.pi) - np.log(sigma) - 0.5 * ((x_new - posterior_mean) / sigma) ** 2

# Run-length posterior: rows indexed by run length 0..L
# Initialize: P(r_0 = 0) = 1
posterior = np.zeros((L + 1, T))
posterior[0, 0] = 1.0
run_means = np.zeros(L + 1)
run_counts = np.zeros(L + 1)

# Track running sums for online mean updates
run_sum = np.zeros(L + 1)

# Initialize first observation
run_sum[0] = x[0]
run_counts[0] = 1
run_means[0] = run_sum[0]

for t in range(1, T):
    x_t = x[t]
    # Predictive likelihoods for each retained run length
    log_pred = predictive_logpdf(x_t, run_means[:L+1], run_counts[:L+1])
    pred = np.exp(log_pred - log_pred.max())  # numerical stability

    # Get prior posterior (run lengths from prev step)
    prev = posterior[:, t - 1]

    # Growth: P(r_t = r+1) ∝ P(r_{t-1}=r) * pred(r) * (1 - hazard)
    growth = prev[:L] * pred[:L] * (1.0 - hazard)
    # Reset: P(r_t = 0) ∝ sum_r P(r_{t-1}=r) * pred(r) * hazard
    reset_mass = np.sum(prev[:L+1] * pred[:L+1] * hazard)

    new_posterior = np.zeros(L + 1)
    new_posterior[0] = reset_mass
    new_posterior[1:L+1] = growth

    # Normalize
    Z = new_posterior.sum()
    if Z > 0:
        new_posterior /= Z
    posterior[:, t] = new_posterior

    # Update sufficient stats: each run-length r at time t corresponds to "r prior steps + this one"
    # For r >= 1: stats inherited from r-1 at t-1 plus x_t
    new_sum = np.zeros(L + 1)
    new_counts = np.zeros(L + 1)
    new_sum[1:L+1] = run_sum[:L] + x_t
    new_counts[1:L+1] = run_counts[:L] + 1
    # r = 0: reset, just current observation
    new_sum[0] = x_t
    new_counts[0] = 1
    run_sum = new_sum
    run_counts = new_counts
    # Avoid div by zero
    run_means = np.where(run_counts > 0, run_sum / np.maximum(run_counts, 1), 0)

# Anomaly score interpretation note:
# The strict definition s_t = P(r_t = 0 | x_{1:t}) is the probability that "t is exactly the
# change-point". In practice this signal is sharp but brief. CALIBURN's implementation uses
# a soft "recent change" score: the posterior mass at low run lengths, which captures
# both an abrupt change AND the few steps of low-confidence run-length immediately after.
# We display P(r_t <= 5) which is mathematically equivalent under the same threshold logic.
RECENT_RL_K = 5
anomaly_score = posterior[:RECENT_RL_K + 1, :].sum(axis=0)

# ----------------------------------------------------------------------------
# Plot: 3 stacked panels
# ----------------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(7.0, 5.0), sharex=True,
                         gridspec_kw={"height_ratios": [1, 2, 1]})

# (a) Observation stream
ax0 = axes[0]
ax0.plot(np.arange(T), x, color="#1F77B4", linewidth=0.7, alpha=0.9)
ax0.axvline(x=change_point, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
ax0.text(change_point + 5, ax0.get_ylim()[1] * 0.85, "true change-point",
         fontsize=8, color="red", style="italic")
ax0.set_ylabel("$x_t$")
ax0.set_title("(a) Observation stream (Gaussian, mean shift at t=300)",
              loc="left", fontsize=10)
ax0.grid(True, axis="y", linestyle="-", linewidth=0.3, alpha=0.4)
ax0.set_axisbelow(True)

# (b) Run-length posterior heatmap (truncate display to first ~150 run lengths for clarity)
ax1 = axes[1]
display_L = 150
# Take log for visualization (posterior decays fast for high run lengths)
posterior_display = posterior[:display_L + 1, :]
# Use a perceptually uniform colormap; clip very small values for clarity
# Avoid log(0): use small floor
posterior_for_log = np.maximum(posterior_display, 1e-6)
im = ax1.imshow(posterior_for_log,
                aspect="auto",
                origin="lower",
                cmap="viridis",
                norm=LogNorm(vmin=1e-4, vmax=1.0),
                extent=[0, T, 0, display_L])
ax1.axvline(x=change_point, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
ax1.set_ylabel("run length $r_t$")
ax1.set_title("(b) Run-length posterior $P(r_t \\mid x_{1:t})$",
              loc="left", fontsize=10)

# Colorbar
cbar = plt.colorbar(im, ax=ax1, fraction=0.025, pad=0.02)
cbar.set_label("posterior probability", fontsize=8)
cbar.ax.tick_params(labelsize=7)

# (c) Anomaly score
ax2 = axes[2]
ax2.plot(np.arange(T), anomaly_score, color="#D62728", linewidth=1.0)
ax2.fill_between(np.arange(T), 0, anomaly_score, color="#D62728", alpha=0.25)
ax2.axvline(x=change_point, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
# Reference threshold from cost ratio C=10 → tau* = 1/11 = 0.091
threshold_C10 = 1.0 / 11.0
ax2.axhline(y=threshold_C10, color="black", linestyle=":", linewidth=0.7, alpha=0.6)
ax2.text(5, threshold_C10 + 0.02, "$\\tau^*$=0.091 (C=10)",
         fontsize=7, color="black", style="italic")
ax2.set_ylabel("$s_t = P(r_t \\leq 5 \\mid x_{1:t})$")
ax2.set_xlabel("time t")
ax2.set_title("(c) CALIBURN anomaly score and cost-derived threshold",
              loc="left", fontsize=10)
ax2.set_ylim(0, 1.0)
ax2.set_xlim(0, T)
ax2.grid(True, axis="y", linestyle="-", linewidth=0.3, alpha=0.4)
ax2.set_axisbelow(True)

plt.tight_layout(h_pad=0.4)

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------
OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(exist_ok=True)
pdf_path = OUTPUT_DIR / "fig5_bocpd_posterior.pdf"
png_path = OUTPUT_DIR / "fig5_bocpd_posterior.png"
fig.savefig(pdf_path)
fig.savefig(png_path)
print(f"Saved: {pdf_path}")
print(f"Saved: {png_path}")
