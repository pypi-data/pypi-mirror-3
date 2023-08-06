import os
import csv


def read_csv(file_name):
    return csv.DictReader(open(file_name, 'rb'),
                               delimiter='\t',
                               skipinitialspace=True)


def add_runs(runs_file, profile, dumps_folder):
    file_name = "%s_experiments.csv" % profile['COMMONDB']
    path = os.path.join(dumps_folder, file_name)
    if not os.path.exists(path):
        print "Warning: Path to dumped file does not exist: %s" % path
        return
    experiments = read_csv(path)
    for experiment in experiments:
        line = [experiment['project_id'],
                experiment['experiment_id'],
                experiment['CellType'],
                experiment['RNAType'],
                experiment['Compartment'],
                experiment['read_length'],
                experiment['partition'],
                experiment['Bioreplicate'],
                experiment['template_file'],
                experiment['mismatches'],
                experiment['paired'],
                experiment['lab'],
                experiment['exp_description'],
                experiment['expDate'],
                experiment.get('Preprocessing', '')]
        # species_id
        # genome_id
        # annotation_id
        runs_file.write('\t'.join(line))
        runs_file.write('\n')


def main(workspace, dumps_folder):
    runs_file_name = os.path.join(workspace, 'runs.csv')
    runs_file = open(runs_file_name, 'w')
    headers = ['project_id',
               'run_id',
               'cell',
               'rnaExtract',
               'localization',
               'read_length',
               'partition',
               'replicate',
               'template_file',
               'mismatches',
               'paired',
               'lab',
               'exp_description',
               'expDate',
               'Preprocessing'
                ]
    runs_file.write('\t'.join(headers))
    runs_file.write('\n')
    commondbs = []
    profiles_file_name = os.path.join(workspace, 'profiles.csv')
    for profile in read_csv(profiles_file_name):
        if profile["COMMONDB"] in commondbs:
            continue
        else:
            commondbs.append(profile["COMMONDB"])
            add_runs(runs_file, profile, dumps_folder)
    runs_file.close()
