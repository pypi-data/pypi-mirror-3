from xml.etree import ElementTree

from .ns import _ns, _ns1

class Spreadsheet(object):
    """A model for representing a spreadsheet object.

    """
    def __init__(self, client, feed_entry):
        self.client = client
        id_parts = feed_entry.find(_ns('id')).text.split('/')
        self.id = id_parts[-1]
        self._sheet_list = []

    def sheet_by_name(self, sheet_name):
        pass

    def _fetch_sheets(self):
        feed = self.client.get_worksheets_feed(self.id)
        for elem in feed.findall(_ns('entry')):
            self._sheet_list.append(Worksheet(self, elem))

    def worksheets(self):
        """Return a list of all worksheets in a spreadsheet."""
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[:]

    def get_worksheet(self, sheet_index):
        """Return a worksheet with index `sheet_index`.

        Indexes start from zero.

        """
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[sheet_index]


class Worksheet(object):
    """A model for worksheet object.

    """
    def __init__(self, spreadsheet, feed_entry):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self.id = feed_entry.find(_ns('id')).text.split('/')[-1]

    def _cell_addr(self, row, col):
        return 'R%sC%s' % (row, col)

    def _fetch_cells(self):
        feed = self.client.get_cells_feed(self.spreadsheet.id, self.id)
        cells_list = []
        for elem in feed.findall(_ns('entry')):
            c_elem = elem.find(_ns1('cell'))
            cells_list.append(Cell(self, c_elem.get('row'),
                                   c_elem.get('col'), c_elem.text))

        return cells_list

    def cell(self, row, col):
        """Return a Cell object.

        Fetch a cell in row `row` and column `col`.

        """
        feed = self.client.get_cells_feed(self.spreadsheet.id,
                                          self.id, self._cell_addr(row, col))
        cell_elem = feed.find(_ns1('cell'))
        return Cell(self, cell_elem.get('row'), cell_elem.get('col'),
                    cell_elem.text)

    def get_all_rows(self):
        """Return a list of lists containing worksheet's rows."""
        cells = self._fetch_cells()

        rows = {}
        for cell in cells:
            rows.setdefault(int(cell.row), []).append(cell)

        rows_list = []
        for r in sorted(rows.keys()):
            rows_list.append(rows[r])

        simple_rows_list = []
        for r in rows_list:
            simple_row = []
            for c in r:
                simple_row.append(c.value)
            simple_rows_list.append(simple_row)

        return simple_rows_list

    def row_values(self, row):
        """Return a list of all values in row `row`.

        Empty cells in this list will be rendered as None.

        """
        cells_list = self._fetch_cells()

        cells = {}
        for cell in cells_list:
            if int(cell.row) == row:
                cells[int(cell.col)] = cell

        last_index = max(cells.keys())
        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def col_values(self, col):
        """Return a list of all values in column `col`.

        Empty cells in this list will be rendered as None.

        """
        cells_list = self._fetch_cells()

        cells = {}
        for cell in cells_list:
            if int(cell.col) == col:
                cells[int(cell.row)] = cell

        last_index = max(cells.keys())
        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def update_cell(self, row, col, val):
        """Set new value to a cell."""
        feed = self.client.get_cells_feed(self.spreadsheet.id,
                                          self.id, self._cell_addr(row, col))
        cell_elem = feed.find(_ns1('cell'))
        cell_elem.set('inputValue', val)
        edit_link = filter(lambda x: x.get('rel') == 'edit',
                feed.findall(_ns('link')))[0]
        uri = edit_link.get('href')

        self.client.put_cell(uri, ElementTree.tostring(feed))


class Cell(object):
    """A model for cell object.

    """
    def __init__(self, worksheet, row, col, value):
        self.row = row
        self.col = col
        self.value = value
