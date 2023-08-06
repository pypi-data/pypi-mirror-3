# Copyright 2012 Stefan Hoening
# 
# This file is part of the "Chess-Problem-Editor" software.
# 
# Chess-Problem-Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Chess-Problem-Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Diese Datei ist Teil der Software "Chess-Problem-Editor".
# 
# Chess-Problem-Editor ist Freie Software: Sie koennen es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Option) jeder spaeteren
# veroeffentlichten Version, weiterverbreiten und/oder modifizieren.
# 
# Chess-Problem-Editor wird in der Hoffnung, dass es nuetzlich sein wird, aber
# OHNE JEDE GEWAEHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewaehrleistung der MARKTFAEHIGKEIT oder EIGNUNG FUER EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License fuer weitere Details.
# 
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.

'''
This module contains special gtk user interface elements used to display chess problem information.
'''
import gtk
import pango
import gobject

from chessproblem.config import DEFAULT_CONFIG

from chessproblem.ui.gtk_search import SearchPanel, AbstractDataListBox, AbstractSearchDialog

from chessproblem.ui.search_descriptors import AuthorSearchDataProvider, SourceSearchDataProvider

from chessproblem.ui.gtk_common import create_button

LABEL_PADDING=4

_ENTRIES = ['specialdiagnum', 'sourcenr', 'source', 'issue', 'day', 'month', 'year', 'dedication', 'after', 'award', 'tournament', 'stipulation', 'remark']

_TEXTVIEWS = ['solution', 'comment']

_CHECKBOXES = ['gridchess', 'verticalcylinder', 'horizontalcylinder']

def _non_none_str(value):
    if value != None:
        return value
    else:
        return ''

def _do_nothing():
    pass

class SourceSearchDialog(AbstractSearchDialog):
    '''
    A dialog to search for sources.
    '''
    def __init__(self, db_service):
        AbstractSearchDialog.__init__(self, 'Source search', SourceSearchDataProvider(db_service), self.object_selected)
        self.result = None

    def object_selected(self, source):
        self.set_response_sensitive(gtk.RESPONSE_ACCEPT, source != None)
        self.result = source

class InfoArea(gtk.Table):
    def __init__(self, db_service):
        gtk.Table.__init__(self, 8, 12, False)
        self.db_service = db_service
        self.visual_change_listener = _do_nothing
        row = 0
        self._create_and_attach_labelled_entry('specialdiagnum', 0, row, char_width=10)
        self._create_and_attach_labelled_entry('sourcenr', 2, row, char_width=8)
        self.button_select_source = create_button('source', self._on_select_source)
        self._attach_button(self.button_select_source, 4, row)
        self._create_and_attach_entry('source', 5, row, width=4)
        row += 1
        self._create_and_attach_labelled_entry('issue', 0, row, char_width=10)
        self._create_and_attach_labelled_entry('day', 2, row, char_width=2)
        self._create_and_attach_labelled_entry('month', 4, row, char_width=5)
        self._create_and_attach_labelled_entry('year', 6, row, char_width=4)
        row += 1
        self._create_and_attach_label('authors', 0, row)
        self.button_edit_authors = create_button('edit', self._on_edit_authors)
        self._attach_button(self.button_edit_authors, 0, row + 1)
        self.liststore_authors = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.listbox_authors = gtk.TreeView(self.liststore_authors)
        self.listbox_authors.append_column(gtk.TreeViewColumn('lastname', gtk.CellRendererText(), text=0))
        self.listbox_authors.append_column(gtk.TreeViewColumn('givenname', gtk.CellRendererText(), text=1))
        self.listbox_authors.append_column(gtk.TreeViewColumn('city', gtk.CellRendererText(), text=2))
        self.listbox_authors.set_size_request(-1, 100)
        self.listbox_authors.show()
        self._attach_listbox(self.listbox_authors, 1, row)
        row += 3
        self._create_and_attach_labelled_entry('dedication', 0, row, width=3)
        self._create_and_attach_labelled_entry('after', 4, row, width=3)
        row += 1
        self._create_and_attach_labelled_entry('award', 0, row, char_width=10)
        self._create_and_attach_labelled_entry('tournament', 2, row, width=5)
        row += 1
        self._create_and_attach_labelled_entry('stipulation', 0, row, width=2)
        self._create_and_attach_labelled_entry('remark', 3, row, width=4)
        row += 1
        self._create_and_attach_label('conditions', 0, row)
        self.button_edit_conditions = create_button('edit', self._on_edit_conditions)
        self._attach_button(self.button_edit_conditions, 0, row + 1)
        self.liststore_conditions = gtk.ListStore(gobject.TYPE_STRING)
        self.listbox_conditions = gtk.TreeView(self.liststore_conditions)
        self.listbox_conditions.append_column(gtk.TreeViewColumn('condition', gtk.CellRendererText(), text=0))
        self.listbox_conditions.set_size_request(-1, 80)
        self.listbox_conditions.show()
        self._attach_listbox(self.listbox_conditions, 1, row, width=3)
        self._create_and_attach_label('twins', 4, row)
        self.button_edit_twins = create_button('edit', self._on_edit_twins)
        self._attach_button(self.button_edit_twins, 4, row + 1)
        self.liststore_twins = gtk.ListStore(gobject.TYPE_STRING)
        self.listbox_twins = gtk.TreeView(self.liststore_twins)
        self.listbox_twins.append_column(gtk.TreeViewColumn('twin', gtk.CellRendererText(), text=0))
        self.listbox_twins.set_size_request(-1, 80)
        self.listbox_twins.show()
        self._attach_listbox(self.listbox_twins, 5, row, width=3)
        row += 3
        self._create_and_attach_label('solution', 1, row)
        self.scrolledwindow_solution = gtk.ScrolledWindow()
        self.scrolledwindow_solution.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textbuffer_solution = gtk.TextBuffer()
        self.textview_solution = gtk.TextView()
        self.textview_solution.set_size_request(-1, 51)
        self.textview_solution.show()
        self.scrolledwindow_solution.show()
        self.scrolledwindow_solution.add(self.textview_solution)
        self.attach(self.scrolledwindow_solution, 2, 8, row, row + 2, xpadding=2, ypadding=2)
        row += 2
        self._create_and_attach_label('comment', 1, row)
        self.scrolledwindow_comment = gtk.ScrolledWindow()
        self.scrolledwindow_comment.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textbuffer_comment = gtk.TextBuffer()
        self.textview_comment = gtk.TextView()
        self.textview_comment.set_size_request(-1, 51)
        self.textview_comment.show()
        self.scrolledwindow_comment.show()
        self.scrolledwindow_comment.add(self.textview_comment)
        self.attach(self.scrolledwindow_comment, 2, 8, row, row + 2, xpadding=2, ypadding=2)
        row -= 2
        self._create_and_attach_checkbox('gridchess', 0, row)
        row += 1
        self._create_and_attach_checkbox('verticalcylinder', 0, row)
        row += 1
        self._create_and_attach_checkbox('horizontalcylinder', 0, row)

    def save_to_problem(self):
        '''
        Transfers the value of all text fields to the current problem.
        '''
        for name in _ENTRIES:
            entry = getattr(self, 'entry_' + name)
            value = entry.get_text()
            if value == '':
                setattr(self._problem, name, None)
            else:
                setattr(self._problem, name, value)
        for name in _TEXTVIEWS:
            entry = getattr(self, 'textview_' + name)
            textbuffer = entry.get_buffer()
            value = textbuffer.get_property('text')
            if value == '':
                setattr(self._problem, name, None)
            else:
                setattr(self._problem, name, value)
        for name in _CHECKBOXES:
            self.save_checkbox_to_problem(name)

    def save_checkbox_to_problem(self, name):
        '''
        Stores the value of the checkbox with the given name to the problem.
        '''
        checkbox = getattr(self, 'checkbox_' + name)
        setattr(self._problem, name, checkbox.get_active())

    def set_problem(self, problem):
        '''
        Registers the given problem and transfers its data to the widgets.
        '''
        self._problem = problem
        # Show all normal text values
        for name in _ENTRIES:
            value = getattr(problem, name)
            entry = getattr(self, 'entry_' + name)
            entry.set_text(_non_none_str(value))
        for name in _TEXTVIEWS:
            value = getattr(problem, name)
            textview = getattr(self, 'textview_' + name)
            textbuffer = textview.get_buffer()
            if value != None:
                textbuffer.set_text(value)
            else:
                textbuffer.set_text('')
        self._fill_authors_liststore()
        self._fill_conditions_liststore()
        self._fill_twins_liststore()
        self.textbuffer_solution.set_text(_non_none_str(problem.solution))
        self.textbuffer_comment.set_text(_non_none_str(problem.comment))
        for name in _CHECKBOXES:
            checkbox = getattr(self, 'checkbox_' + name)
            value = getattr(self._problem, name)
            checkbox.set_active(value)

    def _fill_conditions_liststore(self):
        self.liststore_conditions.clear()
        for condition in self._problem.condition:
            self.liststore_conditions.append([condition])


    def _fill_twins_liststore(self):
        self.liststore_twins.clear()
        for twin in self._problem.twins:
            self.liststore_twins.append([twin])

    def _fill_authors_liststore(self):
        self.liststore_authors.clear()
        for author in self._problem.authors:
            self.liststore_authors.append([author.lastname, author.firstname, str(author.city)])

    def _create_and_attach_label(self, name, x, y):
        label = gtk.Label(name)
        setattr(self, 'label_' + name, label)
        label.show()
        self.attach(label, x, x + 1, y, y + 1, xpadding=LABEL_PADDING)

    def _create_and_attach_checkbox(self, name, x, y):
        '''
        Creates a checkbox with the given name suffix and attaches this checkbox at position x, y.
        Additionally the 'toggled' event is registered to the _on_checkbox method.
        '''
        checkbox = gtk.CheckButton(name)
        setattr(self, 'checkbox_' + name, checkbox)
        checkbox.show()
        checkbox.connect('toggled', self._on_checkbox, name)
        self.attach(checkbox, x, x + 1, y, y + 1, xpadding=LABEL_PADDING)

    def set_visual_change_listener(self, listener):
        self.visual_change_listener = listener

    def _on_checkbox(self, widget, data=None):
        self.save_checkbox_to_problem(data)
        self.visual_change_listener()

    def _attach_button(self, button, x,  y):
        self.attach(button, x, x + 1, y, y + 1, yoptions=0)

    def _create_and_attach_labelled_entry(self, name, x, y, char_width=None, width=1):
        '''
        Creates a label with the given name prefixed by 'label_' and an entry with the given name prefixed by 'entry_'.
        The label is attached at position x, y; the entry is attached at position x + 1, y.
        '''
        self._create_and_attach_label(name, x, y)
        self._create_and_attach_entry(name, x + 1, y, char_width, width)

    def _create_and_attach_entry(self, name, x, y, char_width=None, width=1):
        entry = gtk.Entry()
        setattr(self, 'entry_' + name, entry)
        entry.show()
        if char_width != None:
            entry.set_width_chars(char_width)
        self.attach(entry, x, x + width, y, y + 1)

    def _attach_entry(self, entry, x, y, width=1):
        self.attach(entry, x, x + width, y, y + 1)

    def _attach_listbox(self, listbox, x, y, width=7, height=3):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(listbox)
        scrolled_window.show()
        self.attach(scrolled_window, x, x + width, y, y + height, xpadding=2, ypadding=2)

    def _on_select_source(self, widget, data=None):
        search_dialog = SourceSearchDialog(self.db_service)
        response = search_dialog.run()
        search_dialog.hide()
        if response == gtk.RESPONSE_ACCEPT:
            source = search_dialog.result
            self.entry_source.set_text(source.name)

    def _on_edit_authors(self, widget, data=None):
        '''
        Called when the 'edit' button for authors is pressed.
        '''
        _edit_authors_dialog = EditAuthorsDialog(self.db_service, self._problem.authors)
        response = _edit_authors_dialog.run()
        _edit_authors_dialog.hide()
        if response == gtk.RESPONSE_ACCEPT:
            self._problem.authors = _edit_authors_dialog.get_values()
            self._problem.cities = [author.city for author in self._problem.authors]
            self._fill_authors_liststore()

    def _on_edit_conditions(self, widget, data=None):
        '''
        Called when the 'edit' button for conditions is pressed.
        '''
        _edit_conditions_dialog = EditStringListDialog(self._problem.condition, 'edit conditions', 'condition')
        response = _edit_conditions_dialog.run()
        _edit_conditions_dialog.hide()
        if response == gtk.RESPONSE_ACCEPT:
            self._problem.condition = _edit_conditions_dialog.get_values()
            self._fill_conditions_liststore()

    def _on_edit_twins(self, widget, data=None):
        '''
        Called when the 'edit' button for twins is pressed.
        '''
        _edit_twins_dialog = EditStringListDialog(self._problem.twins, 'edit twins', 'twin')
        response = _edit_twins_dialog.run()
        _edit_twins_dialog.hide()
        if response == gtk.RESPONSE_ACCEPT:
            self._problem.twins = _edit_twins_dialog.get_values()
            self._fill_twins_liststore()

class AuthorsListBox(AbstractDataListBox):
    def __init__(self, db_service, selection_handler):
        AbstractDataListBox.__init__(self, AuthorSearchDataProvider(db_service), selection_handler)

    def add_author(self, author):
        self.objects.append(author)
        self._on_objects_changed()


class EditAuthorsDialog(gtk.Dialog):
    def __init__(self, db_service, authors):
        gtk.Dialog.__init__(self,
                title='edit authors',
                flags=gtk.DIALOG_MODAL,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.db_service = db_service
        self.table_layout = gtk.Table(3, 3, False)
        self.table_layout.show()
        self.get_content_area().pack_start(self.table_layout)
        self.box_selected_authors = gtk.VBox(False, 0)
        self.box_selected_authors.show()
        self.table_layout.attach(self.box_selected_authors, 0, 1, 0, 3)
        self.label_selected_authors = gtk.Label('selected authors')
        self.label_selected_authors.show()
        self.box_selected_authors.pack_start(self.label_selected_authors)
        self.listbox_selected_authors = AuthorsListBox(db_service, self._on_selected_authors_changed)
        self.listbox_selected_authors.set_objects(authors)
        self.listbox_selected_authors.show()
        self.scrolledwindow_selected_authors = gtk.ScrolledWindow()
        self.scrolledwindow_selected_authors.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledwindow_selected_authors.add(self.listbox_selected_authors)
        self.scrolledwindow_selected_authors.show()
        self.box_selected_authors.pack_start(self.scrolledwindow_selected_authors)
        self.button_box = gtk.VBox(False, 0)
        self.button_box.show()
        self.table_layout.attach(self.button_box, 1, 2, 1, 2, xpadding=10)
        self.button_add_author = gtk.Button('add author')
        self.button_add_author.set_sensitive(False)
        self.button_add_author.connect('clicked', self._on_button_add_author)
        self.button_add_author.show()
        self.button_box.pack_start(self.button_add_author, False, False, 5)
        self.button_remove_author = gtk.Button('remove author')
        self.button_remove_author.set_sensitive(False)
        self.button_remove_author.connect('clicked', self._on_button_remove_author)
        self.button_remove_author.show()
        self.button_box.pack_start(self.button_remove_author, False, False, 5)
        self.authors_search_panel = SearchPanel(AuthorSearchDataProvider(self.db_service), self._on_search_author_selected)
        self.authors_search_panel.show()
        self.table_layout.attach(self.authors_search_panel, 2, 3, 0, 3)

    def _on_search_author_selected(self, author):
        self.selected_search_author = author
        self.button_add_author.set_sensitive(author != None)

    def _on_selected_authors_changed(self, author):
        self.button_remove_author.set_sensitive(author != None)

    def _on_button_add_author(self, widget, data=None):
        if self.selected_search_author != None:
            self.listbox_selected_authors.add_author(self.selected_search_author)

    def _on_button_remove_author(self, widget, data=None):
        self.listbox_selected_authors.remove_selected()
    
    def get_values(self):
        return self.listbox_selected_authors.objects

class EditStringListDialog(gtk.Dialog):
    def __init__(self, string_list, title, name):
        gtk.Dialog.__init__(self,
                title=title,
                flags=gtk.DIALOG_MODAL,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.table_layout = gtk.Table(3, 2, False)
        self.table_layout.show()
        self.get_content_area().pack_start(self.table_layout)
        self.liststore_strings = gtk.ListStore(gobject.TYPE_STRING)
        self.listbox_strings = gtk.TreeView(self.liststore_strings)
        self.listbox_strings.set_size_request(200, 100)
        self.listbox_strings.append_column(gtk.TreeViewColumn(name, gtk.CellRendererText(), text=0))
        self.listbox_strings.show()
        self.table_layout.attach(self.listbox_strings, 0, 1, 0, 2)
        self.entry_string = gtk.Entry()
        self.entry_string.show()
        self.table_layout.attach(self.entry_string, 0, 1, 2, 3, yoptions=0)
        self.button_delete = gtk.Button('delete ' + name)
        self.button_delete.connect('clicked', self._on_button_delete)
        self.button_delete.show()
        self.table_layout.attach(self.button_delete, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0)
        self.button_add = gtk.Button('add ' + name)
        self.button_add.connect('clicked', self._on_button_add)
        self.button_add.show()
        self.table_layout.attach(self.button_add, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0)
        # Fill the liststore with the values given
        for string in string_list:
            self.liststore_strings.append([string])

    def _on_button_add(self, widget, data=None):
        value = self.entry_string.get_text()
        if value != '':
            print 'adding value to listbox: ' + value
            self.liststore_strings.append([value])
            self.entry_string.set_text('')

    def _on_button_delete(self, widget, data=None):
        selection = self.listbox_strings.get_selection()
        model, it = selection.get_selected()
        if it != None:
            self.liststore_strings.remove(it)

    def get_values(self):
        result = []
        it = self.liststore_strings.get_iter_first()
        while it != None:
            value = self.liststore_strings.get_value(it, 0)
            result.append(value)
            it = self.liststore_strings.iter_next(it)
        return result


class AuthorsDisplay(gtk.TextView):
    '''
    A spcial display to for the list of authors.
    '''

    def __init__(self):
        gtk.TextView.__init__(self)
        self.textbuffer = gtk.TextBuffer()
        self.set_buffer(self.textbuffer)
        self.set_editable(False)

    def set_problem(self, problem):
        self.problem = problem
        self.redisplay()

    def redisplay(self):
        text = ''
        if self.problem != None:
            first = True
            for author in self.problem.authors:
                if first:
                    first = False
                else:
                    text = text + '\n'
                text = text + str(author)
        self.textbuffer.set_text(text)
