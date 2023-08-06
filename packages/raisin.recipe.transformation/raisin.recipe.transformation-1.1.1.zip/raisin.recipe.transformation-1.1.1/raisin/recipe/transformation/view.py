import os


def view_for_type(views):
    for files in views.values():
        if len(files) == 1:
            info = files[0]
            if info['type'] in ['fasta', 'fastq']:
                info['view'] = "RawData"
            elif info['type'] == 'bam':
                info['view'] = "Alignments"
            else:
                raise AttributeError
        else:
            number = 1
            for info in files:
                if info['type'] == 'fastq':
                    info['view'] = 'FastqRd%d' % number
                elif info['type'] == 'fasta':
                    info['view'] = 'FastaRd%d' % number
                elif info['type'] == 'bam':
                    info['view'] = 'Alignment%d' % number
                else:
                    raise AttributeError
                number += 1


def main(data, workspace):

    views = {}

    for info in data['files.csv']:
        key = (info['project_id'], info['accession_id'])
        if key in views:
            views[key].append(info)
        else:
            views[key] = [info]

    view_for_type(views)

    path = os.path.join(workspace, "view.csv")
    view = open(path, "w")
    view.write("project_id\taccession_id\tfile_location\tview\n")

    for key, files in views.items():
        for info in files:
            view.write("%s\t%s\t%s\t%s\n" % (info['project_id'],
                                             info['accession_id'],
                                             info['file_location'],
                                             info['view']))
    view.close()
