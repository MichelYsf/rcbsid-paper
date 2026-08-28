#!/usr/bin/env python
"""Fail the build if the printed page does not add up.

Two checks, both enforcing the reporting rule in `provenance.REPORT_DP`:

  1. DERIVED CONSISTENCY. Every quantity derived from other reported
     quantities -- a margin, a spread, a delta, a normalized lift -- must equal
     the arithmetic a reader performs on the values printed beside it. This is
     the guarantee the rule exists to provide, and it is worth checking rather
     than asserting: it held for 17 of 21 derived quantities before the rule
     was adopted, so the four that failed were invisible against a background
     of agreement.

  2. DISPLAY WIDTH. Metric-valued macros in one family must render at one
     width. `repr()` drops trailing zeros, so a value of 0.799910 printed as
     "0.79991" sat 5-wide beside 6-wide neighbours in the same table, and
     unrounded floats leaked in at 15 and 16 decimals.

Neither check can be satisfied by editing the manuscript: both read the
generated macro file and the archived index, so the only way to pass is to fix
the emitting run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import REPORT_DP, is_metric  # noqa: E402

NUMBERS = ROOT / "paper" / "numbers.tex"
NEWCMD = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}(?:\s*%\s*([^\n]*))?")

# (derived macro, operator, operand macros)
RELATIONS: list[tuple[str, str, list[str]]] = [
    ("RevSharedMarginNatural", "sub",
     ["RevSharedDetectorNaturalAucpr", "RevSharedEcodNaturalAucpr"]),
    ("RevSharedMarginSynthetic", "sub",
     ["RevSharedDetectorSyntheticAucpr", "RevSharedEcodSyntheticAucpr"]),
    ("RevSharedDetectorSpread", "absub",
     ["RevSharedDetectorNaturalAucpr", "RevSharedDetectorSyntheticAucpr"]),
    ("RevBranchTailMinusCombinedAucpr", "sub",
     ["RevBranchTailOnlyAucpr", "RevBranchCombinedAucpr"]),
    ("RevBranchTailMinusCombinedAucroc", "sub",
     ["RevBranchTailOnlyAucroc", "RevBranchCombinedAucroc"]),
    ("RevEcodBatchDelta", "absub",
     ["RevEcodBatchFourEightZeroZeroZeroZeroAucpr",
      "RevEcodBatchTwoFourZeroZeroZeroZeroAucpr"]),
    ("RevEcodBatchSpread", "spread",
     ["RevEcodBatchTwoFourZeroZeroZeroZeroAucpr",
      "RevEcodBatchThreeZeroZeroZeroZeroZeroAucpr",
      "RevEcodBatchThreeSixZeroZeroZeroZeroAucpr",
      "RevEcodBatchFourEightZeroZeroZeroZeroAucpr"]),
    ("SSixOriginalLift", "sub", ["SSixOriginalAucpr", "SSixChanceFloor"]),
    ("SSixCorrectedLift", "sub", ["SSixCorrectedAucpr", "SSixChanceFloor"]),
    ("SSixOriginalNormLift", "normlift",
     ["SSixOriginalAucpr", "SSixChanceFloor"]),
    ("SSixCorrectedNormLift", "normlift",
     ["SSixCorrectedAucpr", "SSixChanceFloor"]),
]
for _arm in ("Natural", "Synthetic"):
    for _m in ("ProposedDetector", "Ecod", "Hst"):
        RELATIONS.append(("SFourCicids" + _arm + _m + "NormLift", "normlift",
                          ["SFourCicids" + _arm + _m + "Aucpr",
                           "SFourCicids" + _arm + "ChanceFloor"]))
for _arm in ("Natural", "Synthetic"):
    for _m in ("Detector", "Ecod"):
        RELATIONS.append(("RevShared" + _m + _arm + "NormLift", "normlift",
                          ["RevShared" + _m + _arm + "Aucpr",
                           "RevSharedPrevalence"]))
# Additive lift is printed beside its AP and its floor in the outcome bullets,
# so it is bound by the same rule as the normalized form.
for _arm in ("Natural", "Synthetic"):
    for _m in ("ProposedDetector", "Ecod", "Hst"):
        RELATIONS.append(("SFourCicids" + _arm + _m + "Lift", "sub",
                          ["SFourCicids" + _arm + _m + "Aucpr",
                           "SFourCicids" + _arm + "ChanceFloor"]))

# Quantities the manuscript prints beside the values they are computed from,
# outside the margin/lift families. The pooling identity in particular is
# asserted in the abstract as exact arithmetic, so a reader will check it.
# The prevalence sweep. These were the group the check did NOT cover when the
# reporting rule was adopted, and three of the five normalized lifts printed in
# sec:sweep disagreed with the table above them for exactly that reason. The
# level and method keys are read from the macro index rather than hard-coded,
# so a new level or method is covered the moment it is emitted.
def _sweep_relations() -> list:
    import re as _re
    from pathlib import Path as _P
    txt = _P(__file__).resolve().parents[1] / "paper" / "numbers.tex"
    if not txt.exists():
        return []
    names = set(_re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", txt.read_text(encoding="utf-8")))
    out = []
    for n in sorted(names):
        m = _re.fullmatch(r"STwoL([A-Z][a-z]+)([A-Z][A-Za-z]*?)NormLift", n)
        if not m:
            continue
        lvl, meth = m.group(1), m.group(2)
        mean, floor = "STwoL" + lvl + meth + "Mean", "STwoL" + lvl + "Floor"
        if mean in names and floor in names:
            out.append((n, "normlift", [mean, floor]))
            lift = "STwoL" + lvl + meth + "Lift"
            if lift in names:
                out.append((lift, "sub", [mean, floor]))
    return out


RELATIONS += _sweep_relations()

RELATIONS += [
    # abstract: "prevalences of X% and Y% --- a Z-point difference"
    ("SFourCicidsPrevShiftAbsPp", "absub",
     ["SFourCicidsNaturalTestPrev", "SFourCicidsInterleavedTestPrev"]),
    # the LITNET pooling identity: pooled prevalence IS the equal-weight mean
    ("SFourLitnetPooledTestPrev", "mean",
     ["SFourLitnetSpamTestPrev", "SFourLitnetBlasterWormTestPrev",
      "SFourLitnetUdpFloodTestPrev"]),
    # abstract: slices "share only P% of their records"
    ("CicidsHeldoutOverlapPct", "pct",
     ["CicidsHeldoutOverlap", "CicidsHeldoutSize"]),
    # sec:shared: "N records, carrying K attacks, at prevalence p"
    ("RevSharedPrevalence", "ratio",
     ["RevSharedAttacks", "RevSharedRecords"]),
]


def compute(op: str, vs: list[float]) -> float:
    if op == "sub":
        return vs[0] - vs[1]
    if op == "absub":
        return abs(vs[0] - vs[1])
    if op == "spread":
        return max(vs) - min(vs)
    if op == "normlift":
        return (vs[0] - vs[1]) / (1.0 - vs[1])
    if op == "mean":
        return sum(vs) / len(vs)
    if op == "pct":
        return 100.0 * vs[0] / vs[1]
    if op == "ratio":
        return vs[0] / vs[1]
    raise KeyError(op)


def dps(s: str) -> int:
    return len(s.split(".")[1]) if "." in s else 0


def main() -> int:
    if not NUMBERS.exists():
        print("DECIMALS FAILED - paper/numbers.tex is absent; nothing to check.")
        return 1
    _text = NUMBERS.read_text(encoding="utf-8")
    printed = {m.group(1): m.group(2).strip() for m in NEWCMD.finditer(_text)}
    # the generated comment carries the emitting run's own description, which
    # is what decides whether a value is a metric (see provenance.is_metric)
    descs = {m.group(1): (m.group(3) or "") for m in NEWCMD.finditer(_text)}
    if not printed:
        print("DECIMALS FAILED - no macros parsed; the check must never pass "
              "vacuously.")
        return 1

    rc = 0

    # ---- 1. derived quantities vs their printed operands -------------------
    bad, checked, absent = [], 0, []
    for name, op, ins in RELATIONS:
        if name not in printed or any(i not in printed for i in ins):
            absent.append(name)
            continue
        try:
            d = float(printed[name])
            vs = [float(printed[i]) for i in ins]
        except ValueError:
            absent.append(name)
            continue
        want = compute(op, vs)
        shown = ("%." + str(dps(printed[name])) + "f") % want
        checked += 1
        if float(shown) != d:
            bad.append((name, printed[name], shown))
    print("decimal check: %d derived quantity/ies checked against their "
          "printed operands" % checked)
    for name, got, want in bad:
        print("  DOES NOT ADD UP  %-42s printed %s  operands give %s"
              % (name, got, want))
    if absent:
        print("  (not in numbers.tex, skipped: %d)" % len(absent))
    if bad:
        print("FAILED - a derived value disagrees with the values printed "
              "beside it; derive it from reported() inputs (REPORT_DP).")
        rc = 1
    elif checked:
        print("PASSED - every derived value equals the arithmetic on its "
              "printed operands.")

    # ---- 2. one display width per metric family ---------------------------
    fams: dict[str, dict[int, list[str]]] = {}
    for name, body in printed.items():
        if not is_metric(name, descs.get(name, "")):
            continue
        if "e" in body or "E" in body:      # exponent form, exempt by policy
            continue
        try:
            float(body)
        except ValueError:
            continue
        if "." not in body:                 # integral value, exempt
            continue
        suf = next((s for s in ("Aucpr", "Aucroc", "NormLift", "Lift", "Margin",
                                "Spread", "ChanceFloor", "Prevalence", "Delta")
                    if name.endswith(s)), "declared-metric")
        fams.setdefault(suf, {}).setdefault(dps(body), []).append(name)
    mixed = {k: v for k, v in fams.items() if len(v) > 1}
    wrong = {k: v for k, v in fams.items()
             if len(v) == 1 and next(iter(v)) != REPORT_DP}
    print("display width: %d metric family/ies, target %d dp"
          % (len(fams), REPORT_DP))
    for suf in sorted(mixed):
        print("  MIXED WIDTH  %-12s %s" % (suf, sorted(mixed[suf])))
        for w in sorted(mixed[suf]):
            print("        %d dp: %s" % (w, ", ".join(sorted(mixed[suf][w])[:4])))
    for suf in sorted(wrong):
        print("  WRONG WIDTH  %-12s renders at %d dp" % (suf, next(iter(wrong[suf]))))
    if mixed or wrong:
        print("FAILED - metric families must render at %d decimal places."
              % REPORT_DP)
        rc = 1
    elif fams:
        print("PASSED - every metric family renders at one width.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
