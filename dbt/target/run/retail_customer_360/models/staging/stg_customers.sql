
  create view "retaildb"."public_retail_dbt_staging"."stg_customers__dbt_tmp"
    
    
  as (
    select
    customer_id,
    signup_date,
    city,
    segment
from retail_staging.customers
  );