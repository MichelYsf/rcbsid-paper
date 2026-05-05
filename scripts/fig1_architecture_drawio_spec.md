# Figure 1: CALIBURN Architecture Diagram — draw.io Specification

## Goal

A clean, single-panel block diagram showing CALIBURN's four-layer architecture and explicit data flow from raw network flow to alert output. This is the most important figure in the paper because it visualizes the architectural separation that distinguishes CALIBURN from other streaming detectors.

## Tool

Use **draw.io** (free, web-based) at https://app.diagrams.net.

1. Go to https://app.diagrams.net/
2. Choose "Blank Diagram"
3. Save as: `caliburn_architecture.drawio` (it will store in your Google Drive or download)
4. When done, **File → Export As → SVG** (or PDF)
5. Save the SVG to your repo as `figures/fig1_architecture.svg`
6. Convert to PDF for paper inclusion: open SVG in Inkscape or browser, print to PDF

## Layout (target ~7" wide × ~3" tall, double-column figure)

The diagram should be read **left to right** with four colored vertical "swimlanes," one per layer. Connections between layers go horizontally.

### Color palette (use exactly these hex codes for consistency with other figures)

| Element | Fill | Stroke | Text |
|---|---|---|---|
| Layer 1 box (BOCPD scoring) | #E8F1F8 (light blue) | #1F77B4 | black |
| Layer 2 box (cost-sensitive threshold) | #FCE8E6 (light red) | #D62728 | black |
| Layer 3 box (multi-window burn-rate) | #FFF4E6 (light orange) | #FF7F0E | black |
| Layer 4 box (alert output) | #E8F5E9 (light green) | #2CA02C | black |
| Network flow input | #F5F5F5 (light gray) | #888888 | black |
| Operator inputs | #FFFFFF (white, dashed border) | #555555 | #555555 |
| Arrows | #444444 | — | — |

### Layout grid (left to right)

```
[ x_t flow ]  →  [ Layer 1: BOCPD scoring ]  →  [ Layer 2: Threshold ]  →  [ Layer 3: Burn-rate ]  →  [ Alerts ]
   gray             blue                            red                       orange                    green

                       ↑                             ↑                         ↑
                  hyperparams                    cost ratio C            SLO budget B
                  (H, L, W₀)                     (operator)               (operator)
                  (operator)
```

### Layer-by-layer specification

#### Input box (leftmost, gray)
- **Shape:** Rectangle, rounded corners (radius 8)
- **Size:** 110 × 60 pixels
- **Position:** x=20, y=110 (vertically centered)
- **Text:**
  ```
  Network flow
  x_t ∈ ℝᵈ
  ```
- **Font:** Helvetica 11pt, line spacing 1.4

#### Layer 1: Truncated BOCPD (blue)
- **Shape:** Rectangle, rounded corners (radius 8)
- **Size:** 180 × 100 pixels
- **Position:** x=170, y=90
- **Text (centered):**
  ```
  Layer 1: Streaming scorer
  ─────────────────────
  Truncated BOCPD
  P(rₜ | x₁:ₜ)
  ↓
  sₜ = P(rₜ ≤ K | x₁:ₜ)
  ```
- **Sub-label below box:** "Section 3.2 · O(L) per flow" in 8pt italic gray

#### Layer 2: Cost-sensitive threshold (red)
- **Shape:** Rectangle, rounded corners (radius 8)
- **Size:** 180 × 100 pixels
- **Position:** x=400, y=90
- **Text:**
  ```
  Layer 2: Decision rule
  ─────────────────────
  τ* = 1 / (1 + C)

  zₜ = 1 if sₜ > τ*
  zₜ = 0 otherwise
  ```
- **Sub-label below box:** "Section 3.3 · Elkan-style" in 8pt italic gray

#### Layer 3: Multi-window burn-rate (orange)
- **Shape:** Rectangle, rounded corners (radius 8)
- **Size:** 180 × 100 pixels
- **Position:** x=630, y=90
- **Text:**
  ```
  Layer 3: Alerting policy
  ─────────────────────
  burn rate b_w
  page-fast (5,60) min
  page-slow (30,360) min
  ticket (360,4320) min
  ```
- **Sub-label below box:** "Section 3.4 · SRE Workbook" in 8pt italic gray

#### Output box (rightmost, green)
- **Shape:** Rectangle, rounded corners (radius 8)
- **Size:** 130 × 100 pixels
- **Position:** x=860, y=90
- **Text:**
  ```
  Alert output

  • page-fast
  • page-slow
  • ticket
  • no alert
  ```

#### Operator input boxes (below, dashed)
Three boxes positioned BELOW each of layers 1, 2, 3 with vertical arrows pointing UP into them.

**Below Layer 1** (x=170, y=240, size 180×40):
```
operator: hazard H, max length L,
warm-up W₀
```

**Below Layer 2** (x=400, y=240, size 180×40):
```
operator: cost ratio C = C_FN / C_FP
```

**Below Layer 3** (x=630, y=240, size 180×40):
```
operator: SLO budget B, period T,
burn thresholds {14.4, 6.0, 1.0}
```

### Arrows

**Horizontal flow** (heavy black, 1.5pt, with arrowhead):
- Input box → Layer 1
- Layer 1 → Layer 2 (label "sₜ" mid-arrow, in italic 9pt)
- Layer 2 → Layer 3 (label "zₜ" mid-arrow, in italic 9pt)
- Layer 3 → Output box

**Vertical operator-input arrows** (lighter, dashed, 1pt, with arrowhead):
- Operator input box (below Layer 1) → Layer 1, going up
- Operator input box (below Layer 2) → Layer 2, going up
- Operator input box (below Layer 3) → Layer 3, going up

### Title

Top-center of canvas:
```
CALIBURN: layered architecture for streaming intrusion detection
```
Font: Helvetica 12pt bold, color #222

### Caption (in paper, not in diagram itself)

> **Figure 1.** CALIBURN architecture. Layer 1 (truncated BOCPD) produces a probabilistic anomaly score s_t with bounded per-flow update cost. Layer 2 (cost-sensitive thresholding) converts the score into a budget-consuming event z_t using an operator-specified cost ratio C. Layer 3 (multi-window burn-rate alerting) escalates events into pages or tickets only when both short and long windows exceed the burn-rate threshold. Each layer takes its operational parameters from the operator before deployment, not from a validation set, making the alerting policy explainable in advance.

## Step-by-step in draw.io

1. Open https://app.diagrams.net/, choose "Blank Diagram"
2. Set page size: File → Page Setup → Custom 800 × 320
3. For each box:
   - Drag a rectangle from left panel
   - Right-click → Edit Style, paste:
     `rounded=1;whiteSpace=wrap;html=1;arcSize=20;fillColor=#E8F1F8;strokeColor=#1F77B4;fontSize=11;fontFamily=Helvetica;`
     (change colors per layer per the table above)
   - Double-click box, type the text
4. For dashed operator-input boxes, add `dashed=1;` to the style
5. For arrows: hover over a box edge, drag to next box
   - Edit arrow style: `endArrow=classic;html=1;rounded=0;strokeColor=#444;strokeWidth=1.5;`
   - Add edge label by double-clicking the arrow line
6. For title: drag text element, font 14pt bold
7. Verify everything aligns: View → Grid (turn on)
8. File → Export As → SVG → File → Export As → PDF

If you prefer a faster route: I can also produce this as raw SVG/TikZ code if you want to skip draw.io entirely. Just ask.
