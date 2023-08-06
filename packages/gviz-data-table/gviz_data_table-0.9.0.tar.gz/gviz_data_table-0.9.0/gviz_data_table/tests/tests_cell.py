from unittest import TestCase


class TestCell(TestCase):

    def make_one(self):
        from gviz_data_table.cell import Cell
        return Cell

    def test_valid_data(self):
        Cell = self.make_one()
        c = Cell(int, 1)
        self.assertEqual(c.value, 1)
        self.assertEqual(c.type, int)
        c = Cell(str, 'a')
        self.assertEqual(c.value, "a")
        self.assertEqual(c.type, str)

    def test_empty_cell(self):
        Cell = self.make_one()
        c = Cell(int, None)
        self.assertFalse(c.value)

    def test_invalid_data(self):
        Cell = self.make_one()
        self.assertRaises(ValueError,
                          Cell,
                          str, 1)

    def test_label(self):
        Cell = self.make_one()
        c = Cell(int, 1)
        self.assertFalse(c.label)
        c = Cell(int, 1, "Birthday")
        self.assertEqual(c.label, "Birthday")

    def test_invalid_options(self):
        Cell = self.make_one()
        c = Cell(int, 1)
        self.assertRaises(
            AssertionError,
            c.options,
            1
        )
        self.assertRaises(
            AssertionError,
            c.options,
            [1, 2, 3]
        )

    def test_options(self):
        Cell = self.make_one()
        c = Cell(int, 1)
        c.options = dict(foo='bar')
        self.assertEqual(c.options, {'foo':'bar'})


    def test_dictionary_interface(self):
        Cell = self.make_one()
        c = Cell(int, 1, "Number", {'foo':'bar'})
        expected = dict(v=1, f="Number", p={'foo':'bar'})
        self.assertEqual(dict(c), expected)
