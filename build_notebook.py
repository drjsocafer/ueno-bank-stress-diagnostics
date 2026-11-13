"""Build an executed, portable notebook from the repository's actual code."""
import contextlib, io, json, os, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def markdown(text):
    return dict(cell_type='markdown',metadata={},source=text.splitlines(True))

def execute(source,count):
    stdout,stderr=io.StringIO(),io.StringIO()
    ns={'__name__':'__main__','__file__':str(ROOT/'analysis.py')}
    with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
        exec(compile(source,str(ROOT/'Ueno_analysis.ipynb'),'exec'),ns)
    outputs=[dict(output_type='stream',name=n,text=s.getvalue().splitlines(True))
             for n,s in [('stdout',stdout),('stderr',stderr)] if s.getvalue()]
    return dict(cell_type='code',metadata={},execution_count=count,
                source=source.splitlines(True),outputs=outputs)

if __name__=='__main__':
    os.chdir(ROOT);sys.path.insert(0,str(ROOT))
    cells=[markdown('# Opening balance sheet and sustainable growth diagnostics\n\nPublic-information cutoff: 12 November 2026. Methods revised 13 November 2026. Synthetic sensitivities, not bank-calibrated forecasts. Core calculations use only the Python standard library. Run this notebook from the repository root.\n\nThe code below was executed during notebook construction; outputs are captured from those executions.')]
    source="from pathlib import Path\n__file__ = str(Path.cwd() / 'analysis.py')\n"+(ROOT/'analysis.py').read_text()
    cells.append(execute(source,1))
    cells.append(markdown('## Independent implementation and numerical checks\n\nThe time-forward ledger is distinct from the direct stock calculation. It verifies324 stationary configurations and61 monthly transition values. Reverse-PD residuals and capital identities are also checked.'))
    cells.append(execute((ROOT/'validate.py').read_text(),2))
    cells.append(markdown('## Article Figure 1: changing origination growth\n\n![Figure 1](figures/figure_1_growth_transition.svg)\n\nAt month zero the growth rate of monthly originations changes from46.4% annually to0%. New lending continues at a constant monthly volume. Credit quality stays constant; the pool of individual loans and its age mix change. The model moves from1.80085% NPL to2.26759%; at24months it is2.22204%. This is not a prediction of a particular bank\'s future NPLs.'))
    cells.append(markdown('## Article Figure 2: inverse PD configurations\n\n![Figure 2](figures/figure_2_non_identification.svg)\n\nTwelve different default-timing and stock-retention assumptions fit the same0.4% NPL reference using different lifetime PDs. This range is not a confidence interval.'))
    cells.append(markdown('## Capital-only growth budget\n\nFor capital15, opening RWA100, net retained earnings1.5 and a chosen management target15%, RWA growth capacity is10%. An opening correction1 reduces capacity to3.33%. The function allows negative capacity, which means additional capital or RWA contraction is needed to meet the assumed target.\n\nThis excludes liquidity, funding concentration, leverage, operating capacity and other potential binding constraints. It is not a recommended growth rate. Complete assumptions and primary sources are in README.md.'))
    cells.append(markdown('## Article Figure 3: Nu Holdings comparator\n\n![Figure 3](figures/figure_3_nu_comparator.svg)\n\nHistorical source observations are separate from the synthetic model. Credit and deposit growth use issuer-reported FX-neutral rates, not changes in nominal USD balances. Funding coverage uses management definitions and is not a regulatory liquidity ratio. The latest disclosed 90+ day NPL increase is included. Entity scope, products and definitions differ from ueno. Read COMPARATOR.md and data/nu_sources.json for exact sources and limitations.'))
    cells.append(execute("from comparator import load_observations, summarise\nimport json\nprint(json.dumps(summarise(load_observations()), indent=2))",3))
    for i,c in enumerate(cells):c['id']=f'ueno-revised-{i+1}'
    nb=dict(nbformat=4,nbformat_minor=5,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}},cells=cells)
    (ROOT/'Ueno_analysis.ipynb').write_text(json.dumps(nb,indent=1)+'\n')
    print('Executed notebook rebuilt from current source.')
