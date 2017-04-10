Method 1 - Optimized Prediction ( by using Google Maps optimized traffic model for future traffic predictions)
===============================================================================================================

In this method, since google gives you few traffic models via which you can predict future traffic duration to reach from point A to point B, we can pre decide the time.

**Example :** 
Request by User 1 - 

* Source - Bellandur
* Destination - Koramangala
* Time of giving request -  2pm
* Time to reach destination -  8pm.


Lets say, calls to **uber apis** as **UP**, and calls to **google maps apis** as **GP**, where **UP1**, **UP2**, **UP3...UPi** means the number of calls to Uber Apis, similarly **GP1**, **GP2**, **GP3**. All these numbering are per request basis. I mean suppose **user 1** sent the above request, then **UP1, UP2, UP3...GP1, GP2, GP3...etc** will be for **user 1**. For another user, these UPi's and GPi's set will be different though their numbering for each user will be same.


Step 1
-------

* UP1 at 2pm => result - 7 mins.
* GP1 at 2pm =>

Now GP1 will do 2 different types of requests, i.e based on 2 different traffic models of google Maps.

1. **Traffic Model = Best_Guess:** Takes departure time as input and sends the duration to reach as a best guess which considers past history at that time and current traffic conditions. 

2. **Traffic Model = Pessimistic:** Takes departure time as input and sends the duration to reach as a pessimistic time which considers the past history and gives a time which is higher than most days.


**NOTE :** We can use both models to build the predictions simultaneously and use one of them for few days and the other for some days and see which one gives us better results and then with continuous use, we will be able to choose one over the other eventually.

* **GP1.1** => Best Guess with dep. time = now(2pm) => result = 57mins
* **GP1.2** => Pessimistic with dep. time = now(2pm) => result = 70 mins

These our base rough estimations so that we can start our predictions from some base values.

* **best_guess_suitable_starting_times** = BST = { }
* **pessimistic_suitable_starting_times** = PST = { }
 


Step 2 (our real predictions start from this step)
---------------------------------------------------

**New dep. time** = 8pm - [57mins (best_guess) or 70mins (pessimistic)]
lets say, dep_t_b_g = 7.03pm and dep_t_p = 6.50pm

* **GP2.1** => Best Guess with dep. time as 7.03pm => result = 59mins
Difference to reach before 8pm = 57-59 = -2 (negative means its going to cross 8pm by 2 mins, so not a suitable starting time)

* **GP2.2** = Pessimistic with dep. time as 6.50pm => result = 72mins
Difference to reach before 8pm = 70-72 = -2 (negative means its going to cross 8pm by 2 mins, so not a suitable starting time)



Step 3
-------

**New dep. time** = 8pm - [59mins (best_guess) or 72mins (pessimistic)]
lets say, dep_t_b_g = 7.01pm and dep_t_p = 6.48pm

* **GP3.1** => Best Guess with dep. time as 7.01pm => result = 60mins
Difference to reach before 8pm = 59-60 = -1 (negative means its going to cross 8pm by 1 mins, so not a suitable starting time)

* **GP3.2** => pessimistic with dep. time as 6.48pm => result = 70 mins
Difference to reach before 8pm = 72-70 = 2 (positive means its going to reach 8pm earlier by 2 mins, so its a suitable starting time. Thus at this we will mark MIN diff for now as = 2 min)

* **PST** = { 6.48 : 2,  }



Step 4
-------

**New dep. time** = 8pm - [60mins (Best Guess) or 70mins (Pessimistic) ]
dep_t_b_g = 7pm and dep_t_p = 6.50 pm

* **GP4.1** => best_guess with dep. time as 7pm => result = 58mins
Difference to reach before 8pm = 60-58 =2  (positive means its going to reach 8pm earlier by 2 mins, so its a suitable starting time. Thus at this we will mark MIN diff for now as = 2 min)

* **BST** = { 7.00 : 2, } 

* **GP4.2** => pessimistic with dep. time as 6.50pm => result = 69mins
Difference to reach before 8pm = 70-69 =1  (positive means its going to reach 8pm earlier by 1 min, so its a suitable starting time. Thus at this we will mark MIN diff for now as = 1 min, since its less than the current MIN of 2 mins)

* **PST** = { 6.48 : 2,  6.50 : 1, } 



Step 5
-------

**New dep. time** = 8pm - [58mins (best_guess) or 69mins (pessimistic)]
dep_t_b_g = 7.02pm and dep_t_p = 6.51pm 

* **GP5.1** => best_guess with dep. time as 7.02min => result = 58mins
Difference to reach before 8pm = 58-58 =0  (positive means its going to reach 8pm earlier by 0 mins, so its a suitable starting time. Thus at this we will mark MIN diff for now as = 0 min, since its minimum than than the last minimum of 2 mins)      
                             
* **BST** = { 7.00 : 2, 7.02 : 0, } 

Here, in case of best_guess we found that if we leave at 7.02 pm we will reach at 8pm exact, i.e. the difference to reach before 8pm is minimal here, in this special case its 0. So we will stop our best case.

* **GP5.2** => pessimistic with dep. time as 6.51pm => result = 66mins
Difference to reach before 8pm = 69-66 =3  (positive means its going to reach 8pm earlier by 0 mins, so its a suitable starting time. Thus we will not change the minimum since its higher than the current MIN of 1min)  

* **PST** = { 6.48 : 2,  6.50 : 1, 6.51 : 3, } 



Hence we will continue the pessimistic until we get few possible suitable starting times as k-minimum of the list, where k can be 3 to 5 or more.

While in the process, anytime its possible that we get a negative time difference continuously for more than 3-5 times, then we will start going back in time by 5 mins and start the cases again.


**NOTE :** I tested the above method with different source and destination pairs and different reaching time per pair. So I tested for several combinations, and in all the cases I found this method to converge and give a result having minimum time difference as 0 at some point in time in more than majority of the cases.

You can say this method to be some kind of **heuristic** approach which has shown positive results although I tested it with only 30 combinations with consistent results.


Now what we are left with are **BST** and **PST**, now we have to somehow consider the **Uber APIs** and consider the **uber ETAs**. 

**NOTE :** Uber APIs are real time, we cannot pool uber apis for future time like we did for google apis.


For this we can start pooling Uber APIs with our base uber eta case, which was 7 mins.

So for  **BST = { 7.00 : 2, 7.02 : 0, }** we will start pooling uber at times equal to:

* **UP2.1** =  7.02pm - 7mins = 6.55pm
Now if eta is 2 mins, then we find that, we will have to start at 6.57. but we have our data as to start at 7.02 pm.
So 6.55 pm is not that suitable. 

We need a time, so that the eta for uber should reach as close to 7.02pm, i.e lets say if eta is 5mins at 6.55pm, then we can start our trip at 7.00pm which is closer to 7.02 pm than the earlier 6.57pm.

So 6.55 pm in this case when eta is 5 mins is better suitable time than the earlier one when eta was 2 mins.


So how to figure this out?
---------------------------

**Heuristic :**

Suppose initially we find **ETA** to be 2 mins. And our base case eta was 7mins.

* pessimistic eta = 7mins
* best_guess eta  = avg of previous etas = (7-2)/2 = 4.5 mins

So using **best_guess** we can again pool uber api for eta at (7.02pm - 4.5mins)= 06:57:30pm.

We need to consider if the time to pool uber api has already gone or not, if yes, then we simple pool uber api at current time, else we call at that future time, in this case at 06.57.30pm.

If eta at 6:57:30pm is 2 mins again, then we can start our trip at 6.59:30 which is close to 7.02pm positively by 2.5 mins.

Now in all this, we have to simultaneously consider the other options in the BST, for example in this case 7:00pm. 

Now we see that if we start at 6.57:30 pm then eta is 2 mins and uber will reach at 6.59:30pm which is only 30 seconds earlier to the 7:00pm option, in which we will reach our final destination earlier by 2 mins at 7.58pm.

So we can either choose this option or pool the uber apis again for a new eta.

Lets say we already pooled at 6.57:30pm with eta 2.

* pessimistic eta is still 7min
* best_guess eta  = avg of previous = (4.5-2)/2 = 3.25 mins

So a next suitable uber api pooling time would be 7.02pm - 3.25mins = 6.58:45 pm

Now if this time has not been gone than we can pool at this time and get new data or we can just choose the other above option.

**NOTE :** At anytime, when we see that our etas are becoming longer, we can just stop processing further and send that current time as the suitable time so as to not affect our actual destination reaching time by very big margins.

**NOTE :** This whole method was optimized prediction using google's traffic models.

There is another basic predictions which is not going to use google's future time traffic predictions and pool google apis always in real time. This basic prediction will be more difficult and will consider the assumption of deviation to be at most by 1 hour.


