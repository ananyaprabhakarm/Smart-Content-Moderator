from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base


class ModerationRequest(Base):
    __tablename__ = "moderation_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_type = Column(String(50), nullable=False)  # 'text' or 'image'
    content_hash = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    results = relationship("ModerationResult", back_populates="request", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="request", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ModerationRequest(id={self.id}, type={self.content_type}, status={self.status})>"


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    classification = Column(String(100), nullable=False)  # appropriate, inappropriate, or specific categories
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    llm_response = Column(Text, nullable=True)

    # Relationship
    request = relationship("ModerationRequest", back_populates="results")

    def __repr__(self):
        return f"<ModerationResult(id={self.id}, request_id={self.request_id}, classification={self.classification})>"


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    channel = Column(String(100), nullable=False)  # email, webhook, slack, etc.
    status = Column(String(50), nullable=False)  # sent, failed, pending
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    request = relationship("ModerationRequest", back_populates="notifications")

    def __repr__(self):
        return f"<NotificationLog(id={self.id}, request_id={self.request_id}, channel={self.channel}, status={self.status})>"
