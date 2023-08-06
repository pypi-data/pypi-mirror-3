import os


def file_info(file_location):
    info = {'file_not_found': 1,
            'file_size': 0}
    if os.path.exists(file_location):
        info['file_not_found'] = 0
        info['file_size'] = os.path.getsize(file_location)
    return info


def check_accession(accession):
    # The accession values should be given on one line when they don't
    # concern files
    for key in ["species",
                "cell",
                "mate_id",
                "pair_id",
                "label",
                "readType",
                "type",
                "qualities",
                "dataType",
                "rnaExtract",
                "localization",
                "replicate",
                "lab",
                "view",
                "type"
               ]:
        if '\n' in accession.get(key, ''):
            message = "One line for attribute %s (%s)" % (key, accession)
            raise AttributeError(message)
