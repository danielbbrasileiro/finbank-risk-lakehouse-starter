create database if not exists FINBANK;
create schema if not exists FINBANK.RAW;
create schema if not exists FINBANK.STAGING;
create schema if not exists FINBANK.MARTS;

create or replace table FINBANK.RAW.CUSTOMERS (
    customer_id string,
    customer_name string,
    document_type string,
    segment string,
    state string,
    created_at date,
    internal_score number
);

create or replace table FINBANK.RAW.TRANSACTIONS (
    transaction_id string,
    customer_id string,
    account_id string,
    transaction_date date,
    channel string,
    transaction_type string,
    amount number(18,2),
    is_suspicious boolean
);

create or replace table FINBANK.RAW.LOANS (
    loan_id string,
    customer_id string,
    product_type string,
    origination_date date,
    maturity_date date,
    principal_amount number(18,2),
    outstanding_balance number(18,2),
    interest_rate number(10,4),
    days_past_due number,
    risk_rating string
);
