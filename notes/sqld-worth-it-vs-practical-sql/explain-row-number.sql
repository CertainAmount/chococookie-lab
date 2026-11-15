\pset pager off
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  id          bigserial PRIMARY KEY,
  customer_id int         NOT NULL,
  ordered_at  timestamptz NOT NULL,
  amount      int         NOT NULL
);
SELECT setseed(0.42);
INSERT INTO orders (customer_id, ordered_at, amount)
SELECT (random() * 19999)::int + 1,
       timestamptz '2025-01-01' + random() * interval '365 days',
       (random() * 100000)::int
FROM generate_series(1, 200000);
ANALYZE orders;

-- 캡처 대상: 인덱스 전
EXPLAIN (ANALYZE, COSTS OFF, BUFFERS OFF)
SELECT *
FROM (
  SELECT o.*,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at DESC) AS rn
  FROM orders o
) t
WHERE rn = 1;

-- 연구 노트용: 인덱스 후
CREATE INDEX orders_customer_recent ON orders (customer_id, ordered_at DESC);
ANALYZE orders;
EXPLAIN (ANALYZE, COSTS OFF, BUFFERS OFF)
SELECT *
FROM (
  SELECT o.*,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at DESC) AS rn
  FROM orders o
) t
WHERE rn = 1;
