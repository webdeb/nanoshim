# Define here all User Inputs like Buttons and Rotary Encoder
from machine import Pin
import rotary
from button import Button

ENCODER_LEFT = rotary.Rotary(0, 1, 2)
ENCODER_RIGHT = rotary.Rotary(3, 4, 5)
BUTTON = Button(12)
