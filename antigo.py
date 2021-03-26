import numpy as np
import cv2 as cv2
from tkinter import Tk, Label, Menu, simpledialog, BooleanVar, filedialog
import os

from PIL import Image, ImageTk
import sys
from configparser import ConfigParser
from math import ceil

config = ConfigParser()

try:
    with open('config.ini') as f:
        config.read_file(f)
except IOError:
    config['config'] = {
        'label_height': 200,
        'label_width': 300,
        'label_position_x': 35,
        'label_position_y': 550,
        'background_color': '#ff0035',
        'opacity': 90,
        'cameraid': 0,
        'horizontalinvert': False,
        'fps': 30,
        'border_size': 3,
        'show_logo': True,
        'webcam_logo': 'logo.png',
        'pause_image': 'bg.jpg',
        'show_cam': True
    }


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError


window = Tk()  # Makes main window

# Variáveis de configuração
opacity = int(config['config']['opacity'])
fps = int(config['config']['fps'])
border_size = int(config['config']['border_size'])
bg_color = config['config']['background_color']
label_height = int(config['config']['label_height'])
label_width = int(config['config']['label_width'])
label_position_y = int(config['config']['label_position_y'])
label_position_x = int(config['config']['label_position_x'])
img_pause = None

has_img_pause = False

# Prepara o logo da webcam
logo = Image.open(config['config']['webcam_logo'])
logo.thumbnail((150, 150))

# Prepara a imagem de pausa

try:
    f = open(config['config']['pause_image'])
    has_img_pause = True
    f.close()
except IOError:
    print('Erro ao carregar imagem de pausa')
    has_img_pause = False

if has_img_pause:
    img_pause = Image.open(config['config']['pause_image'])
    img_pause.thumbnail((label_width, label_height))

    img_pause = ImageTk.PhotoImage(image=img_pause)

# Define a visibilidade da webcam
show_cam = BooleanVar()
show_cam.set(False)

# Define a direção da webcam
horizontal_invert = BooleanVar()
horizontal_invert.set(str_to_bool((config['config']['horizontalinvert'])))

# Define a visibilidade do logo
show_logo = BooleanVar()
show_logo.set(str_to_bool(config['config']['show_logo']))


def do_popup(event):
    # global show_cam
    # create a menu
    popup = Menu(window, tearoff=0)

    popup.add_checkbutton(label="Mostrar webcam", onvalue=1, offvalue=0, variable=show_cam)

    popup.add_checkbutton(label="Inverter webcam horizontal", onvalue=1, offvalue=0, variable=horizontal_invert)

    popup.add_checkbutton(label="Mostrar logo", onvalue=1, offvalue=0, variable=show_logo)

    popup.add_separator()

    popup.add_command(label="Salvar alterações", command=do_save)

    popup.add_separator()

    settings = Menu(popup, tearoff=0)
    settings.add_command(label="Tamanho da janela", command=do_size)
    settings.add_command(label="Opacidade da janela", command=do_opacity)
    settings.add_command(label="Posição da janela", command=do_position)
    settings.add_command(label="Largura da borda", command=do_border_sze)
    settings.add_command(label="Cor da borda", command=do_change_border_color)
    settings.add_command(label="Imagem background", command=do_custom_pause_image)
    settings.add_command(label="FPS", command=do_fps)

    popup.add_cascade(label="Configurações", menu=settings)

    popup.add_separator()

    popup.add_command(label="Fechar", command=do_close)

    # display the popup menu
    try:
        popup.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # make sure to release the grab (Tk 8.0a1 only)
        popup.grab_release()


def do_position():
    global label_position_y
    global label_position_x

    value = simpledialog.askstring("Posição da janela", "X, Y",
                                   initialvalue="%s, %s" % (label_position_x, label_position_y))
    if value != None:
        positions = value.split(', ')
        label_position_x = int(positions[0])
        label_position_y = int(positions[1])

        save_change('label_position_x', positions[0])
        save_change('label_position_y', positions[1])

        window.geometry("+%s+%s" % (label_position_x, label_position_y))


def do_size():
    global label_height
    global label_width

    value = simpledialog.askstring("Tamanho da janela", "Altura x Largura",
                                   initialvalue="%sx%s" % (label_height, label_width))
    if value != None:
        sizes = value.split('x')
        label_height = int(sizes[0])
        label_width = int(sizes[1])

        save_change('label_height', sizes[0])
        save_change('label_width', sizes[1])


def do_opacity():
    global opacity

    value = simpledialog.askinteger("Opacidade", "0 - 100", initialvalue=str(opacity))
    if value != None:
        window.attributes('-alpha', int(value) / 100)
        opacity = value
        save_change('opacity', value)


def do_fps():
    global fps

    value = simpledialog.askinteger("FPS", "0 - 60", initialvalue=str(fps))
    if value != None:
        fps = value
        save_change('fps', value)


def do_border_sze():
    global border_size

    value = simpledialog.askinteger("Largura da borda", "0 - 20", initialvalue=str(border_size))
    if value != None:
        border_size = value

        display1.configure(borderwidth=border_size)
        save_change('border_size', value)


def do_change_border_color():
    global bg_color

    value = simpledialog.askstring("Cor da borda", "Hex", initialvalue=bg_color)

    if value != None:
        display1.configure(background=value)
        save_change('background_color', value)


def do_custom_pause_image():
    global img_pause
    global has_img_pause

    value = filedialog.askopenfile()

    if value != None:
        save_change('pause_image', value.name)

        img_pause = Image.open(value.name)
        img_pause.thumbnail((label_width, label_height))
        img_pause = ImageTk.PhotoImage(image=img_pause)

        has_img_pause = True


def do_close():
    window.withdraw()  # if you want to bring it back
    sys.exit()  # if you want to exit the entire thing

    do_close()
    show_frame()


def do_save():
    config['config']['show_cam'] = str(show_cam.get())
    config['config']['horizontalinvert'] = str(horizontal_invert.get())
    config['config']['show_logo'] = str(show_logo.get())

    save()


def save_change(key, value):
    config['config'][key] = str(value)


def save():
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def show_frame():
    global fps
    global logo
    global brightness
    global contrast
    global img_pause

    # Se a camera puder ser exibida
    if show_cam.get() == 1:
        _, frame = cap.read()

        # Se a imagem da webcam puder ser invertida horizontalmente
        if horizontal_invert.get() == 1:
            frame = cv2.flip(frame, 1)

            # Converte a cor do frame
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Transforma o array em imagem
        img = Image.fromarray(cv2image)

        # Reduz o tamanhp da imagem
        img.thumbnail((label_width, label_height), reducing_gap=1.0)

        # Se o logo puder ser exibido
        if show_logo.get():
            img.paste(logo, (1, 1), logo)

        imgtk = ImageTk.PhotoImage(image=img)
        display1.imgtk = imgtk  # Shows frame for display 1
        display1.configure(image=imgtk)

        window.after(ceil(1000 / fps), show_frame)
    else:
        if not has_img_pause:
            img_pause = Image.new("RGB", (label_width, label_height))
            img_pause = ImageTk.PhotoImage(image=img_pause)

        display1.img = img_pause  # Shows frame for display 1
        display1.configure(image=img_pause)

        window.after(1000, show_frame)


window.attributes('-alpha', opacity / 100)
window.overrideredirect(True)
window.wm_attributes("-topmost", True)
window.geometry("+%s+%s" % (label_position_x, label_position_y))

display1 = Label(window, borderwidth=border_size)

display1.grid(row=1, column=0, padx=0, pady=0)  # Display 1

display1.configure(background=bg_color)
cap = cv2.VideoCapture(int(config['config']['CameraID']))

show_frame()
window.bind("<ButtonRelease-3>", do_popup)
window.mainloop()