from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# Enums for type safety
class UserRole(str, Enum):
    FIRM_ADMIN = "firm_admin"
    MANAGING_PARTNER = "managing_partner"
    ATTORNEY = "attorney"
    PARALEGAL = "paralegal"
    ACCOUNTING_STAFF = "accounting_staff"
    CLIENT = "client"
    HR_REPRESENTATIVE = "hr_representative"
    COMPANY_MANAGER = "company_manager"
    INDIVIDUAL_EMPLOYEE = "individual_employee"


class ClientType(str, Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"


class CaseStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    STOPPED = "stopped"


class ActivityBillableStatus(str, Enum):
    NON_BILLABLE = "non_billable"
    BILLABLE = "billable"
    BILLED = "billed"


class ActivityStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BillingModel(str, Enum):
    HOURLY = "hourly"
    FLAT_FEE = "flat_fee"
    CONTINGENCY = "contingency"
    RETAINER = "retainer"


class ExpenseType(str, Enum):
    REIMBURSABLE = "reimbursable"
    NON_REIMBURSABLE = "non_reimbursable"


class ResourceType(str, Enum):
    ATTORNEY = "attorney"
    PARALEGAL = "paralegal"
    ADMIN = "admin"


class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    BILLING = "billing"


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


# User Management Models
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole
    is_active: bool = Field(default=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assigned_cases: List["Case"] = Relationship(back_populates="assigned_attorney")
    activities: List["Activity"] = Relationship(back_populates="assigned_user")
    expenses: List["Expense"] = Relationship(back_populates="user")
    time_entries: List["TimeEntry"] = Relationship(back_populates="user")


# Client Management Models
class Client(SQLModel, table=True):
    __tablename__ = "clients"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    client_type: ClientType

    # Individual client fields
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    date_of_birth: Optional[datetime] = Field(default=None)

    # Organization client fields
    organization_name: Optional[str] = Field(default=None, max_length=200)
    tax_id: Optional[str] = Field(default=None, max_length=50)

    # Common fields
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address_line1: Optional[str] = Field(default=None, max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=50)
    zip_code: Optional[str] = Field(default=None, max_length=20)
    country: Optional[str] = Field(default=None, max_length=100)

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    cases: List["Case"] = Relationship(back_populates="client")
    beneficiary_relationships: List["BeneficiaryRelationship"] = Relationship(back_populates="beneficiary")
    dependent_relationships: List["BeneficiaryRelationship"] = Relationship(back_populates="dependent")


class BeneficiaryRelationship(SQLModel, table=True):
    __tablename__ = "beneficiary_relationships"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiary_id: int = Field(foreign_key="clients.id")
    dependent_id: int = Field(foreign_key="clients.id")
    relationship_type: str = Field(max_length=50)  # spouse, child, parent, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    beneficiary: Client = Relationship(back_populates="beneficiary_relationships")
    dependent: Client = Relationship(back_populates="dependent_relationships")


# Case Management Models
class CaseType(SQLModel, table=True):
    __tablename__ = "case_types"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    default_billing_model: BillingModel
    default_hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)
    default_flat_fee: Optional[Decimal] = Field(default=None, decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    cases: List["Case"] = Relationship(back_populates="case_type")


class Case(SQLModel, table=True):
    __tablename__ = "cases"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_number: str = Field(unique=True, max_length=100)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: CaseStatus = Field(default=CaseStatus.PENDING)

    client_id: int = Field(foreign_key="clients.id")
    case_type_id: int = Field(foreign_key="case_types.id")
    assigned_attorney_id: Optional[int] = Field(default=None, foreign_key="users.id")

    billing_model: BillingModel
    hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)
    flat_fee: Optional[Decimal] = Field(default=None, decimal_places=2)
    contingency_percentage: Optional[Decimal] = Field(default=None, decimal_places=2)
    retainer_amount: Optional[Decimal] = Field(default=None, decimal_places=2)

    opened_date: Optional[datetime] = Field(default=None)
    closed_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    client: Client = Relationship(back_populates="cases")
    case_type: CaseType = Relationship(back_populates="cases")
    assigned_attorney: Optional[User] = Relationship(back_populates="assigned_cases")
    activities: List["Activity"] = Relationship(back_populates="case")
    expenses: List["Expense"] = Relationship(back_populates="case")
    documents: List["Document"] = Relationship(back_populates="case")
    opposing_parties: List["OpposingParty"] = Relationship(back_populates="case")
    jurisdictions: List["CaseJurisdiction"] = Relationship(back_populates="case")
    invoices: List["Invoice"] = Relationship(back_populates="case")
    trust_transactions: List["TrustTransaction"] = Relationship(back_populates="case")


class OpposingParty(SQLModel, table=True):
    __tablename__ = "opposing_parties"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id")
    party_type: ClientType  # Individual or Organization

    # Individual fields
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)

    # Organization fields
    organization_name: Optional[str] = Field(default=None, max_length=200)

    # Common fields
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address_line1: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=50)

    # Counsel information
    counsel_name: Optional[str] = Field(default=None, max_length=200)
    counsel_firm: Optional[str] = Field(default=None, max_length=200)
    counsel_email: Optional[str] = Field(default=None, max_length=255)
    counsel_phone: Optional[str] = Field(default=None, max_length=20)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Case = Relationship(back_populates="opposing_parties")


class Jurisdiction(SQLModel, table=True):
    __tablename__ = "jurisdictions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    jurisdiction_type: str = Field(max_length=50)  # Federal, State, Local, etc.
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case_jurisdictions: List["CaseJurisdiction"] = Relationship(back_populates="jurisdiction")


class CaseJurisdiction(SQLModel, table=True):
    __tablename__ = "case_jurisdictions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id")
    jurisdiction_id: int = Field(foreign_key="jurisdictions.id")
    is_primary: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Case = Relationship(back_populates="jurisdictions")
    jurisdiction: Jurisdiction = Relationship(back_populates="case_jurisdictions")


class Document(SQLModel, table=True):
    __tablename__ = "documents"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id")
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=1000)
    file_path: str = Field(max_length=1000)
    file_name: str = Field(max_length=255)
    file_size: int  # in bytes
    mime_type: str = Field(max_length=100)
    uploaded_by_id: int = Field(foreign_key="users.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Case = Relationship(back_populates="documents")


# Activity Tracking Models
class Activity(SQLModel, table=True):
    __tablename__ = "activities"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id")
    assigned_user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    activity_type: str = Field(max_length=100)  # Meeting, Phone Call, Court Date, Research, etc.
    status: ActivityStatus = Field(default=ActivityStatus.PENDING)
    billable_status: ActivityBillableStatus = Field(default=ActivityBillableStatus.NON_BILLABLE)

    due_date: Optional[datetime] = Field(default=None)
    completed_date: Optional[datetime] = Field(default=None)

    # Court dates and critical deadlines
    is_court_date: bool = Field(default=False)
    is_critical_deadline: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Case = Relationship(back_populates="activities")
    assigned_user: Optional[User] = Relationship(back_populates="activities")
    time_entries: List["TimeEntry"] = Relationship(back_populates="activity")


class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activities.id")
    user_id: int = Field(foreign_key="users.id")

    hours: Decimal = Field(decimal_places=1)  # 6-minute increments (0.1 hours)
    rate_per_hour: Decimal = Field(decimal_places=2)
    total_amount: Decimal = Field(decimal_places=2)

    description: str = Field(max_length=1000)
    date: datetime
    billable_status: ActivityBillableStatus = Field(default=ActivityBillableStatus.BILLABLE)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    activity: Activity = Relationship(back_populates="time_entries")
    user: User = Relationship(back_populates="time_entries")
    invoice_line_items: List["InvoiceLineItem"] = Relationship(back_populates="time_entry")


# Expense Tracking Models
class Expense(SQLModel, table=True):
    __tablename__ = "expenses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id")
    user_id: int = Field(foreign_key="users.id")

    description: str = Field(max_length=500)
    expense_type: ExpenseType
    amount: Decimal = Field(decimal_places=2)
    markup_percentage: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total_amount: Decimal = Field(decimal_places=2)  # amount + markup

    expense_date: datetime
    category: str = Field(max_length=100)  # Travel, Filing Fees, etc.
    vendor: Optional[str] = Field(default=None, max_length=200)
    receipt_file_path: Optional[str] = Field(default=None, max_length=1000)

    is_reimbursed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Case = Relationship(back_populates="expenses")
    user: User = Relationship(back_populates="expenses")
    invoice_line_items: List["InvoiceLineItem"] = Relationship(back_populates="expense")


# Billing and Invoicing Models
class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id")
    invoice_number: str = Field(unique=True, max_length=100)

    invoice_date: datetime
    due_date: datetime

    subtotal_time: Decimal = Field(default=Decimal("0"), decimal_places=2)
    subtotal_expenses: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total_amount: Decimal = Field(decimal_places=2)

    status: str = Field(max_length=50)  # Draft, Sent, Paid, Overdue, Cancelled
    notes: Optional[str] = Field(default=None, max_length=2000)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)
    paid_at: Optional[datetime] = Field(default=None)

    # Relationships
    case: Case = Relationship(back_populates="invoices")
    line_items: List["InvoiceLineItem"] = Relationship(back_populates="invoice")


class InvoiceLineItem(SQLModel, table=True):
    __tablename__ = "invoice_line_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoices.id")
    time_entry_id: Optional[int] = Field(default=None, foreign_key="time_entries.id")
    expense_id: Optional[int] = Field(default=None, foreign_key="expenses.id")

    line_type: str = Field(max_length=50)  # time, expense
    date: datetime
    resource_name: str = Field(max_length=200)  # Attorney/Paralegal/Admin name
    resource_type: ResourceType
    description: str = Field(max_length=1000)

    quantity: Decimal = Field(decimal_places=3)  # hours or units
    rate: Decimal = Field(decimal_places=2)  # rate per hour or unit
    amount: Decimal = Field(decimal_places=2)  # quantity * rate

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    invoice: Invoice = Relationship(back_populates="line_items")
    time_entry: Optional[TimeEntry] = Relationship(back_populates="invoice_line_items")
    expense: Optional[Expense] = Relationship(back_populates="invoice_line_items")


# Trust Accounting Models
class TrustAccount(SQLModel, table=True):
    __tablename__ = "trust_accounts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    account_name: str = Field(max_length=200)
    account_number: str = Field(unique=True, max_length=100)
    bank_name: str = Field(max_length=200)
    current_balance: Decimal = Field(default=Decimal("0"), decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    trust_transactions: List["TrustTransaction"] = Relationship(back_populates="trust_account")


class TrustTransaction(SQLModel, table=True):
    __tablename__ = "trust_transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    trust_account_id: int = Field(foreign_key="trust_accounts.id")
    case_id: int = Field(foreign_key="cases.id")

    transaction_type: TransactionType
    amount: Decimal = Field(decimal_places=2)
    description: str = Field(max_length=500)
    reference_number: Optional[str] = Field(default=None, max_length=100)

    transaction_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    trust_account: TrustAccount = Relationship(back_populates="trust_transactions")
    case: Case = Relationship(back_populates="trust_transactions")


# General Ledger and Accounting Models
class Account(SQLModel, table=True):
    __tablename__ = "accounts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    account_number: str = Field(unique=True, max_length=20)
    account_name: str = Field(max_length=200)
    account_type: AccountType
    parent_account_id: Optional[int] = Field(default=None, foreign_key="accounts.id")

    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    parent_account: Optional["Account"] = Relationship(back_populates="sub_accounts")
    sub_accounts: List["Account"] = Relationship(back_populates="parent_account")
    journal_entries: List["JournalEntry"] = Relationship(back_populates="account")


class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.id")

    entry_date: datetime
    reference_number: Optional[str] = Field(default=None, max_length=100)
    description: str = Field(max_length=500)

    debit_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    credit_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)

    source_type: Optional[str] = Field(default=None, max_length=50)  # invoice, expense, etc.
    source_id: Optional[int] = Field(default=None)  # ID of source record

    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: int = Field(foreign_key="users.id")

    # Relationships
    account: Account = Relationship(back_populates="journal_entries")


# Non-persistent schemas for validation and forms
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole
    phone: Optional[str] = Field(default=None, max_length=20)
    hourly_rate: Optional[Decimal] = Field(default=None, decimal_places=2)


class ClientCreate(SQLModel, table=False):
    client_type: ClientType
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    organization_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)


class CaseCreate(SQLModel, table=False):
    case_number: str = Field(max_length=100)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    client_id: int
    case_type_id: int
    assigned_attorney_id: Optional[int] = Field(default=None)
    billing_model: BillingModel


class ActivityCreate(SQLModel, table=False):
    case_id: int
    assigned_user_id: Optional[int] = Field(default=None)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    activity_type: str = Field(max_length=100)
    due_date: Optional[datetime] = Field(default=None)
    is_court_date: bool = Field(default=False)
    is_critical_deadline: bool = Field(default=False)


class TimeEntryCreate(SQLModel, table=False):
    activity_id: int
    user_id: int
    hours: Decimal = Field(decimal_places=1)
    rate_per_hour: Decimal = Field(decimal_places=2)
    description: str = Field(max_length=1000)
    date: datetime


class ExpenseCreate(SQLModel, table=False):
    case_id: int
    user_id: int
    description: str = Field(max_length=500)
    expense_type: ExpenseType
    amount: Decimal = Field(decimal_places=2)
    markup_percentage: Decimal = Field(default=Decimal("0"), decimal_places=2)
    expense_date: datetime
    category: str = Field(max_length=100)
    vendor: Optional[str] = Field(default=None, max_length=200)


class InvoiceCreate(SQLModel, table=False):
    case_id: int
    invoice_date: datetime
    due_date: datetime
    notes: Optional[str] = Field(default=None, max_length=2000)
