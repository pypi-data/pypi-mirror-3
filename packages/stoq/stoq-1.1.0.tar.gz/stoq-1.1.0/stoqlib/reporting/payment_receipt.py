# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
##
##  Author(s): Stoq Team <stoq-devel@async.com.br>
##
##

""" A payment receipt implementation """

from stoqlib.domain.interfaces import ICompany, IIndividual
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.reporting.template import BaseRMLReport

_ = stoqlib_gettext


class PaymentReceipt(BaseRMLReport):
    """Payment receipt
        This class builds the namespace used in template
    """
    template_name = 'receipt.rml'
    title = _("Payment receipt")

    def __init__(self, filename, payments, purchase):
        self.payments = payments
        self.order = purchase
        BaseRMLReport.__init__(self, filename)

    #
    # BaseRMLReport
    #

    def get_namespace(self):
        company = ICompany(self.order.supplier.person, None)
        individual = IIndividual(self.order.supplier.person, None)
        if company:
            document = company.cnpj
        elif individual:
            document = individual.cpf
        else:
            document = ""
        return dict(document=document,
                    drawee=self.order.supplier.person,
                    order=self.order,
                    payer=self.order.branch.person,
                    payments=self.payments)
