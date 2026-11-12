"""Public-data diagnostics for a LinkedIn article, as of 2026-11-12.

Run: python analysis.py (Python 3.10+; stdlib only).
Not a reconstruction of Ueno's regulatory capital, loan tape or liquidity.
All synthetic parameters are explicit below. No estimated event probabilities.
"""
from pathlib import Path
import csv, itertools, json, math, unittest

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)

def cohort_npl(growth=0.464, term=36, lifetime_pd=0.06,
               retention=12, scale=18.0, shape=2.0):
    """Exact expected stock for monthly equal-principal cohorts.

    Originations grow at (1+growth) annually indefinitely. Age zero is a new
    cohort at observation month. Defaults occur at months 1..term, with a
    Weibull timing distribution truncated/renormalised to term and multiplied
    by lifetime_pd. No competing prepayment. Performing principal amortises
    linearly; defaulted principal freezes at start-of-default-month EAD and
    stays in the gross book for retention monthly observations. Then exits
    (collection/writeoff/transfer unspecified), with no recovery model.
    These are expected stocks, not a random draw. No classification delay,
    acquired legacy pool, forbearance or bank-specific calibration is assumed.
    """
    if growth <= -1 or term < 1 or not 0 <= lifetime_pd <= 1 or retention < 1:
        raise ValueError('Invalid economic domain')
    cdf = lambda t: 1 - math.exp(-(t / scale) ** shape)
    masses = [0.] + [lifetime_pd * (cdf(d)-cdf(d-1))/cdf(term)
                      for d in range(1, term+1)]
    performing = npl = 0.
    for age in range(term + retention):
        origination = (1 + growth) ** (-age / 12)
        if age < term:
            survival = 1 - sum(masses[:age+1])
            performing += origination * (1 - age/term) * survival
        for d in range(max(1, age-retention+1), min(age, term)+1):
            ead = (term-d+1)/term
            npl += origination * masses[d] * ead
    return npl / (performing+npl)

def capital_ratio(c0=.15, correction=0., scenario_loss=0., rwa_change=0.):
    """Ratios and losses in opening RWA units; ignores tax/profit/actions.
    rwa_change is net total denominator change including provision effects.
    No bank-specific legal/economic capital conversion is implied.
    """
    if rwa_change <= -1: raise ValueError('Nonpositive RWA')
    return (c0-correction-scenario_loss)/(1+rwa_change)

def correction_budget(target=.12, c0=.15, scenario_loss=0., rwa_change=0.):
    return c0-scenario_loss-target*(1+rwa_change)

def funding_ratio(ldr=.919, runoff=0.):
    """Loans unchanged; customer deposits reduced; other funding ignored."""
    if not 0 <= runoff < 1: raise ValueError('Invalid runoff')
    return ldr/(1-runoff)

def write_csv(name, rows):
    with (OUT/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

class Checks(unittest.TestCase):
    def test_capital_identity_and_inversion(self):
        for g in [-.1,0,.1,.25]:
            d=correction_budget(rwa_change=g)
            self.assertAlmostEqual(capital_ratio(correction=d,rwa_change=g),.12)
        self.assertAlmostEqual(capital_ratio(),.15)
    def test_cohort_zero_defaults(self):
        self.assertEqual(cohort_npl(lifetime_pd=0),0)
    def test_cohort_invariants(self):
        for growth, term, window in itertools.product([0,.464,1],[24,36,60],[3,12,24]):
            value=cohort_npl(growth,term,.06,window)
            self.assertTrue(0 < value < 1)
            self.assertGreater(cohort_npl(growth,term,.10,window),value)
            self.assertGreaterEqual(cohort_npl(growth,term,.06,window+1),value)
    def test_retention_analytic_special_case(self):
        # One-month loans: performing age0 =1, default stock at age1 = PD.
        self.assertAlmostEqual(cohort_npl(0,1,.06,1),.06/1.06)
    def test_funding_identity(self):
        self.assertAlmostEqual(funding_ratio(runoff=1-.919),1)
        self.assertGreater(funding_ratio(runoff=.1),funding_ratio())

def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful(): raise SystemExit(1)
    rows=[]
    for term,pd,window,scale,growth in itertools.product(
            [24,36,60],[.02,.06,.10],[3,6,12,24],[9.,18.,30.],[0.,.464,1.]):
        rows.append(dict(term_months=term,lifetime_pd=pd,retention_months=window,
                         weibull_scale=scale,growth=growth,
                         npl_ratio=cohort_npl(growth,term,pd,window,scale)))
    write_csv('cohort_sensitivity.csv',rows)
    core=[dict(term_months=t,growth=g,npl_ratio=cohort_npl(g,t))
          for t,g in itertools.product([36,60],[0,.464,1])]
    write_csv('cohort_core.csv',core)
    capital=[dict(rwa_change=g,target=t,
                  max_correction=correction_budget(target=t,rwa_change=g))
             for g,t in itertools.product([-.1,0,.1,.25],[.12,.06])]
    write_csv('capital_thresholds.csv',capital)
    funding=[dict(runoff=r,loan_deposit_ratio=funding_ratio(runoff=r))
             for r in [0,.05,.081,.10,.20,.30]]
    write_csv('funding_sensitivity.csv',funding)
    p=.06
    fitted=[]
    # Invert PD to match 0.4% for several unobserved exit/timing structures.
    for window,scale in itertools.product([3,6,12,24],[9.,18.,30.]):
        lo,hi=0.,1.
        for _ in range(70):
            mid=(lo+hi)/2
            if cohort_npl(lifetime_pd=mid,retention=window,scale=scale)<.004: lo=mid
            else: hi=mid
        fitted.append(dict(retention_months=window,weibull_scale=scale,
                           implied_lifetime_pd=(lo+hi)/2))
    write_csv('non_identification.csv',fitted)
    rel=[]
    for term,pd,window,scale in itertools.product([24,36,60],[.02,.06,.10],[3,6,12,24],[9.,18.,30.]):
        base=cohort_npl(0,term,pd,window,scale)
        grown=cohort_npl(.464,term,pd,window,scale)
        rel.append((grown/base-1)*100)
    summary=dict(as_of='2026-11-12',synthetic_sensitivity_rows=len(rows),
       cohort_core=core,relative_change_growth_46_4_pct=[min(rel),max(rel)],
       capital_thresholds=capital,funding_sensitivity=funding,
       pd_fitting_0_4_pct_range=[min(x['implied_lifetime_pd'] for x in fitted),max(x['implied_lifetime_pd'] for x in fitted)],
       fitch_ye25_capital_definition_gap_bps=round((.152-.103)*10000),
       reported_provisions_over_ye25_impaired_loans=1_621_853_458_972/(50_314*1e6),
       checks_run=result.testsRun,checks_passed=result.wasSuccessful())
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
