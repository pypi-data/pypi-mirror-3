VERSION = 0.2

from db import create_session, tables
from config import use_genome


def use(name):
    session = create_session(name)
    genome = use_genome(name)
    return session, genome
