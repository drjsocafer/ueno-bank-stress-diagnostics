"""A frozen-quarter IFRS expense sensitivity and separate managerial ratios.

These calculations do not constitute a dynamic bank stress test. ECL expense
is a flow, distinct from the allowance stock, realised losses or capital.
"""
from pathlib import Path
import csv
import json
import math
from datetime import date

ROOT = Path(__file__).resolve().parent


def observations():
    catalog = json.loads((ROOT / 'data/nu_sources.json').read_text())
    with (ROOT / 'data/nu_quarterly_financials.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    result = {}
    for row in rows:
        key = row['period'], row['metric']
        if key in result:
            raise ValueError(f'Duplicate input: {key}')
        if row['unit'] != 'USD_million' or row['scope'] != 'Nu Holdings consolidated':
            raise ValueError('Incompatible reporting unit or scope')
        source = catalog['sources'][row['source_id']]
        if date.fromisoformat(source['published']) > date.fromisoformat(catalog['cutoff']):
            raise ValueError('Input was published after the information cutoff')
        row['value'] = float(row['value'])
        if not math.isfinite(row['value']) or row['value'] <= 0:
            raise ValueError('Positive finite inputs required')
        result[key] = row
    return result


def calculate(data):
    def get(period, metric, basis):
        row = data[period, metric]
        if row['basis'] != basis:
            raise ValueError(f'Incompatible accounting basis for {metric}')
        return row['value']
    ratios = []
    for period in ('Q32025', 'Q32026'):
        income = get(period, 'credit_income', 'managerial_quarterly_reported')
        cost = get(period, 'cost_of_credit', 'managerial_quarterly_expense_positive')
        ratios.append({'period': period, 'cost_of_credit_over_credit_income': cost / income})
    ecl = get('Q32026', 'ecl_expense', 'IFRS_quarterly_expense_positive')
    pbt = get('Q32026', 'profit_before_tax', 'IFRS_quarterly_reported')
    breakeven = pbt / ecl
    scenarios = [
        {'increase_in_IFRS_ECL_expense': shock,
         'incremental_ECL_expense_USD_million': ecl * shock,
         'profit_before_tax_USD_million': pbt - ecl * shock}
        for shock in (0., .2, .5, .8, breakeven, 1.)]
    result = {
        'scope': 'Nu Holdings consolidated', 'period': 'Q32026',
        'IFRS_ECL_expense_USD_million': ecl,
        'IFRS_profit_before_tax_USD_million': pbt,
        'additional_ECL_expense_to_zero_PBT_USD_million': pbt,
        'proportional_ECL_expense_increase_to_zero_PBT': breakeven,
        'managerial_ratios_separate_basis': ratios,
        'managerial_ratio_change_percentage_points': 100 * (
            ratios[1]['cost_of_credit_over_credit_income'] -
            ratios[0]['cost_of_credit_over_credit_income']),
        'frozen_quarter_scenarios': scenarios,
        'interpretation': 'Only IFRS ECL expense changes; all other quarterly '
            'income and expenses are fixed. No tax response, future path, '
            'capital, RWA or liquidity reaction is modelled. Managerial cost '
            'of credit is not substituted for IFRS ECL expense.'
    }
    return result


def main():
    def clean(value):
        if isinstance(value, float):
            return float(format(value, '.12g'))
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v) for v in value]
        return value
    result = clean(calculate(observations()))
    (ROOT / 'results/earnings_sensitivity.json').write_text(
        json.dumps(result, indent=2) + '\n')
    with (ROOT / 'results/earnings_sensitivity.csv').open('w', newline='') as f:
        rows = result['frozen_quarter_scenarios']
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
