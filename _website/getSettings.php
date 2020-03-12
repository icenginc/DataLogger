
<?PHP

error_reporting(E_ALL);
ini_set('display_errors', 1);

	include 'functions.php';

	$settingsFile = "/home/pi/Documents/DataLogger/_settings/SystemConfig.txt";
	$returnData = readSystemSettings($settingsFile);

	//print_r($returnData[1]);

	$sensorID = $_GET["sensorIndex"];

	foreach($returnData[$sensorID] as $key => $item)
	{
		if (trim($key) != "ID")
			echo trim($key).':'.trim($item).';';


	}//End foreach

?>