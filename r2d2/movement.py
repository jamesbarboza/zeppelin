import RPi.GPIO as GPIO
import time


backmotor_a = 7
backmotor_b = 5
backmotor_pwm = 3

frontmotor_a = 8
frontmotor_b = 10
frontmotor_pwm = 12

GPIO.cleanup()


def setup():
    GPIO.setmode(GPIO.BOARD)
    print('mode set to BOARD')

    # back motor
    GPIO.setup(backmotor_a, GPIO.OUT)
    GPIO.setup(backmotor_b, GPIO.OUT)
    GPIO.setup(backmotor_pwm, GPIO.OUT)
    print('back motor set up')

    # front motor
    GPIO.setup(frontmotor_a, GPIO.OUT)
    GPIO.setup(frontmotor_b, GPIO.OUT)
    GPIO.setup(frontmotor_pwm, GPIO.OUT)
    print('front motor set up')


def stop():
    GPIO.cleanup()
    setup()


def move_forward():

    GPIO.output(backmotor_a, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(backmotor_b, GPIO.LOW)
    time.sleep(1)
    back_pwm = GPIO.PWM(backmotor_pwm, 1000)
    time.sleep(1)
    back_pwm.start(100)  # Set duty cycle to 50%
    print('back motor started')

    GPIO.output(frontmotor_a, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(frontmotor_b, GPIO.LOW)
    time.sleep(1)
    front_pwm = GPIO.PWM(frontmotor_pwm, 1000)
    time.sleep(1)
    front_pwm.start(100)  # Set duty cycle to 50%

    print('front motor started')



def move_backward():
    GPIO.output(backmotor_a, GPIO.LOW)
    GPIO.output(backmotor_b, GPIO.HIGH)
    back_pwm = GPIO.PWM(backmotor_pwm, 1000)
    back_pwm.start(100)  # Set duty cycle to 50%

    GPIO.output(frontmotor_a, GPIO.LOW)
    GPIO.output(frontmotor_b, GPIO.HIGH)
    front_pwm = GPIO.PWM(frontmotor_pwm, 1000)
    front_pwm.start(100)  # Set duty cycle to 50%




from pynput import keyboard

def on_press(key):
    try:
        if key == keyboard.Key.up:
            stop()
            move_forward()
        elif key == keyboard.Key.down:
            print('Down arrow pressed')
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def run():
    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Stopping movement")
        stop()
    except Exception as e:
        print(f"An error occurred: {e}")
        stop()
    finally:
        print("Cleaning up GPIO")
        GPIO.cleanup()
