import json
from unittest import TestCase

class TestTable(TestCase):

    valid_schema = (
        {'id':'age', 'type':int, 'label':'Age'},
        {'id':'name', 'type':str, 'label':'Name'}
    )

    schema_missing_id = (
        {'type':int},
        {'name':'age', 'type':int}
    )

    bob = (18, 'Bob')
    sally = (20, 'Sally')

    def make_one(self):
        from gviz_data_table.table import Table
        return Table

    def test_constructor(self):
        Table = self.make_one()
        table = Table()
        self.assertEqual(table.schema.keys(), [])
        self.assertEqual(table.rows, [])

    def test_invalid_options(self):
        Table = self.make_one()
        table = Table()
        self.assertRaises(
            AssertionError,
            table.options,
            1
        )
        self.assertRaises(
            AssertionError,
            table.options,
            [1, 2, 3]
        )

    def test_options(self):
        Table = self.make_one()
        table = Table()
        table.options = dict(bar='baz')
        self.assertEqual(table.options, {'bar':'baz'})

    def test_missing_id(self):
        Table = self.make_one()
        self.assertRaises(
            TypeError,
            Table,
            self.schema_missing_id
        )

    def test_duplicate_column(self):
        Table = self.make_one()
        table = Table(self.valid_schema)
        self.assertRaises(ValueError,
                          table.add_column,
                          'age',
                          int
                          )

    def test_add_column(self):
        Table = self.make_one()
        table = Table()
        table.add_column(**self.valid_schema[0])
        table.add_column(**self.valid_schema[1])
        self.assertEqual(table.schema['age'].id, "age")
        self.assertEqual(table.schema['name'].type, str)
        table.append(self.bob)
        self.assertRaises(TypeError,
                          table.add_column,
                          'height'
                          )

    def test_insert_row_no_columns(self):
        Table = self.make_one()
        table = Table()
        self.assertRaises(AssertionError,
                          table.append,
                          ('Bob', )
                          )

    def test_insert_row(self):
        Table = self.make_one()
        table = Table(self.valid_schema)
        table.append(self.bob)
        row = table.rows.pop()
        self.assertEqual(row['age'].value, 18)
        self.assertEqual(row['name'].value, 'Bob')

    def test_with_label(self):
        Table = self.make_one()
        table = Table(self.valid_schema)
        table.append(self.bob)
        rows = table.rows
        row = rows.pop()
        self.assertFalse(row['name'].label)

        harry = (17, ('Harry', 'Big Man'))
        table.append(harry)
        row = rows.pop()
        self.assertEqual(row['age'].value, 17)
        self.assertEqual(row['name'].value, 'Harry')
        self.assertEqual(row['name'].label, 'Big Man')

    def test_cell_options(self):
        Table = self.make_one()
        table = Table(self.valid_schema)

        jack = [17, ('Jack', 'Beanstalk', dict(key='value'))]
        table.append(jack)
        row = table.rows.pop()
        self.assertEqual(row['name'].options, {'key':'value'})

        kate = [26, dict(value='Kate', options={'hair':'long'})]
        table.append(kate)
        row = table.rows.pop()
        self.assertEqual(row['name'].value, 'Kate')
        self.assertEqual(row['name'].label, None)
        self.assertEqual(row['name'].options, {'hair':'long'})

    def test_insert_rows(self):
        Table = self.make_one()
        table = Table(self.valid_schema)
        table.extend([self.bob, (20, 'Sally')])
        rows = table.rows
        bob = rows.pop()
        self.assertEqual(bob['name'].value, 'Sally')

        sally = rows.pop()
        self.assertEqual(sally['age'].value, 18)

    def test_invalid_row(self):
        Table = self.make_one()
        table = Table(self.valid_schema)
        self.assertRaises(AssertionError,
                          table.append,
                          [1, 2, 3]
                          )

    def test_dictionary_interface(self):
        Table = self.make_one()
        table = Table(options={'foo':'bar'})
        expected = dict(rows=[], cols=[], p={'foo':'bar'})
        self.assertEqual(dict(table), expected)
