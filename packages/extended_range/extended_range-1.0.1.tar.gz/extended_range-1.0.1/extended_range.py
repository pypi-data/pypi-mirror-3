#Defines an extended version of the range() BIF that along with the usual behaviour can also repeat each element of the list 
#a certain number of times in continuation.
def range_ext(start=0, stop=None, steps=1, reps=1):
#'reversed_range_list' is the variable that contains the list the function produces.
	reversed_range_list=[]
#This part ensures that the first argument is taken as the stop value if no second argument is provided.
	if stop==None:
		start_mod=0
		stop_mod=start
#This part is to ensure that if stop value is less than start value, the list is produced accordingly i.e. in a descending order.
	elif start>stop:
		start_mod=stop
		stop_mod=start
	else:
		start_mod=start
		stop_mod=stop
	for number in range(start_mod, stop_mod, steps):
		reversed_range_list=[number]*reps+reversed_range_list
	if stop==None:
#The list comes out in descending order. So we just need to reverse it.
		list.reverse(reversed_range_list)
	elif start<stop:
		list.reverse(reversed_range_list)
#If start value is greater than stop value, then the list is already in the order we want.
	return(reversed_range_list)
#Report any bugs or suggestions for improvement at bolt.khan@gmail.com
#range_ext version 1.0.1
                         
