<?PHP

	error_reporting(-1);
	ini_set('display_errors', 'On');

	function runScript()
	{
		$scriptName = "getRevision.py";
		$command = escapeshellcmd("/home/pi/Documents/DataLogger/_software/website/".$scriptName);
		//echo "/home/pi/Documents/DataLogger/_software/".$scriptName;
		$command = "python ".$command.' 2>&1';
		
		//echo $command;

		//exec($command, $output, $status);
	
		$output = shell_exec($command);

		if($output > 0)# (sizeof($output) > 0)
		{
			echo($output);
		}

	}//End of runScript


	runScript();

	


?>
