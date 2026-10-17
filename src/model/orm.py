"""
Clases de Model (ORM) de la calculadora de incapacidades.

Cada clase se mapea a una tabla de la base de datos mediante SQLAlchemy:

    TipoIncapacidad  ->  tipos_incapacidad   (catálogo de tipos)
    CasoIncapacidad  ->  casos_incapacidad   (cálculos guardados)

Relación: un TipoIncapacidad tiene muchos CasoIncapacidad.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


class Base(DeclarativeBase):
    """Clase base de todos los modelos ORM."""


class TipoIncapacidad(Base):
    """Tipo de incapacidad (enfermedad general, maternidad, ...)."""

    __tablename__ = "tipos_incapacidad"

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)

    casos: Mapped[list["CasoIncapacidad"]] = relationship(
        back_populates="tipo"
    )

    def __repr__(self) -> str:
        return f"TipoIncapacidad(id={self.id}, clave={self.clave!r})"


class CasoIncapacidad(Base):
    """Cálculo de incapacidad guardado por el usuario."""

    __tablename__ = "casos_incapacidad"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    tipo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_incapacidad.id"), nullable=False
    )
    salario: Mapped[float] = mapped_column(Float, nullable=False)
    dias: Mapped[int] = mapped_column(Integer, nullable=False)
    pago: Mapped[float] = mapped_column(Float, nullable=False)

    tipo: Mapped[TipoIncapacidad] = relationship(
        back_populates="casos"
    )

    def a_diccionario(self) -> dict:
        """Convierte el caso en un diccionario simple para la UI."""
        return {
            "id": self.id,
            "fecha": self.fecha.strftime(FORMATO_FECHA),
            "tipo_incapacidad": self.tipo.clave,
            "tipo_nombre": self.tipo.nombre,
            "salario": self.salario,
            "dias": self.dias,
            "pago": self.pago,
        }

    def __repr__(self) -> str:
        return f"CasoIncapacidad(id={self.id}, pago={self.pago})"
