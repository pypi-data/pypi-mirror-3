# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2012 Async Open Source
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
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
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
""" Base classes for editors """

import gtk
from gtk import gdk
from kiwi.enums import ListType
from kiwi.log import Logger
from kiwi.ui.delegates import GladeSlaveDelegate
from kiwi.ui.listdialog import ListContainer
from kiwi.ui.widgets.label import ProxyLabel

from stoqlib.database.runtime import StoqlibTransaction
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.gui.base.dialogs import RunnableView, BasicDialog, run_dialog
from stoqlib.gui.events import EditorSlaveCreateEvent

log = Logger('stoqlib.gui.editors')

_ = stoqlib_gettext


class BaseEditorSlave(GladeSlaveDelegate):
    """ Base class for editor slaves inheritance. It offers methods for
    setting up focus sequence, required attributes and validated attrs.

    :cvar gladefile:
    :cvar model_type:
    """
    gladefile = None
    model_type = None
    proxy_widgets = ()

    def __init__(self, conn, model=None, visual_mode=False):
        """ A base class for editor slaves inheritance

        :param conn: a connection
        :param model: the object model tied with the proxy widgets
        :param visual_mode: does this slave must be opened in visual mode?
                            if so, all the proxy widgets will be disable
        """
        self.conn = self.trans = conn
        self.edit_mode = model is not None
        self.visual_mode = visual_mode

        if model:
            created = ""
        else:
            created = "created "
            model = self.create_model(self.conn)

            if model is None:
                raise ValueError(
                    "%s.create_model() must return a valid model, not %r" % (
                    self.__class__.__name__, model))

        log.info("%s editor using a %smodel %s" % (
            self.__class__.__name__, created, type(model).__name__))

        if self.model_type:
            if not isinstance(model, self.model_type):
                raise TypeError(
                    '%s editor requires a model of type %s, got a %r' % (
                    self.__class__.__name__, self.model_type.__name__,
                    model))
        else:
            raise ValueError("Editor %s must define a model_type "
                             "attribute" % (
                self.__class__.__name__, ))
        self.model = model

        GladeSlaveDelegate.__init__(self, gladefile=self.gladefile)
        if self.visual_mode:
            self._setup_visual_mode()
        self.setup_proxies()
        self.setup_slaves()

        EditorSlaveCreateEvent.emit(self, model, conn, visual_mode)

    def _setup_visual_mode(self):
        widgets = self.__class__.proxy_widgets
        for widget_name in widgets:
            widget = getattr(self, widget_name)
            if isinstance(widget, ProxyLabel):
                continue
            widget.set_sensitive(False)

        if self.fields:
            for field in self.fields.values():
                field.set_sensitive(False)
                field.can_edit = False

        self.update_visual_mode()

    def create_model(self, trans):
        """Creates a new model for the editor.
        After this method is called, the model can be accessed as self.model.
        The default behavior is to raise a TypeError, which can
        be overridden in a subclass.
        :param trans: a database transaction
        """
        raise TypeError(
                "%r needs a model, got None. Perhaps you want to "
                "implement create_model?" % (self.__class__.__name__))

    def setup_proxies(self):
        """A subclass can override this
        """

    def setup_slaves(self):
        """A subclass can override this
        """

    #
    # Hook methods
    #

    def on_cancel(self):
        """ This is a hook method which must be redefined when some
        action needs to be executed when cancelling in the dialog. """
        return False

    def on_confirm(self):
        """ This is a hook method which must be redefined when some
        action needs to be executed when confirming in the dialog. """
        return self.model

    def update_visual_mode(self):
        """This method must be overwritten on child if some addition task in
        visual mode are needed
        """

    def validate_confirm(self):
        """ Must be redefined by childs and will perform some validations
        after the click of ok_button. It is interesting to use with some
        special validators that provide some tasks over more than one widget
        value """
        return True


class BaseEditor(BaseEditorSlave, RunnableView):
    """ Base class for editor dialogs. It offers methods of
    BaseEditorSlave, a windows title and OK/Cancel buttons.

    :cvar model_name: the model type name of the model we are editing.
       This value will be showed in the title of the editor and can not
       be merely the attribute __name__ of the object for usability reasons.
       Call sites will decide what could be the best name applicable in each
       situation.
    :cvar confirm_widgets: a list of widget names that when activated will
        confirm the dialog
    :cvar fields: a dictionary that contains :class:`stoqlib.gui.field.Field` attributes
    """

    model_name = None
    header = ''
    size = ()
    title = None
    hide_footer = False
    confirm_widgets = ()
    help_section = None
    fields = None
    form_holder_name = 'toplevel'

    def __init__(self, conn, model=None, visual_mode=False):
        if conn is not None and isinstance(conn, StoqlibTransaction):
            conn.needs_retval = True
        self._confirm_disabled = False

        # FIXME:
        # BasicEditor should inheirt from BasicDialog and instantiate
        # the slave inside here, but it requires some major surgery
        BaseEditorSlave.__init__(self, conn, model,
                                 visual_mode=visual_mode)

        self.main_dialog = BasicDialog(title=self.get_title(self.model),
                                       header_text=self.header,
                                       help_section=self.help_section,
                                       size=self.size)
        # Do not close the dialog if re return False on self.confirm
        self.main_dialog.enable_confirm_validation = True
        self.main_dialog.attach_slave("main", self)
        self.main_dialog.connect('confirm', self._on_main_dialog__confirm)
        self.main_dialog.connect('cancel', self._on_main_dialog__cancel)

        # This helps kiwis ui test, set the name of ourselves to
        # the classname of the slave, which is much more helpful than
        # just "BasicDialog"
        self.main_dialog.get_toplevel().set_name(self.__class__.__name__)

        if self.hide_footer or self.visual_mode:
            self.main_dialog.hide_footer()

        for name in self.confirm_widgets:
            self.set_confirm_widget(getattr(self, name))

        self.register_validate_function(self._validation_function)
        self.force_validation()

    def _get_title_format(self):
        if self.visual_mode:
            return _(u"Details of %s")
        if self.edit_mode:
            return _(u'Edit Details of "%s"')
        return _(u"Add %s")

    def get_title(self, model):
        if self.title:
            return self.title
        if not model:
            raise ValueError("A model should be defined at this point")

        title_format = self._get_title_format()
        if self.model_name:
            model_name = self.model_name
        else:
            # Fallback to the name of the class
            model_name = type(self.model).__name__

        return title_format % model_name

    def enable_window_controls(self):
        """Enables the window controls
        See :class:`kiwi.ui.views.BaseView.enable_window_controls`.
        """
        self.main_dialog.enable_window_controls()

    def set_description(self, description):
        """Sets the description of the model object which is used by the editor
        :param description:
        """
        format = self._get_title_format()
        self.main_dialog.set_title(format % description)

    def refresh_ok(self, validation_value):
        """ Refreshes ok button sensitivity according to widget validators
        status """
        if self._confirm_disabled:
            return
        self.main_dialog.ok_button.set_sensitive(validation_value)

    def add_button(self, label=None, stock=None):
        """
        Adds a button to editor. The added button is returned which you
        can use to connect signals on.
        :param label: label of the button
        :param stock: stock label of the button
        :param returns: the button added
        :rtype: gtk.Button
        """

        if label is None and stock is None:
            raise TypeError("You need to provide a label or a stock argument")

        button = gtk.Button(label=label, stock=stock)
        button.props.can_focus = True
        self.main_dialog.action_area.pack_start(button, False, False)
        self.main_dialog.action_area.reorder_child(button, 0)
        button.show()
        return button

    def cancel(self):
        """
        Cancel the dialog.
        """
        # self.on_cancel() should return a considered failure value
        self.retval = self.on_cancel()
        self.main_dialog.close()

        log.info("%s: Closed (cancelled), retval=%r" % (
            self.__class__.__name__, self.retval))

    def confirm(self):
        """
        Confirm the dialog.
        """
        if not self.is_valid or self._confirm_disabled:
            return False
        if not self.validate_confirm():
            return False

        # self.on_confirm() should return a considered success
        # value. It can be an integer or a model object.
        self.retval = self.on_confirm()
        self.main_dialog.close()
        if isinstance(self.conn, StoqlibTransaction):
            self.conn.retval = self.retval

        log.info("%s: Closed (confirmed), retval=%r" % (
            self.__class__.__name__, self.retval))

        return True

    def enable_ok(self):
        """
        Enable the ok button of the dialog, eg makes it possible
        to close/confirm the dialog.
        """
        self.main_dialog.enable_ok()
        self._confirm_disabled = False

    def disable_ok(self):
        """
        Enable the ok button of the dialog, eg makes it possible
        to close/confirm the dialog.
        """
        self.main_dialog.disable_ok()
        self._confirm_disabled = True

    def enable_normal_window(self):
        """
        Enable the dialog as a normal window.
        This tells the window manager that the window
        should behave as a normal window instead of a dialog.
        """
        toplevel = self.main_dialog.get_toplevel()
        toplevel.set_type_hint(gdk.WINDOW_TYPE_HINT_NORMAL)

    def set_confirm_widget(self, widget_name):
        """
        Make a widget confirmable, eg activating that widget would
        close the dialog.
        :param widget_name: name of the widget to be confirmable
        """
        self.main_dialog.set_confirm_widget(widget_name)

    def set_message(self, message, message_type=gtk.MESSAGE_INFO):
        """Sets a message for this editor
        :param message: message to add
        :param message_type: type of message to add
        """
        self.main_dialog.set_message(message, message_type)

    # RunnableView
    # This delegate everything to self.main_dialog

    def close(self):
        self.main_dialog.close()

    def run(self):
        self.main_dialog.run()

    def get_current_toplevel(self):
        return self.main_dialog.get_current_toplevel()

    def destroy(self):
        self.main_dialog.destroy()

    def set_transient_for(self, window):
        self.main_dialog.set_transient_for(window)

    # Callbacks

    def _on_main_dialog__cancel(self, dialog, retval):
        self.cancel()

    def _on_main_dialog__confirm(self, dialog, retval):
        return self.confirm()

    def _validation_function(self, is_valid):
        self.refresh_ok(is_valid)


class BaseRelationshipEditorSlave(GladeSlaveDelegate):
    """An editor for relationships between objects

    BaseRelationshipEditor provides an easy way to edit (add/remove) relations
    between objects.

    It doesn't allow creations of new objects, only linking between them.
    (the linking might require new objects, though)

    For example, you could edit suppliers for a product (or produts supplied
    by an supplier).

    Subclasses must implement get_targets, get_columns, get_relations, and
    create_model.
    """
    gladefile = 'RelationshipEditor'
    target_name = None
    model_type = None
    editor = None

    def __init__(self, conn, parent=None, visual_mode=False):
        self._parent = parent
        self.conn = conn
        self.visual_mode = visual_mode
        GladeSlaveDelegate.__init__(self, gladefile=self.gladefile)
        self._setup_widgets()

    def _setup_relations_list(self):
        self.relations_list = ListContainer(self.get_columns(), gtk.ORIENTATION_HORIZONTAL)
        self.relations_list._vbox.padding = 0
        self.model_vbox.pack_start(self.relations_list)

        self.relations_list.set_list_type(ListType.UNADDABLE)

        self.relations_list.connect('remove-item',
                                    self._on_remove_item__clicked)
        self.relations_list.connect('edit-item', self._on_edit_item__clicked)

        self.relations_list.show()

    def _setup_widgets(self):
        self.model_name_label.set_label(self.target_name + ':')
        targets = self.get_targets()
        self.target_combo.prefill(targets)

        self._setup_relations_list()

        size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        size_group.add_widget(self.add_button)
        size_group.add_widget(self.relations_list.edit_button)
        size_group.add_widget(self.relations_list.remove_button)

        self.add_button.set_sensitive(False)

        if not self.editor:
            self.relations_list.edit_button.set_sensitive(False)

        self.relations_list.add_items(self.get_relations())

        if self.visual_mode:
            self.target_combo.set_sensitive(False)
            self.add_button.set_sensitive(False)
            self.relations_list.set_list_type(ListType.READONLY)

    def get_targets(self):
        """Returns a list of valid taret objects.

        for instance, if suppliers for a product are being edited, then this
        should return a list fo suppliers.
        """
        raise NotImplementedError

    def get_columns(self):
        """Columns to display"""
        raise NotImplementedError

    def get_relations(self):
        """Returns the already existing relations.

        This may be entries from a maping table or entries from the target
        table itself, depending on the type of relationship
        """
        raise NotImplementedError

    def create_model(self):
        """This method should create the model when adding a new relationship.

        If the addition is canceled. It will automatically be removed.
        """
        raise NotImplementedError

    def add(self):
        model = self.create_model()

        if not model:
            return False

        if not self.editor:
            return model

        res = run_dialog(self.editor, self._parent, self.conn, model)

        if not res:
            self.model_type.delete(id=model.id, connection=self.conn)

        return res

    def edit(self, model):
        return run_dialog(self.editor, self._parent, self.conn, model)

    def remove(self, model):
        self.model_type.delete(model.id, connection=self.conn)
        return True

    def _run_editor(self, model=None):
        """Runs an editor for the relationship (if necessary).

        An editor may be necessary only if there is an mapping table and
        and extra information in this table.
        """
        if model is None:
            res = self.add()
        else:
            res = self.edit(model)

        return res

    def on_add_button__clicked(self, widget):
        result = self._run_editor()
        if result:
            self.relations_list.add_item(result)

    def on_target_combo__content_changed(self, widget):
        has_selected = self.target_combo.read() is not None
        self.add_button.set_sensitive(has_selected and not self.visual_mode)

    def _on_edit_item__clicked(self, list, item):
        result = self._run_editor(item)

        if result:
            self.relations_list.update_item(result)

    def _on_remove_item__clicked(self, list, item):
        if self.remove(item):
            self.relations_list.remove_item(item)
