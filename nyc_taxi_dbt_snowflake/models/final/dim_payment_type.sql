{{ config(materialized='table', schema='FINAL') }}

SELECT 1 AS payment_type_id, 'Credit card' AS payment_type_label UNION ALL
SELECT 2, 'Cash'                                                   UNION ALL
SELECT 3, 'No charge'                                              UNION ALL
SELECT 4, 'Dispute'                                                UNION ALL
SELECT 5, 'Unknown'
