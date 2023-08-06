import yaml
import os
import sys
import logging; log = logging.getLogger(__name__)
import fastinterval

fasta_dir = None
database_uri = None
public_database_uri = 'mysql://genome@genome-mysql.cse.ucsc.edu/'
genome = None

def load_yaml(fname):
    global fasta_dir, database_uri
    try:
        data = yaml.load(file(fname))

        if 'fasta_dir' in data:
            fasta_dir = os.path.expanduser(data['fasta_dir'])

        if 'database_uri' in data:
            database_uri = data['database_uri']

    except IOError:
        pass

load_yaml(os.path.expanduser('/etc/pyucsc'))
load_yaml(os.path.expanduser('~/.pyucsc'))

# TODO environment variable configuration, other paths

def get_fasta_path(name):
    if not fasta_dir:
        raise Exception('No directory configured for UCSC fasta files')
    return os.path.join(fasta_dir, name + '.fa')

def get_database_uri(name):
    uri = database_uri
    if not uri:
        print >>sys.stderr, 'Falling back to public UCSC server, please see the usage policy:'
        print >>sys.stderr, 'http://genome.ucsc.edu/FAQ/FAQdownloads.html#download29'
        uri = public_database_uri

    return uri + name

def use_genome(name):
    global genome
    genome = fastinterval.Genome(os.path.join(fasta_dir, name) + '.fa')
    return genome
