from pygame.sprite import Group
from pygame.sprite import Sprite
from threading import Thread
from time import sleep
import pygame_textinput
import pygame
import pygame.font
import random
import sys
import time

from finalimu.msg import fimu
from std_msgs.msg import String
import rospy

version = "2.24.19.20.04"
yaw = 0
mode = "dev" # "dev" \\ "prod"
screen_width = 290
screen_height = 290
background_color = (0,0,0)
text_color = (255, 255, 255)


class Nav_Arrow(Sprite):
    
    global yaw

    def __init__(self, screen):
        """Initialize the triangle and set its starting position."""
        super(Nav_Arrow, self).__init__()
        self.screen = screen

        self.image = pygame.image.load('images/icon.png')
        self.rect = self.image.get_rect()

        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)

    def blitme(self):
        rect = self.image.get_rect()
        image = self.image

        if (mode == "prod"):
            image = pygame.transform.rotate(image, yaw * -1)

        if (mode == "dev"):
            image = pygame.transform.rotate(image, float(yaw) * -1)

        rect = image.get_rect(center=rect.center)

        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)

        self.rect.centerx = 300
        self.rect.centery = 300

        self.screen.blit(image, rect)


class Scoreboard():


    def blitme(self):
        self.screen.blit(self.high_score_image, self.high_score_rect)


    def update(self):
        high_score = float(yaw)
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str, True, self.text_color, background_color)

        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.high_score_rect.top


    def __init__(self, screen):
        """Initializing scorekeeping attributes."""
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 48)

        self.update()


def begin():
    pygame.init()

    listener() # Start listening to ROS

    screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption('Rover Heading ' + version)

    scoreboard = Scoreboard(screen)

    nav_arrow = Nav_Arrow(screen)

    while True:

        check_control_events()

        nav_arrow.update()

        scoreboard.update()

        update_screen(screen, scoreboard, nav_arrow)


def callback(data):
    global yaw

    if (mode == "prod"):
        yaw = data.yaw.yaw
        #print("callback(): [PROD]: ", yaw)

    if (mode == "dev"):
        yaw = data.data
        print("callback(): [DEV]: ", yaw)


def check_control_events():
    # Respond to keypress and mouse events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()


def check_keydown_events(event):
    if event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event):
    pass


def listener():

    status = rospy.init_node('listener', anonymous=True)
    print("Status", status)

    if mode == "prod":
        rospy.Subscriber("imu", fimu, callback)

    elif mode == "dev":
        rospy.Subscriber("chatter", String, callback)


def update_screen(screen, scoreboard, nav_arrow):
    screen.fill(background_color)
    scoreboard.blitme()
    nav_arrow.blitme()
    pygame.display.flip()


begin()
