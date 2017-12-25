"""
board.py

Boards for text games.

!! contents instead of piece/pieces

Classes:
BoardCell: A square (or other shape) in a board that holds one piece. (object)
Coordinate: A cartesian coordinate in an n-dimensional space. (tuple)
GridBoard: A rectangular board of squares. (object)
"""


import itertools


class BoardCell(object):
    """
    A square (or other shape) in a board that holds one piece. (object)

    The piece attribute may be any object, but it should convert to a string that
    correctly displays it on the board. Likewise, the location can be any object,
    but it should be hashable and support addition.

    Attributes:
    empty: How the cell looks when empty. (str)
    location: Where on the board the cell is. (object)
    piece: The piece occupying the board. (object)

    Methods:
    add_piece: Add a piece to the cell. (object)
    clear: Remove any piece from the cell. (None)
    remove_piece: Remove a piece from the cell. (object)

    Overridden Methods:
    __init__
    __contains__
    __hash__
    __iter__
    __repr__
    __str__
    """

    def __init__(self, location, piece = None, empty = ' '):
        """
        Initialize the cell. (None)

        Parameters:
        location: The location of the cell on the board. (hashable)
        piece: The piece initially in the cell. (object)
        empty: How the cell looks when empty. (str)
        """
        self.location = location
        self.contents = piece
        self.empty = empty

    def __contains__(self, other):
        """
        Check for a piece in the cell. (bool)

        other: The piece to check for. (object)
        """
        return self.contents == other

    def __hash__(self):
        """
        Hash function on the cell. (int)
        """
        return hash(self.location)

    def __iter__(self):
        """Iterate over the piece in the cell. (iterator)"""
        if self.contents is None:
            return iter([])
        else:
            return iter([self.contents])

    def __len__(self):
        """Return the number of pieces in the cell. (int)"""
        return self.contents is not None

    def __repr__(self):
        """
        Computer readable text representation. (str)
        """
        # keyword parameters
        if self.contents:
            piece_text = ', piece = {!r}'.format(self.contents)
        else:
            piece_text = ''
        if self.empty != ' ':
            empty_text = ', empty = {!r}'.format(self.empty)
        else:
            empty_text = ''
        # complete and return
        return '{}({!r}{}{})'.format(self.__class__.__name__, self.location, piece_text, empty_text)

    def __str__(self):
        """
        Human readable text representation. (str)
        """
        if self.contents:
            return str(self.contents)
        else:
            return self.empty

    def add_piece(self, piece):
        """
        Add a piece to the cell. (object)

        The return value is the piece that was in the cell before.

        Parameters:
        piece: The piece to add to the cell. (object)
        """
        capture = self.contents
        self.contents = piece
        return capture

    def clear(self, nothing = None):
        """
        Remove any piece from the cell. (None)
        """
        self.contents = nothing

    def copy_piece(self):
        """
        Copy the piece in the cell. (object)

        This should be overridden for boards with mutable pieces.
        """
        return self.contents

    def get_piece(self):
        """Get the cell's piece. (object)"""
        return self.contents

    def remove_piece(self, piece = None):
        """
        Remove a piece from the cell. (object)

        Parameters:
        piece: The piece to remove from the cell. (object)
        """
        piece = self.contents
        self.clear()
        return piece


class MultiCell(BoardCell):
    """
    A position on a board that holds multiple pieces. (object)

    The pieces attribute is a list of objects. Each object should convert to a 
    string that correctly displays it on the board. Likewise, the location can 
    be any object, but it should be hashable and support addition.

    Attributes:
    empty: How the cell looks when empty. (str)
    location: Where on the board the cell is. (object)
    contents: The pieces occupying the cell. (object)

    Overridden Methods:
    __init__
    __hash__
    __repr__
    """

    def __init__(self, location, pieces = None, empty = ' '):
        """
        Initialize the cell. (None)

        Parameters:
        location: The location of the cell on the board. (hashable)
        pieces: The pieces initially in the cell. (list)
        empty: How the cell looks when empty. (str)
        """
        self.location = location
        self.empty = empty
        if pieces is None:
            self.contents = []
        else:
            self.contents = pieces

    def __contains__(self, other):
        """
        Check for a piece in the cell. (bool)

        other: The piece to check for. (object)
        """
        return other in self.contents

    def __iter__(self):
        """Iterate over the piece in the cell. (iterator)"""
        return iter(self.contents)

    def __len__(self):
        """Return the number of pieces in the cell. (int)"""
        return len(self.contents)

    def __repr__(self):
        """
        Computer readable text representation. (str)
        """
        # keyword parameters
        if self.contents:
            piece_text = ', pieces = {!r}'.format(self.contents)
        else:
            piece_text = ''
        if self.empty != ' ':
            empty_text = ', empty = {!r}'.format(self.empty)
        else:
            empty_text = ''
        # complete and return
        return '{}({}{}{})'.format(self.__class__.__name__, self.location, piece_text, empty_text)

    def __str__(self):
        """
        Human readable text representation. (str)
        """
        if self.contents:
            return ', '.join([str(piece) for piece in self.contents])
        else:
            return self.empty

    def add_piece(self, piece):
        """
        Add a piece to the cell. (object)

        The return value is the piece that was in the cell before.

        Parameters:
        piece: The piece to add to the cell. (object)
        """
        self.contents.append(piece)

    def copy_piece(self):
        """
        Copy the piece in the cell. (object)

        This should be overridden for boards with mutable pieces.
        """
        return self.contents[:]

    def clear(self, nothing = []):
        """
        Remove any piece from the cell. (None)
        """
        self.contents = nothing

    def remove_piece(self, piece = None):
        """
        Remove a piece to the cell. (object)

        Parameters:
        piece: The piece to remove from the cell. (object)
        """
        if piece:
            self.contents.remove(piece)
        else:
            piece = self.contents.pop()
        return piece


class Coordinate(tuple):
    """
    A cartesian coordinate in an n-dimensional space. (tuple)

    Overridden Methods:
    __abs__
    __add__
    __mul__
    __neg__
    __radd__
    __rmul__
    __rsub__
    __sub__
    """

    def __abs__(self):
        """
        Absolute value (Cooordinate)
        """
        return Coordinate([abs(a) for a in self])

    def __add__(self, other):
        """
        Coordinate addition

        Coordinates add with lists, tuples, and Coordinates of the same length.

        Parameters:
        other: The coordinate to add to (list, tuple, or Coordinate)
        """
        if isinstance(other, (Coordinate, tuple, list)):
            if len(self) == len(other):
                return Coordinate([a + b for a, b in zip(self, other)])
            else:
                raise ValueError('Coordinates can only add in the same dimension.')
        else:
            return NotImplemented

    def __mul__(self, other):
        """
        Scalar multiplication. (Coordinate)

        Parameters:
        other: The scale to multiply by. (int or float)
        """
        return Coordinate([a * other for a in self])

    def __neg__(self):
        """
        Negation (Coordinate)
        """
        return Coordinate([-a for a in self])

    def __radd__(self, other):
        """
        Right side coordinate addition. (Coordinate)

        Coordinates add with lists, tuples, and Coordinates of the same length.

        Parameters:
        other: The coordinate to add to (list, tuple, or Coordinate)
        """
        return self + other

    def __rmul__(self, other):
        """
        Right side scalar multiplication. (Coordinate)

        Parameters:
        other: The scale to multiply by. (int or float)
        """
        return other * self

    def __rsub__(self, other):
        """
        Right side coordiante subtraction. (Coordinate)

        Parameters:
        other: The coordinate to subtract from. (list, tuple, or Coordinate)
        """
        return -(self - other)

    def __sub__(self, other):
        """
        Coordiante subtraction. (Coordinate)

        Parameters:
        other: The coordinate to subtract. (list, tuple, or Coordinate)
        """
        if isinstance(other, (Coordinate, tuple, list)):
            if len(self) == len(other):
                return Coordinate([a - b for a, b in zip(self, other)])
            else:
                raise ValueError('Coordinates can only add in the same dimension.')
        else:
            return NotImplemented


class Board(object):
    """
    A playing board for a game. (object)

    Methods:
    clear: Clear all pieces off the board. (None)
    move: Move a piece from one cell to another. (object)
    offset: Return a cell offset from another cell (BoardCell)
    place: Place a piece in a cell. (None)

    Overriddent Methods:
    __init__
    __iter__
    """

    def __init__(self, locations = [], cell_class = BoardCell):
        """
        Set up the cells. (None)

        Parameters:
        locations: The locations of the cells on the board. (list of hashable)
        cell_class: The class for the cells on the board. (class)
        """
        self.cells = {location: cell_class(location) for location in locations}

    def __iter__(self):
        """
        Iterator for the board (iterator)

        the iterator for a board iterates over the cell locations (keys).
        """
        return iter(self.cells)

    def clear(self):
        """Clear all pieces off the board. (None)"""
        for cell in self.cells.values():
            cell.clear()

    def copy_pieces(self, parent):
        """
        Copy all of the pieces from another board. (None)

        Parameters:
        parent: The board to copy pieces from. (Board)
        """
        for location in parent.cells:
            self.cells[location].contents = parent.cells[location].copy_piece()

    def displace(self, start, end, piece = None):
        """
        Move a piece from one cell to another with displace capture. (object)

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        # store the captured piece
        capture = self.cells[end].get_piece()
        # move the piece
        mover = self.cells[start].remove_piece(piece)
        self.cells[end].clear()
        self.cells[end].add_piece(mover)
        return capture

    def move(self, start, end, piece = None):
        """
        Move a piece from one cell to another with displace capture. (object)

        This should be overridden for the specific capture type of the board.

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        # default is displace capture.
        return self.displace(start, end, piece)

    def offset(self, cell, offset):
        """
        Return a cell offset from another cell (BoardCell)

        Parameters:
        cell: The location of the starting cell. (Coordinate)
        offset: The relative location of the target cell. (Coordinate)
        """
        return self.cells[cell + offset]

    def place(self, piece, cell):
        """
        Place a piece in a cell. (None)

        The piece parameter should be a key appropriate to cells on the board.

        Paramters:
        piece: The piece to place on the board. (See BoardCell)
        cell: The location to place the piece in. (Coordinate)
        """
        self.cells[cell].clear()
        self.cells[cell].add_piece(piece)

    def safe(self, location, piece):
        """
        Determine if a cell is safe from capture. (bool)

        Parameter:
        location: The location of the cell to check. (hashable)
        piece: The piece that would move to that spot. (object)
        """
        return piece in self.cells[location] or len(self.cells[location]) < 2

    def safe_displace(self, start, end, piece = None):
        """
        Move a piece from one cell to another with displace capture. (object)

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        mover = self.cells[start].remove_piece(start, end, piece)
        if self.safe(start, mover):
            capture = self.cells[end].get_piece()
            self.cells[end].clear()
            self.cells[end].add_piece(mover)
            return capture
        else:
            self.cells[start].add_piece(mover)
            raise ValueError('Attempt to capture safe cell {!r}.'.format(start))


class DimBoard(Board):
    """
    A board of squares in variable dimensions. (Board)

    Methods:
    copy: Create a copy of the board. (GridBoard)

    Overridden Methods:
    __init__
    """

    def __init__(self, dimensions, cell_class = BoardCell):
        """
        Set up the grid of cells. (None)

        Parameters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        cell_class: The class for the cells on the board. (class)
        """
        # store definition
        self.dimensions = dimensions
        self.cell_class = cell_class
        # calculate locations
        locations = itertools.product(*[range(1, dimension + 1) for dimension in self.dimensions])
        locations = [Coordinate(location) for location in locations]
        # set up cells
        super(DimBoard, self).__init__(locations, cell_class)

    def copy(self, **kwargs):
        """Create a copy of the board. (GridBoard)"""
        clone = self.__class__(self.dimensions, self.cell_class, **kwargs)
        clone.copy_pieces(self)
        return clone


class LineBoard(Board):
    """
    A board of space in a line. (Board)

    The line may be bent or looped.
    """

    def __init__(self, length, cell_class = MultiCell, extra_cells = []):
        """
        Set up the line of cells. (None)

        Parameters:
        length: The number of cells in the board. (int)
        cell_class: The class for the cells on the board. (class)
        extra_cells: The keys for any cells outside the line. (list of hashable)
        """
        self.length = length
        self.cell_class = cell_class
        super(LineBoard, self).__init__(range(1, length + 1), cell_class)
        for location in extra_cells:
            self.cells[location] = cell_class(location)

    def copy(self, **kwargs):
        """Create a copy of the board. (GridBoard)"""
        clone = self.__class__(self.length, self.cell_class, **kwargs)
        clone.copy_pieces(self)
        return clone


class GridBoard(Board):
    """
    A rectangular board of squares. (Board)

    Methods:
    copy: Create a copy of the board. (GridBoard)

    Overridden Methods:
    __init__
    """

    def __init__(self, columns, rows, default_piece = None):
        """
        Set up the grid of cells. (None)

        Paramters:
        columns: The number of columns on the board. (int)
        rows: The number of rows on the board. (int)
        """
        # store dimensions
        self.columns = columns
        self.rows = rows
        # create cells
        self.default_piece = default_piece
        self.cells = {}
        for column in range(columns):
            for row in range(rows):
                location = Coordinate((column, row))
                self.cells[location] = BoardCell(location, default_piece)

    def copy(self, **kwargs):
        """Create a copy of the board. (GridBoard)"""
        # clone the cells
        clone = self.__class__(self.columns, self.rows, **kwargs)
        # clone the cell contents
        for location in clone:
            clone.cells[location].piece = self.cells[location].piece
        return clone


class MultiBoard(DimBoard):
    """
    A board with multiple pieces per cell. (Board)
    """

    def __init__(self, dimensions):
        """
        Set up the grid of cells. (None)

        Paramters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        """
        super(MultiBoard, self).__init__(dimensions, list)

    def copy(self, **kwargs):
        """Create a copy of the board. (GridBoard)"""
        # clone the cells
        clone = self.__class__(self.dimensions, **kwargs)
        # clone the cell contents
        for location in clone:
            clone.cells[location].piece = self.cells[location].piece[:]
        return clone

    def move(self, start, end):
        """
        Move a piece from one cell to another. (object)

        The object returned is any piece that is in the destination cell before the
        move. The parameters should be keys appropriate to cells on the board.

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        """
        # store the captured piece
        capture = self.cells[end].piece[:]
        # move the piece
        mover = self.cells[start].piece.pop()
        if not (capture == self.default_piece() or mover == capture[0]):
            self.cells[end].piece = self.default_piece()
        else:
            capture = self.default_piece()
        self.cells[end].piece.append(mover)
        return capture

    def place(self, piece, cell):
        """
        Place a piece in a cell. (None)

        The piece parameter should be a key appropriate to cells on the board.

        Paramters:
        piece: The piece to place on the board. (See BoardCell)
        cell: The location to place the piece in. (Coordinate)
        """
        self.cells[cell].piece.append(piece)
