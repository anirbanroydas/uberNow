uberNow
========

It is an app to notify users via email as to when to book an uber as per given time to reach a specified destination from a specified source.


Documentation
--------------

**Link :** http://uberNow.readthedocs.io/en/latest/


Project Home Page
--------------------

**Link :** https://pypi.python.org/pypi/uberNow



Details
--------


:Author: Anirban Roy Das
:Email: anirban.nick@gmail.com
:Copyright(C): 2016, Anirban Roy Das <anirban.nick@gmail.com>

Check ``uberNow/LICENSE`` file for full Copyright notice.




Overview
---------

uberNow is a small web app which takes four inputs from the user and notifies the user via email as to when to book an Uber.

All you(the user) have to do is give the 4 required inputs and submit the request. The app will take care of the rest.

The inputs are:

* A. source
* B. destination
* C. email address 
* D. time to reach destination 



It uses `Tornado <http://www.tornadoweb.org/>`_ as the application server. The web app is created using the `sockjs <https://github.com/sockjs/sockjs-client>`_ protocol. **SockJS** is implemented in many languages, primarily in Javascript to talk to the servers in real time, which tries to create a duplex bi-directional connection between the **Client(browser)** and the **Server**. Ther server should also implement the **sockjs** protocol. Thus using the  `sockjs-tornado <https://github.com/MrJoes/sockjs-tornado>`_ library which exposes the **sockjs** protocol in `Tornado <http://www.tornadoweb.org/>`_ server.

It first tries to create a `Websocket <https://en.wikipedia.org/wiki/WebSocket>`_ connection, and if it fails then it fallbacks to other transport mechanisms, such as **Ajax**, **long polling**, etc. After the connection is established, the tornado server **(sockjs-tornado)** calls `Uber Apis <https://developer.uber.com>`_ and `Google Maps Apis <https://developers.google.com/maps/>`_ to process the requests.



Technical Specs
----------------


:sockjs-client (optional): Advanced Websocket Javascript Client used in **webapp example**
:Tornado: Async Python Web Library + Web Server
:sockjs-tornado: SockJS websocket server implementation for Tornado
:Uber Time-Estimation Apis: HTTP Rest APIs to estimate time required to book an uber at given time
:Google Maps Distance-Matrix Apis: HTTP Rest Apis to calculate distance and duration to reach from source to destination



Features
---------

* Web App 
* Email Notification
* Uber Booking Reminder




Installation
------------

Prerequisites
~~~~~~~~~~~~~

1. python 2.7+
2. tornado
3. sockjs-tornado 
4. sockjs-client (optional, just for example webapp)


Install
~~~~~~~
::

        $ pip install uberNow

If above dependencies do not get installed by the above command, then use the below steps to install them one by one.

 **Step 1 - Install pip**

 Follow the below methods for installing pip. One of them may help you to install pip in your system.

 * **Method 1 -**  https://pip.pypa.io/en/stable/installing/

 * **Method 2 -** http://ask.xmodulo.com/install-pip-linux.html

 * **Method 3 -** If you installed python on MAC OS X via ``brew install python``, then **pip** is already installed along with python.


 **Step 2 - Install tornado**
 ::

         $ pip install tornado

 **Step 3 - Install sockjs-tornado**
 ::

         $ pip install sockjs-tornado






Usage
-----

After having installed uberNow, just run the following commands to use it:


* **Start uberNow Applcation**
  ::

          $ uberNow [options]

  - **Options**

    :--port: Port number where the uberNow app will start
    :--log_path: Path where the application will log the details

    **default** : ``/usr/local/var/uberNow/log/uberNow.log``


  - **Example**
    ::

          # Starting the server
          $ uberNow --port=9191

          # Starting the server with custom log path
          $ uberNow --port=9191 --log_path=projects/ubernow/log/ubernow.log        
  
* **Stop uberNow**



  Click ``Ctrl+C`` to stop the server.


* **More Details** 

  Please follow the documentation for more usage details. Documentation link is `this <http://uberNow.readthedocs.io/en/latest/>`_.

Todo
-----

1. Add Blog post regarding this topic.


