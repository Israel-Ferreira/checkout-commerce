from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Float, Integer, String


from checkout_commerce.infra.database import Base



class CheckoutStatus(Enum):
    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"

    PROCESSING_PAYMENT = "processing_payment"
    PROCESSING_INVENTORY = "processing_inventory"
    CREATING_ORDER = "creating_order"



class Checkout(Base):
    __tablename__ = "checkouts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_email = Column(String(128), nullable=False)
    status = Column(String(24), default=CheckoutStatus.PENDING.value, nullable=False)
    payment_id = Column(String(64), nullable=True)
    order_id = Column(String(64), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )
    error = Column(String(256), nullable=True)
    total_amount = Column(Float, nullable=False)