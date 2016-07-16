Overview
=========

uberNow is a small web app which takes four inputs from the user and notifies the user via email as to when to book an Uber.

All you(the user) have to do is give the 4 required inputs and submit the request. The app will take care of the rest.

The inputs are:

* A. source
* B. destination
* C. email address 
* D. time to reach destination 



It uses `Tornado <http://www.tornadoweb.org/>`_ as the application server. The web app is created using the `sockjs <https://github.com/sockjs/sockjs-client>`_ protocol. **SockJS** is implemented in many languages, primarily in Javascript to talk to the servers in real time, which tries to create a duplex bi-directional connection between the **Client(browser)** and the **Server**. Ther server should also implement the **sockjs** protocol. Thus using the  `sockjs-tornado <https://github.com/MrJoes/sockjs-tornado>`_ library which exposes the **sockjs** protocol in `Tornado <http://www.tornadoweb.org/>`_ server.

It first tries to create a `Websocket <https://en.wikipedia.org/wiki/WebSocket>`_ connection, and if it fails then it fallbacks to other transport mechanisms, such as **Ajax**, **long polling**, etc. After the connection is established, the tornado server **(sockjs-tornado)** calls `Uber Apis <https://developer.uber.com>`_ and `Google Maps Apis <https://developers.google.com/maps/>`_ to process the requests.

