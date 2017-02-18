#!/usr/bin/env python

import rospy
# from beginner_tutorials.srv import StartBagging
from std_srvs.srv import SetBool

def bagging_client():
	rospy.wait_for_service('/bagging_server')
	try: 
		bagging_server = rospy.ServiceProxy('/bagging_server', SetBool)
		bag_status = bagging_server(True)
	except rospy.ServiceException, e:
		print "/bagging_server failed: %s" %e


bagging_client()

# if __name__ == '__main__':
# 	rospy.wait_for_service('bagging_server')
# 	self.bagging_service = rospy.Service('bagging_server', StartBagging, self.start_bagging())
# 	self.bagging_service(True)
# 	rospy.spin()




# KKJJJKJJ