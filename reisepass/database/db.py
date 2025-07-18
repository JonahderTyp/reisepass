from __future__ import annotations

import base64
import json
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

    def to_dict(self, depth: int = 1, _visited: set[int] | None = None) -> dict:
        if _visited is None:
            _visited = set()

        # Only check for cycles in the current recursion path.
        if id(self) in _visited:
            # Instead of returning an empty dict, you might return a minimal representation.
            return {"id": getattr(self, "id", None)}

        _visited.add(id(self))
        data = {}

        # Serialize columns
        mapper = self.__mapper__
        for column in mapper.columns:
            data[column.key] = getattr(self, column.key)

        # Serialize relationships if depth allows
        if depth > 0:
            for rel in mapper.relationships:
                rel_val = getattr(self, rel.key)
                if rel_val is None:
                    data[rel.key] = None
                elif isinstance(rel_val, list):
                    data[rel.key] = [
                        item.to_dict(depth=depth - 1, _visited=_visited.copy())
                        for item in rel_val
                    ]
                else:
                    data[rel.key] = rel_val.to_dict(
                        depth=depth - 1, _visited=_visited.copy())

        _visited.remove(id(self))
        return data


class stufe(BaseTable):
    __tablename__ = "stufe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    members: Mapped[List[member]] = relationship(
        "member", back_populates="stufe")

    @staticmethod
    def get_via_name(name: str) -> stufe:
        item = db.session.query(stufe).filter_by(name=name).first()
        if not item:
            raise ElementDoesNotExsist(
                f"Stufe mit dem Namen \"{name}\" existiert nicht")
        return item

    @staticmethod
    def create_new(name: str) -> stufe:
        if stufe.filter_by(name=name):
            raise ElementAlreadyExists(
                f"Stufe mit dem Namen \"{name}\" existiert bereits")
        s = stufe(name=name)
        db.session.add(s)
        db.session.commit()
        return s


class member(BaseTable):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    vorname: Mapped[str] = mapped_column(String(255), nullable=False)
    nachname: Mapped[str] = mapped_column(String(255), nullable=False)
    geburtstag: Mapped[str] = mapped_column(String(255), nullable=False)
    jsondata: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=None)  # Use JSON type for jsondata
    stufe_id: Mapped[int] = mapped_column(
        ForeignKey("stufe.id"), nullable=False)
    stufe: Mapped[stufe] = relationship("stufe", back_populates="members")

    def update(self, code: Optional[str] = None, vorname: Optional[str] = None,
               nachname: Optional[str] = None, geburtstag: Optional[str] = None,
               jsondata: Optional[dict] = None, stufe: Optional[stufe] = None) -> member:
        if code:
            self.code = code
        if vorname:
            self.vorname = vorname
        if nachname:
            self.nachname = nachname
        if geburtstag:
            self.geburtstag = geburtstag
        if jsondata is not None:
            if isinstance(jsondata, str):
                try:
                    jsondata = json.loads(jsondata)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid jsondata string: {e}")
            if not isinstance(jsondata, dict):
                raise ValueError("jsondata must be a dictionary")
            self.jsondata = jsondata
        if stufe:
            self.stufe_id = stufe.id
        db.session.commit()
        return self

    @staticmethod
    def get_via_code(code: str) -> member:
        item = db.session.query(member).filter_by(code=code).first()
        if not item:
            raise ElementDoesNotExsist(
                f"Mitglied mit dem Code \"{code}\" existiert nicht")
        return item

    @staticmethod
    def create_new(code: str, vorname: str, nachname: str, geburtstag: str, jsondata: dict, stufe: stufe) -> member:
        if member.filter_by(code=code):
            raise ElementAlreadyExists(
                f"Mitglied mit dem Code \"{code}\" existiert bereits")
        m = member(code=code, vorname=vorname, nachname=nachname,
                   geburtstag=geburtstag, jsondata=jsondata, stufe_id=stufe.id)
        db.session.add(m)
        db.session.commit()
        return m
