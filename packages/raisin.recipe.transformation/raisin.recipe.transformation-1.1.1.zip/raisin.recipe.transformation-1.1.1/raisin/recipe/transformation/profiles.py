import logging

logger = logging.getLogger('raisin.recipe.transformation.profiles')


def detect_missing_annotation(data):
    """
    Go through all profiles and check whether the annotation is defined
    in annotations/db.cfg.
    """
    annotation_files = []
    for annotation in data['annotations.csv']:
        annotation_files.append(annotation['file_location'])

    missing = {}
    for profile in data['profiles.csv']:
        annotation = profile['ANNOTATION']
        if not annotation.strip():
            continue
        if not annotation in annotation_files:
            if annotation in missing:
                missing[annotation].append(profile)
            else:
                missing[annotation] = [profile]

    if missing:
        message = []
        message.append("Add an annotation for the following files in")
        message.append("../../annotations/db.cfg:")
        message.append("")
        for annotation, profiles in missing.items():
            projects = set([p['project_id'] for p in profiles])
            message.append("# projects: %s" % ', '.join(projects))
            message.append("[annotation]")
            message.append("species =")
            message.append("version =")
            message.append("url =")
            message.append("file_location = %s" % annotation)
            message.append("")
        message = "\n".join(message)
        logger.info(message)


def detect_missing_genomes(data):
    """
    Go through all profiles and check whether the genome is defined
    in genomes/db.cfg.
    """
    genome_files = []
    for genome in data['genomes.csv']:
        genome_files.append(genome['file_location'])

    missing = {}
    for profile in data['profiles.csv']:
        genome = profile['GENOMESEQ']
        if not genome.strip():
            continue
        if not genome in genome_files:
            if genome in missing:
                missing[genome].append(profile)
            else:
                missing[genome] = [profile]

    if missing:
        message = []
        message.append("Add an genome for the following files in")
        message.append("../../genomes/db.cfg:")
        message.append("")
        for genome, profiles in missing.items():
            projects = set([p['project_id'] for p in profiles])
            message.append("# projects: %s" % ', '.join(projects))
            message.append("[genome]")
            message.append("species =")
            message.append("version =")
            message.append("url =")
            message.append("file_location = %s" % genome)
            message.append("")
        message = "\n".join(message)
        logger.info(message)


def main(data):
    detect_missing_annotation(data)
    detect_missing_genomes(data)
