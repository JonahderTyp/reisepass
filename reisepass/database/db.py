from __future__ import annotations

import base64
from datetime import datetime as dt
from typing import List, Optional, Type, TypeVar

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import (DeclarativeBase, Mapped, declarative_base,
                            mapped_column, relationship)
from werkzeug.security import check_password_hash, generate_password_hash

from .exceptions import ElementAlreadyExists, ElementDoesNotExsist


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

T = TypeVar('T', bound='BaseTable')


class BaseTable(Base):
    __abstract__ = True

    @classmethod
    def filter_by(cls: Type[T], **kwargs) -> List[T]:
        return db.session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def get_all(cls: Type[T]) -> List[T]:
        return db.session.query(cls).all()

    @classmethod
    def get_via_id(cls: Type[T], id: int) -> T:
        item = db.session.query(cls).get({"id": id})
        if not item:
            raise ElementDoesNotExsist(
                f"{str(cls.__name__).replace('Table', '')} mit der ID \"{id}\" existiert nicht")
        return item

    def to_dict(self) -> dict:
        data = {key: getattr(self, key)
                for key in self.__table__.columns.keys()}
        return data


class member(BaseTable):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    vorname: Mapped[str] = mapped_column(String(255), nullable=False)
    nachname: Mapped[str] = mapped_column(String(255), nullable=False)
    geburtstag: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[str] = mapped_column(String(255), nullable=False)

    @staticmethod
    def get_via_code(code: str) -> member:
        item = db.session.query(member).filter_by(code=code).first()
        if not item:
            raise ElementDoesNotExsist(
                f"Mitglied mit dem Code \"{code}\" existiert nicht")
        return item

    @staticmethod
    def create(code: str, vorname: str, nachname: str, geburtstag: str, size: str) -> member:
        if member.filter_by(code=code):
            raise ElementAlreadyExists(
                f"Mitglied mit dem Code \"{code}\" existiert bereits")
        m = member(code=code, vorname=vorname, nachname=nachname,
                   geburtstag=geburtstag, size=size)
        db.session.add(m)
        db.session.commit()
        return m
