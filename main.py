import webcam

from tkinter import Tk, Label, Menu, simpledialog, BooleanVar, filedialog, IntVar

from PIL import Image, ImageTk
import sys
from configparser import ConfigParser
from math import ceil

# Cria a janela principal
window = Tk()

# Obtem as configurações salvas
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


# Variáveis de configuração
size = int(config['config']['size'].split("x")[0]), int(config['config']['size'].split("x")[1])
position = int(config['config']['position'].split(",")[0]), int(config['config']['position'].split(",")[1])

opacity = int(config['config']['opacity'])
fps = ceil(1000 / int(config['config']['fps']))
border_size = int(config['config']['border_size'])
bg_color = config['config']['background_color']

logo = config['config']['logo']
pause_image = config['config']['pause_image']

# Define a camera inical
camera = IntVar()
camera.set(int(config['config']['camera']))

# Define a visibilidade da webcam
show_cam = BooleanVar()
show_cam.set(True)

# Inicia a configuração de flip da imagem
flip = IntVar()

# Define a visibilidade do logo
show_logo = BooleanVar()
show_logo.set(str_to_bool(config['config']['show_logo']))


def menu(event):
    popup = Menu(window, tearoff=0)

    popup.add_checkbutton(label="Mostrar facecam", onvalue=1, offvalue=0, variable=show_cam, command=show_webcam)

    camera_menu = Menu(window, tearoff=0)

    for item in cam.list:
        camera_menu.add_radiobutton(label="Câmera 0%s" % item, value=item, variable=camera, command=do_camera)

    popup.add_cascade(label="Alterar facecam", menu=camera_menu)

    flip_menu = Menu(window, tearoff=0)
    flip_menu.add_radiobutton(label="Original", value=cam.FLIP_ORIGINAL, variable=flip, command=do_flip)
    flip_menu.add_radiobutton(label="Horizontal", value=cam.FLIP_HORIZONTAL, variable=flip, command=do_flip)
    flip_menu.add_radiobutton(label="Vertical", value=cam.FLIP_VERTICAL, variable=flip, command=do_flip)
    flip_menu.add_radiobutton(label="Horizontal + vertical", value=cam.FLIP_HORIZONTAL_VERTICAL, variable=flip,
                              command=do_flip)

    popup.add_cascade(label="Flip", menu=flip_menu)

    popup.add_separator()
    popup.add_checkbutton(label="Mostrar logo", onvalue=1, offvalue=0, variable=show_logo, command=do_show_logo)
    popup.add_command(label="Alterar logo", command=do_add_logo)
    popup.add_separator()

    settings = Menu(popup, tearoff=0)
    settings.add_command(label="Tamanho da janela", command=do_size)
    settings.add_command(label="Opacidade da janela", command=do_opacity)
    settings.add_command(label="Posição da janela", command=do_position)
    settings.add_command(label="Largura da borda", command=do_border_size)
    settings.add_command(label="Cor da borda", command=do_change_border_color)
    settings.add_command(label="FPS", command=do_fps)

    settings.add_separator()
    settings.add_command(label="Alterar imagem de pausa", command=do_custom_pause_image)

    popup.add_cascade(label="Configurações", menu=settings)

    popup.add_command(label="Salvar alterações", command=do_save)
    popup.add_separator()

    popup.add_command(label="Fechar", command=do_close)

    # display the popup menu
    try:
        popup.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # make sure to release the grab (Tk 8.0a1 only)
        popup.grab_release()


def do_camera():
    global camera

    if cam.is_open():
        cam.stop_cam()

    cam.change_camera(camera.get())

    save_change('camera', camera.get())


def do_flip():
    global flip
    cam.flip = flip.get()

    save_change('flip', flip.get())


def do_show_logo():
    global show_logo
    cam.show_logo = show_logo.get()

    save_change('show_logo', show_logo.get())


def do_size():
    global size

    value = simpledialog.askstring("Tamanho da janela", "Altura x Largura",
                                   initialvalue="%sx%s" % (size[0], size[1]))
    if value is not None:
        size = int(value.split('x')[0]), int(value.split('x')[1])

        save_change('size', value)


def do_position():
    global position

    value = simpledialog.askstring("Posição da janela", "X, Y",
                                   initialvalue="%s,%s" % (position[0], position[1]))
    if value is not None:
        position = value.split(',')[0], value.split(',')[1]
        save_change('position', value)

        window.geometry("+%s+%s" % (value.split(',')[0], value.split(',')[1]))


def do_opacity():
    global opacity

    value = simpledialog.askinteger("Opacidade", "0 - 100", initialvalue=str(opacity))
    if value is not None:
        window.attributes('-alpha', int(value) / 100)
        opacity = value
        save_change('opacity', value)


def do_fps():
    global fps

    value = simpledialog.askinteger("FPS", "0 - 60", initialvalue=str(fps))
    if value is not None:
        fps = ceil(1000 / int(value))
        save_change('fps', value)


def do_border_size():
    global border_size

    value = simpledialog.askinteger("Largura da borda", "0 - 20", initialvalue=str(border_size))
    if value is not None:
        border_size = value

        display.configure(borderwidth=border_size)
        save_change('border_size', value)


def do_change_border_color():
    global bg_color

    value = simpledialog.askstring("Cor da borda", "Hex", initialvalue=bg_color)

    if value is not None:
        display.configure(background=value)
        save_change('background_color', value)


def do_custom_pause_image():
    global pause_image

    value = filedialog.askopenfile('r', filetypes=[('Arquivos de imagem', ['*.jpg', '*.png', '*.jpeg', '*.gif'])])

    if value is not None:
        save_change('pause_image', value.name)
        pause_image = value.name

        if not cam.is_open():
            show_pause_image()


def do_add_logo():
    global logo

    value = filedialog.askopenfile('r', filetypes=[('Arquivos de imagem', ['*.jpg', '*.png', '*.jpeg', '*.gif'])])

    if value is not None:
        save_change('logo', value.name)
        logo = value.name

        if not cam.is_open():
            show_pause_image()


def do_close():
    window.withdraw()  # if you want to bring it back
    sys.exit()  # if you want to exit the entire thing


def do_save():
    config['config']['show_cam'] = str(show_cam.get())
    config['config']['flip'] = str(flip.get())
    config['config']['show_logo'] = str(show_logo.get())

    save()


def save_change(key, value):
    config['config'][key] = str(value)


def save():
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def show_webcam():
    global fps

    if not show_cam.get():
        if cam.is_open():
            cam.stop_cam()

        show_pause_image()
        return False

    if not cam.is_open():
        cam.open_cam()

    img = cam.get_frame()

    imgtk = ImageTk.PhotoImage(image=img)
    display.imgtk = imgtk  # Shows frame for display 1
    display.configure(image=imgtk)

    window.after(fps, show_webcam)


def show_pause_image():
    global pause_image

    # Tenta carregar a imagem do disco
    try:
        img_pause = Image.open(pause_image)
        img_pause.thumbnail((size[0], size[1]))

        img_pause = ImageTk.PhotoImage(image=img_pause)
    except IOError:
        img_pause = Image.new("RGB", (size[0], size[1]))
        img_pause = ImageTk.PhotoImage(image=img_pause)

    # Mostra a imagem
    display.img = img_pause
    display.configure(image=img_pause)


# Aplica as definições da janela principal
window.iconbitmap('icon.ico')
window.attributes('-alpha', opacity / 100)
window.overrideredirect(True)
window.wm_attributes("-topmost", True)
window.geometry("+%s+%s" % (position[0], position[1]))

# Cria o display de exibição
display = Label(window, borderwidth=border_size)
display.grid(row=1, column=0, padx=0, pady=0)
display.configure(background=bg_color)

# Obtem a Webcam
cam = webcam.WebCam(0, (size[0], size[1]))
cam.set_logo(logo)
cam.show_logo = show_logo.get()

# Define o primeiro flip
flip.set(cam.FLIP_ORIGINAL)

# Inicia a webcam
show_webcam()

window.bind("<ButtonRelease-3>", menu)
window.mainloop()
