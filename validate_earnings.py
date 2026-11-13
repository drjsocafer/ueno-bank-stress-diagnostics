"""Check the frozen-quarter identity and prevent IFRS/managerial mixing."""
import copy
import unittest
from pathlib import Path
from earnings_sensitivity import observations, calculate


class EarningsChecks(unittest.TestCase):
    def setUp(self):
        self.data = observations()

    def test_incremental_charge_eliminates_pretax_profit(self):
        r = calculate(self.data)
        self.assertAlmostEqual(r['proportional_ECL_expense_increase_to_zero_PBT'],
                               1350.3 / 1668.5)
        for row in r['frozen_quarter_scenarios']:
            self.assertAlmostEqual(row['profit_before_tax_USD_million'] +
                                   row['incremental_ECL_expense_USD_million'], 1350.3)
        self.assertAlmostEqual(r['frozen_quarter_scenarios'][-2][
            'profit_before_tax_USD_million'], 0.)

    def test_reject_mixed_accounting_basis(self):
        changed = copy.deepcopy(self.data)
        changed['Q32026', 'ecl_expense'] = copy.deepcopy(
            self.data['Q32026', 'cost_of_credit'])
        with self.assertRaises(ValueError):
            calculate(changed)

    def test_managerial_cost_does_not_change_IFRS_sensitivity(self):
        before = calculate(self.data)
        changed = copy.deepcopy(self.data)
        changed['Q32026', 'cost_of_credit']['value'] *= 1.5
        after = calculate(changed)
        self.assertEqual(before['frozen_quarter_scenarios'], after['frozen_quarter_scenarios'])
        self.assertNotEqual(before['managerial_ratios_separate_basis'],
                            after['managerial_ratios_separate_basis'])


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(EarningsChecks))
    if not result.wasSuccessful():
        raise SystemExit(1)
    Path(__file__).with_name('EARNINGS_VALIDATION.txt').write_text(
        'PASS: frozen-quarter incremental IFRS ECL expense eliminates pre-tax profit.\n'
        'PASS: mixed managerial/IFRS input is rejected.\n'
        'PASS: managerial credit costs do not alter the separate IFRS sensitivity.\n'
        'These are arithmetic and accounting-basis checks, not empirical bank validation.\n')
