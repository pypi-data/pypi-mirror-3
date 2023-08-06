import os

EXPERIMENT_PARAMETERS = ['project_id',
                         'species',
                         'cell',
                         'readType',
                         'type',
                         'qualities',
                         'dataType',
                         'rnaExtract',
                         'localization',
                         'lab']


def main(data, staging):
    """
    Assign each biological replicate in an experiment a unique replicate_id.

    The parameters that define an experiment are used as a key
    to group all the accessions. Then the replicate that may be defined in
    the accession alreay is used for ordering the accessions.

    The result is stored in the experiments.csv file:

    project_id  accession_id        replicate_id
    ENCODE7     CALTECH41414922872  1
    ENCODE7     CALTECH542983812759 2
    """
    experiments = {}

    for accession in data['accessions.csv']:
        project_id = accession['project_id']

        experiment_key = []
        for parameter in EXPERIMENT_PARAMETERS:
            experiment_key.append(accession[parameter])
        experiment_key = tuple(experiment_key)

        # The order is important so that the natural order of the
        # replicates is kept when sorting.
        value = (accession['project_id'],
                 accession['accession_id']
                )

        if experiment_key in experiments:
            experiments[experiment_key].append(value)
        else:
            experiments[experiment_key] = [value]

    path = os.path.join(staging, "experiments.csv")
    file = open(path, "w")
    file.write("project_id\taccession_id\treplicate_id\n")

    for accessions in experiments.values():
        accessions.sort()
        replicate_id = 1
        for project_id, accession_id in accessions:
            file.write("%s\t%s\t%s\n" % (project_id,
                                         accession_id,
                                         replicate_id))
            replicate_id += 1
