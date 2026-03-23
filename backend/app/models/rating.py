from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("rater_id", "listing_id", name="uq_rater_listing"),)

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id  = Column(Integer, ForeignKey("users.id",    ondelete="CASCADE"), nullable=False, index=True)
    rater_id   = Column(Integer, ForeignKey("users.id",    ondelete="CASCADE"), nullable=False, index=True)
    score      = Column(Integer, nullable=False)
    comment    = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="ratings")
    seller  = relationship("User", foreign_keys=[seller_id], back_populates="ratings_received",
                           overlaps="ratings_received")
    rater   = relationship("User", foreign_keys=[rater_id], back_populates="ratings_given",
                           overlaps="ratings_given")
