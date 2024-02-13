#!/usr/bin/env python3
import cv2
import mediapipe as mp 
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

mp_hands = mp.solutions.hands
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

vid = cv2.VideoCapture(0)
def func():
    init_point_x = None
    init_point_y = None
    with mp_hands.Hands(min_tracking_confidence = 0.5, min_detection_confidence = 0.5) as model:
        while True:
            ret, frame = vid.read()

            if ret == False or cv2.waitKey(1) == ord("q"):
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            image.flags.writeable = False
            results = model.process(frame)
            image.flags.writeable = True

            image_height, image_width = image.shape[0], image.shape[1]
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    x_coods = list()
                    y_coods = list()
                    for ids, landmarks in enumerate(hand_landmarks.landmark):
                        cx, cy = int(landmarks.x * image_width) , int(landmarks.y * image_height)
                        x_coods.append(cx)
                        y_coods.append(cy)
                    sum_point_x = int(sum(x_coods)/len(x_coods))
                    sum_point_y = int(sum(y_coods)/len(y_coods))
                    ##calculate displacement
                    if init_point_x is not None and init_point_y is not None:
                        #calculate displacement
                        disp_x = sum_point_x - init_point_x
                        disp_y = sum_point_y - init_point_y
                        return (disp_x, disp_y)


                    cv2.circle(frame, (sum_point_x, sum_point_y), 5, (0, 0, 255), -1)
                    ##update the init_x, init_y values
                    init_point_x = sum_point_x
                    init_point_y = sum_point_y

                        

                ###mp_drawing.draw_landmarks(
                ###    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS    
                ##)
            #frame = cv2.flip(frame, 1)
            cv2.imshow("", frame)

    vid.release()
    cv2.destroyAllWindows()

class Publisher(Node):
    def __init__(self):
        super().__init__("Publisher")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.timer = self.create_timer(0.5, self.callback)

    def callback(self):
        vals = func()
        msg = Twist()
        
        if vals is not None:
            x_delta, y_delta = vals
            msg.linear.x = msg.linear.x + (x_delta * 0.1)
            msg.linear.y = msg.linear.y + (y_delta * -0.1)
            self.publisher.publish(msg)
        
        

def main(args = None):
    rclpy.init(args = args)

    node = Publisher()
    rclpy.spin(node)

    rclpy.shutdown()

if __name__ == "__main__":
    main()

