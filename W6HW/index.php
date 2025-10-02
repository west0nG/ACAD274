<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Healthcare Data</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Healthcare Data</h1>
        </header>

        <main>
        
        <?php
        require_once 'db_connect.php';
        

        $query1 = "SELECT * FROM healthcare_dataset WHERE Age > 60 AND Gender = 'Male' AND MedicalCondition = 'Cancer' AND InsuranceProvider = 'Medicare'";
        
        try {
            $stmt1 = $pdo->prepare($query1);
            $stmt1->execute();
            $results = $stmt1->fetchAll(PDO::FETCH_ASSOC);
            
            echo "<h2>Filtered Records</h2>";
            echo "<p>Records matching criteria: Age > 60, Gender = Male, Medical Condition = Cancer, Insurance Provider = Medicare</p>";
            
            if (count($results) > 0) {
                echo "<table>";
                echo "<tr>";
                foreach (array_keys($results[0]) as $column) {
                    echo "<th>" . htmlspecialchars($column) . "</th>";
                }
                echo "</tr>";
                
                foreach ($results as $row) {
                    echo "<tr>";
                    foreach ($row as $value) {
                        echo "<td>" . htmlspecialchars($value) . "</td>";
                    }
                    echo "</tr>";
                }
                echo "</table>";
            } else {
                echo "<p>No records found matching the criteria.</p>";
            }
            
            $query2 = "SELECT 
                COUNT(*) as record_count,
                AVG(Age) as average_age,
                SUM(BillingAmount) as total_billing,
                AVG(BillingAmount) as average_billing
                FROM healthcare_dataset 
                WHERE Age > 60 AND Gender = 'Male' AND MedicalCondition = 'Cancer' AND InsuranceProvider = 'Medicare'";
            
            $stmt2 = $pdo->prepare($query2);
            $stmt2->execute();
            $aggregate = $stmt2->fetch(PDO::FETCH_ASSOC);
            
            echo "<h2>Aggregate Statistics</h2>";
            echo "<div class='stats'>";
            echo "<p><strong>Number of Records:</strong> " . $aggregate['record_count'] . "</p>";
            echo "<p><strong>Average Age:</strong> " . number_format($aggregate['average_age'], 2) . " years</p>";
            echo "<p><strong>Total Billing Amount:</strong> $" . number_format($aggregate['total_billing'], 2) . "</p>";
            echo "<p><strong>Average Bill per Patient:</strong> $" . number_format($aggregate['average_billing'], 2) . "</p>";
            echo "</div>";
            
        } catch(PDOException $e) {
            echo "<p>Query failed: " . $e->getMessage() . "</p>";
        }
        ?>
    </div>

    <div class="container">
        <div class="card">
            <h2>Healthcare Data Analysis</h2>
            <p>This is the healthcare data of the patients who are over 60 years old, male, and have cancer, and are insured by Medicare, we can find out some of the conclusion here. Firstly, a lot of them have a Admission type of Emergency or Urgent, which means they are in a critical condition and need to be treated immediately. That might related to the fact that they are over 60 years old and have cancer, which is a critical condition. What's more, most of the patients who are classfied as Urgent or Emergenct have higher billing about, typically excess $20000</p>
        </div>
    </div>
    </main>
    <footer>
        <p>Made by Weston Guo</p>
        <p>AI Disclosure: I use css styles sheet from the past homework, which is AI generated. I also use AI to help me debug the php query</p>
    </footer> 
</body>
</html>
