

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

# Define the Base class

class Base(DeclarativeBase):
    pass

from datetime import date
from typing import List

db = SQLAlchemy(model_class=Base)


# Association table
from sqlalchemy import Table, Column, Integer, ForeignKey

service_mechanics = Table(
    'service_mechanics',
    Base.metadata,
    Column('ticket_id', Integer, ForeignKey('service_tickets.id')),
    Column('mechanic_id', Integer, ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(500), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False, unique=True)

    service_ticket: Mapped['ServiceTicket'] = db.relationship(back_populates='customer')

class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False,)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_description: Mapped[str] = mapped_column(db.String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)

    customer: Mapped[Customer] = db.relationship(back_populates='service_ticket')
    mechanics: Mapped[List['Mechanic']] = db.relationship(
        secondary=service_mechanics, back_populates='service_tickets'
    )

class Mechanic(Base):
    __tablename__ = 'mechanics'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List[ServiceTicket]] = db.relationship(
        secondary=service_mechanics, back_populates='mechanics'
    )
