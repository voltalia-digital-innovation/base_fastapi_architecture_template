from modules.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Integer,
    String
)


class AzureBlobStorageFile(Base):
    """
    This class tracks Azure Blob Storage files

    Author: Matheus Henrique (m.araujo)

    Date: 10th October 2024
    """
    __tablename__ = "azure_integrations_azureblobstoragefile"

    id = Column(BigInteger, primary_key=True, index=True,
                autoincrement=True)
    date_update = Column(DateTime, nullable=False)
    date_create = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)
    uuid = Column(String(50), nullable=False)

    operation_associated_files = relationship(
        'OperationAssociatedFile',
        back_populates='azure_file')

    original_file_name = Column(String(256), nullable=False)
    name = Column(String(256), nullable=False)
    user_id = Column(Integer, nullable=False)
    path = Column(String(256), nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(String(256), nullable=True)
    etag = Column(String(256), nullable=False)
    file_extension = Column(String(256), nullable=False)
    request_id = Column(String(256), nullable=False)
    version = Column(String(256), nullable=False)
    container_name = Column(String(256), nullable=False)
