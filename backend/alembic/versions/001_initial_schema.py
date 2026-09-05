"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-09-05 09:40:18.894000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('customer_type', sa.String(length=20), nullable=True),
        sa.Column('tier', sa.String(length=20), nullable=True),
        sa.Column('lifetime_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_transactions', sa.Integer(), nullable=True),
        sa.Column('failed_transactions', sa.Integer(), nullable=True),
        sa.Column('communication_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_customers_email', 'customers', ['email'])
    op.create_index('idx_customers_tier', 'customers', ['tier'])
    op.create_index(op.f('ix_customers_customer_id'), 'customers', ['customer_id'], unique=True)

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('failure_code', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_transaction_customer_status', 'transactions', ['customer_id', 'status'])
    op.create_index('idx_transaction_status_created', 'transactions', ['status', 'created_at'])
    op.create_index('idx_transactions_customer', 'transactions', ['customer_id'])
    op.create_index('idx_transactions_created', 'transactions', ['created_at'])
    op.create_index('idx_transactions_status', 'transactions', ['status'])
    op.create_index(op.f('ix_transactions_transaction_id'), 'transactions', ['transaction_id'], unique=True)

    # Create revenue_risks table
    op.create_table(
        'revenue_risks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('risk_type', sa.String(length=50), nullable=False),
        sa.Column('risk_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('ai_diagnosis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_revenue_risks_customer', 'revenue_risks', ['customer_id'])
    op.create_index('idx_revenue_risks_detected', 'revenue_risks', ['detected_at'])
    op.create_index('idx_revenue_risks_priority', 'revenue_risks', ['priority'])
    op.create_index('idx_revenue_risks_status', 'revenue_risks', ['status'])
    op.create_index('idx_revenue_risks_type', 'revenue_risks', ['risk_type'])
    op.create_index('idx_risk_priority_status', 'revenue_risks', ['priority', 'status'])
    op.create_index('idx_risk_status_detected', 'revenue_risks', ['status', 'detected_at'])
    op.create_index('idx_risk_type_status', 'revenue_risks', ['risk_type', 'status'])

    # Create interventions table
    op.create_table(
        'interventions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('revenue_risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('intervention_type', sa.String(length=50), nullable=False),
        sa.Column('intervention_strategy', sa.String(length=100), nullable=True),
        sa.Column('channel', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('outcome', sa.String(length=50), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.Column('cost', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['revenue_risk_id'], ['revenue_risks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_intervention_risk_status', 'interventions', ['revenue_risk_id', 'status'])
    op.create_index('idx_intervention_status_scheduled', 'interventions', ['status', 'scheduled_at'])
    op.create_index('idx_interventions_executed', 'interventions', ['executed_at'])
    op.create_index('idx_interventions_risk', 'interventions', ['revenue_risk_id'])
    op.create_index('idx_interventions_scheduled', 'interventions', ['scheduled_at'])
    op.create_index('idx_interventions_status', 'interventions', ['status'])

    # Create recovery_outcomes table
    op.create_table(
        'recovery_outcomes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('revenue_risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('intervention_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recovered_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('recovered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recovery_method', sa.String(length=100), nullable=True),
        sa.Column('time_to_recovery', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('customer_feedback', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['intervention_id'], ['interventions.id'], ),
        sa.ForeignKeyConstraint(['revenue_risk_id'], ['revenue_risks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_recovery_outcomes_recovered', 'recovery_outcomes', ['recovered_at'])
    op.create_index('idx_recovery_outcomes_risk', 'recovery_outcomes', ['revenue_risk_id'], unique=True)

    # Create customer_subscriptions table
    op.create_table(
        'customer_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', sa.String(length=100), nullable=False),
        sa.Column('plan_name', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('next_billing_date', sa.Date(), nullable=True),
        sa.Column('failed_attempts', sa.Integer(), nullable=True),
        sa.Column('last_failure_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('grace_period_end', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_subscription_status_billing', 'customer_subscriptions', ['status', 'next_billing_date'])
    op.create_index('idx_subscriptions_customer', 'customer_subscriptions', ['customer_id'])
    op.create_index('idx_subscriptions_next_billing', 'customer_subscriptions', ['next_billing_date'])
    op.create_index('idx_subscriptions_status', 'customer_subscriptions', ['status'])
    op.create_index(op.f('ix_customer_subscriptions_subscription_id'), 'customer_subscriptions', ['subscription_id'], unique=True)

    # Create abandoned_carts table
    op.create_table(
        'abandoned_carts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cart_id', sa.String(length=100), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('items', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('abandoned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('abandonment_stage', sa.String(length=50), nullable=True),
        sa.Column('recovery_status', sa.String(length=50), nullable=True),
        sa.Column('recovered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_carts_abandoned', 'abandoned_carts', ['abandoned_at'])
    op.create_index('idx_carts_customer', 'abandoned_carts', ['customer_id'])
    op.create_index('idx_carts_status', 'abandoned_carts', ['recovery_status'])
    op.create_index('idx_cart_status_abandoned', 'abandoned_carts', ['recovery_status', 'abandoned_at'])
    op.create_index(op.f('ix_abandoned_carts_cart_id'), 'abandoned_carts', ['cart_id'], unique=True)

    # Create audit_trail table
    op.create_table(
        'audit_trail',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('compliance_check', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_entity', 'audit_trail', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_entity_type', 'audit_trail', ['entity_type'])
    op.create_index('idx_audit_entity_id', 'audit_trail', ['entity_id'])
    op.create_index('idx_audit_timestamp', 'audit_trail', ['timestamp'])

    # Create compliance_rules table
    op.create_table(
        'compliance_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_name', sa.String(length=100), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_rules_rule_name'), 'compliance_rules', ['rule_name'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('compliance_rules')
    op.drop_table('audit_trail')
    op.drop_table('abandoned_carts')
    op.drop_table('customer_subscriptions')
    op.drop_table('recovery_outcomes')
    op.drop_table('interventions')
    op.drop_table('revenue_risks')
    op.drop_table('transactions')
    op.drop_table('customers')
