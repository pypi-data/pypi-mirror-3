"""
Contains an HTML Renderer for some dimensions.
"""


class Renderer:
    """
    Render some specific items in HTML
    """

    def __init__(self, output):
        """
        Store the output to render to
        """
        self.output = output

    def render(self, header, replicate, afile, number):
        """
        Render the cell depending on the header
        """
        if header == "file_location":
            html = self.file_location(header, replicate, afile, number)
        elif header in ["genome_version"]:
            html = self.genome_version(afile)
        elif header in ["annotation_version"]:
            html = self.annotation_version(afile)
        else:
            html = self.header(header, afile)
        self.output.write(html)

    def file_location(self, header, replicate, afile, number):
        """
        Render the file location
        """
        if len(replicate[1]) == 1:
            view = "Raw data"
        else:
            if afile['type'] == 'fastq':
                view = 'FastqRd%d' % number
            elif afile['type'] == 'fasta':
                view = 'FastaRd%d' % number
            elif afile['type'] == 'bam':
                view = 'BAM%d' % number
            else:
                print replicate
                raise AttributeError
        template = """<td><a href="%s">%s</a></td>\n"""
        return template % (afile[header], view)

    def genome_version(self, afile):
        """
        Render the genome version
        """
        template = ("""<td><a href="%s" title="%s">"""
                    """%s</a></td>\n""")
        return template % (afile["genome_url"],
                           afile["genome"],
                           afile["genome_version"])

    def annotation_version(self, afile):
        """
        Render the annotation version
        """
        template = ("""<td><a href="%s" title="%s">"""
                    """%s</a></td>\n""")
        return template % (afile["annotation_url"],
                           afile["annotation"],
                           afile["annotation_version"])

    def header(self, header, afile):
        """
        Render the header
        """
        return "<td>%s</td>\n" % afile[header]
