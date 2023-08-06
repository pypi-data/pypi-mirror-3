# -*- coding: utf-8 -*-

from versionetape import VersionEtape
from elementpedagogi import ElementPedagogi

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class IndContratElp(Base):
    __tablename__ = "ind_contrat_elp"

    VV_COD_ETP = Column(String(6), primary_key=True)
    VV_COD_ELP = Column(String(8))
    COD_VRS_VET = Column(Integer)
    COD_IND = Column(Integer)
    COD_ANU = Column(String(4))
    COD_LSE = Column(String(8))
    COD_ETP = Column(String(6), ForeignKey(VersionEtape.COD_ETP))
    COD_ELP = Column(String(8), ForeignKey(ElementPedagogi.COD_ELP))

    V_COD_ETP = relationship(VersionEtape, backref=backref('ind_contrat_elp', order_by=VV_COD_ETP))
    V_COD_ELP = relationship(ElementPedagogi, backref=backref('ind_contrat_elp', order_by=VV_COD_ELP))

    def __init__(self, COD_ETP=None, COD_VRS_VET=None, COD_ELP=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET
        self.COD_ELP = COD_ELP

    def __repr__(self):
        return "<IndContratElp COD_ETP=%d COD_VRS_VET=%s COD_ELP=%s>" % (self.COD_ETP, self.COD_VRS_VET, self.COD_ELP)