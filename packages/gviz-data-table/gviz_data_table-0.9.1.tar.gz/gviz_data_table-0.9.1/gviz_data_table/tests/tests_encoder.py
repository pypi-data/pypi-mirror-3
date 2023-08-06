import datetime
import json
from unittest import TestCase

class TestEncoder(TestCase):

    def make_one(self):
        from gviz_data_table.encoder import Encoder
        return Encoder

    def test_encode_time(self):
        time = datetime.time(10, 30, 45)
        encoder = self.make_one()
        js = encoder().encode(time)
        python = json.loads(js)
        self.assertEqual(python, [10, 30, 45])

    def test_encode_date(self):
        today = datetime.date(2012, 1, 31)
        encoder = self.make_one()
        js = encoder().encode(today)
        python = json.loads(js)
        self.assertEqual(python, "Date(2012, 0, 31)")

    def test_encode_datetime(self):
        today = datetime.datetime(2012, 1, 31, 12, 30, 45)
        encoder = self.make_one()
        js = encoder().encode(today)
        python = json.loads(js)
        self.assertEqual(python, u"Date(2012, 0, 31, 12, 30, 45)")

    def test_encode_cell(self):
        from gviz_data_table.cell import Cell
        c = Cell(int, 1)
        encoder = self.make_one()
        js = encoder().encode(c)
        python = json.loads(js)
        self.assertEqual(python, {"v": 1})

    def test_encode_column(self):
        from gviz_data_table.column import Column
        schema = Column(id='age', type=int)
        encoder = self.make_one()
        js = encoder().encode(schema)
        python = json.loads(js)
        self.assertEqual(python,
                         {"type": "number", "id": "age", "label": "age"})

    def test_encode_table(self):
        from gviz_data_table.table import Table
        table = Table()
        encoder = self.make_one()
        js = encoder().encode(table)
        python = json.loads(js)
        self.assertEqual(python,
                         {'rows':[], 'cols':[]})

    def test_encode_unknown(self):
        encoder = self.make_one()
        self.assertRaises(TypeError,
                          encoder.encode,
                          object)
