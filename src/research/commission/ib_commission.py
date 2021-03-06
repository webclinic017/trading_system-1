from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt


class IBCommission(bt.CommInfoBase):

    """A :class:`IBCommission` charges the way interactive brokers does.
    """

    params = (
        #('stocklike', True),
        #('commtype', bt.CommInfoBase.COMM_PERC),
        #('percabs', True),

        # Float. The amount charged per share. Ex: 0.005 means $0.005
        ('per_share', 0.005),

        # Float. The minimum amount that will be charged. Ex: 1.0 means $1.00
        ('min_per_order', 1.0),

        # Float. The maximum that can be charged as a percent of the trade value. Ex: 0.005 means 0.5%
        ('max_per_order_abs_pct', 0.005),
    )

    def _getcommission(self, size, price, pseudoexec):

        """
        :param size: current position size. > 0 for long positions and < 0 for short positions (this parameter will not be 0)
        :param price: current position price
        :param pseudoexec:
        :return: the commission of an operation at a given price
        """

        #TODO: This commission does not include the cost of exchange (I.e nasdaq/amex).
        # Additional mapping or charges are needed

        commission = abs(size * self.p.per_share) # absolute to make sure it doensn't get -ve
        order_price = price * size
        commission_as_percentage_of_order_price = commission / order_price

        if commission < self.p.min_per_order:
            commission = self.p.min_per_order
        elif commission_as_percentage_of_order_price > self.p.max_per_order_abs_pct:
            commission = order_price * self.p.max_per_order_abs_pct
        return commission
