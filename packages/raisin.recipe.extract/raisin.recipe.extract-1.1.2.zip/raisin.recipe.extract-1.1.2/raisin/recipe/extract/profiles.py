import os
import ConfigParser


def parse_profile_file(profile_file):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(profile_file)
    profiles = {}
    for section in parser.sections():
        profiles[section] = dict(parser.items(section))
    return profiles


def extract_profiles(parsed):
    pipelines = set([])
    for value in parsed.values():
        # Recognize a pipeline run from the existence of a 'pipeline'
        # or 'accession' attribute
        if 'pipeline' in value:
            pipelines.add(value['pipeline'])
        elif 'accession' in value:
            pipelines.add('pipeline')
    for pipeline in pipelines:
        if pipeline == 'pipeline':
            profile = parsed['pipeline'].copy()
            profile['pipeline_id'] = 'pipeline'
        else:
            profile = parsed['pipeline'].copy()
            profile.update(parsed[pipeline])
            profile['pipeline_id'] = pipeline
        yield profile


def main(workspace, profile_files):
    headers = ["project_id",
               "pipeline_id",
               "MAPPER",
               "MISMATCHES",
               "PROJECTID",
               "DB",
               "CLUSTER",
               "HOST",
               "THREADS",
               "TEMPLATE",
               "COMMONDB",
               "ANNOTATION",
               "GENOMESEQ",
               "PREPROCESS",
               "PREPROCESS_TRIM_LENGTH"
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    output_file = open(os.path.join(workspace, "profiles.csv"), "w")
    output_file.write('\t'.join(headers) + '\n')

    for profile_file_name in profile_files:
        profile_file = open(profile_file_name, 'r')

        parsed = parse_profile_file(profile_file)
        profiles = [profile for profile in extract_profiles(parsed)]
        if not profiles:
            # No profiles have been found, so just use the minimal
            # necessary information
            profile = {'PROJECTID': '',
                       'pipeline_id': '',
                       'MAPPER': '',
                       'MISMATCHES': '',
                       'THREADS': '',
                       'TEMPLATE': '',
                       'COMMONDB': '',
                       'ANNOTATION': '',
                       'GENOMESEQ': ''}
            profile.update(parsed['pipeline'])
            profiles = [profile]
        for profile in profiles:
            output_file.write(template % (
                                  profile['PROJECTID'],
                                  profile['pipeline_id'],
                                  profile['MAPPER'],
                                  profile['MISMATCHES'],
                                  profile['PROJECTID'],
                                  profile['DB'],
                                  profile.get('CLUSTER', ''),
                                  profile.get('HOST', ''),
                                  profile['THREADS'],
                                  profile['TEMPLATE'],
                                  profile['COMMONDB'],
                                  profile['ANNOTATION'],
                                  profile['GENOMESEQ'],
                                  profile.get('PREPROCESS', ''),
                                  profile.get('PREPROCESS_TRIM_LENGTH', '')
                                  )
                             )
