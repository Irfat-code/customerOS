-- SaaS schemas
CREATE SCHEMA IF NOT EXISTS saas_crm;
CREATE SCHEMA IF NOT EXISTS saas_product;
CREATE SCHEMA IF NOT EXISTS saas_support;
CREATE SCHEMA IF NOT EXISTS saas_billing;
CREATE SCHEMA IF NOT EXISTS saas_nps;

-- Fintech schemas
CREATE SCHEMA IF NOT EXISTS fintech_accounts;
CREATE SCHEMA IF NOT EXISTS fintech_transactions;
CREATE SCHEMA IF NOT EXISTS fintech_cards;
CREATE SCHEMA IF NOT EXISTS fintech_loans;

-- Observability schema
CREATE SCHEMA IF NOT EXISTS observability;

-- Pipeline watermarks
CREATE TABLE IF NOT EXISTS observability.watermarks (
    entity_name     VARCHAR(200) PRIMARY KEY,
    last_updated_at TIMESTAMPTZ,
    last_run_at     TIMESTAMPTZ DEFAULT NOW()
);