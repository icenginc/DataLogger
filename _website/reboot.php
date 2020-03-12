<?PHP

	header("Location: ../");
	$scriptName = "reboot.sh";
	$command = escapeshellcmd("/home/pi/Documents/DataLogger/_software/".$scriptName);
	$command = "bash ".$command;
	//echo $command;
	exec($command, $output, $status);
	if (sizeof($output) > 0)
	{
		echo($output[0]);
	}
	
	


?>