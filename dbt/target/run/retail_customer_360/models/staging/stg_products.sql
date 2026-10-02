
  create view "retaildb"."public_retail_dbt_staging"."stg_products__dbt_tmp"
    
    
  as (
    select
    product_id,
    category,
    brand,
    description,
    price
from retail_staging.products
  );