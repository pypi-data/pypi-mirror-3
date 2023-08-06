import os
import ConfigParser
from grape.recipe.pipeline.prepare import check_read_labels

def extract_accessions(accessions):
    for accession_id, accession in accessions.items():
        if accession_id == "labeling":
            continue
        yield accession_id, accession


def parse_accession_file(accession_file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(accession_file)
    accessions = {}
    for section in parser.sections():
        accessions[section] = dict(parser.items(section))
    return accessions


def main(workspace, accession_files):
    headers = ["project_id",
               "accession_id",
               "species",
               "partition",
               "gender",
               "cell",
               "readType",
               "type",
               "qualities",
               "dataType",
               "rnaExtract",
               "localization",
               "replicate",
               "lab"
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    output_file = open(os.path.join(workspace, "accessions.csv"), "w")
    output_file.write('\t'.join(headers) + '\n')

    parsed_accessions = {}
    for accession in accession_files:
        accession_file = open(accession, 'r')
        parsed_accessions[accession] = parse_accession_file(accession_file)

    for key, value in parsed_accessions.items():
        project_id = os.path.split(os.path.split(key)[0])[-1]

        accessions = extract_accessions(value)

        for accession_id, accession in accessions:
            check_read_labels(accession, accession_id)
            for attribute in ['species',
                              'label',
                              'gender',
                              'qualities',
                              'replicate',
                              'rnaExtract',
                              'localization',
                              'cell',
                              'type',
                              'dataType',
                              'lab',
                              'readtype']:
                if not attribute in accession:
                    accession[attribute] = ''
                else:
                    if '\n' in accession[attribute]:
                        first = accession[attribute].split('\n')[0]
                        accession[attribute] = first

            output_file.write(template % (project_id,
                                          accession_id,
                                          accession['species'],
                                          accession['label'],
                                          accession['gender'],
                                          accession['cell'],
                                          accession['readType'],
                                          accession['type'],
                                          accession['qualities'],
                                          accession['dataType'],
                                          accession['rnaExtract'],
                                          accession['localization'],
                                          accession['replicate'],
                                          accession['lab']
                                          ))
