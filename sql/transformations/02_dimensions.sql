CREATE OR REPLACE TABLE mart.reporting_policy AS
SELECT cast(getvariable('cutoff') AS DATE) cutoff;
CREATE TABLE mart.dim_date(date_key DATE PRIMARY KEY, calendar_year INTEGER, month_number INTEGER,
month_start DATE, day_of_week INTEGER, day_name VARCHAR, is_complete_period BOOLEAN);
INSERT INTO mart.dim_date
SELECT cast(d AS DATE) date_key, year(d) calendar_year, month(d) month_number,
 cast(date_trunc('month',d) AS DATE) month_start, dayofweek(d) day_of_week,
 strftime(d,'%A') day_name,
 d < cast(getvariable('cutoff') AS DATE) is_complete_period
FROM generate_series((SELECT min(cast(invoice_ts AS DATE)) FROM staging.lines),
 (SELECT max(cast(invoice_ts AS DATE)) FROM staging.lines), INTERVAL 1 DAY) t(d);

CREATE TABLE mart.dim_customer(customer_key VARCHAR PRIMARY KEY, first_seen DATE, observed_country_count BIGINT);
INSERT INTO mart.dim_customer
SELECT customer_key, min(cast(invoice_ts AS DATE)) first_seen,
 count(DISTINCT country) observed_country_count
FROM staging.lines GROUP BY 1;

-- Latest observed description is a display attribute, not a historical category.
CREATE TABLE mart.dim_product(product_key VARCHAR PRIMARY KEY, product_name VARCHAR, description_variants BIGINT);
INSERT INTO mart.dim_product
SELECT stock_code product_key,
 arg_max(description,struct_pack(ts:=invoice_ts,id:=line_id)) product_name,
 count(DISTINCT description) description_variants
FROM staging.lines WHERE is_merchandise GROUP BY 1;

CREATE TABLE mart.dim_country(country_key VARCHAR PRIMARY KEY);
INSERT INTO mart.dim_country
SELECT DISTINCT country country_key FROM staging.lines;
