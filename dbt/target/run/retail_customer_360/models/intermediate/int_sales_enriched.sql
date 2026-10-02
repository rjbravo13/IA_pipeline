
  
    

  create  table "retaildb"."public_retail_dbt_intermediate"."int_sales_enriched__dbt_tmp"
  
  
    as
  
  (
    with sales as (

    select *
    from "retaildb"."public_retail_dbt_staging"."stg_sales"

),

customers as (

    select *
    from "retaildb"."public_retail_dbt_staging"."stg_customers"

),

products as (

    select *
    from "retaildb"."public_retail_dbt_staging"."stg_products"

)

select
    s.sale_id,
    s.customer_id,
    s.product_id,
    s.timestamp,
    s.quantity,
    s.unit_price,

    c.signup_date,
    c.city,
    c.segment,

    p.category,
    p.brand,
    p.description,
    p.price as product_price,

    s.quantity * s.unit_price as total_line

from sales s

left join customers c
    on s.customer_id = c.customer_id

left join products p
    on s.product_id = p.product_id
  );
  