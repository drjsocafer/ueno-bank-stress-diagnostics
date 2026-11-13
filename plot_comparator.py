"""Draw Article Figure 3 from sourced data, without cross-bank ratio overlays."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from comparator import load_observations, summarise
from earnings_sensitivity import observations, calculate

ROOT = Path(__file__).resolve().parent
data = load_observations()
summary = summarise(data)
earnings = calculate(observations())

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.titleweight': 'bold', 'figure.facecolor': '#f6f7f5',
    'axes.facecolor': '#f6f7f5', 'text.color': '#123c40',
    'axes.labelcolor': '#123c40', 'xtick.color': '#34565a',
    'ytick.color': '#34565a', 'svg.hashsalt': 'nu-comparator', 'text.parse_math': False})
fig, (left, right) = plt.subplots(1, 2, figsize=(13, 8),
                                gridspec_kw={'width_ratios': [1.15, 1], 'wspace': .38})
x = np.arange(3)
for offset, metric, label, color in [(-.19, 'credit_growth', 'Credit cards + loans', '#17646b'),
                                   (.19, 'deposit_growth', 'Deposits', '#a3bbb2')]:
    values = [data[p, metric]['value'] for p in ('FY2023', 'FY2024', 'FY2025')]
    bars = left.bar(x + offset, values, width=.36, color=color, label=label)
    left.bar_label(bars, labels=[f'{v:.0f}%' for v in values], padding=5)
left.set_xticks(x, ['2023', '2024', '2025'])
left.set_ylim(0, 68)
left.set_ylabel('Year-on-year growth, FX-neutral (%)')
left.set_title('Credit and deposit growth', loc='left', fontsize=15, pad=18)
left.legend(frameon=False, loc='upper left', fontsize=10)
values = [data['FY2025', k]['value'] for k in ('available_funding', 'net_credit_portfolio')]
bars = right.barh([1, 0], values, color=['#17646b', '#a3bbb2'], height=.48)
right.bar_label(bars, labels=[f'${v:.1f}bn' for v in values], padding=7)
right.set_yticks([1, 0], ['Available\nfunding', 'Net credit\nportfolio'])
right.set_xlim(0, 48)
right.set_ylim(-.65, 2.1)
right.set_xlabel('US$ billion at year-end 2025')
right.set_title('Reported funding resources', loc='left', fontsize=15, pad=18)
right.text(0, 1.75, f"{summary['FY2025_available_funding_to_net_credit']:.2f}×", fontsize=29,
           fontweight='bold', va='center')
right.text(17, 1.75, 'funding / net credit\nmanagement definitions', fontsize=10, va='center')
fig.suptitle('Nu Holdings: growth and reported resources',
             x=.07, y=.96, ha='left', fontsize=18, fontweight='bold')
fig.text(.07, .90, 'Figure 3  |  Consolidated group  |  Historical comparator with distinct definitions', fontsize=12)
fig.subplots_adjust(left=.07, right=.96, top=.78, bottom=.38)
fig.text(.07, .29, 'Annual net income (reported US$):  $1.03bn in 2023   →   $1.97bn in 2024   →   $2.9bn in 2025',
         fontsize=12, fontweight='bold')
fig.text(.07, .22, 'Q3 2026 · Credit +33% vs deposits +19% YoY (FXN); 90+ day NPL 7.3% vs 6.9% in Q2.', fontsize=12)
ratios=earnings['managerial_ratios_separate_basis']
fig.text(.07, .17, f"Managerial credit cost / credit income: {ratios[0]['cost_of_credit_over_credit_income']:.1%} → {ratios[1]['cost_of_credit_over_credit_income']:.1%} YoY.", fontsize=12)
fig.text(.07, .095, 'Sources: Nu FY2024–2025 releases and Q3 2026 SEC filings. Data and definitions in the repository.', fontsize=10)
fig.text(.07, .05, 'Funding coverage is not a regulatory liquidity ratio. NPL definitions and group scope differ from ueno bank.', fontsize=10)
for ext in ('png', 'svg'):
    fig.savefig(ROOT / f'figures/figure_3_nu_comparator.{ext}', dpi=180,
                metadata={'Date': None} if ext == 'svg' else {})
plt.close(fig)
print('Rendered Figure 3 from data/nu_comparator.csv.')
