<?PHP

	
	ini_set('display_errors',1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);

	function temp()
	{
	
		$scriptName = "adc.py";
		$command = escapeshellcmd("/home/pi/Documents/DataLogger/_software/".$scriptName);
		//echo "/home/pi/Documents/DataLogger/_software/".$scriptName."<br />";
		$command = "python ".$command;
		exec($command, $output, $status);
		//print_r($output);
		if (sizeof($output) > 0)
		{
			echo($output[0]);
		}
		//echo "<br />Status: ".$status;

	}//End of function


	function readFromDatabase($channel)
	{
		$directory = "/home/pi/Documents/DataLogger/_database/";
		$db = new SQLite3($directory.'temperatures.db');


		$statement = "";
		$tempString = "";

		for($i=1; $i < 7; $i++)
		{

			if ($i == 1)
			{
				$statement = "SELECT * FROM tempData WHERE inputType = \"ADC 1\" ORDER BY date DESC LIMIT 1";
			}
			elseif ($i == 2)
			{
				$statement = "SELECT * FROM tempData WHERE inputType = \"ADC 2\" ORDER BY date DESC LIMIT 1";
			}
			elseif ($i == 3)
			{
				$statement = "SELECT * FROM tempData WHERE inputType = \"ADC 3\" ORDER BY date DESC LIMIT 1";
			}
			elseif ($i == 4)
			{
				$statement = "SELECT * FROM tempData WHERE inputType = \"ADC 4\" ORDER BY date DESC LIMIT 1";
			}
			elseif ($i == 5)
			{
				$statement = "SELECT * FROM tempData WHERE inputType = \"I2C 1\" ORDER BY date DESC LIMIT 1";
			}
			elseif ($i == 6)
			{
				$statement = "SELECT * FROM tempData WHERE inputType = \"I2C 2\" ORDER BY date DESC LIMIT 1";
			}

			$results = $db->query($statement);
			$row = $results->fetchArray();

			//print_r($row);

			$tempOutput = $row['data'];

			if (strlen($tempOutput) <= 0)
			{
				$tempString = $tempString.",-";			
			}
			else
			{
				$tempString = $tempString.",".$row['data'];
			}
			

		}// End of for

		$db->close();
		unset($db);

		$tempString = trim($tempString,",");

		echo $tempString;

	}//End of function readFromDatabase


	$channel = $_GET["channel"];

	

	//echo $channel;

	readFromDatabase($channel);

?>