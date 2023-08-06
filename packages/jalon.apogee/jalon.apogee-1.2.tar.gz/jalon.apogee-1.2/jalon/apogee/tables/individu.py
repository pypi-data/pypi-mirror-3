# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class Individu(Base):
    __tablename__ = "individu"

    COD_IND = Column(Integer, primary_key=True)
    DATE_NAI_IND = Column(String(10))
    LIB_NOM_PAT_IND = Column(String(30))
    LIB_NOM_USU_IND = Column(String(30))
    LIB_PR1_IND = Column(String(20))
    COD_ETU = Column(Integer)
    LIB_VIL_NAI_ETU = Column(String(20))

    def __init__(self, COD_IND=None):
        self.COD_IND = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET

    def __repr__(self):
        return "<Individu COD_IND=%d COD_VRS_VET=%s>" % self.COD_IND