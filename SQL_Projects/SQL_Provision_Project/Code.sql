--Postgres Code
--Create  nall

drop table if exists npolicy;
drop table if exists npolicy_transactions;
drop table if exists nportfolio;
drop table if exists nsales_org;
select * into npolicy_transactions from policy_transactions;
select * into npolicy from policy;
select * into nportfolio from portfolio;
select * into nsales_org from sales_org;
-- edit names of key_policy and key_ss_org in order to select * without dupcliate column with the same name
ALTER TABLE pro.nsales_org RENAME COLUMN key_ss_org TO key_ss_or;
ALTER TABLE pro.npolicy RENAME COLUMN key_policy TO key_polic;
ALTER TABLE pro.npolicy RENAME COLUMN vld_fm_tms TO vld_fm_tm;
ALTER TABLE pro.npolicy RENAME COLUMN vld_to_tms TO vld_to_tm;
--join all tables to a big table, in order to have all information in one place without having to do joins everytime you need to referance something
drop table if exists nall;
CREATE TABLE nall AS
SELECT *
FROM npolicy as p3
	left join nportfolio as p1
	on p1.key_policy = p3.key_polic
	left join nsales_org as p2
	ON p2.key_ss_or= p1.key_ss_org
	left join npolicy_transactions as p4
	on p4.po_no = p3.ext_refr;
--Create  NTRIm


drop table if EXISTS before_null_removals;
drop table if exists temp_ntrim;
drop table if exists ntrim;
select * into ntrim from nall;
--this whole next section is deleting from the big table all rows which does not fullfill the criteria
with a as
(
	select
	ext_refr ,
	count(distinct pev_portfolioresponsiblecode)
	from nall
	group by ext_refr
	having count(distinct pev_portfolioresponsiblecode)>=2
)
delete from ntrim
where ext_refr in (select ext_refr from a);
--this is deleting based on Criteria 3
delete from ntrim
where ext_refr in
		(select ext_refr
		from ntrim
		where payment_status = 'Not Paid'
		)
;
--this is deleting based on Criteria 1
delete FROM ntrim
where ext_refr IN (SELECT ext_refr
	FROM ntrim
	WHERE pev_portfolioresponsiblecode not IN('WILDWEST-2','WILDWEST-3')
		or pev_portfolioresponsiblecode is NULL) ;
--this is deleting based on Criteria 4
	
DELETE FROM ntrim
where ext_refr IN (SELECT ext_refr
	FROM ntrim
	WHERE CAST(SUBSTRING(product_name, 8) as INT) in(9,10,11,12));
--this is deleting based on Criteria 5 	
delete from ntrim
where ext_refr IN (SELECT ext_refr
	FROM ntrim
	WHERE not(org_lvl_nm IN ('Outbound','Internet') and pev_portfolioresponsiblecode = 'WILDWEST-3' )
	AND not(org_lvl_nm = 'Inbound' and pev_portfolioresponsiblecode = 'WILDWEST-2' ));
--Add a table for sales month and payment month, also DELETING rows where payment date happens before salesdate to happens when the sales happend
alter table ntrim
add column sale_month  date;
update ntrim set sale_month =date_trunc('Month', sales_date);
alter table ntrim
add column pay_month  date;
update ntrim set pay_month =date_trunc('Month', paymentdate);
delete from ntrim
where ext_refr IN (SELECT ext_refr
	FROM ntrim
	WHERE sales_date> paymentdate);
delete from ntrim
where sales_date>='2024-09-01';
delete from ntrim
where pay_month>='2024-09-01';
--Alter the annual premium to a number
update ntrim set annual_premium=left(annual_premium,position(',' in annual_premium)-1);
ALTER TABLE pro.ntrim ALTER COLUMN annual_premium TYPE int4 USING annual_premium::int4;
--drop  tables with unnecessary information duplicate information
ALTER TABLE ntrim
DROP COLUMN pev_createdat;
ALTER TABLE ntrim
DROP COLUMN pev_id;
select distinct * into temp_ntrim from ntrim;
drop table ntrim;
select * into ntrim from temp_ntrim;
drop table temp_ntrim;
select * into before_null_removals from ntrim;
delete from ntrim
where annual_premium is NULL;
CREATE table temp_ntrim as
select
			MAX(pln_end_dt) over(partition by ext_refr)-incp_dt as days_valid,
			case when agrm_sts_cd = 'ACTIVE' then date_trunc('day',vld_to_tm-vld_fm_tm)
			else date_trunc('day',Max(pln_end_dt) over(partition by ext_refr) -vld_fm_tm)end as time
			,*
from ntrim;
drop table ntrim;
select * into ntrim from temp_ntrim;
drop table temp_ntrim;
CREATE TABLE temp_ntrim AS
with a as(select ext_refr as ext_ref,row_number() over(order by MIN(paymentdate),MIN(sales_date))
from ntrim
group by ext_ref)
select *
from ntrim as n
left join a as a
ON n.ext_refr=a.ext_ref;
drop table ntrim;
select * into ntrim from temp_ntrim;
drop table temp_ntrim;
CREATE TABLE temp_ntrim AS
select 	
	case
		when row_number>=1501 then annual_premium*0.14*(days_valid-extract(day from date_trunc('day',vld_fm_tm-incp_dt)))/days_valid
		ELSE annual_premium*0.12*(days_valid-extract(day from date_trunc('day',vld_fm_tm-incp_dt)))/days_valid		
	end as revenue,
	*
from ntrim;
drop table ntrim;
select * into ntrim from temp_ntrim;
drop table temp_ntrim;
CREATE TABLE temp_ntrim AS(
select case when date(vld_to_tm)<>rnew_dt then revenue-extract(day from time)/days_valid*revenue
	when cncl_dt is not null then extract(day from time)/days_valid*revenue
	else NULL end as claw,*
from ntrim);
drop table ntrim;
select * into ntrim from temp_ntrim;
drop table temp_ntrim;
alter table ntrim
add column claw_month date;
update ntrim set claw_month =case when claw>0  and agrm_sts_cd = 'ACTIVE' then date_trunc('Month', vld_to_tm)
when agrm_sts_cd = 'CANCEL' then date_trunc('Month', vld_fm_tm)
else null end;
select
	pay_month,
	Count(*),
	round(sum(revenue),2)
from ntrim
group by pay_month
order by 1;
select
	claw_month,
	Count(*),
	round(sum(claw),2)
from ntrim
group by claw_month
order by 1;

select *
from ntrim;


--Create strim
drop table if exists temp_strim;
drop table if exists strim;
select * into strim from nall;
with a as
(
	select
	ext_refr ,
	count(distinct pev_portfolioresponsiblecode)
	from nall
	group by ext_refr
	having count(distinct pev_portfolioresponsiblecode)>=2
)
delete from strim
where ext_refr in (select ext_refr from a);
delete FROM strim
where ext_refr IN (SELECT ext_refr
	FROM strim
	WHERE pev_portfolioresponsiblecode not IN('WILDWEST-2','WILDWEST-3')
		or pev_portfolioresponsiblecode is NULL) ;
	
DELETE FROM strim
where ext_refr IN (SELECT ext_refr
	FROM strim
	WHERE CAST(SUBSTRING(product_name, 8) as INT) in(9,10,11,12));
	
delete from strim
where ext_refr IN (SELECT ext_refr
	FROM strim
	WHERE not(org_lvl_nm IN ('Outbound','Internet') and pev_portfolioresponsiblecode = 'WILDWEST-3' )
	AND not(org_lvl_nm = 'Inbound' and pev_portfolioresponsiblecode = 'WILDWEST-2' ));
alter table strim
add column sale_month  date;
update strim set sale_month =date_trunc('Month', sales_date);
alter table strim
add column pay_month  date;
update strim set pay_month =date_trunc('Month', paymentdate);
delete from strim
where ext_refr IN (SELECT ext_refr
	FROM strim
	WHERE sales_date>paymentdate);
delete from strim
where sales_date>='2024-09-01';
update strim set annual_premium=left(annual_premium,position(',' in annual_premium)-1);
ALTER TABLE pro.strim ALTER COLUMN annual_premium TYPE int4 USING annual_premium::int4;
ALTER TABLE strim
DROP COLUMN pev_createdat;
ALTER TABLE strim
DROP COLUMN pev_id;
select distinct * into temp_strim from strim;
drop table strim;
select * into strim from temp_strim;
drop table temp_strim;
delete from strim
where annual_premium is NULL;
CREATE table temp_strim as
select
			MAX(pln_end_dt) over(partition by ext_refr)-incp_dt as days_valid,
			case when agrm_sts_cd = 'ACTIVE' then date_trunc('day',vld_to_tm-vld_fm_tm)
			else date_trunc('day',Max(pln_end_dt) over(partition by ext_refr) -vld_fm_tm)end as time
			,*
from strim;
drop table strim;
select * into strim from temp_strim;
drop table temp_strim;
CREATE TABLE temp_strim AS
with a as(select ext_refr as ext_ref,row_number() over(order by MIN(paymentdate),MIN(sales_date))
from strim
group by ext_ref)
select *
from strim as n
left join a as a
ON n.ext_refr=a.ext_ref;
drop table strim;
select * into strim from temp_strim;
drop table temp_strim;
CREATE TABLE temp_strim AS
select 	
	case
		when row_number>=1501 then annual_premium*0.14*(days_valid-extract(day from date_trunc('day',vld_fm_tm-incp_dt)))/days_valid
		ELSE annual_premium*0.12*(days_valid-extract(day from date_trunc('day',vld_fm_tm-incp_dt)))/days_valid		
	end as revenue,
	*
from strim;
drop table strim;
select * into strim from temp_strim;
drop table temp_strim;
CREATE TABLE temp_strim AS(
select case
	when date(vld_to_tm)<>rnew_dt then revenue-extract(day from time)/days_valid*revenue
	when cncl_dt is not null then extract(day from time)/days_valid*revenue
	else NULL end as claw,
	*
from strim);
drop table strim;
select * into strim from temp_strim;
drop table temp_strim;
alter table strim
add column claw_month date;
update strim set claw_month =case when claw>0  and agrm_sts_cd = 'ACTIVE' then date_trunc('Month', vld_to_tm)
when agrm_sts_cd = 'CANCEL' then date_trunc('Month', vld_fm_tm)
else null end;
select *
from strim


--ALL ANALYSIS IN strim

with A as
(
	select
		fld_rep_cd as fld_a,
		count(*) as salec_month,
		ROUND(avg (revenue),2)as saleavg_month,
		ROund(sum(revenue),2) as salesum_month
	from strim
	where sale_month ='2024-08-01' -- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd
)
,B as
(
	select
		fld_rep_cd as fld_b,
		count(*) as paidc_year,
		ROund(avg(revenue),2)as paidavg_year,
		ROund(sum(revenue),2) as paidsum_year
	from ntrim
	where pay_month <='2024-08-01'-- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd
)
,C as
(
	select
		fld_rep_cd as fld_c,
		count(*) as salec_year,
		ROund(sum(revenue),2) as salesum_year,
		ROUND(AVG(extract(month from sale_month)),2) as avgsale_month
	from strim
	where sale_month <='2024-08-01'-- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd
)
,D as
(
	select
		fld_rep_cd as fld_D,
		count(*) as clawc_year,
		round(sum(claw),2) as clawsum_year
	from strim
	where claw_month <='2024-08-01'
	and agrm_sts_cd='CANCEL'-- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd
)
select
	fld_a,
	salec_month,
	salesum_month,
	salec_year,
	paidc_year,
	avgsale_month,
	coalesce (ROUND((paidc_year*100.0)/(salec_year),2),0) as percent_paid,
	coalesce (ROUND((CLAWc_year*100.0)/(salec_year),2),0) as percent_CLAW,
	clawc_year,
	salesum_year,
	paidsum_year,
	clawsum_year	
from a
left join b
on a.fld_a = b.fld_b
left join C
on a.fld_a = c.fld_c
left join D
on a.fld_a = d.fld_d;


with A as
(select
		fld_rep_cd as fld_a,
		count(*) as salec_month,
		ROUND(avg (revenue),2)as saleavg_month,
		ROund(sum(revenue),2) as salesum_month
	from strim
	where sale_month ='2024-08-01' -- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd)
select
	fld_a,
	salesum_month	
from a
order by 2 desc
limit 5;


with a as
(select count(*) as clawc_year
from strim
	where claw_month <='2024-08-01'
	and agrm_sts_cd='CANCEL')
,b as		
(select count(distinct (ext_refr)) as salec_year	
	from strim
	where sale_month <='2024-08-01')
select
(select clawc_year from a),
salec_year,
ROUND((select clawc_year*100.0 from a)/salec_year,2) as percent_CLAW
from b;
	
select *
from before_null_removals;


with a as
(
	select
		fld_rep_cd as fld_a,
		count(*) as salec_year,
		ROund(sum(revenue),2) as salesum_year,
		ROUND(AVG(extract(month from sale_month)),2) as avgsale_month
	from strim
	where sale_month <='2024-08-01'-- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd
)
,b as
(
	select
		fld_rep_cd as fld_b,
		count(*) as clawc_year,
		round(sum(claw),2) as clawsum_year
	from strim
	where claw_month <='2024-08-01'
	and agrm_sts_cd='CANCEL'-- CHANGE THIS TO CURRENT MONTH
	group by fld_rep_cd
)
select fld_a,
	salec_year,
	clawc_year,	
	coalesce (ROUND((CLAWc_year*100.0)/(salec_year),2),0) as percent_CLAW
from a
left join b
on a.fld_a = b.fld_b
where coalesce (ROUND((CLAWc_year*100.0)/(salec_year),2),0)>5
order by 4 DESC;