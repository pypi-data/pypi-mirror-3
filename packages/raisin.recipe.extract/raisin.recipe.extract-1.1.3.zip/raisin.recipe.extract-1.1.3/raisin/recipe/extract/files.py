import os
import ConfigParser
from raisin.recipe.extract import utils


def extract_files(accessions):
    for accession_id, accession in accessions.items():
        if accession_id == "labeling":
            continue
        file_locations = accession['file_location'].split('\n')
        if len(file_locations) > 1:
            for key, value in accession.items():
                accession[key] = [i.strip() for i in value.split('\n')]
            for i in range(0, len(file_locations)):
                item = {}
                for key, value in accession.items():
                    if len(value) == 1:
                        item[key] = value[0]
                    else:
                        item[key] = value[i]
                yield accession_id, item
        else:
            yield accession_id, accession


def parse_accession_file(accession_file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(accession_file)
    accessions = {}
    for section in parser.sections():
        accessions[section] = dict(parser.items(section))
    return accessions


def main(workspace, accessions_files):
    headers = ["project_id",
               "accession_id",
               "species",
               "cell",
               "label",
               "readType",
               "qualities",
               "file_location",
               "dataType",
               "rnaExtract",
               "localization",
               "lab",
               "view",
               "type",
               "replicate",
               "file_not_found",
               "file_size",
               "configuration_file"
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    output_file = open(os.path.join(workspace, "files.csv"), "w")
    output_file.write('\t'.join(headers) + '\n')

    for input_file in accessions_files:
        accession_file = open(input_file, 'r')
        accessions = parse_accession_file(accession_file)

        project_id = os.path.split(os.path.split(input_file)[0])[-1]
        files = extract_files(accessions)
        for accession_id, item in files:
            file_info = utils.file_info(item['file_location'])
            output_file.write(template % (project_id,
                                          accession_id,
                                          item.get('species', ''),
                                          item.get('cell', ''),
                                          item.get('label', ''),
                                          item.get('readType', ''),
                                          item.get('qualities', ''),
                                          item.get('file_location', ''),
                                          item.get('dataType', ''),
                                          item.get('rnaExtract', ''),
                                          item.get('localization', ''),
                                          item.get('lab', ''),
                                          item.get('view', ''),
                                          item.get('type', ''),
                                          item.get('replicate', ''),
                                          file_info['file_not_found'],
                                          file_info['file_size'],
                                          input_file
                                          ))
        accession_file.close()

    output_file.close()
