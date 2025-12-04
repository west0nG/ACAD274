<?php
// social_data.php
// Simple database connection and JSON output

// Database connection configuration
$host    = 'webdev.iyaserver.com';
$db      = 'westongu_memecoin';
$user    = 'westongu_guest';
$pass    = 'acad274final';
$charset = 'utf8mb4';

// Table name - modify according to your actual table name
$table   = 'social_final_2'; // or your table name

// PDO connection settings
$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
];

// Set output to JSON format
header('Content-Type: application/json; charset=utf-8');

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (PDOException $e) {
    echo json_encode([
        "success" => false,
        "error"   => "Database connection failed: " . $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// SQL query with all columns
$sql = "
    SELECT
        coin_id,
        timestamp,
        ts,
        market_cap,
        sentiment,
        low_price,
        social_dominance,
        high_price,
        posts_created,
        market_dominance,
        open_price,
        galaxy_score,
        spam,
        contributors_created,
        posts_active,
        volume_usd,
        interactions,
        contributors_active,
        alt_rank,
        close_price,
        circulating_supply
    FROM $table
    ORDER BY ts DESC
";

try {
    $stmt = $pdo->prepare($sql);
    $stmt->execute();
    $rows = $stmt->fetchAll();
} catch (PDOException $e) {
    echo json_encode([
        "success" => false,
        "error"   => "Query execution failed: " . $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Return JSON data
echo json_encode($rows, JSON_UNESCAPED_UNICODE | JSON_NUMERIC_CHECK);

?>

