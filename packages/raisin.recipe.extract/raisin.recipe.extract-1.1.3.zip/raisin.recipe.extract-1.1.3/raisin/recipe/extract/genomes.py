import os
import ConfigParser
from raisin.recipe.extract import utils


def main(workspace, genomes_file):
    headers = ("species",
               "version",
               "url",
               "file_location",
               "file_not_found",
               "file_size")
    template = '\t'.join(['%s'] * len(headers)) + '\n'
    output_file = open(os.path.join(workspace, "genomes.csv"), "w")
    output_file.write(template % headers)
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(genomes_file)

    for section in parser.sections():
        data = dict(parser.items(section))
        data.update(utils.file_info(data['file_location']))
        output_file.write(template % tuple([data[h] for h in headers]))

    genomes_file.close()
    output_file.close()
