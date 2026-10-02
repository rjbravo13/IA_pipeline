with sales as (

    select *
    from {{ ref('int_sales_enriched') }}

),

customer_metrics as (

    select
        customer_id,

        max(city) as city,
        max(segment) as segment,
        max(signup_date) as signup_date,

        count(distinct sale_id) as total_purchases,

        sum(quantity) as total_quantity,

        sum(total_line) as total_spent,

        avg(total_line) as average_ticket,

        max(timestamp) as last_purchase_date,

        count(distinct product_id) as unique_products

    from sales

    group by customer_id

)

select
    customer_id,
    city,
    segment,
    signup_date,
    total_purchases,
    total_quantity,
    total_spent,
    average_ticket,
    last_purchase_date,
    unique_products

from customer_metrics