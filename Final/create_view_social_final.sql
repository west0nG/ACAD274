-- CREATE VIEW for social_final.csv
-- This view is formatted to match the price_data table structure for easy comparison
-- Price table structure: id, coin_id, ts, open_price, high_price, low_price, close_price, volume_usd
-- Social table structure: coin_symbol -> coin_id, datetime -> ts, open -> open_price, etc.

CREATE OR REPLACE VIEW v_social_final AS
SELECT 
    coin_symbol AS coin_id,
    datetime AS ts,
    open AS open_price,
    high AS high_price,
    low AS low_price,
    close AS close_price,
    volume_24h AS volume_usd,
    -- Additional social metrics (not in price table)
    market_cap,
    sentiment,
    social_dominance,
    market_dominance,
    galaxy_score,
    alt_rank,
    posts_created,
    posts_active,
    interactions,
    contributors_created,
    contributors_active,
    spam,
    circulating_supply,
    timestamp AS timestamp_raw
FROM social_final
WHERE coin_symbol IS NOT NULL
  AND datetime IS NOT NULL
ORDER BY coin_id, ts;

-- This view matches the price_data table format:
-- - coin_id (same as price_data.coin_id)
-- - ts (same as price_data.ts, datetime format)
-- - open_price, high_price, low_price, close_price (same as price_data)
-- - volume_usd (same as price_data.volume_usd)
-- Plus additional social metrics for analysis

-- Usage examples for comparison:
-- 
-- Compare price and social data:
-- SELECT p.coin_id, p.ts, p.close_price, s.sentiment, s.galaxy_score
-- FROM price_data p
-- JOIN v_social_final s ON p.coin_id = s.coin_id AND p.ts = s.ts
-- WHERE p.coin_id = 'bome';
--
-- Get matching records:
-- SELECT * FROM v_social_final WHERE coin_id = 'doge' AND ts >= '2024-11-01';
--
-- Compare structure:
-- SELECT 'price' as source, coin_id, ts, open_price, high_price, low_price, close_price, volume_usd FROM price_data WHERE coin_id = 'bome' LIMIT 5
-- UNION ALL
-- SELECT 'social' as source, coin_id, ts, open_price, high_price, low_price, close_price, volume_usd FROM v_social_final WHERE coin_id = 'bome' LIMIT 5;

