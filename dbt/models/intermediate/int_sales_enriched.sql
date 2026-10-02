with sales as (

    select *
    from {{ ref('stg_sales') }}

),

customers as (

    select *
    from {{ ref('stg_customers') }}

),

products as (

    select *
    from {{ ref('stg_products') }}

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