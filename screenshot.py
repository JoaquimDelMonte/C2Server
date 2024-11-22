from PIL import ImageGrab



def screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    screenshot.show()
    screenshot.close()


# MAIN FUNCTION

if __name__ == "__main__":

    screenshot()