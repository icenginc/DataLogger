<?PHP
	

	$channel = $_GET["channel"];
	$type = modifyType($_GET["type"], $channel);
	$value = $_GET["value"];

	set_time_limit(20);

	$arguments = $channel." ".$type." '".$value."'";

	//echo $arguments;

	function modifyType($type, $thisChannel)
	{

		if ($thisChannel == "0")// System Info Related
		{
			//echo "System Info";

			$output = str_replace(" ","", $type);

			if ( strpos($output, "LogServerLocation") !== false )
				$output = "LogServerLocation";

			if ( strpos($output, "FactoryLocation") !== false )
				$output = "FactoryLocation";

			if ( strpos($output, "EmailAlerts") !== false )
				$output = "EmailAlert";

			if ( strpos($output, "SystemName") !== false )
				$output = "SystemName";

			if ( strpos($output, "SaveDuration") !== false )
				$output = "LogGenerationInterval";

			return $output;

		}
		else
		{
			if ($type == "Min")
				return "MinSetting";
			elseif ($type == "Max")
				return "MaxSetting";
			elseif ($type == "Gain")
				return "Gain";
			elseif ($type == "Offset")
				return "Offset";
			elseif ($type == "Units")
				return "SensorUnit";
			elseif ($type == "Type")
				return "SensorType";
			elseif ($type == "Log Interval")
				return "LogInterval";
			elseif ($type == "Log Channel Assignment")
				return "LogFileChannelAssignment";
			elseif ($type == "Enabled")
				return "Enabled";

		}//End else	

	}//End modifyType

	function runScript($arguments)
	{
		$scriptName = "updateWebsiteSettings.py";
		$command = escapeshellcmd("/home/pi/Documents/DataLogger/_software/".$scriptName);
		//echo "/home/pi/Documents/DataLogger/_software/".$scriptName;
		$command = "python ".$command." ".$arguments;
		
		//echo $command;

		exec($command, $output, $status);
		//print_r($output);
		if (sizeof($output) > 0)
		{
			echo($output[0]);
		}

	}//End of runScript

	runScript($arguments);


?>