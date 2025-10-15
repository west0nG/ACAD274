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
    .box, .box2 {
        background: #fff;
        color: #111;
        border-radius: 3px;
        border: 1px solid #111;
        font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
        box-shadow: none;
        text-align: center;
        font-weight: bold;
        letter-spacing: 1px;
        transition: background 0.2s;
    }

    .box { 
        width: 60px; height: 24px; 
        position: absolute;
        font-size: 12px;
        line-height: 24px;
        background: #fff;
        color: #111;
        border: 1px solid #111;
    }
    .box2 { 
        width: 160px; height: 36px;
        position: absolute;
        font-size: 18px; 
        line-height: 36px;
        background: #fff;
        color: #111;
        border: 2px solid #111;
        font-weight: bold;
    }

    #chart { 
        width: 400px; 
        height: 240px; 
        position: relative;
        background: #fff;
        border: 2px solid #111;
        box-shadow: none;
        margin: 32px auto 0 auto;
        border-radius: 10px;
    }

    #condition { left: 120px; top:40px;}
    #patients { left: 260px; top:94px;}
    #avgage { left: 130px; top:130px;}
    #lowage { left: 128px; top:170px;}
    #highage { left: 220px; top:170px;}

    /* Remove background image for extreme minimalism */
</style>

<div id="chart">
<!-- chart emptied of all by boxes -->

    <div class="box2" id="condition"></div>
    <div class="box" id="patients"></div>
    <div class="box" id="avgage"></div>
    <div class="box" id="lowage"></div>
    <div class="box" id="highage"></div>

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



