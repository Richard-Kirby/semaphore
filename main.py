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
    time.sleep(3)

pi = pigpio.pi()

class Servo:

    def __init__(self, pwm_pin, low_duty, high_duty):
        self.pwm_pin = pwm_pin
        self.low_duty = low_duty
        self.high_duty = high_duty

    def set_angle(self, angle):

        if angle < 0:
            pass
            servo_pulse = self.high_duty + (float(angle / 180) * (self.high_duty - self.low_duty))

        else:
            servo_pulse = int((float(angle / 180) * (self.high_duty - self.low_duty)) + self.low_duty)

        print(angle, servo_pulse)
        pi.set_servo_pulsewidth(self.pwm_pin, int(servo_pulse))


class SemaphoreFlagger(threading.Thread):

    def __init__(self, left_servo, right_servo, pause_time):
        threading.Thread.__init__(self)

        self.left_servo = left_servo
        self.right_servo = right_servo
        self.pause_time = pause_time
        self.cmd_queue = queue.Queue()

    def run(self):

        try:

            while True:

                if not self.cmd_queue.empty():
                    left_angle, right_angle = self.cmd_queue.get_nowait()

                    self.left_servo.set_angle(left_angle)
                    self.right_servo.set_angle(right_angle)

                    print(left_angle, right_angle)

                time.sleep(self.pause_time)

        except KeyboardInterrupt:
            pi.set_servo_pulsewidth(self.pwm_pin, self.low_duty)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise


if __name__ == "__main__":

    left_servo = Servo(27, 500, 2500)
    right_servo = Servo(9, 500, 2500)

    semaphore_flagger = SemaphoreFlagger(left_servo, right_servo, 0.6)

    semaphore_flagger.start()


    print("home")
    semaphore_flagger.cmd_queue.put_nowait((0,0))
    time.sleep(5)


    try:
        while True:

            semaphore_flagger.cmd_queue.put_nowait((-1, 0))
            semaphore_flagger.cmd_queue.put_nowait((-30, 30))
            semaphore_flagger.cmd_queue.put_nowait((-90, 90))
            semaphore_flagger.cmd_queue.put_nowait((-120, 120))
            semaphore_flagger.cmd_queue.put_nowait((-180, 180))

            print("start")
            time.sleep(1)


    except KeyboardInterrupt:
        print("Quitting the program due to Ctrl-C")

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    finally:
        print("\nTidying up")
        pi.stop()
