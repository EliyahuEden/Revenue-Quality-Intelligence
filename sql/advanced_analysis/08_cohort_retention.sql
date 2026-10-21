-- Product/CRM: monthly active-purchase retention, not survival or contractual churn.
SELECT * FROM mart.cohort_retention ORDER BY cohort_month,month_age;
