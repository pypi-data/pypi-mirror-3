# -*- Mode: Python; coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2007 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
#
""" Main gui definition for purchase application.  """

import gettext
import datetime
from decimal import Decimal

import pango
import gtk
from kiwi.datatypes import currency
from kiwi.enums import SearchFilterPosition
from kiwi.python import all
from kiwi.ui.objectlist import Column, SearchColumn
from kiwi.ui.search import ComboSearchFilter
from stoqlib.api import api
from stoqlib.domain.payment.operation import register_payment_operations
from stoqlib.domain.purchase import PurchaseOrder, PurchaseOrderView
from stoqlib.gui.dialogs.purchasedetails import PurchaseDetailsDialog
from stoqlib.gui.dialogs.sellablepricedialog import SellablePriceDialog
from stoqlib.gui.dialogs.stockcostdialog import StockCostDialog
from stoqlib.gui.editors.producteditor import ProductEditor
from stoqlib.gui.search.categorysearch import (SellableCategorySearch,
                                               BaseSellableCatSearch)
from stoqlib.gui.search.consignmentsearch import ConsignmentItemSearch
from stoqlib.gui.search.personsearch import SupplierSearch, TransporterSearch
from stoqlib.gui.search.productsearch import (ProductSearch,
                                              ProductStockSearch,
                                              ProductClosedStockSearch,
                                              ProductsSoldSearch)
from stoqlib.gui.search.purchasesearch import PurchasedItemsSearch
from stoqlib.gui.search.sellableunitsearch import SellableUnitSearch
from stoqlib.gui.search.servicesearch import ServiceSearch
from stoqlib.gui.wizards.consignmentwizard import (ConsignmentWizard,
                                                   CloseInConsignmentWizard)
from stoqlib.gui.wizards.purchasefinishwizard import PurchaseFinishWizard
from stoqlib.gui.wizards.purchasequotewizard import (QuotePurchaseWizard,
                                                     ReceiveQuoteWizard)
from stoqlib.gui.wizards.purchasewizard import PurchaseWizard
from stoqlib.lib.formatters import format_quantity
from stoqlib.lib.message import warning, yesno
from stoqlib.reporting.purchase import PurchaseReport

from stoq.gui.application import SearchableAppWindow

_ = gettext.gettext


class PurchaseApp(SearchableAppWindow):

    # TODO: Change all widget.set_sensitive to self.set_sensitive([widget])

    app_name = _('Purchase')
    app_icon_name = 'stoq-purchase-app'
    gladefile = "purchase"
    search_table = PurchaseOrderView
    search_label = _('matching:')
    embedded = True

    #
    # Application
    #

    def create_actions(self):
        actions = [
            ('menubar', None, ''),

            # Purchase
            ("Print", gtk.STOCK_PRINT, _("Print"), '',
             _("Print the list of orders")),
            ("StockCost", None, _("_Stock cost...")),
            ('ExportCSV', gtk.STOCK_SAVE_AS, _('Export CSV...'), '<Control>F10'),
            # Consignment
            ("CloseInConsignment", None, _("Close consigment...")),
            ("SearchInConsignmentItems", None, _("Search consigment items...")),

            # Order
            ("OrderMenu", None, _("Order")),

            # Search
            ("BaseCategories", None, _("Base categories..."), "<Control>b"),
            ("Categories", None, _("Categories..."), "<Control>c"),
            ("Products", 'stoq-products', _("Products..."), "<Control>d"),
            ("ProductUnits", None, _("Product units..."), "<Control>u"),
            ("Services", None, _("Services..."), "<Control>s"),
            ("SearchStockItems", None, _("Stock items..."), "<Control>i"),
            ("SearchClosedStockItems", None, _("Closed stock items..."),
             "<Control><Alt>c"),
            ("Suppliers", 'stoq-suppliers', _("Suppliers..."), "<Control>u"),
            ("Transporter", None, _("Transporters..."), "<Control>t"),
            ("SearchQuotes", None, _("Quotes..."), "<Control>e"),
            ("SearchPurchasedItems", None, _("Purchased items..."), "<Control>p"),
            ("ProductsSoldSearch", None, _("Products sold..."), ""),
            ("ProductsPriceSearch", None, _("Prices editor..."), ""),

            # Toolbar
            ("NewOrder", gtk.STOCK_NEW, _("Order"), '<control>o',
             _("Create a new purchase order")),
            ("NewQuote", gtk.STOCK_INDEX, _("Quote"), '<control>e',
             _("Create a new purchase quote")),
            ("NewConsignment", None, _("Consignment"), '',
             _("Create a new purchase consignment")),
            ("NewProduct", None, _("Product"), '',
             _("Create a new product")),

            ("Confirm", gtk.STOCK_APPLY, _("Confirm"), '',
             _("Confirm the selected order(s), marking it as sent to the "
               "supplier")),
            ("Cancel", gtk.STOCK_CANCEL, _("Cancel"), '',
             _("Cancel the selected order")),
            ("Edit", gtk.STOCK_EDIT, _("Edit"), '',
             _("Edit the selected order, allowing you to change it's details")),
            ("Details", gtk.STOCK_INFO, _("Details"), '',
             _("Show details of the selected order")),
            ("Finish", gtk.STOCK_APPLY, _("Finish"), '',
             _('Complete the selected partially received order')),
        ]

        self.purchase_ui = self.add_ui_actions("", actions,
                                               filename="purchase.xml")

        self.Confirm.props.is_important = True

        self.NewOrder.set_short_label(_("New order"))
        self.NewQuote.set_short_label(_("New quote"))
        self.Products.set_short_label(_("Products"))
        self.Suppliers.set_short_label(_("Suppliers"))

        self.set_help_section(_("Purchase help"),
                              'compras-inicio')
        self.popup = self.uimanager.get_widget('/PurchaseSelection')

    def create_ui(self):
        self.app.launcher.add_new_items([
            self.NewOrder,
            self.NewQuote,
            self.NewProduct,
            self.NewConsignment])
        self.app.launcher.add_search_items([
            self.Products,
            self.Suppliers,
            self.SearchQuotes,
            self.Services])
        parent = self.app.launcher.statusbar
        self.search.set_summary_label(column='total',
                                      label=_('<b>Orders total:</b>'),
                                      format='<b>%s</b>',
                                      parent=parent)
        self.search.search.search_button.hide()
        self.results.set_selection_mode(gtk.SELECTION_MULTIPLE)
        self.Confirm.set_sensitive(False)

    def activate(self):
        # Avoid letting this sensitive if has-rows is never emitted
        self.Print.set_sensitive(False)
        self.app.launcher.NewToolItem.set_tooltip(
            _("Create a new purchase order"))
        self.app.launcher.SearchToolItem.set_tooltip(
            _("Search for purchase orders"))
        self._update_view()
        self.results.set_selection_mode(gtk.SELECTION_MULTIPLE)

    def setup_focus(self):
        self.search.refresh()

    def deactivate(self):
        self.uimanager.remove_ui(self.purchase_ui)

    def new_activate(self):
        self._new_order()

    def search_activate(self):
        self.run_dialog(ProductSearch, self.conn, hide_price_column=True)

    def search_completed(self, results, states):
        if len(results):
            return

        supplier, status = states[:2]
        if len(states) > 2 or (supplier.text == '' and status.value is None):
            self.search.set_message("%s\n\n%s" % (
                _("No orders could be found."),
                _("Would you like to %s ?") % (
                    '<a href="new_order">%s</a>' % _("create a new order"))
                ))

        # FIXME: Push number of results to Statusbar

    #
    # SearchableAppWindow
    #

    def create_filters(self):
        self.set_text_field_columns(['supplier_name'])
        self.status_filter = ComboSearchFilter(_('Show orders'),
                                               self._get_status_values())
        self.add_filter(self.status_filter, SearchFilterPosition.TOP, ['status'])

    def get_columns(self):
        return [SearchColumn('id', title=_('#'),
                             data_type=int, justify=gtk.JUSTIFY_RIGHT,
                             width=60),
                Column('status_str', title=_(u'Status'), data_type=str,
                       visible=False),
                SearchColumn('open_date', title=_('Opened'),
                              long_title='Date Opened', width=90,
                              data_type=datetime.date, sorted=True,
                              order=gtk.SORT_DESCENDING),
                SearchColumn('supplier_name', title=_('Supplier'),
                             data_type=str, searchable=True, expand=True,
                             ellipsize=pango.ELLIPSIZE_END),
                SearchColumn('ordered_quantity', title=_('Ordered'),
                             data_type=Decimal, width=90,
                             format_func=format_quantity),
                SearchColumn('received_quantity', title=_('Received'),
                             data_type=Decimal, width=90,
                             format_func=format_quantity),
                SearchColumn('total', title=_('Total'),
                             data_type=currency, width=120)]

    #
    # Private
    #

    def _update_totals(self):
        self._update_view()

    def _update_list_aware_widgets(self, has_items):
        for widget in (self.Edit, self.Details, self.Print):
            widget.set_sensitive(has_items)

    def _update_view(self):
        self._update_list_aware_widgets(len(self.results))
        selection = self.results.get_selected_rows()
        can_edit = one_selected = len(selection) == 1
        can_finish = False
        if selection:
            can_send_supplier = all(
                order.status == PurchaseOrder.ORDER_PENDING
                for order in selection)
            can_cancel = all(order_view.purchase.can_cancel()
                for order_view in selection)
        else:
            can_send_supplier = False
            can_cancel = False

        if one_selected:
            can_edit = (selection[0].status == PurchaseOrder.ORDER_PENDING or
                        selection[0].status == PurchaseOrder.ORDER_QUOTING)
            can_finish = (selection[0].status == PurchaseOrder.ORDER_CONFIRMED and
                          selection[0].received_quantity > 0)

        self.Cancel.set_sensitive(can_cancel)
        self.Edit.set_sensitive(can_edit)
        self.Confirm.set_sensitive(can_send_supplier)
        self.Details.set_sensitive(one_selected)
        self.Finish.set_sensitive(can_finish)

    def _new_order(self, order=None, edit_mode=False):
        with api.trans() as trans:
            order = trans.get(order)
            self.run_dialog(PurchaseWizard, trans, order, edit_mode)

        if trans.committed:
            self.refresh()
            self.select_result(PurchaseOrderView.get(trans.retval.id))

    def _edit_order(self):
        selected = self.results.get_selected_rows()
        qty = len(selected)
        if qty != 1:
            raise ValueError('You should have only one order selected, '
                             'got %d instead' % qty)
        purchase = selected[0].purchase
        if purchase.status == PurchaseOrder.ORDER_PENDING:
            self._new_order(purchase, edit_mode=False)
        else:
            self._quote_order(purchase)

    def _run_details_dialog(self):
        order_views = self.results.get_selected_rows()
        qty = len(order_views)
        if qty != 1:
            raise ValueError('You should have only one order selected '
                             'at this point, got %d' % qty)
        self.run_dialog(PurchaseDetailsDialog, self.conn,
                        model=order_views[0].purchase)

    def _send_selected_items_to_supplier(self):
        api.rollback_and_begin(self.conn)

        orders = self.results.get_selected_rows()
        valid_order_views = [
            order for order in orders
                      if order.status == PurchaseOrder.ORDER_PENDING]

        if not valid_order_views:
            warning(_("There are no pending orders selected."))
            return

        msg = gettext.ngettext(
            _("The selected order will be marked as sent."),
            _("The %d selected orders will be marked as sent.")
            % len(valid_order_views),
            len(valid_order_views))
        confirm_label = gettext.ngettext(_("Confirm order"),
                                         _("Confirm orders"),
                                         len(valid_order_views))
        if yesno(msg, gtk.RESPONSE_NO, _("Don't confirm"), confirm_label):
            return

        with api.trans() as trans:
            for order_view in valid_order_views:
                order = trans.get(order_view.purchase)
                order.confirm()
        self.refresh()
        self.select_result(orders)

    def _finish_order(self):
        order_views = self.results.get_selected_rows()
        qty = len(order_views)
        if qty != 1:
            raise ValueError('You should have only one order selected '
                             'at this point, got %d' % qty)

        with api.trans() as trans:
            order = trans.get(order_views[0].purchase)
            self.run_dialog(PurchaseFinishWizard, trans, order)

        self.refresh()
        self.select_result(order_views)

    def _print_selected_items(self):
        items = self.results.get_selected_rows() or list(self.results)
        self.print_report(PurchaseReport, self.results, items,
                          self.status_filter.get_state().value)

    def _cancel_order(self):
        register_payment_operations()
        order_views = self.results.get_selected_rows()
        assert all(ov.purchase.can_cancel() for ov in order_views)
        cancel_label = gettext.ngettext(_("Cancel order"),
                                        _("Cancel orders"), len(order_views))
        select_label = gettext.ngettext(_('The selected order will be cancelled.'),
                                        _('The selected orders will be cancelled.'),
                                        len(order_views))
        if yesno(select_label, gtk.RESPONSE_NO,
                 _("Don't cancel"), cancel_label):
            return
        with api.trans() as trans:
            for order_view in order_views:
                order = trans.get(order_view.purchase)
                order.cancel()
        self._update_totals()
        self.refresh()
        self.select_result(order_views)

    def _get_status_values(self):
        items = [(text, value)
                    for value, text in PurchaseOrder.statuses.items()]
        items.insert(0, (_('Any'), None))
        return items

    def _quote_order(self, quote=None):
        with api.trans() as trans:
            quote = trans.get(quote)
            self.run_dialog(QuotePurchaseWizard, trans, quote)

        if trans.committed:
            self.refresh()
            self.select_result(PurchaseOrderView.get(trans.retval.id))

    def _new_product(self):
        with api.trans() as trans:
            self.run_dialog(ProductEditor, trans)

    def _new_consignment(self):
        with api.trans() as trans:
            self.run_dialog(ConsignmentWizard, trans)

        if trans.committed:
            self.refresh()
            self.select_result(PurchaseOrderView.get(trans.retval.id))

    #
    # Kiwi Callbacks
    #

    def key_control_a(self, *args):
        # FIXME Remove this method after gazpacho bug fix.
        self._new_order()

    def on_results__has_rows(self, klist, has_rows):
        self.Print.set_sensitive(has_rows)

    def on_results__right_click(self, results, result, event):
        self.popup.popup(None, None, None, event.button, event.time)

    def on_results__row_activated(self, klist, purchase_order_view):
        self._run_details_dialog()

    def on_results__selection_changed(self, results, selected):
        self._update_view()

    def on_results__activate_link(self, results, uri):
        if uri == 'new_order':
            self._new_order()

    def _on_results__double_click(self, results, order):
        self._run_details_dialog()

    def _on_results__has_rows(self, results, has_items):
        self._update_list_aware_widgets(has_items)

    def on_Details__activate(self, action):
        self._run_details_dialog()

    def on_Edit__activate(self, action):
        self._edit_order()

    def on_Print__activate(self, action):
        self._print_selected_items()

    def on_Cancel__activate(self, action):
        self._cancel_order()

    def on_Confirm__activate(self, button):
        self._send_selected_items_to_supplier()

    def on_Finish__activate(self, action):
        self._finish_order()

    # Order

    def on_StockCost__activate(self, action):
        self.run_dialog(StockCostDialog, self.conn, None)

    # Consignment

    def on_CloseInConsignment__activate(self, action):
        with api.trans() as trans:
            self.run_dialog(CloseInConsignmentWizard, trans)

    def on_SearchInConsignmentItems__activate(self, action):
        self.run_dialog(ConsignmentItemSearch, self.conn)

    def on_Categories__activate(self, action):
        self.run_dialog(SellableCategorySearch, self.conn)

    def on_SearchQuotes__activate(self, action):
        self.run_dialog(ReceiveQuoteWizard, self.conn)

    def on_SearchPurchasedItems__activate(self, action):
        self.run_dialog(PurchasedItemsSearch, self.conn)

    def on_SearchStockItems__activate(self, action):
        self.run_dialog(ProductStockSearch, self.conn)

    def on_SearchClosedStockItems__activate(self, action):
        self.run_dialog(ProductClosedStockSearch, self.conn)

    def on_Suppliers__activate(self, action):
        self.run_dialog(SupplierSearch, self.conn, hide_footer=True)

    def on_Products__activate(self, action):
        self.run_dialog(ProductSearch, self.conn, hide_price_column=True)

    def on_ProductUnits__activate(self, action):
        self.run_dialog(SellableUnitSearch, self.conn)

    def on_BaseCategories__activate(self, action):
        self.run_dialog(BaseSellableCatSearch, self.conn)

    def on_Services__activate(self, action):
        self.run_dialog(ServiceSearch, self.conn, hide_price_column=True)

    def on_Transporter__activate(self, action):
        self.run_dialog(TransporterSearch, self.conn, hide_footer=True)

    def on_ProductsSoldSearch__activate(self, action):
        self.run_dialog(ProductsSoldSearch, self.conn)

    def on_ProductsPriceSearch__activate(self, action):
        from stoqlib.domain.person import ClientCategory
        if not ClientCategory.select(connection=self.conn).count():
            warning(_("Can't use prices editor without client categories"))
            return

        with api.trans() as trans:
            self.run_dialog(SellablePriceDialog, trans)

    # Toolitem

    def on_NewOrder__activate(self, action):
        self._new_order()

    def on_NewQuote__activate(self, action):
        self._quote_order()

    def on_NewProduct__activate(self, action):
        self._new_product()

    def on_NewConsignment__activate(self, action):
        self._new_consignment()
