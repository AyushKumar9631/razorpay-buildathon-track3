"""
Import all models for Alembic to detect.
"""

from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.risk import RevenueRisk
from app.models.intervention import Intervention, RecoveryOutcome
from app.models.audit import AuditTrail, ComplianceRule
from app.models.subscription import CustomerSubscription, AbandonedCart

__all__ = [
    "Customer",
    "Transaction",
    "RevenueRisk",
    "Intervention",
    "RecoveryOutcome",
    "AuditTrail",
    "ComplianceRule",
    "CustomerSubscription",
    "AbandonedCart",
]
