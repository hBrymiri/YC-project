import requests 

files={
    "images":open("images.jpg","rb"),
    "video":open("clip.mp4","rb"),
}

r = requests.post("SubDocu/KnownFolder/subBryan.py",files=files)
