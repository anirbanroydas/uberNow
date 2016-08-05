$(document).ready(function() {

	var conn = null;                            // global connection object
    var disconn = 0;                            // checks if connection was closed by server or user
    var errorconn = 0;                          // checks if connection is havving error
    var $apilist = $('.streams');      		// Api calls 
    var source = ''; 
    var destination = ''; 
    var hour = ''; 
    var mins = '';
    var meridian = '';
    var email = '';                             			

                                       		
    // Extended disable function
	$.fn.extend({
	    disable: function(state) {
	        return this.each(function() {
	            var $this = $(this);
	            if($this.is('input, button, textarea, select'))
	              this.disabled = state;
	            else
	              $this.toggleClass('disabled', state);
	        });
	    }
	});







    // Function to be called when a person clicks the Submit button
	$('#sub').click(function(e){
		e.preventDefault();

		$(this).disable(true);

		console.log('insdie #connect.clic()');

		var r = processinputs();
        if (r === 1){

        	if (conn === null) {
	            console.log('insdie conn === null');
	        
	            connect();
	        } 
	        else {
	            console.log('insdie conn !== null');
	        
	            disconnect();
	        }
        }
        else {
        	processerrors(r);
        	$(this).disable(false);
        }

        

        console.log('returning from #connect.clic()');



	});



	// Funciton to update the UI from present status - online/offline, connect/disconnect
    function update_ui(elem) {
        console.log('insdie update_ui()');

        $el = $(elem);
        $apilist.prepend($el);
        

        console.log('returning from update_ui()');
        
    }




    // Function to process inputs 
    function processinputs() { 

    	source = $('#source').val();
    	destination = $('#destination').val(); 
    	time = $('#time').val(); 
    	email = $('#email').val();
    	var r = 0;
    	if (source.length > 0) {
    		r = 1;
    	}
    	else {
    		r = -1;

    	}
    	if (destination.length > 0) {
    		r = 1;
    	}
    	else {
    		r = -2;
    	}
    	if (time.length > 0) {
    		r = 1;
    	}
    	else {
    		r = -3;
    	}
    	if (email.length > 0) {
    		r = 1;
    	}
    	else {
    		r = -4;
    	}

    	return r;

    }



    // Function to process the errors related to inputs
    function processerrors(r) {

    	if (r == -1) {
    		alert('source should be of form latitude,longitude. Example : 12.0875343,77.6318783');
    	}
    	else if (r == -2) {
    		alert('destination should be of form latitude,longitude. Example : 12.0875343,77.6318783');
    	}
    	else if (r == -3) {
    		alert('time should be of form hh:mm pm/am. Example : 08:00pm');
    	}
    	else if (r == -4) {
    		alert('email fiels can\'t be empty. Exmaple : abc@example.com');
    	}
    }




	// Funciton called when user disconnects using Disconnect button
    function disconnect() {
        console.log('insdie diconnect()');
        
        if (conn !== null) {
            console.log('insdieconn !== null');
        
            disconn = 1;
            conn.close();
        }

        console.log('returning from diconnect()');
        
    }



    // function called when user clicks on sumbit button, initated by click event
    function connect() {
        console.log('insdie connect()');
        
        // first call disconnect() to be clean any stale previous connections
        disconnect();



        var transports = ['websocket', 'xhr-streaming', 'xhr-polling', 'iframe-xhr-polling', 'iframe-eventsource', 'iframe-htmlfile', 'jsonp-polling'] ;

        // sockjs connection object created
        conn = new SockJS('http://' + window.location.host + '/ubernow', transports);

        // Sockjs onOpen event triggered when connection is opened and readystate is OPEN
        conn.onopen = function() {
            
            console.log('insdie conn.onopen()');
        

        };

        // sockjs onMessage event triggered whenever there is a message sent on the connection
        conn.onmessage = function(e) {
            console.log('insdie conn.onmessage()');
        
            var m = msgpack.decode(e.data);

            console.log('Message received : ',m);

            if (m.status === 'rabbitmqOK'){
            	sendmsg();
            }
            else {
            	var $apicall = null;

            	if (m.status === 'new_request') {
            		$apicall = $('<li class="stream"/>').html('['+m.req_time+'] New Request: Source- '+m.source+' Destination- '+m.destination+' Time- '+m.time+' Email- '+m.email);
            	}
            	else {

	            	$apicall = $('<li class="stream"/>').html('['+m.req_time+'] Requested '+m.typ+' Api for ['+m.email+']');
	            
	            	update_ui($apicall);
	        	}

        	}
        };

        // sockjs on Close event triggered whenever there is a close event either triggered by
        // server or by user itself via disconnect button -> disconnect()
        conn.onclose = function() {
            console.log('insdie conn.onclose()');
        
            if (errorconn !== 1) {
                console.log('insdie errorconn !== 1');
        
                if (disconn === 0) {
                    console.log('insdie disconn === 0');

                    alert('OOPs! Server is unavailable');
                } else {
                    console.log('insdie disconn !== 0');

                    disconn = 0;
                    alert('Connection To server closed');
                }
            } else if (errorconn === 1) {
                console.log('insdie errorconn === 1');

                alert('OOPs! Some error at server side');
                errorconn = 0;
            }

            conn = null;
        };

        // sockjs Error event triggered whenver there is an error connecting to the connection or
        // error info sent by server
        conn.onerror = function() {
            console.log('insdie conn.onerror');

            errorconn = 1;
        };

        console.log('returning from connect()');
        
    }






    // sends the actual msg after encoding via msgpack it to the connection via conn.send()
    function sendmsg() {
        console.log('insdie sendmsg()');

        var newmsg = { 
                'source' : source,
                'destination' : destination, 
                'destination_time' : {'hour' : hour,
                                      'mins' : mins, 
                                      'meridian' : meridian
                                     },
                'email' : email 
            
        };
        
        
        var res = msgpack.encode(newmsg);

        console.log('senign msg to websesocke conn.send : ', res);
        
        conn.send(res);

        console.log('returning from sendmsg()');
   
    }




});