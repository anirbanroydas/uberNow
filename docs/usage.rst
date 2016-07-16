Usage
=====

After having installed uberNow, just run the following commands to use it:
          
uberNow Application
--------------------------

1. Start Server
   ::          
        
        $ uberNow [options]
        
2. Options    
   
   :--port: Port number where the uberNow app will start
   :--log_path: Path where the application will log the details

   **default** : ``/usr/local/var/uberNow/log/uberNow.log``
   
   * **Example**
     :: 
             
             # Starting the server
             $ uberNow --port=9191

             # Starting the server with custom log path
             $ uberNow --port=9191 --log_path=projects/ubernow/log/ubernow.log 
             
             
3. Stop uberNow Server
   
   Click ``Ctrl+C`` to stop the server.



