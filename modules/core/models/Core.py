import uuid
from datetime import datetime
from modules.core.database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import (
    BigInteger, DateTime, String, Boolean
)


class BaseDB(Base):
    """
    BaseDB class is DB class to be implemented in all
    classes of the system. It will provide lots of facilities

    Author: Matheus Henrique (m.araujo)

    Date: 9th September 2024
    """
    __abstract__ = True  # Indicate that this class is not a table

    id = mapped_column(BigInteger, primary_key=True, index=True,
                       autoincrement=True, sort_order=-5)
    is_active = mapped_column(Boolean, default=True, sort_order=-4)
    uuid = mapped_column(String(36), default=lambda: str(
        uuid.uuid4()), sort_order=-3)
    date_create = mapped_column(DateTime, default=datetime.now, sort_order=-2)
    date_update = mapped_column(DateTime, default=datetime.now,
                                onupdate=datetime.now, sort_order=-1)
