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

"""
This package implements the internal chessproblem (representation) model.
"""

import logging

import re

import kph

LOGGER = logging.getLogger('chessproblem.model')

PIECE_TYPE_PAWN       = 0
PIECE_TYPE_KNIGHT     = 1
PIECE_TYPE_BISHOP     = 2
PIECE_TYPE_ROOK       = 3
PIECE_TYPE_QUEEN      = 4
PIECE_TYPE_KING       = 5
PIECE_TYPE_EQUIHOPPER = 6
PIECE_TYPE_CIRCLE     = 7
PIECE_TYPE_COUNT      = 8

NORMAL_PIECE_TYPE_COUNT = 6

PIECE_COLOR_WHITE   = 0
PIECE_COLOR_BLACK   = 1
PIECE_COLOR_NEUTRAL = 2
PIECE_COLOR_COUNT   = 3

PIECE_ROTATION_NORMAL       = 0
PIECE_ROTATION_LEFT         = 1
PIECE_ROTATION_RIGHT        = 2
PIECE_ROTATION_UPSIDEDOWN   = 3
PIECE_ROTATION_COUNT        = 4

import string

from chessproblem.config import DEFAULT_CONFIG

def _handle_command(command):
    if command == 'i':
        return 'i'
    elif command == 'j':
        return 'j'
    elif command == 'o' or command == 'O':
        return 'o'
    elif command == 'l' or command == 'L':
        return 'l'
    elif command == 'AA' or command == 'aa':
        return 'a'
    elif command == 'AE' or command == 'ae':
        return 'ae'
    elif command == 'OE' or command == 'oe':
        return 'oe'
    elif command == 'ss':
        return 'ss'
    else:
        return ''

def un_latex_string(s):
    '''
    This method is used to remove latex encodings from a string (e.g. a name).

    For special TeX codings like \\i it creates an i. Most other latex codes and macros are simply removed.
    '''
    result = ''
    command = ''
    i = iter(s)
    state = 0
    try:
        while True:
            c = i.next()
            if state == 0:
                if c in string.ascii_letters:
                    result = result + c.lower()
                elif c == '\\':
                    state = 1
                    command = ''
            elif state == 1:
                if c in string.ascii_letters:
                    command = command + c
                    state = 2
                elif c == '3':
                    result = result + 'ss'
                    state = 0
                else:
                    # Ignore this latex command
                    state = 0
            elif state == 2:
                if c in string.ascii_letters:
                    command = command + c
                else:
                    result = result + _handle_command(command)
                    command = ''
                    if c == '\\':
                        state = 1
                    else:
                        state = 0
    except StopIteration:
        if state == 2:
            result = result + _handle_command(command)
    return result


def normalize_string(s):
    '''
    This methos is used to normalize names.
    '''
    return un_latex_string(s)

class Piece(object):
    '''
    Stores the type of the piece.
    '''
    def __init__(self, piece_color, piece_type, piece_rotation=PIECE_ROTATION_NORMAL):
        self.piece_color = piece_color
        self.piece_type = piece_type
        self.piece_rotation = piece_rotation

def normalize_author_name(lastname, firstname):
    return normalize_string(lastname) + ', ' + normalize_string(firstname)

class Country(object):
    '''
    Stores the country, where authors live.
    A list of these "car codes" including a list of ISO 3166 Country codes (2-letter, 3-letter and numeric) can be found
    at: http://www.aufenthaltstitel.de/staaten/schluessel.html
    '''
    def __init__(self, car_code, name=None, iso_3166_2=None, iso_3166_3=None, iso_3166_n=None):
        self.car_code = car_code
        self.name = name
        self.iso_3166_2 = iso_3166_2
        self.iso_3166_3 = iso_3166_3
        self.iso_3166_n = iso_3166_n
        self.search = None


    def on_persist(self):
        '''
        This method is is configured to be called automatically by sqlalchemhy.
        We use it to normalize the car_code column and to create the value for the search column.
        '''
        if self.car_code != None:
            self.car_code = string.upper(self.car_code)
        if self.name == None:
            self.search = ''
        else:
            self.search = normalize_string(self.name)

    def code(self):
        '''
        Our preferred code is the car_code.
        As not all countries in the world have a car code, we use the 3-letter iso code for such countries.
        '''
        if self.car_code != None:
            return self.car_code
        else:
            return self.iso_3166_3

    def __str__(self):
        if self.name != None:
            return '(' + self.code() + ') ' + self.name
        else:
            return '(' + self.code() + ') '

class City(object):
    '''
    Stores the city, where an author lives.
    '''
    def __init__(self, name, country=None):
        self.name = name
        self.search = None
        self.country = country

    def on_persist(self):
        '''
        This method is is configured to be called automatically by sqlalchemhy
        to calculate the value of the search column.
        '''
        if self.name == None:
            self.search = ''
            self.kph = ''
        else:
            self.search = normalize_string(self.name)
            self.kph = kph.encode(self.search)

    def __str__(self):
        '''
        This method creates a string representation including the country if available.
        '''
        if self.country != None:
            return self.country_code() + '--' + self.name
        else:
            return self.name

    def country_code(self):
        if self.country != None:
            return self.country.code()
        else:
            return ''

    def country_name(self):
        if self.country != None:
            return self.country.name
        else:
            return ''


class Author(object):
    '''
    Stores the author of a chessproblem.
    '''
    def __init__(self, lastname=None, firstname=None, city=None):
        self.lastname = lastname
        self.firstname = firstname
        self.city = city
        self.search = None

    def on_persist(self):
        '''
        This method is is configured to be called automatically by sqlalchemhy
        to calculate the value of the search column.
        '''
        self.search = normalize_author_name(self.lastname, self.firstname)
        self.lastname_kph = kph.encode(self.lastname)
        self.firstname_kph = kph.encode(self.firstname)

    def __str__(self):
        namestr = str(self.lastname) + ', ' + str(self.firstname)
        if self.city == None:
            return namestr
        else:
            return namestr + '[' + str(self.city) + ']'


class PieceCounter(object):
    def __init__(self, count_white=0, count_black=0, count_neutral=0):
        self.count_white = count_white
        self.count_black = count_black
        self.count_neutral = count_neutral



class Board(object):
    '''
    Stores the position of the board.
    '''
    def __init__(self, rows=8, columns=8):
        self.rows = rows
        self.columns = columns
        self.fields = [[None for column in range(0, columns)] for row in range(0, rows)]

    def resize(self, new_rows, new_columns):
        '''
        Change the size of the board to the new size and reuse the old position where possible.
        '''
        new_fields =  [[None for column in range(0, new_columns)] for row in range(0, new_rows)]
        if new_rows > self.rows:
            max_rows = self.rows
        else:
            max_rows = new_rows
        if new_columns > self.columns:
            max_columns = self.columns
        else:
            max_columns = new_columns
        for row in range(0, max_rows):
            for column in range(0, max_columns):
                new_fields[row][column] = self.fields[row][column]
        self.rows = new_rows
        self.columns = new_columns
        self.fields = new_fields

    def get_pieces_count(self):
        white = 0
        black = 0
        neutral = 0
        for row in range(0, self.rows):
            for column in range(0, self.columns):
                piece = self.fields[row][column]
                if piece != None:
                    if piece.piece_color == PIECE_COLOR_WHITE:
                        white += 1
                    elif piece.piece_color == PIECE_COLOR_BLACK:
                        black += 1
                    elif piece.piece_color == PIECE_COLOR_NEUTRAL:
                        neutral += 1
        return (white, black, neutral)





class Chessproblem(object):
    '''
    Stores all information about a chessproblem
    '''
    def __init__(self, rows=8, columns=8):
        self.board = Board(rows, columns)
        self.after_command_text = { '{diagram}': '%\n'}
        self.authors = []
        self.cities = []
        self.dedication = None
        self.after = None
        self.version = None
        self.stipulation = None
        self.condition = []
        self.twins = []
        self.remark = None
        self.solution = None
        self.themes = []
        self.comment = None
        self.specialdiagnum = None
        self.sourcenr = None
        self.source = None
        self.issue = None
        self.pages = None
        self.day = None
        self.month = None
        self.year = None
        self.tournament = None
        self.award = None
        # The following members are currently not supported
        self.verticalcylinder = False
        self.horizontalcylinder = False
        self.gridchess = False
        self.noframe = False
        self.nofields = None
        self.fieldframe = None
        self.gridlines = None
        self.fieldtext = None
        self.pieces_control = None
        # self.nofields = []
        # self.fieldframe = []
        # self.gridlines = []
        # self.fieldtext = []

def _is_chessproblem(o):
    return isinstance(o, Chessproblem)

def _is_text(o):
    return isinstance(o, str) or isinstance(o, unicode)

class ChessproblemDocument(object):
    '''
    This class will contain list where an element is either a 'Chessproblem' or a string.
    '''
    def __init__(self, document_content = None):
        if document_content == None:
            self.document_content = ['%\n', Chessproblem(), '%\n%\n']
        else:
            self.document_content = document_content

    def __iter__(self):
        return iter(self.document_content)

    def get_problem(self, index):
        return self._get_typed_element(index, _is_chessproblem)

    def get_text(self, index):
        return self._get_typed_element(index, _is_text)

    def _get_internal_index(self, index, check):
        found_index = -1
        for internal_index in range(len(self.document_content)):
            element = self.document_content[internal_index]
            if check(element):
                found_index += 1
                if found_index == index:
                    return internal_index
        return -1

    def _get_typed_element(self, index, check):
        internal_index = self._get_internal_index(index, check)
        if internal_index == -1:
            return None
        else:
            return self.document_content[internal_index]


    def get_problem_count(self):
        '''
        Return the number of problems contained in this document.
        '''
        return self._get_count(_is_chessproblem)

    def _get_count(self, check):
        count = 0
        for element in self.document_content:
            if check(element):
                count += 1
        return count

    def insert_problem(self, index, problem):
        '''
        Inserts the given problem before the problem with the given (problem) index.
        '''
        if index == self.get_problem_count():
            if self.get_problem_count() == 0:
                internal_index = 0
                LOGGER.debug('insert_problem: no problems in document')
            else:
                internal_index = len(self.document_content)
                LOGGER.debug('insert_problem: new last problem')
        else:
            internal_index = self._get_internal_index(index, _is_chessproblem)
        LOGGER.debug('insert_problem: insert_index = ' + str(internal_index))
        self.document_content.insert(internal_index, '%\n%\n%\n')
        self.document_content.insert(internal_index, problem)

    def set_problem(self, index, problem):
        '''
        Replace the problem with the given (problem) index with the given problem.
        '''
        internal_index = self._get_internal_index(index, _is_chessproblem)
        self.document_content[internal_index] = problem

    def delete_problem(self, index):
        '''
        Delete the problem with the given (problem) index.
        '''
        internal_index = self._get_internal_index(index, _is_chessproblem)
        self.document_content.pop(internal_index)

    def get_text_count(self):
        '''
        Return the number of text sections within the this document.
        '''
        return self._get_count(_is_text)

class ChessProblemModelFactory(object):
    '''
    Factory to create chesspbroblem model objects.
    '''
    def create_country(self, car_code, name=None):
        '''
        Creates a country object with the specified abbreviation.
        '''
        return Country(car_code, name)

    def create_city(self, country, city_name):
        '''
        Creates a city object with the given city_name and a reference to the given country.
        '''
        return City(city_name, country)

    def create_author(self, city, lastname, firstname):
        '''
        Creates an author object, with the given firstname and lastname, which refers to the given city.
        '''
        return Author(lastname, firstname, city)


class Source(object):
    '''
    The name of a book, magazine, newspaper (or even tournament) where a problem was published first.
    '''
    def __init__(self, name):
        '''
        Registers the name of the source.
        '''
        self.name = name

    def on_persist(self):
        '''
        '''
        self.search = normalize_string(self.name)
        self.kph = kph.encode(self.search)

