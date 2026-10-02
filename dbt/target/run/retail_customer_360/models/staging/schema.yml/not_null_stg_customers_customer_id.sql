
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_id
from "retaildb"."public_retail_dbt_staging"."stg_customers"
where customer_id is null



  
  
      
    ) dbt_internal_test