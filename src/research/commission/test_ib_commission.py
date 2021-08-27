import unittest
from ib_commission import IBCommission


class TestIBCommission(unittest.TestCase):

    def test_IBCommission(self):
        ib_comm = IBCommission()

        # test per_share commission
        # 1,000 Shares @ USD 25 Share Price = USD 5.00
        commission = ib_comm.getcommission(1000, 25.00)
        self.assertEqual(commission, 5.00)

        # test min_per_order commission
        # 100 Shares @ USD 25 Share Price = USD 1.00
        commission = ib_comm.getcommission(100, 25.00)
        self.assertEqual(commission, 1.00)

        # test maxPerOrderPct commission
        # 1,000 Shares @ USD 0.25 Share Price = USD 1.25
        commission = ib_comm.getcommission(1000, .25)
        self.assertEqual(commission, 1.25)


if __name__ == '__main__':
    unittest.main()