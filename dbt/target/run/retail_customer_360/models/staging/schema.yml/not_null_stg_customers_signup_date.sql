
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select signup_date
from "retaildb"."public_retail_dbt_staging"."stg_customers"
where signup_date is null



  
  
      
    ) dbt_internal_test