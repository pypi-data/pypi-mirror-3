"""
Prepare the context and the cube and then render the dashboard
"""

import sqlite3

from raisin.recipe.dashboard.dashboard import Dashboard
from raisin.recipe.dashboard.cube import Cube


def get_key(line):
    """
    Get a key for the project_id and accession_id from the line
    """
    return (line['project_id'], line['accession_id'])


def get_dimensions(context):
    """
    Get the dimensions and their label. The vocabulary should define a label
    for every row and col item.
    """
    dimensions = {}
    for row in context['rows']:
        dimensions[row] = context['parameter_vocabulary'][row]
    for col in context['cols']:
        dimensions[col] = context['parameter_vocabulary'][col]
    return dimensions


def main(options, buildout):
    """
    Put the configuration into a context dictionary and render the dashboard
    as HTML.

    Context setup example:

    rows: ['species', 'cell', 'rnaExtract', 'localization', 'label']
    cols: ['readType']
    filters: {}
    lines: <csv.DictReader instance at 0x10138a1b8>
    parameter_vocabulary: {'paired': 'Paired',
                           ...
                           'view': 'View'}
    dimensions: {'localization': 'Localization',
                 'readType': 'Read type',
                 'label': 'Condition',
                 'cell': 'Cell type',
                 'rnaExtract': 'RNA extract',
                 'species': 'Species'}
    parameter_categories: {'paired': 'Experiment',
                           ...
                           'view': 'Results'}
    """

    cubes = {}

    # context for experiments
    context = {}
    context['rows'] = options['rows'].split('\n')
    context['cols'] = options['cols'].split('\n')
    context['subset_parameters'] = options['subset_parameters'].split('\n')
    context['dbconn'] = sqlite3.connect(options['database'])
    context['parameter_vocabulary'] = buildout['parameter_vocabulary']
    context['dimensions'] = get_dimensions(context)
    context['parameter_categories'] = buildout['parameter_categories']
    cubes['experiments'] = Cube(context, 'experiments')

    # context for replicates
    context = context.copy()
    context['rows'] = context['rows'] + context['cols']
    context['cols'] = ['project_id',
                       'parameter_list',
                       'parameter_values',
                       'lab',
                       'species',
                       'cell',
                       'localization',
                       'rnaExtract',
                       'partition',
                       'annotation_version',
                       'readType',
                       'read_length',
                       'paired',
                       'number_of_replicates']
    cubes['replicates'] = Cube(context, 'experiments')

    # context for accessions
    context = context.copy()
    context['cols'] = ['project_id',
                       'accession_id',
                       'species',
                       'partition',
                       'cell',
                       'readType',
                       'read_length',
                       'qualities',
                       'gender',
                       'dataType',
                       'rnaExtract',
                       'localization',
                       'replicate',
                       'lab']
    cubes['accessions'] = Cube(context, 'accessions')

    # context for files
    context = context.copy()
    context['cols'] = ['project_id',
                       'accession_id',
                       'species',
                       'partition',
                       'cell',
                       'label',
                       'readType',
                       'read_length',
                       'qualities',
                       'file_location',
                       'dataType',
                       'rnaExtract',
                       'localization',
                       'replicate',
                       'lab',
                       'view',
                       'type']
    cubes['files'] = Cube(context, 'files')

    # context for runs
    context = context.copy()
    context['cols'] = ['run_id',
                       'project_id',
                       'run_id',
                       'species',
                       'cell',
                       'lab',
                       'localization',
                       'rnaExtract',
                       'partition',
                       'readType',
                       'read_length',
                       'paired']
    cubes['runs'] = Cube(context, 'runs')

    title = options['title']
    description = options['description']

    dashboard = Dashboard(cubes, title, description)
    html = dashboard.render()

    # Write the dashboard to the output file
    static_file = open(options['output_file'], "w")
    static_file.write(html)
    static_file.close()

    # Return the output file that buildout asks for
    return options['output_file']
