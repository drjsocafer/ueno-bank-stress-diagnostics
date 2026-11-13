"""Reproduce the descriptive Nu comparator from explicitly sourced observations.

This is historical arithmetic, not a fitted model or a causal success test.
FX-neutral growth is read from releases, never inferred from USD balance changes.
"""
from pathlib import Path
import csv
import json
from datetime import date

ROOT = Path(__file__).resolve().parent


def load_observations():
    sources = json.loads((ROOT / 'data/nu_sources.json').read_text())
    with (ROOT / 'data/nu_comparator.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    observations = {}
    for row in rows:
        key = (row['period'], row['metric'])
        if key in observations:
            raise ValueError(f'Duplicate observation: {key}')
        source = sources['sources'][row['source_id']]
        if date.fromisoformat(source['published']) > date.fromisoformat(sources['cutoff']):
            raise ValueError('Observation published after the information cutoff')
        value = float(row['value'])
        if not value >= 0:
            raise ValueError(f'Invalid value: {key}')
        if row['metric'].endswith('_growth'):
            if row['basis'] != 'year_on_year_FX_neutral' or row['unit'] != 'percent':
                raise ValueError('Incompatible growth basis')
        if row['metric'] == 'npl_90_plus':
            if row['scope'] != 'Nu reported portfolio (see source scope notes)' or value > 100:
                raise ValueError('Incompatible NPL scope or value')
        if row['metric'] == 'net_income' and not row['period'].startswith('FY'):
            raise ValueError('Do not mix quarterly profit with full-year profit')
        observations[key] = {**row, 'value': value}
    return observations


def summarise(observations):
    def value(period, metric):
        return observations[period, metric]['value']
    funding = observations['FY2025', 'available_funding']
    credit = observations['FY2025', 'net_credit_portfolio']
    if (funding['scope'], funding['unit'], funding['basis']) != (
            credit['scope'], credit['unit'], credit['basis']):
        raise ValueError('Funding coverage requires consistent scope, date and units')
    return {
        'annual_growth_percent_FXN': [
            {'period': p, 'credit': value(p, 'credit_growth'),
             'deposits': value(p, 'deposit_growth')}
            for p in ('FY2023', 'FY2024', 'FY2025')],
        'FY2025_available_funding_to_net_credit': funding['value'] / credit['value'],
        'Q32026_credit_minus_deposit_growth_pp': (
            value('Q32026', 'credit_growth') - value('Q32026', 'deposit_growth')),
        'Q32026_reported_90plus_NPL_change_bps': round(100 * (
            value('Q32026', 'npl_90_plus') - value('Q22026', 'npl_90_plus')), 10),
        'interpretation': 'Descriptive comparator; no regulatory liquidity ratio, '
                          'matched control, causal estimate or assurance of future resilience.'
    }


if __name__ == '__main__':
    result = summarise(load_observations())
    (ROOT / 'results').mkdir(exist_ok=True)
    (ROOT / 'results/nu_comparator.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
