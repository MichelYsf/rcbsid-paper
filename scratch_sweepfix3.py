"""B1-B4b, lost when script 1 crashed pre-write. B5 was a false positive:
the file's \\ref tokens were always intact - the auditor's reader consumed
the literal backslash-r as a carriage return."""
from pathlib import Path

p = Path("paper/main.tex")
s = p.read_text(encoding="utf-8")
applied = []


def sub(tag, old, new):
    global s
    assert old in s, tag + " anchor missing:\n" + old[:120]
    s = s.replace(old, new, 1)
    applied.append(tag)


sub("B1",
    """on the identical natural-order held-out slice, a
batch LOF reference scores \\STwoLUnresampledLofMean{} AUC-PR against the
detector's \\STwoLUnresampledProposedMean{}""",
    """on the identical held-out slice of the
interleaved (unresampled) stream, a batch LOF reference scores
\\STwoLUnresampledLofMean{} AUC-PR against the detector's
\\STwoLUnresampledProposedMean{}""")

sub("B2",
    """Second, the detector's lift over the chance floor
falls monotonically from $+\\STwoLFiveProposedLift$ at 5\\%\\ and
$+\\STwoLTenProposedLift$ at 10\\%\\ to $\\STwoLSixtyFourProposedLift$ at
64\\%\\ --- below the floor a constant predictor achieves.""",
    """Second, the detector's lift over the chance floor
runs $+\\STwoLFiveProposedLift$ at 5\\%, peaks at $+\\STwoLTenProposedLift$
at 10\\%, and falls from there to $\\STwoLSixtyFourProposedLift$ at
64\\%\\ --- below the floor a constant predictor achieves.""")

sub("B3",
    """\\SFourLitnetPooledEcodAucpr: pooling manufactures a uniform dominance that
the per-stream results do not uniformly show
(Table~\\ref{tab:litnet}).""",
    """\\SFourLitnetPooledEcodAucpr: pooling collapses three heterogeneous
held-out regimes into one operating point and erases the per-stream
structure the table shows (Table~\\ref{tab:litnet}).""")

sub("B4",
    """\\begin{itemize}
\\item \\textbf{Natural order:} ECOD \\SFourCicidsNaturalEcodAucpr{} $>$
detector \\SFourCicidsNaturalProposedDetectorAucpr{} $>$ HST
\\SFourCicidsNaturalHstAucpr. Against the \\SFourCicidsNaturalChanceFloor{}
floor, no method clears $+\\SFourCicidsNaturalBestLift$, and HST sits
\\SFourCicidsNaturalHstLift{} \\emph{below} chance; the raw triple is not a
performance claim.
\\item \\textbf{Synthetic:} detector
\\SFourCicidsSyntheticProposedDetectorAucpr{} $>$ HST
\\SFourCicidsSyntheticHstAucpr{} $>$ ECOD
\\SFourCicidsSyntheticEcodAucpr. Against the
\\SFourCicidsSyntheticChanceFloor{} floor, every method's lift is
\\emph{higher} than in the natural arm.
\\end{itemize}""",
    """\\begin{itemize}
\\item \\textbf{Natural order:} ECOD \\SFourCicidsNaturalEcodAucpr{} $>$
detector \\SFourCicidsNaturalProposedDetectorAucpr{} (both deterministic).
Against the \\SFourCicidsNaturalChanceFloor{} floor, neither clears
$+\\SFourCicidsNaturalBestLift$; these values are not a performance claim.
HST scores \\SFourCicidsNaturalHstAucpr{} here ---
\\SFourCicidsNaturalHstLiftAbs{} \\emph{below} chance --- from a single
seed, so no placement relative to the other methods is asserted for it.
\\item \\textbf{Synthetic:} detector
\\SFourCicidsSyntheticProposedDetectorAucpr{} $>$ ECOD
\\SFourCicidsSyntheticEcodAucpr{} (both deterministic). Against the
\\SFourCicidsSyntheticChanceFloor{} floor, every method's lift is
\\emph{higher} than in the natural arm. HST's three-seed values here are
mean \\SFourSeedCicidsTwoZeroOneSevenInterleavedSyntheticHstMean{} $\\pm$
\\SFourSeedCicidsTwoZeroOneSevenInterleavedSyntheticHstSd; its ordering
against ECOD flips across those seeds, so it carries no placement.
\\end{itemize}""")

sub("B4b",
    """The ordering of the two deterministic methods inverts: ECOD is best under
natural order and worst under the synthetic construction, on identical
records. This comparison is seed-free --- both methods are deterministic
here --- and it is the paper's central evidence. The full ranking change is
a rotation, not a reversal: Kendall
$\\tau = \\SFourCicidsRankingKendallTau$, with
\\SFourCicidsPairwiseOrderingsPreserved{} of
\\SFourCicidsPairwiseOrderingsTotal{} pairwise orderings preserved
(detector $>$ HST holds in both arms). HST is stochastic; its placement
rests on seeds reported in Section~\\ref{sec:seeds}.""",
    """The ordering of the two deterministic methods inverts: ECOD beats the
detector under natural order and loses to it under the synthetic
construction, on identical records. This comparison is seed-free --- both
methods are deterministic here --- and it is the paper's central evidence.
Computed over all three methods at the seeds run, the ranking change is a
rotation, not a reversal (Kendall
$\\tau = \\SFourCicidsRankingKendallTau$, with
\\SFourCicidsPairwiseOrderingsPreserved{} of
\\SFourCicidsPairwiseOrderingsTotal{} pairwise orderings preserved), but
any placement of HST within it is single-draw here, and
Section~\\ref{sec:seeds} reports how it moves with the seed.""")

p.write_text(s, encoding="utf-8")
print("applied: " + ", ".join(applied))
