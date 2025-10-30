-- ==========================================================
-- COMPLETE INSTALLATION OF NYC TAXI DB V2 PROJECT
-- Database, schemas, warehouse, role, user, and RAW tables
-- ==========================================================

-- 1️⃣ Create database and schemas
create database if not exists NYC_TAXI_DB_V2;
create schema if not exists NYC_TAXI_DB_V2.RAW;
create schema if not exists NYC_TAXI_DB_V2.STAGING;
create schema if not exists NYC_TAXI_DB_V2.FINAL;

-- 2️⃣ Create transformation warehouse
create warehouse if not exists NYC_TAXI_WH_V2
  warehouse_size = 'MEDIUM'
  auto_suspend = 60
  auto_resume = true
  initially_suspended = true;

-- 3️⃣ Create TRANSFORM role
create role if not exists TRANSFORM;

-- 4️⃣ Create DBT user (if not existing)
-- ⚠️ Use a temporary password here
create user if not exists DBT
  password = 'Password123!'
  default_role = TRANSFORM
  default_warehouse = NYC_TAXI_WH_V2
  must_change_password = true;

-- 5️⃣ Grant TRANSFORM role to DBT user
grant role TRANSFORM to user DBT;

-- 6️⃣ Grant warehouse privileges
grant usage, operate on warehouse NYC_TAXI_WH_V2 to role TRANSFORM;

-- 7️⃣ Grant database and schema usage
grant usage on database NYC_TAXI_DB_V2 to role TRANSFORM;

grant usage on schema NYC_TAXI_DB_V2.RAW to role TRANSFORM;
grant usage on schema NYC_TAXI_DB_V2.STAGING to role TRANSFORM;
grant usage on schema NYC_TAXI_DB_V2.FINAL to role TRANSFORM;

-- ==========================================================
-- 8️⃣ Create RAW tables
-- ==========================================================

use role TRANSFORM;
use warehouse NYC_TAXI_WH_V2;
use database NYC_TAXI_DB_V2;

-- 🧱 Temporary table RAW.BUFFER_YELLOW_TAXI_TRIPS_V2
create or replace table RAW.BUFFER_YELLOW_TAXI_TRIPS_V2 (
    vendor_id string,
    pickup_datetime timestamp_ntz,
    dropoff_datetime timestamp_ntz,
    passenger_count int,
    trip_distance float,
    rate_code_id int,
    store_and_fwd_flag string,
    pu_location_id int,
    do_location_id int,
    payment_type int,
    fare_amount float,
    extra float,
    mta_tax float,
    tip_amount float,
    tolls_amount float,
    improvement_surcharge float,
    total_amount float,
    congestion_surcharge float,
    airport_fee float,
    load_ts timestamp_ntz default current_timestamp()
);

-- 🚕 Main table RAW.YELLOW_TAXI_TRIPS_V2
create or replace table RAW.YELLOW_TAXI_TRIPS_V2 (
    vendor_id string,
    pickup_datetime timestamp_ntz,
    dropoff_datetime timestamp_ntz,
    passenger_count int,
    trip_distance float,
    rate_code_id int,
    store_and_fwd_flag string,
    pu_location_id int,
    do_location_id int,
    payment_type int,
    fare_amount float,
    extra float,
    mta_tax float,
    tip_amount float,
    tolls_amount float,
    improvement_surcharge float,
    total_amount float,
    congestion_surcharge float,
    airport_fee float,
    ingestion_ts timestamp_ntz default current_timestamp()
);

-- ==========================================================
-- 9️⃣ Grant privileges to TRANSFORM role
-- ==========================================================

grant all privileges on all tables in schema NYC_TAXI_DB_V2.RAW to role TRANSFORM;
grant all privileges on future tables in schema NYC_TAXI_DB_V2.RAW to role TRANSFORM;

grant all privileges on all tables in schema NYC_TAXI_DB_V2.STAGING to role TRANSFORM;
grant all privileges on all tables in schema NYC_TAXI_DB_V2.FINAL to role TRANSFORM;

-- ==========================================================
-- ✅ Installation complete: RAW ready for ingestion
-- ==========================================================
