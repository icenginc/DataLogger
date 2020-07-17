<?PHP


	function runScript()
	{
		$scriptName = "checkIfRunning.py";
		$command = escapeshellcmd("/home/pi/Documents/DataLogger/_software/website/".$scriptName);
		//echo "/home/pi/Documents/DataLogger/_software/".$scriptName;
		$command = "python ".$command;
		
		//echo $command;

		exec($command, $output, $status);
		//print_r($output);
		if (sizeof($output) > 0)
		{
			echo($output[0]);
		}

	}//End of runScript


	runScript();


?>
