"""
Implements a hype cube for creating a dashboard.
"""
import itertools


class Cube:
    """
    Implementation of a cube that provides the rows and columns and their
    values.
    """

    def __init__(self, context, table_name):
        """
        Precalculate the row_values, col_values and dim_values.
        """
        self.context = context
        self.table_name = table_name

        if len(self.context['rows']) == 0:
            raise AttributeError
        if len(self.context['cols']) == 0:
            raise AttributeError

        template = """select distinct %s from %s"""

        cursor = self.context['dbconn'].cursor()

        sql = template % (','.join(self.context['rows']), table_name)
        self.row_values = cursor.execute(sql).fetchall()

        sql = template % (','.join(self.context['cols']), table_name)
        self.col_values = cursor.execute(sql).fetchall()

        self.dim_values = {}
        for dimension in self.get_dimensions():
            sql = template % (dimension, table_name)
            rows = cursor.execute(sql).fetchall()
            self.dim_values[dimension] = [r[0] for r in rows]

        self.mapping = {}
        template = """select %s from %s"""
        sql = template % (','.join(self.get_dimensions()), table_name)
        for line in cursor.execute(sql).fetchall():
            key = line[:len(self.context['rows'])]
            value = line[len(self.context['rows']):]
            if key in self.mapping:
                self.mapping[key].append(value)
            else:
                self.mapping[key] = [value]

    def get_rows(self):
        """
        Return the rows of the cube.
        """
        return self.context['rows']

    def get_cols(self):
        """
        Return the cols of the cube.
        """
        return self.context['cols']

    def get_dimensions(self):
        """
        Return the dimensions of the cube.
        """
        return self.context['rows'] + self.context['cols']

    def get_dim_values(self, dimension):
        """
        Return the distinct values for the dimension
        """
        return self.dim_values[dimension]

    def get_row_values(self):
        """
        Return the distinct row values.
        """
        return self.row_values

    def get_col_product(self):
        """
        Return the product of the col values.
        """
        col_values = []
        for dimension in self.context['cols']:
            col_values.append(self.get_dim_values(dimension))
        return itertools.product(*col_values)

    def get_cell(self, row):
        """
        Return the value for all col dimensions in the row
        """
        return self.mapping[row]
