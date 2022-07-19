from picamera import PiCamera

camera = PiCamera()
camera.capture("/home/davidcalles/Pictures/pic0.jpg")
print("Done.")