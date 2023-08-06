"""
Render a dashboard as HTML given the context and a cube
"""
import StringIO


class Table:
    """
    Renders the dashboard table.
    """

    def __init__(self, cubes):
        """
        Store the contect and the cube.
        """
        self.cubes = cubes
        self.dimensions = cubes['experiments'].context['dimensions']

    def render(self):
        """
        Render the HTML page parts.
        """
        output = StringIO.StringIO()
        self.top(output)
        self.rows_header(output)
        self.columns_header(output)
        self.rows(output)
        self.bottom(output)
        html = output.getvalue()
        output.close()
        return html

    def top(self, output):
        """
        Render the top of the table.
        """
        output.write('''<table><tbody>''')
        if len(self.cubes['experiments'].get_cols()) > 1:
            for col in self.cubes['experiments'].get_cols()[:-1]:
                output.write("""<tr>\n""")
                self.space_above_rows(output)
                self.columns_tree(output, col)
                output.write("</tr>\n")

    def space_above_rows(self, output):
        """
        Render the space above the rows of the table.
        """
        num = len(self.cubes['experiments'].get_rows())
        output.write("""<th class="all_null"><div>&nbsp;</div></th>\n""" * num)

    def columns_tree(self, output, col):
        """
        Render the columns tree of the table.
        """
        col_index = self.cubes['experiments'].get_cols().index(col)
        for item in self.cubes['experiments'].get_col_product():
            template = """<th class="col"><div>%s</div></th>\n"""
            output.write(template % item[col_index])

    def rows_header(self, output):
        """
        Render the rows header of the table.
        """
        output.write("""<tr>\n""")
        for dimension in self.cubes['experiments'].get_rows():
            template = """<th class="row_header"><div>%s</div></th>\n"""
            output.write(template % self.dimensions[dimension])

    def columns_header(self, output):
        """
        Render the columns header of the table.
        """
        for item in self.cubes['experiments'].get_col_product():
            output.write("""<th class="col"><div>%s</div></th>\n""" % item[-1])
        output.write("</tr>\n")

    def rows(self, output):
        """
        Render the rows of the table.
        """
        row_index = 0
        for row_value in self.cubes['experiments'].get_row_values():
            output.write("""<tr>\n""")
            self.row(output, row_value, row_index)
            row_index += 1
            output.write("</tr>\n")

    def row(self, output, row_value, row_index):
        """
        Render the row labels and values
        """
        self.row_labels(output, row_value)
        self.row_values(output, row_value, row_index)

    def row_labels(self, output, row_value):
        """
        Render the row labels
        """
        for index in range(0, len(self.cubes['experiments'].get_rows())):
            output.write("""<th class="row">\n""")
            output.write("""<div>%s</div>\n""" % row_value[index])
            output.write("""</th>\n""")

    def row_values(self, output, row_value, row_index):
        """
        Render the row values
        """
        data = {'row_value': row_value,
                'row_index': row_index}
        col_index = 0
        for col_value in self.cubes['experiments'].get_col_product():
            data['col_index'] = col_index
            data['col_value'] = col_value
            self.cell(output, data)
            col_index += 1

    def cell(self, output, data):
        """
        Render the cell
        """
        key = data['row_value'] + data['col_value']
        if key in self.cubes['replicates'].get_row_values():
            output.write("""<td class="data">\n""")
            output.write("""<div style="width: 48px; ">\n""")
            cols = self.cubes['replicates'].context['cols']
            index = cols.index('number_of_replicates')
            cell = self.cubes['replicates'].get_cell(key)
            number_of_replicates = cell[0][index]
            self.rnaseq_homepage_link(output, key, number_of_replicates)
            output.write("""</div>\n""")
            output.write("""</td>\n""")
        else:
            html = ("""<td class="data"><div style="width: 48px; ">"""
                    """</div></td>\n""")
            output.write(html)

    def bottom(self, output):
        """
        Render bottom of the table and the html page.
        """
        output.write("</tbody></table>")

    def rnaseq_homepage_link(self, output, key, text):
        """
        Produce the homepage link
        """
        all_headers = []
        new_headers = []
        for header in self.cubes['files'].get_cols():
            if not header in self.dimensions:
                new_headers.append(header)
            all_headers.append(header)
        link = self.get_link(key, all_headers, text)
        output.write(link)
        return

    def get_link(self, key, all_headers, text):
        """
        Make a link to the homepage using the parameter information
        """
        replicate = self.cubes['files'].get_cell(key)[0]
        line = dict(zip(all_headers, replicate))
        parameters = []
        subset_parameters = self.cubes['files'].context['subset_parameters']
        for dim in subset_parameters:
            parameters.append(line[dim])
        base = "http://rnaseq.crg.es/project/%s/" % line['project_id']
        params = '-'.join(subset_parameters)
        values = '-'.join(parameters)
        link = base + "%s/%s/tab/overview/" % (params, values)
        tag = """<a href="%s">%s</a>""" % (link, text)
        return tag
