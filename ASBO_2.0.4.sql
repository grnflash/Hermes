/*** Tier1 ASBO Query, 2025-10-23 ***/
with a as (
    select p.product_part_number as SKU
        , p.product_name as Description, parent_company as "Parent Company", product_category_level3 as "Product Category Level 3"
    from chewybi.products p
    where 1=1
		/*** Select a Parent Vendor Below ***/
		--AND LOWER(parent_company) IN ('blue buffalo company ltd')
		--AND LOWER(parent_company) IN ('hill''s pet nutrition sales')
		AND LOWER(parent_company) IN ('mars')
		--AND LOWER(parent_company) IN ('natural balance', 'ethos pet nutrition llc', 'canidae')
		--AND LOWER(parent_company) IN ('nestle purina','nestle purina vet')
		--AND LOWER(parent_company) IN ('post')
		--AND LOWER(parent_company) IN ('royal canin')
		--AND LOWER(parent_company) IN ('smucker''s retail foods')
		--AND LOWER(parent_company) IN ('wellness pet')
        AND p.product_discontinued_flag = false
        AND p.product_status = 'Active'
        AND p.PRODUCT_COMPANY_DESCRIPTION = 'Chewy'
)
,l as (
    select
        ilv.product_part_number
        ,ilv.vendor_product_part_number as VP
    from chewybi.item_location_vendor ilv
    where ilv.vendor_distribution_method = 'DIRECT'
        and ilv.snapshot_date between CURRENT_DATE-360 and current_date
        and ilv.product_part_number in (select a.SKU from a)
        AND ilv.primary_vendor_flag = TRUE
        AND ilv.vendor_distribution_method = 'DIRECT'
        AND ilv.product_vendor_location_disabled_flag = FALSE
    group by 1,2
)
,b as (
    Select
        inv.product_part_number
        , SUM(zeroifnull(inv.bo_sellable_quantity)) as OH
    from chewybi.inventory_snapshot_immutable inv
    left join sc_sandbox.item_attribs t on t.product_part_number = inv.product_part_number
        -- was sandbox_supply_chain.item_attribs t; changed to edldb.sc_sandbox (though domain will already be narrowed to edldb in this scope)
        --sandbox_supply_chain.item_attribs is Vertica! appears a direct port of sandbox_supply_chain in 'edldb.sc_sandbox' in Snowflake
        --also appears to have all the correct fields listed, though I didn't check consistency, range, or wholeness.
        where inv.inventory_snapshot_date = current_date
        and inv.location_code in (select location_code from chewybi.locations where fulfillment_active = true and product_company_description = 'Chewy' and location_warehouse_type in (1,0))
        and inv.product_part_number in (select a.SKU from a)
    group by 1
)
, g as (
    select
        proc.product_part_number,
        sum(zeroifnull(last_version_quantity)) as OO
    from  chewybi.procurement_document_product_measures proc
    join  chewybi.locations loc on loc.location_key = proc.location_key
    left join a 
        on proc.product_part_number = a.SKU
    where document_type = 'Purchase'
        and deleted_by_users = false
        and location_code in (select location_code from chewybi.locations where fulfillment_active = true and product_company_description = 'Chewy' and location_warehouse_type in (1,0))
        and proc.product_part_number in (select a.SKU from a)
        and document_requested_delivery_dttm::date >= current_date-1
    group by 1
)

/*** below is the original CTE 'd' from the original ASBO.sql file ***/
/*** maintaining for context, but bringing the corrected foreacst ****/
/*** CTE from the improved inventory query below ***/
-- , d as (
--     select
--         prod.product_part_number
--         ,(sum(isnull(forecast_snapshot_manual_forecast_quantity,forecast_snapshot_statistical_forecast_quantity))) as Forecast
--     from  chewybi.forecast_snapshot snp
--     join  chewybi.products prod
--         on prod.product_key = snp.product_key
--     left join a on prod.product_part_number = a.SKU
--         where snp.forecast_snapshot_forecast_dt::date between current_date and current_date+29
--         and forecast_snapshot_snapshot_dt::date in (current_date)
--         and prod.product_part_number in (select a.SKU from a)
--     group by 1
-- )
/*** improved inventory query below ***/
/*** it's possible that this will need to get ***/
/*** the item_fc_day_outflow update per the *****/
/*** Nestle_Litter_Forecast.sql example in ******/
/*** Knime_ORG_Queries folder ***/
, d as (
        SELECT
                p.PRODUCT_PART_NUMBER as product_part_number,
                SUM(DW_FCST) as Forecast
        FROM edldb.sc_sandbox.DW_fcst_item_day_network_colt c
        JOIN edldb.chewybi.products p ON c.PRODUCT_PART_NUMBER = p.PRODUCT_PART_NUMBER
        WHERE 1=1
                AND p.product_type = 'Item'
                AND p.product_part_number <> 'PLACEHOLDER'
                AND p.product_company_description = 'Chewy'
                AND p.product_discontinued_flag = false
                AND SNAPSHOT_DATE = CURRENT_DATE - 1
                AND c.FORECAST_DATE between current_date and current_date + 29
                AND p.PRODUCT_PART_NUMBER in (select a.SKU from a)
        GROUP BY 1
)

-- ============================================================================
-- CTE 'e' - AUTOSHIP DEMAND & BACKORDER ANALYSIS (INTEGRATED SCORECARD-BASED LOGIC)
-- ============================================================================
-- UPDATED FROM: chewybi.subscription_order_lines (DEPRECATED)
-- NEW SOURCE: sc_autoship_sandbox.as_sc_autoship_backorders (SNOWFLAKE COMPATIBLE)
-- 
-- KEY CHANGES:
-- 1. Data Source: Changed from subscription_order_lines to as_sc_autoship_backorders
-- 2. Business Logic: Uses autoship_units for demand and backorder_units for backorder analysis
-- 3. Time Windows: AS Demand from last 30 days, Backorder Units from 7/30 day trailing windows
-- 4. Integration: Combines autoship demand and backorder metrics in single CTE
-- 
-- CROSS-CORRELATION VALIDATION:
-- - autoship_units (last 30 days) correlates with AS Demand (forward-looking 30-days)
-- - backorder_units (trailing windows) matches AS Backorder Units patterns
-- - Time windows align with Knime_ASBO_Ethos.csv output structure
-- ============================================================================
, e as (
    select
        asab.product_part_number,
        -- AS Demand: Use autoship_units from last 30 days (correlates with subscription fulfillment)
        sum(case when order_placed_date between current_date - 30 and current_date 
                 then autoship_units else 0 end) as AS_Demand,
        
        -- Backorder Units: Use backorder_units from historical periods
        sum(case when order_placed_date between current_date - 7 and current_date 
                 then backorder_units else 0 end) as BO_Units_7d,
        sum(case when order_placed_date between current_date - 30 and current_date 
                 then backorder_units else 0 end) as BO_Units_30d,
        
         -- Weeks with ASBO: Count distinct weeks with backorders in last 30 days (aligned with BO_Units_30d)
         count(distinct case when order_placed_date between current_date - 30 and current_date 
                            and backorder_units > 0
                            then date_trunc('week', order_placed_date) end) as Weeks_with_ASBO
    from sc_autoship_sandbox.as_sc_autoship_backorders asab
    join (
        -- Enhanced product filtering using SCard-based approach
        select 
            p.snapshot_date,
            p.product_part_number
        from EDLDB.CHEWYBI.PRODUCT_LIFECYCLE_SNAPSHOT p
        left join chewybi.products pr
            on p.product_part_number = pr.product_part_number
        left join chewybi.vendor_agreement_line val
            on p.product_part_number = val.product_part_number
            and val.active_agreement = 1
        where ((not p.product_discontinued_flag and p.PRODUCT_REPLENISHMENT_STATUS in ('Replenishable','One-Time Buy')) or p.product_published_flag)
            and p.product_company_description = 'Chewy'
            and pr.parent_company in ('SMUCKER''S RETAIL FOODS')  -- Match our target company
            and lower(p.product_type) = 'item'
            and p.snapshot_date between date_trunc('week',current_date) - interval '105 week' and current_date - 1
            and p.product_merch_classification1 not in ('Programs', 'Virtual Bundle', 'Gift Cards')
            and p.product_merch_classification1 is not null
            and p.product_dropship_flag = False
            and val.vendor_number is not null
    ) bp
        on asab.product_part_number = bp.product_part_number
        and asab.order_placed_date::date = bp.snapshot_date::date
    group by asab.product_part_number
)
-- ============================================================================
-- CTE 'f' - PDP PERFORMANCE (UPDATED TO SNOWFLAKE SOURCE)
-- ============================================================================
-- UPDATED FROM: chewybi.merch_performance_snapshot (DEPRECATED)
-- NEW SOURCE: mrch.merch_performance_snapshot_pharmacy (SNOWFLAKE COMPATIBLE)
-- 
-- KEY CHANGES:
-- 1. Data Source: Changed from chewybi.merch_performance_snapshot to mrch.merch_performance_snapshot_pharmacy
-- 2. Business Logic: Maintains same PDP calculation logic
-- 3. Timeframe: Maintains 30-day trailing window
-- ============================================================================
, f as (
        select 
                product_part_number
                ,(sum(zeroifnull(OutofStock_Distinct_PDP_Views)) / sum(zeroifnull(Distinct_PDP_Views))) as PDP_Percent
        from mrch.merch_performance_snapshot_pharmacy i
        where product_part_number in (
                select a.SKU
                from a
        )
                and i.activity_date::date between current_date - 30 and current_date
                and Distinct_PDP_Views <> 0
        group by 1
)
-- ============================================================================
-- CTE 'h' - FILL RATE (UPDATED TO SNOWFLAKE SOURCE)
-- ============================================================================
-- UPDATED FROM: sandbox_supply_chain.vendor_compliance_edi_document_metrics (VERTICA)
-- NEW SOURCE: EDLDB.CHEWYBI.DM_SUPPLYCHAIN_PROCUREMENT_METRICS (SNOWFLAKE)
-- 
-- KEY CHANGES:
-- 1. Data Source: Changed from Vertica sandbox_supply_chain to Snowflake EDLDB.CHEWYBI
-- 2. Business Logic: Maintains same fill rate calculation (Capped_Received_Qty / Orig_Order_Qty)
-- 3. Timeframe: Maintains 30-day trailing window
-- 4. Table Name: Updated to DM_SUPPLYCHAIN_PROCUREMENT_METRICS
-- ============================================================================
, h as (
        Select
                inv.product_part_number
                ,case when sum(Orig_Order_Qty) = 0 then 0 else (sum (Capped_Received_Qty) / sum(Orig_Order_Qty)) end as Fill_Rate
        from EDLDB.CHEWYBI.DM_SUPPLYCHAIN_PROCUREMENT_METRICS inv
        left join chewybi.products p
                on (inv.product_part_number = p.product_part_number)
        where
        date(min_AP_closed_date) between current_date - 30 AND current_date
                and inv.product_part_number in (
                        select a.SKU
                        from a
                )
        group by 1
)
select 
    a.SKU, 
    l.VP as "Vendor Number",
    a.Description,
    a."Parent Company",
    a."Product Category Level 3", 
    round(b.OH,0)::int as "OH Units", 
    round(g.OO,0)::int as "OO Units", 
    round(e.AS_Demand,0)::int as "AS Demand (forward looking 30 days)", 
    round(e.BO_Units_7d,0)::int as "AS Backorder Units (last 7-days)",
    round(e.BO_Units_30d,0)::int as "AS Backorder Units (last 30-days)",
    round(e.Weeks_with_ASBO,0)::int as "Weeks with ASBO",
    round(f.PDP_Percent*100,0)::int ||'%' as "PDP % (trailing 30 day average)", 
    round(h.Fill_Rate*100,0)::int ||'%' as "Fill-Rate % (trailing 30 day average)",
    CASE WHEN d.Forecast <> 0 THEN (b.OH / (d.Forecast/30))::int ELSE 0 END as "DOS"
from a 
left join b on a.SKU = b.product_part_number 
left join d on a.SKU = d.product_part_number 
left join e on a.SKU = e.product_part_number 
left join f on a.SKU = f.product_part_number 
left join g on a.SKU = g.product_part_number 
left join h on a.SKU = h.product_part_number 
left join l on a.SKU = l.product_part_number
group by
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
;