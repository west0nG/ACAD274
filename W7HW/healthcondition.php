<?php
// create connection to database
$host = "webdev.iyaserver.com"; // database server address
$userid = "dent_student"; // database user account name
$userpw = "code4Studentuse"; // database user password
$db = "dent_health"; // database name

$mysql = new mysqli(
    $host,
    $userid,
    $userpw,
    $db);

if($mysql->connect_errno) {
    echo "db connection error : " . $mysql->connect_error;
    exit();
}
?>

<!-- these php blocks do not need to be separated, but might as well since in many pages with
    full/normal html likely this block would be lower down in the code -->

<?php

/* php variable notes:
    -  php variables have dollar signs in front of their names, like $filter
    - php variables passed through page url strings are named $_REQUEST["variablename"]
    - if a $_REQUEST variable does not exist it does NOT error, it just returns blank
*/

// if no url condition was passed into page, default to Diabetes
if(!empty($_REQUEST["condition"])) {
	$filter = $_REQUEST["condition"];
} else  {
    $filter = "Aspirin";	
}

// base query
$sql =  "     SELECT 
	                AVG(Age) AS AverageAge,
	                MIN(Age) AS LowAge,
	                MAX(Age) AS HighAge,
	                COUNT(Name) AS NumberPatients
	              FROM healthcare_dataset
	              WHERE Medication='$filter'
	"; // note using $filter variable INSIDE SELECT statement

$results = $mysql->query($sql);

if(!$results) {
    echo "SQL error: ". $mysql->error . " running query <hr>" . $sql . "<hr>";
    exit();
}

// since only query in the page, and just a single line query (one row) that
// does not need a loop, pre-load the query columns into $currentrow
$currentrow = $results->fetch_assoc();

// dump columns into source code of page to debug / see column names and data
echo "<!--<pre> ";
var_dump($currentrow);
echo "</pre>-->";
?>



<!-- this is a javascript block in the page... NOT php ... but that doesn't mean we
    can't choose to output/inject content into it with php -->

<!-- javascript block. setting up variables -->
<script>
    // Note that javascript (and jQuery) variables have no symbol in front of the variable name
    var condition = "<?= $filter ?>";
    var patients = <?= $currentrow["NumberPatients"] ?>;
    var highage = <?= $currentrow["HighAge"] ?>;
    var lowage = <?= $currentrow["LowAge"] ?>;
    var avgage = <?= number_format($currentrow["AverageAge"],2) ?>;
</script>

<style>
    body {
        font-family: Arial, sans-serif;
        background: #f5f5f5;
        margin: 0;
        padding: 20px;
    }

    .container {
        background: white;
        border: 1px solid #ddd;
        padding: 30px;
        max-width: 600px;
        margin: 0 auto;
    }

    .title {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        color: #333;
    }

    .stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }

    .stat-box {
        border: 1px solid #ccc;
        padding: 20px;
        text-align: center;
        background: #fafafa;
    }

    .stat-label {
        font-size: 12px;
        color: #666;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #333;
    }

    .patients-box {
        grid-column: span 2;
        background: #e8e8e8;
    }
    .hyperlink-box {
        grid-column: span 2;
        background: #e8e8e8;
        text-align: center;
    }
</style>

<div class="container">
    <div class="title" id="condition"></div>
    
    <div class="stats">
        <div class="stat-box patients-box">
            <div class="stat-label">Total Patients</div>
            <div class="stat-value" id="patients"></div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Average Age</div>
            <div class="stat-value" id="avgage"></div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Min Age</div>
            <div class="stat-value" id="lowage"></div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Max Age</div>
            <div class="stat-value" id="highage"></div>
        </div>
        <div class="hyperlink-box">
            <a href="healthcondition.php?condition=Aspirin">Aspirin</a>
            <a href="healthcondition.php?condition=Ibuprofen">Ibuprofen</a>
            <a href="healthcondition.php?condition=Paracetamol">Paracetamol</a>
            <a href="healthcondition.php?condition=Penicillin">Penicillin</a>
            <a href="healthcondition.php?condition=Lipitor">Lipitor</a>
        </div>
    </div>
</div>



<script src="https://code.jquery.com/jquery-3.7.1.js"
        integrity="sha256-eKhayi8LEQwp4NKxN+CfCh+3qOVUtJn3QNZ0TciWLP4="
        crossorigin="anonymous"></script>
<script><!-- jQuery block -->
    $(document).ready(function(){
        // jQuery code

        // write variables to div boxes (by id)
        $("#condition").text(condition);
        $("#patients").text(patients);
        $("#highage").text(highage);
        $("#lowage").text(lowage);
        $("#avgage").text(avgage);

        // then go back to php, and put output php values in place of 0s

    });
</script>



