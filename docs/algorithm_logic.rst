Algorithm & Logic
==================

This project does not have a definitive solution. Its an open ended problem. So the attempt to solve the problem is to find a good solution that solves the problem with as much less complexity and as much better scalability as possible. Since this is an open ended problem, the solutions and algorithms put forward here may not be convincing to you but this is the one that is being used to solve this project presently. You can fork the project and apply your own logic to it. Send a PR and we will see if it improves upon the present logic.

Before moving forward lets discuss the problem first and why a straight definitive solution is not possible here.


Discussion
-----------

The Uber Api only allows to check for drivers and book can instantly. Now whenever you try to book anduber its not always certain that the cab will be present in your area and thus you have to keep  checking once in a while to book a cab if no cabs present at the time you are trying to book. There is not provision to book an uber for a furture time. Its always on the spot instant booking.

This means being certain about uber cab booking is difficult and you have to have hitory of booking data to be certain that at a particular time and place what is the probability that you will get a successful booking. Also you sometimes have to book the cab in advance even if taht means reaching destination before but its always better thatn reaching destination after the specified time. That means piniding uber api in intervals is a safe (not the best) way to start.




.. toctree::
   :maxdepth:2

   logic_method_1
   logic_method_2

