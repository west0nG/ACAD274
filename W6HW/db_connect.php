<?php

$servername = "webdev.iyaserver.com";
$username = "dent_student";
$password = "code4Studentuse";
$dbname = "dent_health";

try {

    $pdo = new PDO("mysql:host=$servername;dbname=$dbname;charset=utf8", $username, $password);
    
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    echo "connected";
    
} catch(PDOException $e) {
    echo "failed: " . $e->getMessage();
}
?>
