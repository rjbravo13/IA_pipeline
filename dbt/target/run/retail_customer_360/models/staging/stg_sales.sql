
  create view "retaildb"."public_retail_dbt_staging"."stg_sales__dbt_tmp"
    
    
  as (
    select
    sale_id,
    customer_id,
    product_id,
    timestamp,
    quantity,
    unit_price
from retail_staging.sales
  );