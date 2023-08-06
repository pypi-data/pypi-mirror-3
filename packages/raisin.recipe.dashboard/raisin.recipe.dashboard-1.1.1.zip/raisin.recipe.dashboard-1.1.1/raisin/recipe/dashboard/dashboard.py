"""
Render a dashboard as HTML given the context and a cube
"""
import StringIO
from raisin.recipe.dashboard.table import Table


class Dashboard:
    """
    Renders a dashboard using a context and a cube.

    How to render the dashboard:

    dashboard = Dashboard(cubes, title, description)
    html = dashboard.render()
    """

    def __init__(self, cubes, title, description):
        """
        Store the contect and the cube.
        """
        self.cubes = cubes
        self._title = title
        self._description = description

    def render(self):
        """
        Render the HTML page parts.
        """
        output = StringIO.StringIO()
        self.header(output)
        self.heading(output)
        self.description(output)
        self.workspace(output)
        output.write(Table(self.cubes).render())
        self.footer(output)
        html = output.getvalue()
        output.close()
        return html

    def header(self, output):
        """
        Render the HTML page header.
        """
        html = ('''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"'''
                ''' "http://www.w3.org/TR/html4/strict.dtd">\n''')
        output.write(html)
        output.write("<html>\n")
        output.write("""
        <head>
            <title>%s</title>
            <link rel="stylesheet" href="../../assets/css/reset.css"
                  type="text/css" media="screen, projection">
            <link rel="stylesheet" href="../../assets/css/typography.css"
                  type="text/css" media="screen, projection">
            <link rel="stylesheet" href="../../assets/css/forms.css" type="text/css"
                  media="screen, projection">
            <link rel="stylesheet" href="../../assets/css/styles.css" type="text/css"
                  media="screen, projection">
            <script type="text/javascript">
                function expandCollapse(id){
                    if(document.getElementById(id).className == 'hide'){
                        document.getElementById(id).className='show';
                        }
                    else{
                        document.getElementById(id).className='hide';
                        }
                    }
            </script>
        </head>
        <body>
        """ % self._title)

    def heading(self, output):
        """
        Render the HTML page heading 1.
        """
        output.write("<h1>%s</h1>\n" % self._title)

    def description(self, output):
        """
        Render the description.
        """
        output.write("<div>%s</div>\n" % self._description)

    def workspace(self, output):
        """
        Render the description.
        """
        output.write("""<div class="workspace_results">""")

    def footer(self, output):
        """
        Render the footer
        """
        output.write("</div></body></html>")
