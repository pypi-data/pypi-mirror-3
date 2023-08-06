import os
import glob
import ConfigParser

ACCESSION_ATTRIBUTES = set(['file_location',
                            'mate_id',
                            'pair_id',
                            'label',
                            'dataType',
                            'cell',
                            'rnaExtract',
                            'localization',
                            'replicate',
                            'lab',
                            'view',
                            'type',
                            'readType',
                            'qualities',
                            'species'])

def parse_profile_file(file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(file)
    profile = {}
    if "pipeline" in parser.sections():
        profile = dict(parser.items("pipeline"))
    else:
        raise AttributeError("The profile is missing a pipeline secion")
    return profile

def parse_accession_file(file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(file)
    accessions = {}
    for section in parser.sections():
        accessions[section] = dict(parser.items(section))
    return accessions

def parse_annotations_file(file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(file)
    annotations = {}
    for section in parser.sections():
        data = dict(parser.items(section))
        key = data['file_location']
        annotations[key] = data
    return annotations

def parse_genomes_file(file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(file)
    genomes = {}
    for section in parser.sections():
        data = dict(parser.items(section))
        key = data['file_location']
        genomes[key] = data
    return genomes

def check(project, read_length, accessions, profile, annotations, genomes):
    """
    Just some sanity checks to make sure that some basic assumptions are kept.
    """
    if not profile['MAPPER'] == 'GEM':
        raise AttributeError

    if not profile['MISMATCHES'] == '2':
        raise AttributeError

    if not profile['PROJECTID'] == project + read_length:
        raise AttributeError

    if not profile['DB'].startswith(project):
        raise AttributeError

    if not profile['COMMONDB'].startswith(project):
        raise AttributeError

    if not profile['DB'].endswith("_RNAseqPipeline"):
        raise AttributeError

    if not profile['COMMONDB'].endswith("_RNAseqPipelineCommon"):
        raise AttributeError

    #if not profile['ANNOTATION'].endswith(".gtf"):
    #    raise AttributeError

    if not profile['GENOMESEQ'].endswith(".fa"):
        raise AttributeError

    for accession_id, accession in accessions.items():

        if not set(accession.keys()) == ACCESSION_ATTRIBUTES:
            raise AttributeError

        for file in accession['file_location'].split(';'):
            if not accession['file_location'].endswith(".fastq.gz"):
                raise AttributeError

        if accession['readType'].split('x')[-1] != read_length:
            raise AttributeError

        #if not accession['mate_id'] == accession['pair_id']:
        #    raise AttributeError
        
        #if not accession['mate_id'].startswith(accession['label']):
        #    print accession
        #    raise AttributeError

def extract_files(accessions):
    for accession_id, accession in accessions.items():
        if accession_id == "labeling":
            continue
        file_locations = accession['file_location'].split('\n')
        print accession
        if len(file_locations) == 1:
            if accession['type'] in ['fasta', 'fastq']:
                accession['view'] = "RawData"
            elif accession['type'] == 'bam':
                accession['view'] = "Alignments"
        else:
            if accession['type'] == 'fastq':
                accession['view'] = '\n'.join(['FastqRd%d' % number for number in range(1, len(file_locations)+1)])
            elif accession['type'] == 'fasta':
                accession['view'] = '\n'.join(['FastqRd%d' % number for number in range(1, len(file_locations)+1)])
            elif accession['type'] == 'bam':
                accession['view'] = '\n'.join(['Alignment%d' % number for number in range(1, len(file_locations)+1)])
        if len(file_locations) > 1:
            for key, value in accession.items():
                accession[key] = [i.strip() for i in value.split('\n')]
            for i in range(0, len(file_locations)):
                file = {}
                for key, value in accession.items():
                    if len(value) == 1:
                        file[key] = value[0]
                    else:
                        file[key] = value[i]
                yield accession_id, file
        else:
            yield accession_id, accession

class Accession:
    def __init__(self):
        pass

def main(options, buildout):
    annotations_file = open('../annotations/db.cfg', 'r')
    annotations = parse_annotations_file(annotations_file)

    genomes_file = open('../genomes/db.cfg', 'r')
    genomes = parse_genomes_file(genomes_file)

    accession_files = [f for f in glob.glob('../accessions/*/*.cfg')]
    profile_files = [f for f in glob.glob('../profiles/*/*.cfg')]

    headers = ["project_id",
               "accession_id",
               "species",
               "cell",
               "mate_id",
               "pair_id",
               "label",
               "readType",
               "read_length",
               "file_type",
               "qualities",
               #"mapper",
               #"mismatches",
               "file_location",
               #"annotation",
               #"annotation_version",
               #"annotation_url",
               #"genome",
               #"",
               #"genome_url",
               "dataType",
               "rnaExtract",
               "localization",
               "replicate",
               "lab",
               "view",
               "type"
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    output_file = open("static/generic/dashboard.csv", "w")
    output_file.write('\t'.join(headers) + '\n')

    parsed_profiles = {}
    for profile in profile_files:
        profile_file = open(profile, 'r')
        parsed_profiles[profile] = parse_profile_file(profile_file)

    parsed_accessions = {}
    for accession in accession_files:
        accession_file = open(accession, 'r')
        parsed_accessions[accession] = parse_accession_file(accession_file)
        
    # check(project, read_length, accessions, profile, annotations, genomes)

    for key, value in parsed_accessions.items():
        project_id = os.path.split(os.path.split(key)[0])[-1]
        
        files = extract_files(value)

        for accession_id, file in files:
            #labeling
            for label in ['mate_id', 'pair_id', 'label']:
                if not label in file:
                    file[label] = 'need to use labeling'

            if not 'species' in file:
                file['species'] = 'species'
            if not 'qualities' in file:
                file['qualities'] = 'qualities'
            if not 'replicate' in file:
                file['replicate'] = 'replicate'
            if not 'rnaExtract' in file:
                file['rnaExtract'] = 'rnaExtract'
            if not 'localization' in file:
                file['localization'] = 'localization'
            if not 'cell' in file:
                file['cell'] = 'cell'
            if not 'readType' in file:
                print "No read type given"
                file['readType'] = 'NA'
                read_length = 'NA'
            elif file['readType'] == '2x76D':
                read_length = 76
            elif file['readType'] == '1x70D':
                read_length = 70
            elif file['readType'] == '2x75':
                read_length = 75
            elif file['readType'] == '1x80':
                read_length = 80
            elif file['readType'] == '1x40':
                read_length = 40
            elif file['readType'] == '1x75D':
                read_length = 75
            elif file['readType'] == '2x100':
                read_length = 100
            elif file['readType'] == '2x96':
                read_length = 96
            elif file['readType'] == '2x53':
                read_length = 53
            elif file['readType'] == '2x76':
                read_length = 76
            elif file['readType'] == '2x46':
                read_length = 46
            elif file['readType'] == '2x35':
                read_length = 35
            elif file['readType'] == '2x34':
                read_length = 34
            elif file['readType'] == '100':
                read_length = 100
            elif file['readType'] == '2x40':
                read_length = 40
            elif file['readType'] == '2x50':
                read_length = 50
            elif file['readType'] == '2x51':
                read_length = 51
            elif file['readType'] == '2x54':
                read_length = 54
            elif file['readType'] == '2x49':
                read_length = 49
            elif file['readType'] in ['2x36', '1x36']:
                read_length = 36
            elif file['readType'] == '2x37':
                read_length = 37
            elif file['readType'] == '50':
                read_length = 50
            elif file['readType'] == '75':
                read_length = 75
            else:
                print file['readType']
                raise AttributeError
            if not 'type' in file:
                file['type'] = 'type'
            else:
                print file['type']
            if not 'dataType' in file:
                file['dataType'] = 'dataType'
            else:
                print file['dataType']
            if not 'lab' in file:
                file['lab'] = 'lab'
            else:
                print file['lab']
            print file
            print project_id
            output_file.write(template % (project_id,
                                          accession_id, 
                                          file['species'], 
                                          file['cell'], 
                                          file['mate_id'], 
                                          file['pair_id'], 
                                          file['label'], 
                                          file['readType'],
                                          read_length,
                                          file['type'],
                                          file['qualities'],
                                          #profile['MAPPER'],
                                          #profile['MISMATCHES'],
                                          file['file_location'],
                                          #profile['ANNOTATION'],
                                          #annotations[profile['ANNOTATION']]['version'],
                                          #annotations[profile['ANNOTATION']]['url'],
                                          #profile['GENOMESEQ'],
                                          #genomes[profile['GENOMESEQ']]['version'],
                                          #genomes[profile['GENOMESEQ']]['url'],
                                          file['dataType'],
                                          file['rnaExtract'],
                                          file['localization'],
                                          "1", #file['replicate'],
                                          file['lab'],
                                          file['view'],
                                          file['type']
                                          ))

if __name__ == '__main__':
    main()
