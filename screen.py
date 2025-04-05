import RPi.GPIO as GPIO  
from board import SCL, SDA
import busio
import time
import adafruit_ssd1306


class Pages:
    def __init__(self, pgNumber, title, display, unit, sensor):
        self.lastValues = []
        self.pgNumber = pgNumber
        self.pgTitle = title
        self.display = display
        self.unit = unit
        self.sensor = sensor #this is a reference to a function that should be passed in initialization

    def page_write(self):
        """
        Auxiliary function to create the pages
        """
        if not isinstance(self.sensor(), str):
                value = round(self.sensor(), 2)
        else:
                value = self.sensor()
        self.lastValues.append(value)
        if len(self.lastValues) == 11:
            del self.lastValues[0]
        self.display.fill(0)
        self.display.text(str(self.pgTitle), 6, 8, 1)
        self.display.text((str(value) + self.unit), 6, 17, 1)
        self.display.show()
        
class managerPages:
    """
    THIS IS A DEQUE TO MANAGE THE PAGES ON THE DISPLAY
    """

    def __init__(self, display):
        self.size = 0 #how many pages
        self.display = display
        self.currPage = 0
        self.pageList = []

    def push(self, page):
        """
        Creates the page and adds it to the array containing all pages
        """

        self.pageList.append(page)
        self.size += 1
        return 1
    
    def next(self):
        """
        Goes to next page
        """
        if self.currPage == self.size - 1:
            self.currPage = 0
        else:
            self.currPage += 1

        self.pageList[self.currPage].page_write()
        return 1
    
    def previous(self):
        """
        Goes to previous page
        """
        if self.currPage == 0:
            self.currPage = self.size
        else:
            self.currPage -= 1

        self.pageList[self.currPage].page_write()
        return 1

    def pop(self, pageNum):
        """
        Destroys a page with a given number
        """

        for i in self.pageList:
            if i.pgNumber == pageNum:
                self.next()
                self.size -= 1 
                return 1
            
        self.pageList.pop(pageNum)
        return 0
    
    def get(self, pageNum):
        """
        Displays the given page on the LCD
        """

        for i in self.pageList:
            if i.pgNumber == pageNum:
                i.page_write()
                return 1
        
        return 0

    def update(self):
        """
        Updates current page
        """
        #self.printPast()
        self.pageList[self.currPage].page_write()

    def printPast(self):
        """
        Prints last 10 values captured by the sensors
        """
        print(self.pageList[self.currPage].lastValues)
