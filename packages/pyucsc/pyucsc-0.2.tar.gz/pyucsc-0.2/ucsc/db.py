"""
UCSC Interface via SQLalchemy
=============================
"""
import os
import re

from sqlalchemy import sql
from sqlalchemy import orm
import sqlalchemy as sa
import logging; log = logging.getLogger(__name__)


import config
import model

Session = orm.sessionmaker()
session = Session()
initialized = False
meta = None


# Set up mappers
# ==============
class tables(object):
    """ Namespace for tables """
    pass

def abort_ro(*args,**kwargs):
    return


def create_session(name, echo=False):
    """ load UCSC table definitions and create session """
    global initialized, meta, DBSNP
    if initialized:
        return

    uri = config.get_database_uri(name)

    log.info('connecting to UCSC at ' + uri)
    engine = sa.create_engine(uri, echo=echo)
    Session.configure(bind=engine)
    conn = engine.connect()
    # try:
    #     log.info('loading cached UCSC table definitions')
    #     table_file = os.path.join(os.path.split(__file__)[0], '.tables.pickle')
    #     meta = pickle.load(file(table_file))
    #     meta.bind = engine
    # except IOError:
    #     print 'WARNING: could not load table metadata, please call cache_tables()'
    meta = sa.MetaData()
    meta.bind = conn
    meta.reflect()

    # populate tables namespace
    for (name, table) in meta.tables.items():
        if 'wgEncode' not in name:
            setattr(tables, name, table)


    # KGXref is one to one with knownGene, so we can safely always use this join
    join_knowngene_xref = sql.join(tables.knownGene, tables.kgXref,
        tables.kgXref.c.kgID==tables.knownGene.c.name
    )

    join_knowncanonical = join_knowngene_xref.join(tables.knownCanonical, # this join means known gene only returns canonical transcripts
         tables.knownCanonical.c.transcript==tables.knownGene.c.name
    )

    # get the most recent snp table available
    snp_tables = sorted([x for x in meta.tables if re.match('snp\d\d\d$', x)])
    snp_table = snp_tables[-1]
    DBSNP = meta.tables[snp_table]
    model.Snp.table = DBSNP
    orm.mapper(model.Snp, DBSNP, primary_key=DBSNP.c.name, properties={
        'class_': DBSNP.c['class'],
    })
    if snp_table + 'Common' in meta.tables:
        commonSnp = meta.tables[snp_table + 'Common']
        model.CommonSnp.table = commonSnp
        orm.mapper(model.CommonSnp, commonSnp, primary_key=commonSnp.c.name, properties={
            'class_': commonSnp.c['class'],
        })

    # TODO: should remove this join?
    orm.mapper(model.KnownGene, join_knowngene_xref, primary_key=tables.knownGene.c.name,
        exclude_properties=[tables.knownCanonical.c.chrom]
    )
    orm.mapper(model.KnownCanonical, join_knowncanonical, primary_key=tables.knownGene.c.name,
        exclude_properties=[tables.knownCanonical.c.chrom, tables.knownCanonical.c.transcript]
    )

    orm.mapper(model.CcdsGene, tables.ccdsGene, primary_key=tables.ccdsGene.c.name)
    orm.mapper(model.RefGene, tables.refGene, primary_key=tables.refGene.c.name)

    orm.mapper(model.ChainSelf, tables.chainSelf, primary_key=tables.chainSelf.c.id)
    orm.mapper(model.ChainSelfLink, tables.chainSelfLink,
        primary_key=[tables.chainSelfLink.c.qStart, tables.chainSelfLink.c.chainId],
        properties={
            'chain': orm.relationship(model.ChainSelf, backref='links',
                primaryjoin=tables.chainSelfLink.c.chainId==tables.chainSelf.c.id,
                foreign_keys=[tables.chainSelfLink.c.chainId],
                lazy=False
            ),
        }
    )
    # monkeypatch session to enforce readonly
    session.flush = abort_ro

    initialized = True
    model.session = session
    return session
