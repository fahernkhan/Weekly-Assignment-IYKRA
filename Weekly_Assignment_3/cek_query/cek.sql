WITH CTE1 as(
SELECT 
    * EXCEPT(
        ehail_fee,
        store_and_fwd_flag
    ),
    store_and_fwd_flag = 'Y' as store_and_fwd_flag,
    EXTRACT(DAY FROM lpep_pickup_datetime) as pickup_day,
    EXTRACT(MONTH FROM lpep_pickup_datetime) as pickup_month,
    EXTRACT(YEAR FROM lpep_pickup_datetime) as pickup_year FROM 
    `iconic-indexer-418610.taxi_tripdata.taxi_tripdata_raw` 
)

select distinct store_and_fwd_flag, count(*) from CTE1 group by store_and_fwd_flag