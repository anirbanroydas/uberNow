Problem Statement
==================

Short Version
--------------

Given four inputs, (a). **Source** (b). **Destination** (c). **Email Address** (d). **Time of the day to reach the destination**, send an email to the given email address about booking its uber at that very moment so that you have ample time to reach your destination which takes into consideration the following conditions:

* Time the uber driver will take to reach your source.
* Time it will take to reach your destination in the current live traffic conditions.
* Whether you will be actually be able to book an uber at that very moment or not or will it take some time before you can actually book a cab.
* The actual time when you reach your destination should be as accurate or close to the pre defined time as possible.


Long Version with example
--------------------------

Given four inputs, (a). **Source** (b). **Destination** (c). **Email Address** (d). **Time of the day to reach the destination**. Assume that source and destination are provided as latitude/longitude and not as addresses(to keep things simple). The app needs to find the exact time a user needs to book an uber to be at that destination at that time. An email needs to be sent to the above email ID at this time saying “Time to book an uber!”

**Example:** I am in Koramangala(12.927880, 77.627600) and need to be in Hebbal(13.035542, 77.597100) at 8:00 PM for a meeting. The app will have to email me at 6:43 PM because the uberGO will take 9 mins to reach me at 6:43 PM(as per uber) and it takes 68 mins to drive from Koramangala to Hebbal(as per google maps)

**Assumptions:**

* To keep things simple, whatever the uber api and google maps api tell is true.
* Time to arrive at the destination is within today. The time entered is in IST.
* Not considering cases where it’s already too late to book the uber. Assuming that there is still some time left.
* The maximum deviation of driving times at any time of the day is 60 mins. That means, if it takes 40 mins to drive from Koramangala to Hebbal now, assume that it’s not more than 100 mins at any time of the day.
* The cab is UberGO.
* Accuracy is the most important factor.
* Second important factor is optimization of requests to the APIs. Pinging the APIs every minute to see if you should leave now is not the best solution.


**Clarifications:**

1. Lets say you want to reach destination B at 8:00 pm starting from source A at 7:30 pm, the travel time is 25 minutes but the next time you pool google api, it says now the travel time is 40 mins. In such case its already to late to book an uber.

2. Lets say, first time you pool google api and it says that it will take 1 hour from source A to destination B. But next time you check the google api, it says 1:45 mins (Huge Traffic Jam) and then next time it say 2:15 mins (It started raining :( ). You can assume that the maximum deviation is 1 hour at any time of the day i.e max it will take 2 hours to reach destination.
