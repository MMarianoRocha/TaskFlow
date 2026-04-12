from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()