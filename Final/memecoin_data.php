<?php
// get_coins.php
// This script connects to a MySQL database, retrieves coin market data,
// and returns the result in JSON format.

$host    = 'webdev.iyaserver.com';        
$db      = 'westongu_memecoin';   
$user    = 'westongu_guest';    
$pass    = 'acad274final';    
$charset = 'utf8mb4';

// Replace this with your table name
$table   = 'meme_coin_data';

// PDO connection settings
$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
];

// Set output type to JSON
header('Content-Type: application/json; charset=utf-8');


try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (PDOException $e) {
    echo json_encode([
        "success" => false,
        "error"   => "Database connection failed",
        "details" => $e->getMessage()
    ]);
    exit;
}


// Optional filters: ?symbol=DOGE&date=2024-11-25
$where  = [];
$params = [];

// Filter by coin symbol
if (!empty($_GET['symbol'])) {
    $where[] = "coin_symbol = :symbol";
    $params[':symbol'] = $_GET['symbol'];
}

// Filter by date
if (!empty($_GET['date'])) {
    $where[] = "last_updated = :date";
    $params[':date'] = $_GET['date'];
}

// Optional limit parameter
$limit = "";
if (!empty($_GET['limit']) && ctype_digit($_GET['limit'])) {
    $limit = " LIMIT " . intval($_GET['limit']);
}

// Base SQL query
$sql = "
    SELECT 
        coin_name,
        coin_symbol,
        current_price,
        price_24h_ago,
        price_7d_ago,
        percent_change_24h,
        percent_change_7d,
        volatility_index,
        stability_score,
        standard_deviation,
        high_24h,
        low_24h,
        price_range_24h,
        market_cap,
        volume_24h,
        liquidity_ratio,
        last_updated
    FROM $table
";

// Add WHERE conditions if needed
if (!empty($where)) {
    $sql .= " WHERE " . implode(" AND ", $where);
}

// Order by most recent date first
$sql .= " ORDER BY last_updated DESC, coin_symbol ASC";
$sql .= $limit;


try {
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $rows = $stmt->fetchAll();
} catch (PDOException $e) {
    echo json_encode([
        "success" => false,
        "error"   => "Query execution failed",
        "details" => $e->getMessage()
    ]);
    exit;
}


echo json_encode([
    "success" => true,
    "count"   => count($rows),
    "data"    => $rows
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

?>

