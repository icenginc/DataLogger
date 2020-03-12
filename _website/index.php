<?PHP

//------------------------------------------------- VARIABLES

error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'functions.php';

$settingsFile = "/home/pi/Documents/DataLogger/_settings/SystemConfig.txt";
$GLOBALS['systemConfigData'] = readSystemSettings($settingsFile);

$systemInfo = $GLOBALS['systemConfigData'][0];

$systemName = $systemInfo->SystemName;




function createSensorDiv($sensorNumber=0)
{
	
	$sensorObject = $GLOBALS['systemConfigData'][$sensorNumber];

	//print_r($sensorObject);

	$min = $sensorObject->MinSetting;
	$max = $sensorObject->MaxSetting;

	$enabledValue = $sensorObject->Enabled;

	echo '<div class="SensorDiv">

		<div class="SensorNumber">'.$sensorNumber.'</div>
		<div class="EnabledCSS" id="enabled_'.$sensorNumber.'">'.$enabledValue.'</div>
		<div class="SensorDisplay" id="sensorDisplay'.$sensorNumber.'">
			<div class="displayNumber" id="displayNumber'.$sensorNumber.'">125C</div>
			<div class="minNumber" id="minSetting'.$sensorNumber.'">Min: '.number_format((float)$min,1).$sensorObject->SensorUnit.'</div>
			<div class="maxNumber" id="maxSetting'.$sensorNumber.'">Max: '.number_format((float)$max,1).$sensorObject->SensorUnit.'</div>
		</div>

		<div style="height:24px;">
			<div class="SensorConfig">
	
			<select id="selectedSensorID_'.$sensorNumber.'" class="selectSensorType" title="Select Sensor Type" style="width:200px">';

	//echo "Sensor";
	//echo $sensorObject->SensorType;
	//echo strcmp($sensorObject->SensorType, "Temperature");

	if(strcmp($sensorObject->SensorType, "PTS1206100_RTD") == 0)
	{

		echo '<option selected="selected">PTS1206100_RTD</option>
			<option>Generic</option>
			<option>-Unused-</option>';
	}
	elseif(strcmp($sensorObject->SensorType, "Generic") == 0)
	{
		echo '<option selected="selected">Humidity</option>
			<option>PTS1206100_RTD</option>
			<option>-Unused-</option>';
	}
	elseif(strcmp($sensorObject->SensorType, "SHT31-D") == 0) // I2C Temp/Humidity Device
	{
		echo '<option selected="selected">SHT31-D</option>   
  		        <option>-Unused-</option>';
	}
	else
	{
		if($sensorNumber == 5 || $sensorNumber == 6)
		{
			echo '<option selected="selected">-Unused-</option>
				<option>SHT31-D</option>
			      ';

		}
		else
		{
			echo '<option selected="selected">-Unused-</option>
				<option>PTS1206100_RTD</option>
				<option>Generic</option>
			      ';

		}//End of else

	}//End of else

    	echo '</select>


			</div>
			<div id="LogConfig_'.$sensorNumber.'" class="LogConfig">
				
			</div>
			<div class="SettingsMenu" id="SettingsMenu_'.$sensorNumber.'">
		    		<ul>
		     	 	<li><div>Gain</div></li>
		     	 	<li><div>Offset</div></li>
				<li><div>Units</div></li>
				<li><div>Min</div></li>
				<li><div>Max</div></li>
				<li><div>Log Interval</div></li>
				<li><div>Log Channel Assignment</div></li>
				<li><div>Settings Info</div></li>
				</ul>
			</div>

		</div>

		</div><!-- End of SensorDiv -->';

}//End of createSensorDiv

// For Running and Alarm
function createLogicInput($sensorNumber="NA")
{
	echo '<div class="SensorDiv">

		<div class="SensorNumber" style="width:80px;">'.$sensorNumber.'</div>
		<div class="SensorDisplay" id="sensorDisplay'.$sensorNumber.'">
			<div class="displayNumber" id="displayNumber'.$sensorNumber.'">-</div>
		
		</div>

		<div style="height:24px;">
			<div class="SensorConfig">
	
			<select id="selectedSensorID_'.$sensorNumber.'" class="selectSensorType" title="Select Sensor Type">';

	
	echo '<option selected="selected">- Unused -</option>
		<option>Active High</option>
		<option>Active Low</option>
			      ';
	

    	echo '</select>


		</div>



		</div>

		</div><!-- End of SensorDiv -->';

}//End of createLogicInput


?>


<?PHP 
	//------------------------------------------------------------------------- START HTML
?>

<html>

	<head>
		<title>Data Logger</title>
		
		<script type="text/javascript" src="_scripts/jquery-3.1.1.js"></script>
		<script type="text/javascript" src="_scripts/jquery-ui-1.12.1/jquery-ui.js"></script>
		<link rel="stylesheet" type="text/css" href="_scripts/jquery-ui-1.12.1/jquery-ui.css"/>

		<link rel="stylesheet" type="text/css" href="main.css"/>

		 <script>



		  $( function() {

			var global_systemName = "Default";
	
			var dialog,form;

		    	$(".selectSensorType").selectmenu({ width: 154});

			$(".selectSensorType").each(function() {

				$(this).data('previous', $(this).val());

			});

			$(".selectSensorType").selectmenu({
				change: function(event, ui) {
					
					var index = $(this).attr("id");
					console.log(index);

					var previous = $(this).data('previous');
					console.log("Pre: " + previous);
					console.log($(this).val());

					$(this).data('previous', $(this).val());

					if(index !== "selectedSensorID_Run" && index !== "selectedSensorID_Alarm")
						displaySensorConfig(this);

				}//End of change

			});

			$(".EnabledCSS").click(function(){

				console.log("Toggle ");
				//var index = $(this).attr("id");
				var index = $(this).attr("id").substring($(this).attr("id").indexOf("_")+1,$(this).attr("id").length);
				console.log(index);

				var currentText = $(this).html();

			

				if (currentText == "Yes")
				{
					$(this).html("No");
					$("#displayNumber" + index).html("-");
					setSettings($(this), "Enabled", "No");
				}
				else if (currentText == "No")
				{
					$(this).html("Yes");
					setSettings($(this), "Enabled", "Yes");
				}


			});
			
			setInterval(runClock, 1000);
	
			$("#menu").menu();

			$(".LogConfig").hover(function(event) {

				var index = $(this).attr("id").substring($(this).attr("id").indexOf("_")+1,$(this).attr("id").length);
				var p = $(this).position();

				console.log("ID: " + index);

				if(event.type == "mouseenter")
				{
					console.log("Hover" + "#SettingsMenu_" + index);
					$("#SettingsMenu_" + index).css({"left": p.left,"top": p.top + 10});
					$("#SettingsMenu_" + index).stop().slideDown(100);
				}
				//else if(event.type == "mouseleave")
				//{
				//	console.log("Hover");
				//	$("#SettingsMenu_" + index).stop().slideUp(100);
				//}
				else
				{
					console.log("Else");
				}
				
			});

			$(".SettingsMenu").hover(function(event) {

				if(event.type == "mouseleave")
				{
					$(this).stop().slideUp(100);
				}

			});


			$(".SettingsMenu").hide();

			$("#pageSettings").click(function() {

				global_systemName = "Test";

				console.log(global_systemName);

				if ( $("#pageSettings_sub").is(":visible") )
				{
					$("#pageSettings_sub").stop().slideUp(100);
				}
				else
				{
					var p = $(this).position();
					$("#pageSettings_sub").css({"left": p.left - 100,"position": "absolute","top:": p.top + 20});
					$("#pageSettings_sub").stop().slideDown(100);
				}
			});


			

			$(".SettingsMenu li").click(function() {

				var itemClicked = $(this).text();
				var identity = $(this).parent().parent();
				console.log(identity.attr("id"));
				console.log(itemClicked);
				//console.log("This: " + $(this));

				var parentID = identity.attr("id");
				var numberID = parentID.indexOf("_") + 1;
				numberID = parentID.substring(numberID);

				//if(parentID.includes("SettingsMenu"))
				if(parentID.indexOf("SettingsMenu") >= 0)
					identity.stop().slideUp(100);

				console.log("Open Dialog");
				console.log(numberID);

				$("#status").html(itemClicked);


				if(itemClicked == "Settings Info" || itemClicked == "System Info")
				{
	
					dialog = $("#dialogForm").dialog({
	
					autoOpen:false,
					height:400,
					width:300,
					modal:true,
					title: itemClicked,
					buttons: {
						"Close": function() {	dialog.dialog("close");}
					},
					close: function() {
						
					}				
	
					});// End of dialog

				}//End if itemCLicked
				else
				{
					dialog = $("#dialogForm").dialog({
	
					autoOpen:false,
					height:200,
					width:300,
					modal:true,
					title: itemClicked,
					buttons: {
						"Set": function() {
							
							
							Set($(this),itemClicked);
						
							$("input").each(function() {
								console.log("Type: " + itemClicked);
								console.log("Input: " + $(this).val());
								

								setSettings(identity, itemClicked, $(this).val());							
							});
			
							dialog.dialog("close");
	
	
						},
						Cancel: function() {dialog.dialog("close");}
					},
					close: function() {
						
					}				
	
					});// End of dialog

				}//End else

				if(itemClicked == "Settings Info" || itemClicked == "System Info")
				{
					if(itemClicked == "System Info")
						numberID = 0;

					var data = "sensorIndex=" + numberID;

					var getSettingsInfo = "getSettings.php?" + data;
					$.ajax({
						url: getSettingsInfo,
						success: function(result){
							//console.log("Successfully returned Settings Info");
							//console.log(result);
							var splitResults = result.split(";");
							console.log(splitResults);

							var outputHTML = "";
							for(var i in splitResults)
							{
								if(splitResults[i].length > 0)
								{
									var items = splitResults[i].split(":");
									outputHTML += "<b>" + items[0] + ":</b> " + items[1] + "<br />";
									console.log(items);
								}//End if
							}//End for

							dialog.html(outputHTML)

					}});//End of ajax

				}//If
				else
				{
					dialog.html("<input type='text'>");
				}


				dialog.dialog("open");

			});

			function checkRunStatus()
			{
				var checkRunStatus = "getRunningStatus.php";
				$.ajax({
					url: checkRunStatus,
					success: function(result){
						
						//console.log("Run Status: " + result);

						if (result == "Running")
						{
							$("#runStatus").css("background-color", "#51FF0C");
							$("#runStatus").css({"border-color": "green",
								"border-width": "1px",
								"border-style": "solid"});

						}
						else if (result == "Stopped")
							$("#runStatus").css("background-color", "red");							

					}});

			}
			setInterval(checkRunStatus, 10000);

			function checkSystemStatus()
			{
				var checkRunStatus = "getSystemStatus.php";
				$.ajax({
					url: checkRunStatus,
					success: function(result){
						
						//console.log("System Status: " + result);

						var tempStringArray = result.split(":");
						//console.log(tempStringArray[0]);

						if (tempStringArray[0] == "Running")
						{
							$("#displayNumberRun").html("OK");
							$("#displayNumberRun").css("color", "white");
							$("#sensorDisplayRun").css("background-color", "#00FF19");

						}
						else
						{
							$("#displayNumberRun").html("FAIL");
							$("#displayNumberRun").css("color", "white");							
							$("#sensorDisplayRun").css("background-color", "red");
						}

						if (tempStringArray[1] == "Running")
						{
							$("#displayNumberAlarm").html("OK");
							$("#displayNumberAlarm").css("color", "white");
							$("#sensorDisplayAlarm").css("background-color", "#00FF19");

						}
						else
						{
							$("#displayNumberAlarm").html("FAIL");
							$("#displayNumberAlarm").css("color", "white");
							$("#sensorDisplayAlarm").css("background-color", "red");
						}


					}});

			}
			setInterval(checkSystemStatus, 10000);

			function getRPI_Revistion()
			{
				var getRevision = "getRevision.php";
				$.ajax({
					url: getRevision,
					success: function(result){
						
						console.log("Revision: " + result);

						$("#RPI_Revision").html("Revision: " + result);							

					}});



			}//End of getRPI_Revistion
			getRPI_Revistion()


			$("[id^='selectedSensorID_']").each(function() {

				$(this).css({"width" : "160px"})

			});
			

			//------------------ New DOM HERE -------------------------------------

		  } );// End of DOM

			function Set(object, itemClicked)
			{
				console.log("Set: " + itemClicked);

			}

			function runClock()
			{
				var date = new Date();
				var days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
				var months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

				var time = date.getHours() + ":" + date.getMinutes() + ":"
					 + ('0' + date.getSeconds()).slice(-2)
					 + "<br>" + days[date.getDay()] + ", "
					 + date.getDate() + " " + months[date.getMonth()] + " "
					 + date.getFullYear();
				$("#timeInfo").html(time);

				var tempP = $("#rightHeader").position();
				$("#timeInfo").css({"left":tempP.left + 50});
			}

			function displaySensorConfig(thisObject)
			{

				var numberID = $(thisObject).attr("id");
				numberID = numberID.indexOf("_") + 1;
				numberID = $(thisObject).attr("id").substring(numberID);

				var selectedSensor = $(thisObject).val();

				var data = "sensorIndex=" + numberID;
				var outputHTML = "";

				dialog = $("#dialogForm").dialog({
	
					autoOpen:false,
					height:300,
					width:300,
					modal:true,
					title: selectedSensor,
					buttons: {
						"Configure": function() {
							
							var inputs = $("#dialogForm :input");

							
							var channelIndex = $(thisObject).attr("id").substring($(thisObject).attr("id").indexOf("_")+1,$(thisObject).attr("id").length);
							var inputString = "channel=" + channelIndex + "&";
			
							console.log("ID: " + channelIndex);

							for(var i=0; i < inputs.length; i++)
							{
								var tempInput = inputs[i].value;
								//console.log("TempInput: " + tempInput);

								if(tempInput == "" && inputs[i].name.trim() == "LogFileChannelAssignment")
									tempInput = channelIndex;
								else if(tempInput == "")
									tempInput = "NA";

								//console.log("Input: " + inputs[i].value + ", " + tempInput);

								if(i == inputs.length - 1)
								{
									if (tempInput == "NA")
										inputString += inputs[i].name + "=" + tempInput;
									else
										inputString += inputs[i].name + "=" + inputs[i].value;
								}
								else
								{
									if (tempInput == "NA")
										inputString += inputs[i].name + "=" + tempInput + "&";
									else
										inputString += inputs[i].name + "=" + inputs[i].value + "&";
								}

							}//End of for
							
							console.log(inputString);

							configureChannelSettings(inputString);

							dialog.dialog("close");
	
	
						},
						Cancel: function() {dialog.dialog("close");}
					},
					close: function() {
						
					}				
	
					});// End of dialog

				var getSettingsInfo = "getSettings.php?" + data;
				$.ajax({
					url: getSettingsInfo,
					success: function(result){
						//console.log("Successfully returned Settings Info");
						//console.log(result);
						var splitResults = result.split(";");
						//console.log(splitResults);

						for(var i in splitResults)
						{
							if(splitResults[i].length > 0)
							{
								var items = splitResults[i].split(":");
								var inputField = '<input name="' + items[0].trim() + '" type="text" >';
								
								console.log("getSettingsInfo: " + items[0].trim());
								if (items[0].trim() === "SensorType")
								{
									var inputFieldNoEdit = '<input name="' + items[0].trim() + '" type="text" readonly value="' + selectedSensor + '">';
									outputHTML += "<b>" + items[0] + ":</b> " + inputFieldNoEdit + "<br />";

								}
								else if (items[0].trim() === "SensorUnit" && selectedSensor == "SHT31-D")
								{
									var tempUnit = "C,RH %";
									var inputFieldNoEdit = '<input name="' + items[0].trim() + '" type="text" readonly value="' + tempUnit + '">';
									outputHTML += "<b>" + items[0] + ":</b> " + inputFieldNoEdit + "<br />";

								}
								else
								{
									outputHTML += "<b>" + items[0] + ":</b> " + inputField + "<br />";
									//console.log(items);
								}

							}//End if
						}//End for

					}}).done( function() {

						dialog.html(outputHTML);

						console.log("OutputHTML: " + outputHTML);
						

						dialog.dialog("open");

					});//End of done


			}//End of displaySensorConfig

			function getSettingByName(tempSettingsName)
			{
				if (tempSettingsName == "MinSetting")
					return "minSetting";
				else if (tempSettingsName == "MaxSetting")
					return "maxSetting";


			}//End of getSettingsByName

			function editReturnedData(data)
			{
				// dataValues[0] -> "Finished"
				// dataValues[1] -> Channel Number
				// dataValues[2] -> Setting Name
				// dataValues[3] -> Value
				// dataValues[4] -> Unit

				if (data[2] == "MinSetting")
				{
					return "Min:<br />" + parseFloat(data[3]).toFixed(1) + data[4];
				}
				else if (data[2] == "MaxSetting")				
				{
					return "Max:<br />" + parseFloat(data[3]).toFixed(1) + data[4];
				}//End else if

			}//End of editReturnedData

			function setSettings(input, type, value)
			{
				console.log("InputName: " + input.attr("id"));
				console.log("Type: " + type);
				console.log("Value: " + value);

				var numberID = input.attr("id").indexOf("_") + 1;
				numberID = input.attr("id").substring(numberID);

				if (input.attr("id").indexOf("pageSettings") > -1)
				{
					console.log("System Info Related");
					numberID = "0";
				}

				console.log(numberID);

				var data = "channel=" + numberID + "&type=" + type + "&value=" + value;

				console.log(data)

				var setTempURL = "setSettings.php?" + data;
				$.ajax({
					url: setTempURL,
					success: function(result){
						console.log("Returned");
						if (result.indexOf("Finished") > -1)
						{
							console.log(result);
							var dataValues = result.split(">");

							// dataValues[0] -> "Finished"
							// dataValues[1] -> Channel Number
							// dataValues[2] -> Setting Name
							// dataValues[3] -> Value
							// dataValues[4] -> Unit

							if (dataValues[2] == "SensorUnit")
							{
								var minValue = $("#minSetting" + dataValues[1]).html().match(/\d+.\d+/)[0];
								var maxValue = $("#maxSetting" + dataValues[1]).html().match(/\d+.\d+/)[0];

								console.log(minValue);
								console.log(maxValue);

								$("#minSetting" + dataValues[1]).html("Min:<br />" + minValue + dataValues[3]);
								$("#maxSetting" + dataValues[1]).html("Max:<br />" + maxValue + dataValues[3]);


							}
							else
							{
								var settingName = getSettingByName(dataValues[2]) + dataValues[1];
								var editData = editReturnedData(dataValues);
								var text = editData;
								console.log("SettingName: " + settingName);
								$("#" + settingName).html(text);
							}

						}//End if
						else
						{
							console.log("Failed");

						}//End of else
					}});

			}//End of setSettings

			// Configures channel setting when clicking: 
			function configureChannelSettings(inputString)
			{
				console.log("Configure ChannelSettings");

				var setTempURL = "setAllSettings.php?" + inputString;
				$.ajax({
					url: setTempURL,
					success: function(result){
						console.log("Returned");
						if (result.indexOf("Finished") > -1)
						{
							console.log("Result: " + result);
							var result1 = result.split(">");
							//console.log("Split1: " + result1);

							// result1[0] -> "Finished"
							// result1[1] -> Channel Number
							// result1[2] -> Array of Setting Names (separated by ?)
							// result1[3] -> Array of Setting Values (separated by ?)

							var dataValues = result1[3].split("?");
							//console.log("Split2: " + dataValues);

							// dataValues[0] -> Channel
							// dataValues[1] -> Sensor Type
							// dataValues[2] -> Sensor Unit
							// dataValues[3] -> Gain
							// dataValues[4] -> Offset
							// dataValues[6] -> MinSettings
							// dataValues[7] -> MaxSettings
							// dataValues[8] -> Log Channel Assignment
							// dataValues[9] -> Enabled
				
							var channelName = dataValues[0].toString().replace(/["']/g,"");
							//console.log(channelName);

							var minSetting = dataValues[6].toString().replace(/["']/g,"");
							var maxSetting = dataValues[7].toString().replace(/["']/g,"");
			
							var unit = dataValues[2].toString().replace(/["']/g,"");

							$("#minSetting" + channelName).html("Min:<br />" + minSetting + unit);
							$("#maxSetting" + channelName).html("Max:<br />" + maxSetting + unit);



							var isEnabled = dataValues[9].toString().replace(/["']/g,"");
					
							if (isEnabled == "Yes")
								$("#enabled_" + channelName).html("Yes");
							else
								$("#enabled_" + channelName).html("No");


						}//End if
					}});

			}//End of configureChannelSettings


			function getTemperature(inputType)
			{
				var data = "channel=" + inputType;
				var getTemperature = "getTemperature.php?" + data;
				$.ajax({
					url: getTemperature,
					success: function(result){
						//console.log(result)
										

						var displayNum = "#displayNumber";
			
						var dataSplit = result.split(",");

						var i = 1;
						for(i=1; i < 7; i++)
						{

							if ($("#enabled_" + i).html() == "Yes")
							{
								var temperature = parseFloat(result).toPrecision(4);
								var humidity;
								var text = "";	
	
								displayNum = "#displayNumber" + i;
	
								if (i < 5) // For Ports ADC 1-3 (4 is used as Alarm and Run)
								{
									if (dataSplit[i-1] == "-")
										text = "-";
									else
										text = dataSplit[i-1] + "C";
		
									var minLimitName = "minSetting" + i;
									var minLimitValue = $("#" + minLimitName).html().match(/\d+./g);
									minLimitValue = minLimitValue.join("");
									minLimitValue = minLimitValue.substring(0, minLimitValue.length - 1);
									
									//console.log(minLimitName);
									//console.log("Min:" + minLimitValue + ", Value:" + dataSplit[i-1]);
									
									var maxLimitName = "maxSetting" + i;
									var maxLimitValue = $("#" + maxLimitName).html().match(/\d+./g);
	
									maxLimitValue = maxLimitValue.join("");
									maxLimitValue = maxLimitValue.substring(0, maxLimitValue.length - 1);
									
									//console.log(maxLimitValue);
	
									// For Min
									if (parseFloat(dataSplit[i-1]) < parseFloat(minLimitValue))
									{
										//console.log("Lower");
										$("#sensorDisplay" + i).css("background-color", "blue");
										$(displayNum).css("color", "white");
									}
									// For Max
									else if (parseFloat(dataSplit[i-1]) > parseFloat(maxLimitValue))
									{
										//console.log("Value:" + dataSplit[i-1] + ", " + maxLimitValue);
										$("#sensorDisplay" + i).css("background-color", "red");
										$(displayNum).css("color", "white");
									}
									else
									{
										$("#sensorDisplay" + i).css("background-color", "transparent");
										// #ba5203
										$(displayNum).css("color", "#ba5203");
									}
	
									$(displayNum).css("font-size", "60px");
									$(displayNum).html(text)
	
								}//End if
								else if (i >= 5 && i <= 6) // For I2C Ports
								{
									if (dataSplit[i-1] == "-")
									{
										text = "-<br />-";
	
									}
									else
									{
										if (typeof dataSplit[i-1] != "undefined")
										{
											var tempString = dataSplit[i-1].split(":");
			
											
											temperature = parseFloat(tempString[0]).toPrecision(3);
											humidity = parseFloat(tempString[1]).toPrecision(3);
									
											text = temperature + "C<br />" + humidity + "%";
										
										}//End if

									}//End if
	
									$(displayNum).css("font-size", "30px");
									$(displayNum).html(text);
	
								}//End of else if

							}//End if enabled
							else
							{
								var displayNum = "#displayNumber" + i;
								$(displayNum).html("-");
								$(displayNum).css("color", "#ba5203");
								$("#sensorDisplay" + i).css("background-color", "transparent");

							}//End else

						}//End of for

						
						//dialog.html(outputHTML);
						//console.log(text);

					}});

			}//End of getTemperature

			setInterval(function() {getTemperature("ADC1"); }, 5000);
			//setInterval(function() {getTemperature("I2C2"); }, 5200);

		
		  </script>
		  <style>
  			.ui-menu { width: 150px; }
  		  </style>

	</head>

<body>

	<!-- HEADER -->
	<div style="background-color:#FFF">
		<img src="_images/ICE_Logo.png" height="120" width="370" style="border:0px solid;" />
		<div id="rightHeader" style="border:0px solid;display:inline-block;height:120px;float:right;width:200px;">
			<div id="headerInfo">System: <?PHP echo $systemName; ?></div>
			<div id="timeInfo"></div>
		</div>
		<div style="height:3px;background-color:#050291;"></div>
	</div>

	<!-- END of HEADER -->

	<div id="pageSettings" style="float:right;margin-right:20px;margin-top:7px;"><img src="_images/settings_logo.png" height=32 width=32></div>
	<div class="SettingsMenu" id="pageSettings_sub">
		<ul>
			<li><div id="pageSettings_systemName">System Name</div></li>
			<li><div id="pageSettings_factoryLocation">Factory Location</div></li>
			<li><div id="pageSettings_logServerLocation">Log Server Location</div></li>
		 	<!-- <li><div id="pageSettings_logSystemLocation">Log System Location</div></li> -->
		 	<li><div id="pageSettings_email">Email Alerts</div></li>
			<li><div id="pageSettings_saveDuration">Save Duration</div></li>
			<!-- <li><div id="pageSettings_save">Save</div></li> -->
			<!-- <li><div id="pageSettings_load">Load</div></li> -->
			<li><div id="pageSettings_systemInfo">System Info</div></li>
		</ul>
	</div>


	<div id="dialogForm">
	</div><!-- dialogForm -->

	<div id="status"></div>
	<div id="runStatus" style="width:20px;height:20px;margin-top:20px;" title="Script is Running"></div>

	<div style="margin-left:auto;margin-right:auto;margin-top:50px;margin-bottom:50px;
		text-align:center;font-weight:bold;font-size:30px;">Data Logger</div>


	<center>
	<?PHP createSensorDiv(1); ?>
	<?PHP createSensorDiv(2); ?>
	<?PHP createSensorDiv(3); ?>
	<?PHP createSensorDiv(4); ?>
	</center>

	<div style="margin-top:100px;">
		<center>
		<?PHP createSensorDiv(5); ?>
		<?PHP createSensorDiv(6); ?>
		<?PHP createLogicInput("Run"); ?>
		<?PHP createLogicInput("Alarm"); ?>
		</center>
	</div>

	<div id="RPI_Revision" style="margin-top:100px;margin-right:20px;float:right;font-size:12px;"></div>
	
	<!-- FOOTER -->
	<!-- <div id="footer" style="bottom: 0;min-height:33px;width:100%">
		<div style="height:3px;background-color:#050291;margin-top:40px;"></div>
		<div style="background-color:#FFF;min-height:30px;"></div>
	</div> -->
	<!-- END of FOOTER -->

</body>

</html>