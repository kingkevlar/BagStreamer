#!/usr/bin/env python

import rospy
import os
import rosbag
import rostopic
from collections import deque
import yaml
import rospkg
from bag_stream import BagStream

rospy.init_node('ooka')
stream = BagStream()
rospy.spin()