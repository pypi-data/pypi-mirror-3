import os
import csv
import sqlite3

def read_csv(staging, file_name):
    path = os.path.join(staging, file_name)
    read = open(path, 'r')
    items = []
    for item in csv.DictReader(read, delimiter='\t', skipinitialspace=True):
        items.append(item)
    return items


def get_experiments(data):
    experiments = {}
    for experiment in data['experiments']:
        key = (experiment['project_id'], experiment['accession_id'])
        experiments[key] = experiment
    return experiments


def get_accessions(data):
    accessions = {}
    for accession in data['accessions']:
        key = (accession['project_id'], accession['accession_id'])
        accessions[key] = accession
    return accessions

def get_replicates(data):
    replicates = {}
    for replicate in data['replicates']:
        key = (replicate['project_id'], replicate['replicate_id'])
        replicates[key] = replicate
    return replicates

def get_annotations(data):
    annotations = {}
    for annotation in data['annotations']:
        key = annotation['file_location']
        annotations[key] = annotation
    return annotations

def get_runs(data):
    runs = {}
    for run in data['runs']:
        key = (run['project_id'], run['run_id'])
        runs[key] = run
    return runs

def get_view(data):
    views = {}
    for view in data['view']:
        key = (view['project_id'],
               view['accession_id'],
               view['file_location']
              )
        views[key] = view
    return  views


def get_files(data):
    files = {}
    for afile in data['files']:
        key = (afile['project_id'],
               afile['accession_id'],
               afile['file_location'])
        files[key] = afile
    return files


def get_read_lengths(data):
    read_lengths = {}
    for read_length in data['read_length']:
        key = (read_length['project_id'], read_length['accession_id'])
        read_lengths[key] = read_length
    return read_lengths


def produce_files(data, database):

    headers = ["project_id",
               "accession_id",
               "species",
               "partition",
               "cell",
               "label",
               "readType",
               "read_length",
               "qualities",
               "file_location",
               "dataType",
               "rnaExtract",
               "localization",
               "replicate",
               "lab",
               "view",
               "type"
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    path = os.path.join(database, "files.csv")
    output_file = open(path, "w")
    output_file.write('\t'.join(headers) + '\n')

    experiments = get_experiments(data)
    accessions = get_accessions(data)
    views = get_view(data)
    files = get_files(data)
    read_lengths = get_read_lengths(data)

    for key, afile in files.items():
        project_id, accession_id, file_location = key
        experiment = experiments[(project_id, accession_id)]
        accession = accessions[(project_id, accession_id)]
        view = views[key]
        read_length = read_lengths[(project_id, accession_id)]
        row = (afile['project_id'],
               afile['accession_id'],
               accession['species'],
               accession['partition'],
               accession['cell'],
               afile['label'],
               accession['readType'],
               read_length['read_length'],
               accession['qualities'],
               file_location,
               accession['dataType'],
               accession['rnaExtract'],
               accession['localization'],
               experiment['replicate_id'],
               accession['lab'],
               view['view'],
               accession['type']
               )
        output_file.write(template % row)
    output_file.close()

def produce_accessions(data, database):

    headers = ["project_id",
               "accession_id",
               "species",
               "partition",
               "cell",
               "readType",
               "read_length",
               "qualities",
               "gender",
               "dataType",
               "rnaExtract",
               "localization",
               "replicate",
               "lab",
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    path = os.path.join(database, "accessions.csv")
    output_file = open(path, "w")
    output_file.write('\t'.join(headers) + '\n')

    experiments = get_experiments(data)
    accessions = get_accessions(data)
    read_lengths = get_read_lengths(data)

    for key, accession in accessions.items():
        project_id, accession_id = key
        experiment = experiments[(project_id, accession_id)]
        accession = accessions[(project_id, accession_id)]
        read_length = read_lengths[(project_id, accession_id)]
        row = (accession['project_id'],
               accession['accession_id'],
               accession['species'],
               accession['partition'],
               accession['cell'],
               accession['readType'],
               read_length['read_length'],
               accession['qualities'],
               '',
               accession['dataType'],
               accession['rnaExtract'],
               accession['localization'],
               experiment['replicate_id'],
               accession['lab'],
               )
        output_file.write(template % row)
    output_file.close()

def produce_experiments(data, database, project_parameters):

    headers = ["project_id",
               "parameter_list",
               "parameter_values",
               "lab",
               "species",
               "cell",
               "localization",
               "rnaExtract",
               "partition",
               "annotation_version",
               "readType",
               "read_length",
               "paired",
               "number_of_replicates"
               ]

    template = '\t'.join(['%s'] * len(headers)) + '\n'
    path = os.path.join(database, "experiments.csv")
    output_file = open(path, "w")
    output_file.write('\t'.join(headers) + '\n')

    experiments = get_experiments(data)
    accessions = get_accessions(data)
    annotations = get_annotations(data)
    read_lengths = get_read_lengths(data)
    replicates = get_replicates(data)

    results = {}
    for key, replicate in replicates.items():
        project_id, replicate_id = key
        accession_id = replicate['accession_id']
        experiment = experiments[(project_id, accession_id)]
        accession = accessions[(project_id, accession_id)]
        read_length = read_lengths[(project_id, accession_id)]
        annotation_file_location = replicate['ANNOTATION']
        if annotation_file_location in annotations:
            annotation_version = annotations[annotation_file_location]['version']
        else:
            annotation_version = ""
        paired = "0"
        partition = accession['partition']

        info = {'project_id': accession['project_id'],
                'lab': accession['lab'],
                'species': accession['species'],
                'cell': accession['cell'],
                'localization': accession['localization'],
                'rnaExtract': accession['rnaExtract'],
                'partition': partition,
                'annotation_version': annotation_version,
                'readType': accession['readType'],
                'read_length': read_length['read_length'],
                'paired': paired
               }

        parameter_list = []
        parameter_values = []
        
        if project_parameters.has_key(project_id):
            for parameter in project_parameters[project_id].split('\n'):
                parameter_list.append(parameter)
                parameter_values.append(info[parameter])
        else:
            # When no parameter list is given, choose read_length as a default
            parameter_list.append('read_length')
            parameter_values.append(info['read_length'])
        parameters = (info['project_id'],
                      '-'.join(parameter_list),
                      '-'.join(parameter_values),
                      info['lab'],
                      info['species'],
                      info['cell'],
                      info['localization'],
                      info['rnaExtract'],
                      info['partition'],
                      info['annotation_version'],
                      info['readType'],
                      info['read_length'],
                      info['paired'])
        if results.has_key(parameters):
            results[parameters] +=1
        else:
            results[parameters] =1

    for parameters, number_of_replicates in results.items():
        row = list(parameters)
        row.append(number_of_replicates)
        output_file.write(template % tuple(row))
    output_file.close()

def produce_runs(data, database, project_parameters):

    headers = ['project_id',
               'run_id',
               'species',
               'cell',
               'lab',
               'localization',
               'rnaExtract',
               'partition',
               'readType',
               'read_length',
               'paired',
                ]

    
    template = '\t'.join(['%s'] * len(headers)) + '\n'
    path = os.path.join(database, "runs.csv")
    output_file = open(path, "w")
    output_file.write('\t'.join(headers) + '\n')

    experiments = get_experiments(data)
    accessions = get_accessions(data)
    read_lengths = get_read_lengths(data)
    replicates = get_replicates(data)
    runs = get_runs(data)

    for key, run in runs.items():
        project_id, run_id = key
        experiment = experiments.get((project_id, run_id), {})
        accession = accessions.get((project_id, run_id), {})
        read_length = read_lengths.get((project_id, run_id), {})
        row = (run['project_id'],
               run['run_id'],
               accession.get('species', ''),
               run['cell'],
               run['lab'],
               run['localization'],
               run['rnaExtract'],
               run['partition'],
               accession.get('readType', ''),
               run['read_length'],
               run['paired'],
               )
        output_file.write(template % row)
    output_file.close()


def write_sqlite3_table(cursor, csv_file_path, table_name, integer):
    lines = open(csv_file_path, 'r').readlines()
    headers = lines[0].strip('\n').split('\t')
    types = []
    for header in headers:
        if header in integer:
            types.append("%s integer" % header)
        else:
            types.append("%s text" % header)
    cursor.execute('''create table %s (%s)''' % (
        table_name,
        ",".join(types))
        )
    for line in lines[1:]:
        row = line.strip('\n').split('\t')
        cursor.execute("""insert into %s values %s""" % (
            table_name,
            str(tuple(row)))
            )


def produce_sqlite3_database(data, database):
    output = os.path.join(database, "database.db")
    if os.path.exists(output):
        os.remove(output)
    connection = sqlite3.connect(output)
    cursor = connection.cursor()
    write_sqlite3_table(cursor, 
                        os.path.join(database, 'files.csv'), 
                        'files',
                        ["read_length", "replicate"],
                        )
    write_sqlite3_table(cursor, 
                        os.path.join(database, 'accessions.csv'), 
                        'accessions',
                        ["read_length", "replicate"],
                        )
    write_sqlite3_table(cursor, 
                        os.path.join(database, 'experiments.csv'),
                        'experiments',
                        ["read_length", "paired", "number_of_replicates"],
                        )
    write_sqlite3_table(cursor, 
                        os.path.join(database, 'runs.csv'),
                        'runs',
                        [],
                        )
    connection.commit()
    cursor.close()


def main(buildout, staging, database):
    project_parameters = buildout['project_parameters']
    data = {'accessions': read_csv(staging, "accessions.csv"),
            'profiles': read_csv(staging, "profiles.csv"),
            'annotations':  read_csv(staging, "annotations.csv"),
            'files': read_csv(staging, "files.csv"),
            'experiments': read_csv(staging, "experiments.csv"),
            'read_length': read_csv(staging, "read_length.csv"),
            'view': read_csv(staging, "view.csv"),
            'replicates': read_csv(staging, "replicates.csv"),
            'runs': read_csv(staging, "runs.csv"),
           }

    produce_files(data, database)
    produce_accessions(data, database)
    produce_experiments(data, database, project_parameters)
    produce_runs(data, database, project_parameters)
    produce_sqlite3_database(data, database)
