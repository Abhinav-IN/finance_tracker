from enum import Enum

class TransactionDirection(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class BillingPeriod(str, Enum):
    YEARLY = "YEARLY"
    HALF_YEARLY = "HALF_YEARLY"
    QUATERLY = "QUATERLY"
    WEEKLY = "WEEKLY"
    ONE_TIME = "ONE_TIME"
    MONTHLY = "MONTHLY"

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    SUPPORT = "SUPPORT"