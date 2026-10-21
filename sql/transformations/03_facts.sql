CREATE OR REPLACE TABLE mart.fact_invoice_line (
 line_id BIGINT PRIMARY KEY,
 invoice_no VARCHAR NOT NULL,
 invoice_ts TIMESTAMP NOT NULL,
 date_key DATE REFERENCES mart.dim_date(date_key),
 customer_key VARCHAR REFERENCES mart.dim_customer(customer_key),
 product_key VARCHAR REFERENCES mart.dim_product(product_key),
 country_key VARCHAR REFERENCES mart.dim_country(country_key),
 quantity BIGINT, unit_price DECIMAL(18,4), amount_pence BIGINT,
 line_status VARCHAR CHECK(line_status IN ('sale','cancellation')),
 duplicate_ordinal BIGINT
);
INSERT INTO mart.fact_invoice_line
SELECT line_id,invoice_no,invoice_ts,cast(invoice_ts AS DATE),customer_key,stock_code,country,
 quantity,unit_price,amount_pence,line_status,duplicate_ordinal
FROM staging.lines WHERE line_status IN ('sale','cancellation');
CREATE INDEX idx_invoice ON mart.fact_invoice_line(invoice_no);
CREATE INDEX idx_customer ON mart.fact_invoice_line(customer_key);

-- Invoice/customer/country grain avoids silently collapsing inconsistent invoice attributes.
CREATE OR REPLACE TABLE mart.fact_order AS
SELECT invoice_no,customer_key,country_key,min(invoice_ts) invoice_ts,
 cast(min(invoice_ts) AS DATE) date_key,
 sum(amount_pence) gross_pence,count(*) line_count,
 count(DISTINCT product_key) distinct_products,sum(quantity) units
FROM mart.fact_invoice_line WHERE line_status='sale'
GROUP BY 1,2,3;

CREATE OR REPLACE VIEW mart.v_complete_lines AS
SELECT * FROM mart.fact_invoice_line WHERE date_key < (SELECT cutoff FROM mart.reporting_policy);
