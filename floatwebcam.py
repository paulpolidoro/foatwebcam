import webcam

from tkinter import Tk, Label, Menu, simpledialog, BooleanVar, filedialog, IntVar, colorchooser, messagebox, StringVar

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
        'camera': 0,
        'size': '300x200',
        'position': '64,485',
        'background_color': '#00bf49',
        'opacity': 90,
        'cameraid': 0,
        'flip_horizontal': 'True',
        'fps': 60,
        'border_size': 2,
        'show_logo': 'False',
        'logo': '',
        'pause_image': '',
        'show_cam': 'True',
        'flip': '2',
        'lock_position': 'False',
        'border_rgb': 'False'
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
fps = 20
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

show_logo_status = StringVar()
show_logo_status.set('disabled')

# Define a visibilidade do logo
show_logo = BooleanVar()
show_logo.set(str_to_bool(config['config']['show_logo']))

lock_position = BooleanVar()
lock_position.set(str_to_bool(config['config']['lock_position']))

border_rgb = BooleanVar()
border_rgb.set(False)

left_click_x = 0
left_click_y = 0

need_save = False


def menu(event):
    popup = Menu(window, tearoff=0)

    popup.add_checkbutton(label="Mostrar facecam", onvalue=1, offvalue=0, variable=show_cam, command=show_webcam)

    popup.add_checkbutton(label="Bloquear posição", onvalue=1, offvalue=0, variable=lock_position, command=do_lock_position)

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

    popup.add_cascade(label="Flip da facecam", menu=flip_menu)

    popup.add_separator()
    popup.add_checkbutton(label="Mostrar logo", onvalue=1, offvalue=0, variable=show_logo, command=do_show_logo, state=show_logo_status.get())
    popup.add_command(label="Alterar logo", command=do_add_logo)
    popup.add_separator()

    popup.add_command(label="Largura da borda", command=do_border_size)
    popup.add_command(label="Cor da borda", command=do_border_color)
    popup.add_checkbutton(label='Borda RGB', onvalue=1, offvalue=0, variable=border_rgb, command=do_border_rgb)

    popup.add_separator()

    settings = Menu(popup, tearoff=0)
    settings.add_command(label="Tamanho da janela", command=do_size)
    settings.add_command(label="Opacidade da janela", command=do_opacity)

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


def do_border_color():
    global bg_color
    global border_rgb

    if border_rgb.get():
        border_rgb.set(False)

    # variable to store hexadecimal code of color
    color_code = colorchooser.askcolor(title="Selecione uma cor")

    display.configure(background=color_code[1])
    save_change("background_color", color_code[1])
    bg_color = color_code[1]


def do_border_rgb():
    global border_rgb
    global bg_color

    save_change('border_rgb', False)

    if not border_rgb.get():
        display.configure(background=bg_color)


def do_opacity():
    global opacity

    value = simpledialog.askinteger("Opacidade", "0 - 100", initialvalue=str(opacity))
    if value is not None:
        window.attributes('-alpha', int(value) / 100)
        opacity = value
        save_change('opacity', value)


def do_border_size():
    global border_size

    value = simpledialog.askinteger("Largura da borda", "0 - 20", initialvalue=str(border_size))
    if value is not None:
        border_size = value

        display.configure(borderwidth=border_size)
        save_change('border_size', value)


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
    global show_logo_status

    value = filedialog.askopenfile('r', filetypes=[('Arquivos de imagem', ['*.jpg', '*.png', '*.jpeg', '*.gif'])])

    if value is not None:
        save_change('logo', value.name)
        logo = value.name
        cam.set_logo(value.name)

        show_logo_status.set('normal')

        if not cam.is_open():
            show_pause_image()


def do_close():
    global need_save

    if need_save:
        if messagebox.askyesno('Finalizar Float Webcam', 'Existem alterações não salvas, deseja salvá-las antes de '
                                                         'sair?'):
            save()

    window.withdraw()  # if you want to bring it back
    sys.exit()  # if you want to exit the entire thing


def do_save():
    config['config']['show_cam'] = str(show_cam.get())
    config['config']['flip'] = str(flip.get())
    config['config']['show_logo'] = str(show_logo.get())

    save()


def save_position(event):
    value = "%s,%s" % (window.winfo_pointerx() - left_click_x, window.winfo_pointery() - left_click_y)
    save_change('position', value)

    save()


def save_change(key, value):
    global need_save

    config['config'][key] = str(value)

    need_save = True


def save():
    global need_save

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    need_save = False


def rgbtohex(red, green, blue):
    return f'#{red:02x}{green:02x}{blue:02x}'


r = 255
g = 0
b = 0


def show_webcam():
    global fps
    global bg_color
    global border_rgb
    global r
    global g
    global b

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

    if border_rgb.get():
        display.configure(background=rgbtohex(r, g, b))

        if r > 0 and g == 0:
            r = r - 15
            b = b + 15
        elif b > 0 and r == 0:
            b = b - 15
            g = g + 15
        elif g > 0 and b == 0:
            g = g - 15
            r = r + 15

    window.after(fps, show_webcam)


def show_pause_image():
    global pause_image

    if pause_image != '':
        # Tenta carregar a imagem do disco
        try:
            img_pause = Image.open(pause_image)
            img_pause.thumbnail((size[0], size[1]))
        except IOError:
            messagebox.showerror('Imagem de pausa', 'A imagem de pausa não pôde ser carregada.')

            img_pause = Image.new("RGB", (size[0], size[1]))
    else:
        img_pause = Image.new("RGB", (size[0], size[1]))

    img_pause = ImageTk.PhotoImage(image=img_pause)

    # Mostra a imagem
    display.img = img_pause
    display.configure(image=img_pause)


def do_lock_position():
    global lock_position

    save_change('lock_position', lock_position.get())


def dragwin(event):
    global size
    global left_click_x
    global left_click_y
    global lock_position

    if not lock_position.get():
        x = window.winfo_pointerx() - left_click_x
        y = window.winfo_pointery() - left_click_y

        window.geometry('+{x}+{y}'.format(x=x, y=y))


def left_click(event):
    global left_click_x
    global left_click_y

    left_click_x = event.x
    left_click_y = event.y


# Aplica as definições da janela principal
window.title('Float Webcam')
window.iconbitmap('icon.ico')
window.attributes('-alpha', opacity / 100)
window.wm_attributes("-topmost", True)
window.geometry("+%s+%s" % (position[0], position[1]))
window.overrideredirect(True)

# Cria o display de exibição
display = Label(window, borderwidth=border_size)
display.grid(row=1, column=0, padx=0, pady=0)
display.configure(background=bg_color)

# Obtem a Webcam
cam = webcam.WebCam(0, (size[0], size[1]))

cam.show_logo = show_logo.get()

if logo != '':
    if not cam.set_logo(logo):
        show_logo_status.set('disabled')
        show_logo.set(False)
        cam.show_logo = False
        messagebox.showerror('Logo não encontrado', 'O logo selecionado não pôde ser localizado.')

# Define o primeiro flip
flip.set(cam.FLIP_ORIGINAL)

if cam.list is None:
    messagebox.showerror('Webcam', 'Nenhuma webcam foi encontrada. Para utilizar o programa, conecte ou ative uma '
                                   'webcam no seu sistema.')
    do_close()
else:
    # Inicia a webcam
    show_webcam()

window.bind("<ButtonRelease-3>", menu)
window.bind("<Button-1>", left_click)
window.bind("<ButtonRelease-1>", save_position)
window.bind("<B1-Motion>", dragwin)

window.mainloop()
