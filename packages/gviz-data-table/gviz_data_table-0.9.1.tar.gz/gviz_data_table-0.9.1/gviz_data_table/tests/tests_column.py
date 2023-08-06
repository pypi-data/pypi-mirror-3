from unittest import TestCase

class TestColumn(TestCase):

    minimal_schema = dict(id='age', type=int)
    valid_schema = {'id':'age', 'type':int, 'label':'Age', 'options':{}}

    def make_one(self):
        from gviz_data_table.column import Column
        return Column

    def test_constructor(self):
        Column = self.make_one()

        col = Column(**self.minimal_schema)
        self.assertEqual(col.id, 'age')
        self.assertEqual(col.type, int)

        schema = self.minimal_schema.copy()
        schema['options'] = dict(width=100)
        col = Column(**schema)
        self.assertEqual(col.options, {'width':100})

        schema = self.valid_schema.copy()
        col = Column(**schema)
        self.assertEqual(col.id, 'age')
        self.assertEqual(col.type, int)
        self.assertEqual(col.label, 'Age')
        self.assertEqual(col.options, {})

    def test_validate_type(self):
        Column = self.make_one()
        schema = self.minimal_schema
        schema['type'] = dict
        self.assertRaises(AssertionError,
                          Column,
                          **schema)

    def test_invalid_options(self):
        Column = self.make_one()
        schema = self.minimal_schema.copy()
        schema['options'] = 'Age'
        self.assertRaises(AssertionError,
                          Column,
                          **schema)

    def test_dictionary_interface(self):
        Column = self.make_one()
        col = Column(**self.minimal_schema.copy())
        self.assertEqual(dict(col),
                         {'id':'age', 'type':'number', 'label':'age'})
        schema = self.valid_schema.copy()
        col = Column(**schema)
        self.assertEqual(dict(col),
                         {'id':'age', 'type':'number', 'label':'Age'})
        schema['options'] = {'style':'bold', 'width':100, 'color':'red'}
        col = Column(**schema)
        self.assertEqual(dict(col),
                         {'id':'age', 'type':'number', 'label':'Age',
                          'options':{'style':'bold', 'width':100, 'color':'red'}
                          }
                         )
