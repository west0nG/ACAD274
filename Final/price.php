<?php
// price.php
// Cryptocurrency Price Data API - Connect to MySQL and return JSON data

// Database connection configuration - modify according to your actual database information
$host    = 'webdev.iyaserver.com';        // Database host
$db      = 'westongu_memecoin';      // Database name
$user    = 'westongu_guest';             // Database username
$pass    = 'acad274final';                 // Database password
$charset = 'utf8mb4';

// Table name - modify according to your actual table name
$table   = 'price_data';

// PDO connection settings
$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
];

// Set output to JSON format
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (PDOException $e) {
    echo json_encode([
        "success" => false,
        "error"   => "Database connection failed",
        "details" => $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Optional filter parameters
$where  = [];
$params = [];

// Filter by coin: ?coin_id=bome
if (!empty($_GET['coin_id'])) {
    $where[] = "coin_id = :coin_id";
    $params[':coin_id'] = $_GET['coin_id'];
}

// Filter by date: ?date=2025-11-01
if (!empty($_GET['date'])) {
    $where[] = "DATE(ts) = :date";
    $params[':date'] = $_GET['date'];
}

// Date range filter: ?start_date=2025-11-01&end_date=2025-11-02
if (!empty($_GET['start_date'])) {
    $where[] = "ts >= :start_date";
    $params[':start_date'] = $_GET['start_date'];
}

if (!empty($_GET['end_date'])) {
    $where[] = "ts <= :end_date";
    $params[':end_date'] = $_GET['end_date'];
}

// Limit number of results: ?limit=100
$limit = "";
if (!empty($_GET['limit']) && ctype_digit($_GET['limit'])) {
    $limit = " LIMIT " . intval($_GET['limit']);
}

// Base SQL query - adjust fields according to your data structure
$sql = "
    SELECT
        id,
        coin_id,
        ts,
        open_price,
        high_price,
        low_price,
        close_price,
        volume_usd
    FROM $table
";

// Add WHERE conditions
if (!empty($where)) {
    $sql .= " WHERE " . implode(" AND ", $where);
}

// Order by time descending
$sql .= " ORDER BY ts DESC, coin_id ASC";
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
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Return JSON data
echo json_encode([
    "success" => true,
    "count"   => count($rows),
    "data"    => $rows
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

?>
 