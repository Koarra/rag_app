"""
models.py
All Pydantic schemas used across the KYC checks pipeline.
"""

from typing import List
from pydantic import BaseModel, Field


class PurposeOfBusinessRelationship(BaseModel):
    sufficient_explanation: bool = Field(
        description="Whether the details provided in kyc purpose of br justify "
                    "the transaction value present in kyc transactions"
    )
    reasoning: str = Field(
        description="The reason behind the explanation robustness"
    )


class TransactionDetail(BaseModel):
    amount: float = Field(description="Transaction amount")
    date: str = Field(description="Transaction date in YYYY-MM-DD format")
    currency: str = Field(description="Transaction currency code (e.g., USD, EUR)")


class CheckTransactionSummary(BaseModel):
    transactions_exist: bool = Field(
        description="True if any transactions are found, otherwise False"
    )
    transactions_details: List[TransactionDetail] = Field(
        description="A list of summarized transactions with amount, date, and currency"
    )


class CompletenessOriginOfAssets(BaseModel):
    complete: bool = Field(
        description="Whether the origin of assets is complete or not"
    )
    reason: str = Field(
        description="The reason behind the completion status"
    )
