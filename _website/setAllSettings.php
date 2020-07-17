<?PHP
	

	$channel = $_GET["channel"];

	$settingType = "";
	$settingValue = "";


	foreach($_GET as $key => $value)
	{
		//echo $key." : ".$value."<br />\r\n";

		if (strlen($settingType) <= 0)
			$settingType = $key;
		else
			$settingType = $settingType."?".$key;
		

		if ($key == "Gain" && $value == "NA")
			$value = "1.0";
		if ($key == "Offset" && $value == "NA")
			$value = "0.0";

		if ($value == "NA" && $key != "Enabled")
			$value = "";
		elseif ($value == "NA" && $key == "Enabled")
			$value = "No";

		$settingValue = $settingValue.'?"'.$value.'"';

	}//End foreach

	$settingType = trim($settingType,"?");
	$settingValue = trim($settingValue,"?");

	//echo $settingType.'<br />';
	//echo $settingValue;

	$settingValue = str_replace('"','\"', $settingValue);

	$arguments = $channel." ".$settingType." ".$settingValue;
	
	//echo $arguments;

	function runScript($arguments)
	{
		$scriptName = "updateWebsiteSettings.py";
		$command = escapeshellcmd("/home/pi/Documents/DataLogger/_software/website/".$scriptName);
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
