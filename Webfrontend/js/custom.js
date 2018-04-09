/* Javascript Ajax Communicator *
 * Autor Tobias Bossert         *
 * Project start: 23. May 2017  */



// Set Refreshtimer on beginning
$(document).ready(function(){
	setInterval(function(){
		getStatus();
	}, 10000);
});

//define controller IP
var ip = "http://192.168.2.214:8080"

// Get staus at beginning
$(document).ready(function(){
	getStatus();
});

// Turn channel on
function on(id)
{
	var pw = 'test';
	var data;
	$.ajax({
		type: "GET",
		url: ip+"/on/"+id+"/"+pw,
		crossDomain: true,
		dataType: 'json',
		data: data,
		success: function(data)
		{
			//if request was successfull
			if(data.result == 'ok')
			{
				//Update stautus indicator
				updateSign(id, 1);
				//Remove previous errors
				removeError();
			}
			//If Request ok, but server failed to complete
			else
			{
				displayError(data.msg);
			}
		},
		//If request fails
		error: function()
		{
			displayError("Konnte Konroller nicht erreichen")
		}
		
	});
}


//Change status indicator on page
function updateSign(id,task)
{
	//On
	if(task == 1)
	{
		$('span[name=label'+id+']').addClass("label-success");
		$('span[name=label'+id+']').removeClass("label-warn");

	}
	//Off
	else
	{
		$('span[name=label'+id+']').removeClass("label-success");
		$('span[name=label'+id+']').addClass("label-warn");
	}

}

//Show error
function displayError(msg)
{
	$("#error").show();
	$( "div.alert" ).html( "Achtung Fehler: "+msg+"" );
}

//Remove previous error
function removeError()
{
	$("#error").hide();
}


//See on function
function off(id)
{
	var pw = 'test';
	var data;
	$.ajax({
		type: "GET",
		url: ip+"/off/"+id+"/"+pw,
		crossDomain: true,
		dataType: 'json',
		data: data,
		success: function(data)
		{
			if(data.result == 'ok')
			{
				updateSign(id, 0);
				removeError();
			}
			else
			{
				displayError(data.msg)
			}
		},
		error: function()
		{
			displayError("Konnte Konroller nicht erreichen")
		}
	});
}


//Get status for all channels
function getStatus(){
	var pw = "test";
	//How many used channels
	var count = 5;
	//internal counter
	var counter = 1;
	var data;
	$.ajax({
		type: "GET",
		url: ip+"/getall/"+pw,
		crossDomain: true,
		dataType: 'json',
		data: data,
		success: function(data) 
			{
				//Check if Status ok
				if (data.result=='ok')
				{
					removeError();
					//Loop through json response
					$.each(data, function(index, elementd) {
						if(elementd == 0)
						{
							updateSign(index, 0);
						}
						if(elementd == 1)
						{
							updateSign(index, 1);
						}
						counter++;
						if (counter > 5)
						{
							return false;
						}
					});
				}
				else
				{
					displayError(data.msg)
				}
			},
		error: function()
		{
			displayError("Konnte Konroller nicht erreichen")
		}
		 
	});
    };
