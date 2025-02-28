import cv2
import os
import tkinter as tk
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, Canvas,font
from PIL import Image, ImageTk
import numpy as np
from tkinterdnd2 import TkinterDnD, DND_FILES
#Encode
def encode_message():
    if not selected_image_path:
        messagebox.showerror("Error", "Please select an image first.")
        return

    secret_text = message_entry.get()
    if not secret_text:
        messagebox.showerror("Error", "Please enter a message to encode.")
        return
    global output_file
    output_file = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI Video", "*.avi")])

    if output_file:
        image = encode(selected_image_path, secret_text)
        try:
          # Read the first image to determine frame size
          # Convert the Pillow image to a NumPy array
          image_array = np.array(image)
          # Access the shape of the NumPy array
          height, width, _ = image_array.shape
          # Initialize the VideoWriter
          fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # Codec for AVI
          fps = 24  # Frames per second
          video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
        
          # Add each image to the video
          fps = 24  # Frames per second
          frames_to_repeat = 120
          resized_image = cv2.resize(image_array, (width, height))  # Resize if needed
          for _ in range(frames_to_repeat):
            video_writer.write(resized_image)
          video_writer.release()
          status_label.config(text=f"Video saved to {output_file}.")
          message_entry.delete(0, "end")
          messagebox.showinfo("Success", "Video created successfully!")
        except Exception as e:
          status_label.config(text=f"Error: {e}")
          messagebox.showerror("Error", f"Failed to create video: {e}")
def encode(selected_image_path, secret_text):
  s = selected_image_path.find("{")
  e= selected_image_path.find("}")
  if s!=-1 and e!=-1:
    selected_image_path = selected_image_path[s+1:e]
  image = Image.open(selected_image_path)
  image = image.convert('RGB')
  image = np.array(image)
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  image = np.array(image)
  message=message_entry.get()
  string=""
  a=0
  for i in (secret_text):
    mess=ord(i)
    mess2=bin(mess)
    mess3=int(mess2[2:])
    string=string+"{:09d}".format(mess3)
  width, height = image.shape[:2]
  total=width*height*3
  string=string+("0"*total)
  img=[]
  for y in range(height):
      row=[]
      for x in range(width):
          columns=[]
          b, g, r = image[y, x]
          if(b%2!=0):
            b=b-1
            if(string[a]=="0"):
              a+=1
            else:
              b+=1
              a+=1
          else:
            if(string[a]=="0"):
              a+=1
            else:
              b=b+1
              a+=1
          if(g%2!=0):
            g=g-1
            if(string[a]=="0"):
              a+=1
            else:
              g+=1
              a+=1
          else:
            if(string[a]=="0"):
              a+=1
            else:
              g=g+1
              a+=1
          if(r%2!=0):
            r=r-1
            if(string[a]=="0"):
              a=a+1
            else:
              r=r+1
              a+=1
          else:
            if(string[a]=="0"):
              a+=1
            else:
              r=r+1
              a+=1

          columns.append(b)
          columns.append(g)
          columns.append(r)
          row.append(columns)
      img.append(row)
  img=np.array(img, dtype=np.uint8)
  image=Image.fromarray(img)
  return image

#Decode
def decode_message():
    global selected_image_path
    if not selected_image_path:
        messagebox.showerror("Error", "Please select an image first.")
        return
    # Open the video file
    video = cv2.VideoCapture(selected_image_path)

    # Check if the video was opened successfully
    if not video.isOpened():
        messagebox.showerror("Error", "Failed to open the video.")
        

    # Read a single frame from the video
    ret, image = video.read()
    image = Image.fromarray(image)

    # Check if the frame was successfully read
    if ret:
        status_label.config(text=f"Frame extracted.", fg="maroon", font=("Arial", 10, "bold"))
    else:
        status_label.config(text=f"Error: Unable to Extract a frame.", fg="maroon", font=("Arial", 10, "bold"))

    decoded_message = decode(image)
    if decoded_message:
        messagebox.showinfo("Decoded Message", f"Hidden message: {decoded_message}")
        status_label.config(text=f"Decoding done.", fg="maroon", font=("Arial", 10, "bold"))
    else:
        messagebox.showerror("Error", "Failed to decode the message.")
def decode(image):
    img = np.array(image)

    secret=""
    width, height = img.shape[:2]

    for i in range(len(img)):
      for j in range(len(img[0])):
        for k in range(3):
          if(not((j%3==0)and(k==0))):
            if(img[i][j][k]%2!=0):
              secret=secret+"1"
            else:
              secret=secret+"0"
    c="a"
    strin=""
    while(c!="00000000"):
      c=secret[0:8]
      secret=secret[8:]
      binary_string = c
      ascii_character = chr(int(binary_string, 2))
      strin+=ascii_character
    return strin

# Tkinter GUI
def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])
    if file_path:
        global selected_image_path
        selected_image_path = file_path
        img = Image.open(file_path)
        tk_img = ImageTk.PhotoImage(img)
        new_width = 170
        new_height = int((new_width / float(img.width)) * img.height)
        Img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(Img)
        canvas.config(width=new_width, height=new_height)
        global image_id
        image_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)
        canvas.image = tk_img 
        status_label.config(text=f"Inserted: {file_path}", fg="maroon", font=("Arial", 10, "bold"))
def select_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.avi")])
    global selected_image_path
    selected_image_path = file_path
    file_path = file_path.strip("{}")
    video = cv2.VideoCapture(file_path)
    status_label.config(text=f"Selected: {file_path}")
    def play_video():
         ret, frame = video.read()
         if ret:
            # Convert the frame (BGR to RGB) for Tkinter compatibility
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            tk_img = ImageTk.PhotoImage(image)

            # Update the image on the canvas
            canvas.image = tk_img  # Keep a reference to prevent garbage collection
            new_width = 170
            new_height = int((new_width / float(image.width)) * image.height)
            Img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(Img)
            canvas.config(width=new_width, height=new_height)
            global image_id
            image_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)

            # Schedule the next frame update
            root.after(10, play_video)
         else:
            video.release()
    play_video()
def remove_image():
    global image_id
    if canvas.winfo_exists() and image_id:
        canvas.delete(image_id)
        status_label.config(text=f"Image Removed", fg="maroon", font=("Arial", 10, "bold"))
    image_id=None
def remove_video():
    if canvas.find_all(): canvas.delete("all")
    status_label.config(text=f"Video Removed", fg="maroon", font=("Arial", 10, "bold"))
def quit_action():
    print("Quit action triggered!")
    root.destroy()
def padded_label(label, shortcut, width=25):
    return f"{label.ljust(width)}{shortcut}"
# Initialize Tkinter
root = TkinterDnD.Tk()
root.title("I2V Code")
root.geometry("500x700")
root.configure(bg="light yellow")
selected_image_path = None
global image_id
image_id=None
#Shortcuts
root.bind("<Control-d>", lambda event: decode_message())
root.bind("<Control-e>", lambda event: encode_message())
root.bind("<Control-q>", lambda event: quit_action())
root.bind("<Control-i>", lambda event: select_image())
root.bind("<Control-r>", lambda event: remove_image())
#About
def about():
    # Create a new top-level window
    text_window = tk.Toplevel(root)
    text_window.title("About")
    text_window.geometry("250x150")
    
    # Add a label to display text
    text_label = tk.Label(text_window, text=f"Developed By: \nRAMANA \nJUHI \nand \nPHANI", fg="green", font=("Arial Black", 10, "bold"))
    text_label.pack(pady=20)

#Menu Bar
menu_bar = tk.Menu(root)
monospace_font = font.Font(family="Consolas", size=11)
file_menu = tk.Menu(menu_bar, tearoff=0,font=monospace_font)
file_menu.add_command(label=padded_label("Insert Image","Ctrl+I"), command=select_image)
file_menu.add_command(label=padded_label("Remove Image","Ctrl+R"), command=remove_image)
file_menu.add_command(label=padded_label("Encode","Ctrl+E"), command=encode_message)
file_menu.add_command(label=padded_label("Decode","Ctrl+D"), command=decode_message)
file_menu.add_separator()
file_menu.add_command(label=padded_label("Exit","Ctrl+Q"), command=quit_action)
menu_bar.add_cascade(label="File", menu=file_menu)

info = tk.Menu(menu_bar, tearoff=0)
info.add_command(label="About", command=about)
menu_bar.add_cascade(label="Info", menu=info)

root.config(menu=menu_bar)


#Canvas
canvas = tk.Canvas(root, width=180, height=180, bg="light yellow", highlightbackground="light yellow", highlightthickness=0, bd=0)
canvas.pack()



# UI Elements
select_button = Button(root, text="Insert Image", command=select_image, bg="blue", fg="white", font=("Monotype Corsiva", 16))
select_button.pack(pady=10)

select_button = Button(root, text="Insert Video", command=select_video, bg="blue", fg="white", font=("Monotype Corsiva", 16))
select_button.pack(pady=10)

remove_button = Button(root, text="Remove Image", command=remove_image, bg="blue", fg="white", font=("Monotype Corsiva", 16))
remove_button.pack(pady=10)

remove_button = Button(root, text="Remove Video", command=remove_video, bg="blue", fg="white", font=("Monotype Corsiva", 16))
remove_button.pack(pady=10)

message_label = Label(root, text="Enter Message to Encode:", fg="maroon", font=("Arial", 16), bg="light yellow")
message_label.pack(pady=10)

message_entry = Entry(root, width=50, fg="maroon", font=("Lucida Calligraphy", 16))
message_entry.pack(pady=5)

encode_button = Button(root, text="Encode Message", command=encode_message, bg="blue", fg="white", font=("Monotype Corsiva", 16))
encode_button.pack(pady=10)

decode_button = Button(root, text="Decode Message", command=decode_message, bg="blue", fg="white", font=("Monotype Corsiva", 16))
decode_button.pack(pady=10)

status_label = Label(root, text="Status: Waiting for action...", bg="light yellow", fg="maroon", font=("Arial", 10, "bold"))
status_label.pack(pady=15)

# Run the application
root.mainloop()
