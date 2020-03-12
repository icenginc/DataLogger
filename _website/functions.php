
<?PHP

class stdObject 
{
    public function __construct(array $arguments = array()) 
	{
        	if (!empty($arguments)) 
		{
            		foreach ($arguments as $property => $argument) 
			{
               		 	$this->{$property} = $argument;
            		}//End foreach
       		}//End if

	}//End of function __construct

    public function __call($method, $arguments) 
	{
       		$arguments = array_merge(array("stdObject" => $this), $arguments); // Note: method argument 0 will always referred to the main class ($this).
        
		if (isset($this->{$method}) && is_callable($this->{$method})) 
		{
            		return call_user_func_array($this->{$method}, $arguments);
        	} 
		else 
		{
	        	throw new Exception("Fatal error: Call to undefined method stdObject::{$method}()");
        	}//End of else
    	}//End of function __call

}//End of class

function readSystemSettings($settingsFile)
{

	$systemConfig;
	$sensorConfig;
	$configArray = array();
	$startSystemConfig = 0;
	$startSensorConfig = 0;
	$stop = 0;

	$file = fopen($settingsFile,"r");

	while(! feof($file))
	{
		//echo fgets($file)."<BR />";

		$line = fgets($file);

		if(strpos($line,"# System Config") !== false)
		{
			$stop = 0;
			$startSystemConfig = 1;
			$systemConfig = new stdObject();
		}//End if

		if(strpos($line,"# Sensor Config") !== false)
		{
			$stop = 0;
			$startSensorConfig = 1;
			$sensorConfig = new stdObject;
		}//End if

		if(strpos($line,"#End") !== false)
		{
			if($startSystemConfig == 1)
				array_push($configArray, $systemConfig);

			if($startSensorConfig == 1)
				array_push($configArray, $sensorConfig);

			$stop = 1;
			$startSystemConfig = 0;
			$startSensorConfig = 0;
		}//End if	

		if(strlen($line) > 2 && strpos($line,"#") === false)
		{
			if ($startSystemConfig == 1)
			{
				$tempString = substr($line,0,strpos($line,":"));
				$value = substr($line,strpos($line,":")+1,strlen($line));
				$systemConfig->$tempString = trim($value);
			}

			if ($startSensorConfig == 1)
			{
				$tempString =  substr($line,0,strpos($line,":"));
				$value = substr($line,strpos($line,":")+1,strlen($line));
				$sensorConfig->$tempString = trim($value);
			}

		}//End if

	}//End of while

	fclose($file);

	/**
	foreach ($configArray as $item)
	{
		print_r($item);
	}
	**/

	return $configArray;

}// End of readSystemSettings






?>