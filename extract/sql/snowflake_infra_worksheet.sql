SNOWFLAKE_LEARNING_DB-- 1. Database & Schemas
create database if not exists NYC_TAXI_DB;
create schema if not exists NYC_TAXI_DB.SCHEMA_RAW;


-- 2. Warehouse de transformation
create warehouse if not exists NYC_TAXI_WH
  warehouse_size = 'MEDIUM'
  auto_suspend = 60
  auto_resume = true;

-- 3. Rôle TRANSFORM (pour DBT)
create role if not exists TRANSFORM;

-- 4. Création de l'utilisateur DBT (si pas encore fait)
-- ⚠️ Utilise un mot de passe temporaire ici
create user if not exists DBT
  password = 'Password123!'
  default_role = TRANSFORM
  default_warehouse = NYC_TAXI_WH
  must_change_password = true;

-- 5. Grant du rôle à l'utilisateur DBT
grant role TRANSFORM to user DBT;

-- 6. Permissions : usage warehouse
grant usage, operate on warehouse NYC_TAXI_WH to role TRANSFORM;

-- 7. Permissions : accès base
grant usage on database NYC_TAXI_DB to role TRANSFORM;

-- 8. Permissions : schémas
grant usage on schema NYC_TAXI_DB.SCHEMA_RAW to role TRANSFORM;
grant usage on schema NYC_TAXI_DB.SCHEMA_STAGING to role TRANSFORM;
grant usage on schema NYC_TAXI_DB.SCHEMA_FINAL to role TRANSFORM;

-- 9. Permissions : lecture RAW, écriture STAGING et FINAL
grant select on all tables in schema NYC_TAXI_DB.SCHEMA_RAWRAW to role TRANSFORM;
grant select on future tables in schema NYC_TAXI_DB.SCHEMA_RAWRAW to role TRANSFORM;

grant create table, create view on schema NYC_TAXI_DB.SCHEMA_STAGING to role TRANSFORM;
grant create table, create view on schema NYC_TAXI_DB.SCHEMA_FINAL to role TRANSFORM;
