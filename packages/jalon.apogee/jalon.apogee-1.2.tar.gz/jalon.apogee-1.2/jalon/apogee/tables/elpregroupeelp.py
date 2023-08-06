# -*- coding: utf-8 -*-

from elementpedagogi import ElementPedagogi

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class ElpRegroupeElp(Base):
    __tablename__ = "elp_regroupe_elp"

    VV_COD_ELP_FILS = Column(String(8), primary_key=True)
    COD_LSE = Column(String(8))
    ETA_LSE = Column(String(1))
    COD_ELP_PERE = Column(String(8))
    COD_ELP_FILS = Column(String(8), ForeignKey(ElementPedagogi.COD_ELP))

    V_COD_ELP_FILS = relationship(ElementPedagogi, backref=backref('elp_regroupe_elp', order_by=VV_COD_ELP_FILS))

    def __init__(self, COD_ELP_FILS=None, ETA_LSE=None):
        self.COD_ELP_FILS = COD_ELP_FILS
        self.ETA_LSE = ETA_LSE

    def __repr__(self):
        return "<ElpRegroupeElp COD_ELP_FILS=%d ETA_LSE=%s>" % (self.COD_ETP_FILS, self.ETA_LSE)