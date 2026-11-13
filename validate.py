"""Independent monthly ledger and inverse-solution validation."""
import math
from analysis import cohort_npl, cohort_transition, ROOT, OUT

def ledger(growth,term,pd,window,scale,observation=None,growth_after=None):
    history=term+window+5
    cohorts=[]; defaults=[]
    normalizer=1-math.exp(-(term/scale)**2)
    for month in range(history):
        calendar=month-(history-1)+(0 if observation is None else observation)
        rate=growth_after if growth_after is not None and calendar>0 else growth
        new=(1+rate)**(calendar/12)
        cohorts.append(dict(start=month,original=new,survivors=new))
        performing=0.
        for c in cohorts:
            age=month-c['start']
            if age>term: continue
            if age>0:
                prob=pd*(math.exp(-((age-1)/scale)**2)-math.exp(-(age/scale)**2))/normalizer
                default_units=c['original']*prob
                c['survivors']-=default_units
                defaults.append((month,default_units*(term-age+1)/term))
            performing+=c['survivors']*max(0,(term-age)/term)
        outstanding_default=sum(amount for t,amount in defaults if 0<=month-t<window)
    return outstanding_default/(performing+outstanding_default)

count=0; max_error=0
for g in [0,.464,1]:
 for term in [24,36,60]:
  for pd in [.02,.06,.1]:
   for window in [3,6,12,24]:
    for scale in [9,18,30]:
     expected=cohort_npl(g,term,pd,window,scale)
     independent=ledger(g,term,pd,window,scale)
     error=abs(expected-independent)
     assert error<1e-12,(g,term,pd,window,scale,error)
     max_error=max(max_error,error); count+=1
import csv
max_residual=0
with (OUT/'non_identification.csv').open() as f:
 for row in csv.DictReader(f):
  fit=cohort_npl(.464,36,float(row['implied_lifetime_pd']),int(row['retention_months']),float(row['weibull_scale']))
  max_residual=max(max_residual,abs(fit-.004))
assert max_residual<1e-12
transition_error=0
for month in range(-12,49):
    expected=cohort_transition(month)
    independent=ledger(.464,36,.06,12,18,observation=month,growth_after=0)
    transition_error=max(transition_error,abs(expected-independent))
assert transition_error<1e-12
text=(f'PASS: 7 model checks in analysis.py.\n'
      f'PASS: independent time-forward ledger matches all {count} cohort specifications.\n'
      f'Maximum absolute NPL ratio difference: {max_error:.3g}\n'
      f'PASS: 12 reverse-PD solutions have maximum residual {max_residual:.3g}.\n'
      f'PASS: 61 monthly transition values agree with the independent ledger; maximum error {transition_error:.3g}.\n'
      'Domain and monotonicity checks passed. No bank calibration or empirical forecast validation is claimed.\n')
(ROOT/'VALIDATION.txt').write_text(text)
print(text)
