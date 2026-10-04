from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claimant: Mapped[str] = mapped_column(String(120))
    date: Mapped[date] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(80))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(Text)
    receipt_available: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ai_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviews = relationship("Review", back_populates="claim", cascade="all, delete-orphan")


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(160))
    content: Mapped[str] = mapped_column(Text)
    limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"))
    action: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer: Mapped[str] = mapped_column(String(120), default="Reviewer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    claim = relationship("Claim", back_populates="reviews")
