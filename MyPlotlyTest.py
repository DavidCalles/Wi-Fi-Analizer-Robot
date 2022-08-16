# import plotly.io as pio
# import plotly.express as px
# import plotly.plotly as py
# pio.renderers.default = "vscode"

# fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
# fig.show()
# print("Done")
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# from matplotlib import animation
# import time
# import cv2

# #plt.axis([0,600,0,350])
# fig = plt.figure(figsize=(6,4), facecolor="white")
# ax = plt.gca()
# ax.axes.xaxis.set_visible(False)
# ax.axes.yaxis.set_visible(False)
# plt.ion()
# plt.show()
# while(1):

#     img = mpimg.imread('Retrieve_Wi-Fi_Data/Pictures/fig0.jpeg')
#     imgplot = plt.imshow(img)
    
#     plt.draw()
#     plt.pause(0.001)

#     time.sleep(1)
#     print("next")
import cv2
import time
index = 0
while(1):
    img = cv2.imread('RetrieveVideoFeed/Pictures/Img2.jpg', cv2.IMREAD_COLOR)
    cv2.imshow(f"image", img)
    cv2.waitKey(100)
    time.sleep(3)
    index+=1
    print("Hi")

cv2.destroyAllWindows()