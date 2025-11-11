-- ==========================================================
-- CLEAN INSTALLATION OF NYC TAXI DB V2 PROJECT
-- Drops existing objects and recreates database, schemas,
-- warehouse, role, user, and RAW tables
-- ==========================================================

-- 0️⃣ Set role to ACCOUNTADMIN to allow drops
use role ACCOUNTADMIN;

-- ==========================================================
-- 1️⃣ Drop user, role, warehouse and database if they exist
-- ==========================================================

-- Drop DBT user
drop user if exists DBT;

-- Drop TRANSFORM role
drop role if exists TRANSFORM;

-- Drop warehouse
drop warehouse if exists NYC_TAXI_WH_V2;

-- Drop database (cascade deletes all schemas and tables)
drop database if exists NYC_TAXI_DB_V2 cascade;

-- ==========================================================
-- 2️⃣ Recreate database and schemas
-- ==========================================================
create database if not exists NYC_TAXI_DB_V2;
create schema if not exists NYC_TAXI_DB_V2.RAW;
create schema if not exists NYC_TAXI_DB_V2.STAGING;
create schema if not exists NYC_TAXI_DB_V2.FINAL;

-- ==========================================================
-- 3️⃣ Recreate transformation warehouse
-- ==========================================================
create warehouse if not exists NYC_TAXI_WH_V2
  warehouse_size = 'MEDIUM'
  auto_suspend = 60
  auto_resume = true
  initially_suspended = true;

-- ==========================================================
-- 4️⃣ Recreate TRANSFORM role
-- ==========================================================
create role if not exists TRANSFORM;

-- ==========================================================
-- 5️⃣ Recreate DBT user
-- ==========================================================
create user if not exists DBT
  password = 'Password123!'
  default_role = TRANSFORM
  default_warehouse = NYC_TAXI_WH_V2
  must_change_password = true;

-- 6️⃣ Grant TRANSFORM role to DBT
grant role TRANSFORM to user DBT;

-- 7️⃣ Grant warehouse privileges
grant usage, operate on warehouse NYC_TAXI_WH_V2 to role TRANSFORM;

-- 8️⃣ Grant database and schema usage
grant usage on database NYC_TAXI_DB_V2 to role TRANSFORM;

grant usage on schema NYC_TAXI_DB_V2.RAW to role TRANSFORM;
grant usage on schema NYC_TAXI_DB_V2.STAGING to role TRANSFORM;
grant usage on schema NYC_TAXI_DB_V2.FINAL to role TRANSFORM;

-- ==========================================================
-- 9️⃣ Create RAW tables
-- ==========================================================
use role TRANSFORM;
use warehouse NYC_TAXI_WH_V2;
use database NYC_TAXI_DB_V2;

-- Temporary table RAW.BUFFER_YELLOW_TAXI_TRIPS_V2
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

-- Main table RAW.YELLOW_TAXI_TRIPS_V2
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
-- 10️⃣ Grant privileges to TRANSFORM role
-- ==========================================================
grant all privileges on all tables in schema NYC_TAXI_DB_V2.RAW to role TRANSFORM;
grant all privileges on future tables in schema NYC_TAXI_DB_V2.RAW to role TRANSFORM;

grant all privileges on all tables in schema NYC_TAXI_DB_V2.STAGING to role TRANSFORM;
grant all privileges on all tables in schema NYC_TAXI_DB_V2.FINAL to role TRANSFORM;

-- ==========================================================
-- ✅ Clean installation complete: RAW ready for ingestion
-- ==========================================================
