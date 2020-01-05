# !/usr/bin/env python3

import pigpio
import threading
import time
import sys
import subprocess
import queue
import os

"""
This bit just gets the pigpiod daemon up and running if it isn't already.
The pigpio daemon accesses the Raspberry Pi GPIO.  
"""
p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
out, err = p.communicate()

if len(out.strip()) == 0:
    os.system("sudo pigpiod")

pi = pigpio.pi()


class Servo(threading.Thread):
    def __init__(self, pwm_pin, low_duty, high_duty, pause_time):
        threading.Thread.__init__(self)

        self.pwm_pin = pwm_pin
        self.low_duty = low_duty
        self.high_duty = high_duty
        self.pause_time = pause_time
        self.cmd_queue = queue.Queue()

    def run(self):

        try:

            while True:

                if not self.cmd_queue.empty():
                    angle = self.cmd_queue.get_nowait()
                    servo_pulse = int((float(angle/180) * (self.high_duty - self.low_duty))+ self.low_duty)

                    print(angle, servo_pulse)
                    pi.set_servo_pulsewidth(self.pwm_pin, int(servo_pulse))

                time.sleep(self.pause_time)

        except KeyboardInterrupt:
            pi.set_servo_pulsewidth(self.pwm_pin, self.low_duty)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise


if __name__ == "__main__":

    left_servo = Servo(27, 500, 2500, 0.5)
    right_servo = Servo(9, 500, 2500, 0.5)

    left_servo.start()
    right_servo.start()

    print("home")
    left_servo.cmd_queue.put_nowait(0)
    right_servo.cmd_queue.put_nowait(0)
    time.sleep(5)


    try:
        while True:
            left_servo.cmd_queue.put_nowait(0)
            left_servo.cmd_queue.put_nowait(30)
            left_servo.cmd_queue.put_nowait(60)
            left_servo.cmd_queue.put_nowait(90)
            left_servo.cmd_queue.put_nowait(120)
            left_servo.cmd_queue.put_nowait(150)
            left_servo.cmd_queue.put_nowait(180)

            right_servo.cmd_queue.put_nowait(0)
            right_servo.cmd_queue.put_nowait(30)
            right_servo.cmd_queue.put_nowait(60)
            right_servo.cmd_queue.put_nowait(90)
            right_servo.cmd_queue.put_nowait(120)
            right_servo.cmd_queue.put_nowait(150)
            right_servo.cmd_queue.put_nowait(180)

            print("start")
            time.sleep(1)


    except KeyboardInterrupt:
        right_servo.cmd_queue.put_nowait(0)
        left_servo.cmd_queue.put_nowait(0)
        time.sleep(1)
        print("Quitting the program due to Ctrl-C")

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    finally:
        print("\nTidying up")
        pi.stop()
