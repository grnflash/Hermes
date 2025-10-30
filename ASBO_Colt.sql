/*
The below query does 3 important things for AS subscriptions:
1.	Extrapolates the subscriptpons out to a full 365 days (so not just the next event anymore). That’s the first CTE
	a.	Field called ext_NEXT_FULFILLMENT_DTTM
2.	Predicts the true “order_drop_date” which is when the AS orders will get placed/shipped out when accounting for AS pull fwd days that we are in at any given time
	a.	Field called order_drop_date
3.	Predicts the true ‘final’ AS qty that will get shipped based on a historical success rate. The AS qty in the subscription table can’t be taken as truth at face value as push-outs by customers and calcellations happen often.
	a.	Field called AS_qty_adj
*/




with subscription_extended as
(
select
sub.snapshot_date,
partnumber,
case when FULFILLMENT_FREQ_UOM in ('mon','month') then dateadd('month', FULFILLMENT_FREQ * cd.number,NEXT_FULFILLMENT_DTTM)
     when FULFILLMENT_FREQ_UOM in ('week') then dateadd('week', FULFILLMENT_FREQ * cd.number,NEXT_FULFILLMENT_DTTM)
     when FULFILLMENT_FREQ_UOM in ('day') then dateadd('day', FULFILLMENT_FREQ * cd.number,NEXT_FULFILLMENT_DTTM)
     else null end as ext_NEXT_FULFILLMENT_DTTM,
--PULL_FORWARD_DAYS,
--ext_NEXT_FULFILLMENT_DTTM - PULL_FORWARD_DAYS as order_drop_date,
sum(LINE_QUANTITY) as AS_qty
--case when order_drop_date between current_date+1 and current_date+1 then sum(LINE_QUANTITY) * 0.87 
--     when order_drop_date between current_date+2 and current_date+2 then sum(LINE_QUANTITY) * 0.83
--     when order_drop_date between current_date+3 and current_date+3 then sum(LINE_QUANTITY) * 0.79
--     when order_drop_date between current_date+4 and current_date+4 then sum(LINE_QUANTITY) * 0.76
--     when order_drop_date between current_date+5 and current_date+5 then sum(LINE_QUANTITY) * 0.63 
--     else sum(LINE_QUANTITY) * 0.6 end as AS_qty_adj
from (
        select
        snapshot_date,
        SUBSCRIPTION_ID,
        partnumber,
        NEXT_FULFILLMENT_DTTM::date as NEXT_FULFILLMENT_DTTM,
        FULFILLMENT_FREQ,
        lower(FULFILLMENT_FREQ_UOM) as FULFILLMENT_FREQ_UOM,
        sum(LINE_QUANTITY) as LINE_QUANTITY
        from edldb.cdm.subscription_lines_snapshot sub 
        where 1=1
        and snapshot_date = (select max(snapshot_date) from edldb.cdm.subscription_lines_snapshot where snapshot_date <= current_date)
        and status = 'Active'
        and skip_item_next = 'FALSE'
        and one_time_flag = 'FALSE'
--        and lower(fulfillment_freq_uom) in ('week', 'mon', 'month', 'day')
        and fulfillment_freq_uom is not null
        and NEXT_FULFILLMENT_DTTM::date >= current_date+1
--        and partnumber = '151269'
--        and SUBSCRIPTION_LINE_ID in ('107936736','400113091922')
        group by all
        ) sub
cross join (
        select
        common_date_dttm - current_date as number,
        from edldb.chewybi.common_date cd
        where 1=1
        and common_date_dttm between current_date and current_date+365
        ) cd
--cross join (
--        select
--        PULL_FORWARD_DAYS 
--        from EDLDB.SC_SANDBOX.AS_PULL_FORWARD_EVENTS
--        where 1=1
--        and event_date = (select max(event_date) from EDLDB.SC_SANDBOX.AS_PULL_FORWARD_EVENTS where event_date <= current_date)
--        ) pfd
        
where 1=1
and case when FULFILLMENT_FREQ_UOM in ('mon','month') then dateadd('month', FULFILLMENT_FREQ * cd.number,NEXT_FULFILLMENT_DTTM)
     when FULFILLMENT_FREQ_UOM in ('week') then dateadd('week', FULFILLMENT_FREQ * cd.number,NEXT_FULFILLMENT_DTTM)
     when FULFILLMENT_FREQ_UOM in ('day') then dateadd('day', FULFILLMENT_FREQ * cd.number,NEXT_FULFILLMENT_DTTM)
     else null end between current_date+1 and current_date+370
--and order_drop_date between current_date+1 and current_date+365
--and partnumber = '46861'
--and SUBSCRIPTION_LINE_ID = '107936736'
--and partnumber = '1000037020'
group by all
)

select
sub.snapshot_date,
partnumber as product_part_number,
ext_NEXT_FULFILLMENT_DTTM,
PULL_FORWARD_DAYS,
--order_drop_date,
ext_NEXT_FULFILLMENT_DTTM - PULL_FORWARD_DAYS as order_drop_date,
AS_qty,
--AS_qty_adj,
case when order_drop_date between current_date+1 and current_date+1 then sum(AS_qty) * 0.87 
     when order_drop_date between current_date+2 and current_date+2 then sum(AS_qty) * 0.83
     when order_drop_date between current_date+3 and current_date+3 then sum(AS_qty) * 0.79
     when order_drop_date between current_date+4 and current_date+4 then sum(AS_qty) * 0.76
     when order_drop_date between current_date+5 and current_date+5 then sum(AS_qty) * 0.63 
     else sum(AS_qty) * 0.6 end as AS_qty_adj

from subscription_extended sub
left join (
        select
        day_date_daily,
        pfe.event_date,
        PULL_FORWARD_DAYS,
        action
        from EDLDB.SC_SANDBOX.AS_PULL_FORWARD_EVENTS pfe
        join (
                select
                day_date_daily,
                max(event_date) as event_date
                from EDLDB.SC_SANDBOX.AS_PULL_FORWARD_EVENTS
                cross join (select distinct common_date_dttm as day_date_daily from edldb.chewybi.common_date cd where common_date_dttm between current_date and current_date+365) cd
                where 1=1
                and event_date <= day_date_daily
                group by all
                ) ddd on ddd.event_date = pfe.event_date
        where 1=1
        group by all
        ) pfe on pfe.day_date_daily = sub.ext_NEXT_FULFILLMENT_DTTM - PULL_FORWARD_DAYS
    
where 1=1
and order_drop_date between current_date+1 and current_date+365
and ext_NEXT_FULFILLMENT_DTTM - PULL_FORWARD_DAYS <> pfe.event_date --needed since ASPFR days are handled seperately and without this itll cause duplicates
--and product_company_description = 'Chewy'
--and partnumber = '46861'
--and partnumber = '64893'
--and partnumber = '1000037020'
--and order_drop_date = '11/19/2025'

group by all
;
