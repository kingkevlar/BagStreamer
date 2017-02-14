
#!/usr/bin/env python

import rospy
import os
import rosbag
import rostopic
from collections import deque
import yaml
import rospkg
from beginner_tutorials.srv import StartBagging

        
class BagStream(object):
    def __init__(self):

        '''
        - makes dictionary of dequeues
        - subscribes to set of topics defined by the yaml file in directory
        - have a streaming option that can be turned on and off in the callback
        - option to bag data
        - add a re subscribing option for anything that failed? maybe...? 
        '''

        rospack = rospkg.RosPack()
        directory  = os.path.join(rospack.get_path('beginner_tutorials'), 'scripts/')   
        self.directory = directory
        self.failed_topics = []
        
        self.make_dicts()
        self.subscribe()
        self.n = 0 # number of iterations   
        # self.resubscribe
       
        self.streaming = True
        self.dumping = False    

        self.bagging_service = rospy.Service('/bagging_server', StartBagging, self.start_bagging)

    def make_dicts(self):    
        '''
        make dictionaries with deques() that will be filled with topics
        with all of the 5topics defined by the yaml 
        '''
        with open(self.directory + 'topics_to_stream.yaml', 'r') as f:
            self.topics_to_stream = yaml.load(f)

        topics = self.topics_to_stream['TOPICS']
        self.topic_list = {}

        
        for topics in topics.values():
            self.topic_list[topics['message_topic']] = deque()

        rospy.loginfo('topics: %s', self.topic_list.keys())

    def subscribe(self):
        '''
        Immediately initiated when an instance of the BagStream class is created:
        subscribes to the set of topics defined in the yaml configuration file  
        '''
        # empty list that can be resubscribed to at a later time

        for topic in self.topic_list.keys():
            msg_class = rostopic.get_topic_class(topic)
            if msg_class[1] == None:
                self.failed_topics.append(topic)	
            else:
               rospy.Subscriber(topic, msg_class[0], lambda msg, _topic=topic: self.callback(msg, _topic))

    def callback(self, msg, topic):
        # stream, callback function does nothing if streaming is not active
        if self.streaming:
            self.n = self.n + 1
            self.topic_list[topic].append((rospy.get_rostime(), msg))
            
            time_diff = (self.topic_list[topic][-1][ 0].__sub__( 
                        self.topic_list[topic][ 0][ 0])).to_sec()
            hz = (self.topic_list[topic][-1][0].__sub__(self.topic_list[topic][-2][0])).to_sec()
            if self.n % 50 == 0:    
                rospy.loginfo('time_diff: %s', time_diff)
                rospy.loginfo('topic: %s', topic)
            if time_diff > 10:
                self.topic_list[topic].popleft()
            else:
                 pass
            # temp test delete
            # if self.n == 500:
            #     req.bagging = True
            #     self.start_bagging(req)

    def start_bagging(self, req):
        '''
        dumps all of the data to bags, temporarily stops streaming 
        during the bagging process, resumes streaming when over
        '''
        self.dumping = req.startbagging
        self.streaming = False
        bag = rosbag.Bag('ooka.bag', 'w')   

        rospy.loginfo('dumping value: %s', self.dumping)
        rospy.loginfo('bagging commencing!')
            
        for topic in self.topic_list.keys():
            rospy.loginfo('topic: %s', topic)
            for msgs in self.topic_list[topic]:

                bag.write(topic, msgs[1], t=msgs[0])
                # rospy.loginfo('topic: %s, message type: %s, time: %s', topic, type(msgs[1]), type(msgs[0]))
        
        bag.close()
        rospy.loginfo('bagging finished!')
        self.streaming = True  

        return True

if __name__ == "__main__":
    rospy.init_node('ooka')
    stream = BagStream()
    rospy.spin()