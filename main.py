import customtkinter as ctk
import keyboard
import winsound

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#---Microfone---

def obter_mic():
    dispositivo = AudioUtilities.GetMicrophone()

    interface = dispositivo.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )
    return cast(interface, POINTER(IAudioEndpointVolume))

microfone = obter_mic()

#---Interface---

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("Muta Mic")
app.geometry("400x430")
app.resizable(False, False)
app.iconbitmap("microfone.ico")

#---Funções---

def atualizar_interface():

    mutado = bool(microfone.GetMute())
    if mutado:
        icone.configure(text="🔇")
        status.configure(
            text="Microfone Mutado",
            text_color="#ff5555"
        )

        botao.configure(
            text="Desmutar",
            fg_color="#2e8b57",
            hover_color="#246b45",
        )

    else:
        icone.configure(text="🔊")
        status.configure(
            text="Microfone Ativo",
            text_color="#50fa7b"
        )

        botao.configure(
            text="Mutar",
            fg_color="#c0392b",
            hover_color="#922b21",
        )

def alternar_mute():
    mutado = bool(microfone.GetMute())
    if mutado:
        microfone.SetMute(0, None)
        winsound.PlaySound('sounds/unmute.wav', winsound.SND_FILENAME)

    else:
        microfone.SetMute(1, None)
        winsound.PlaySound('sounds/mute.wav', winsound.SND_FILENAME)

    app.after(
        0,
        atualizar_interface
    )

def atalho_mute():
    alternar_mute()

def fechar_programa():
    keyboard.unhook_all()
    app.destroy()

#---Título---

titulo = ctk.CTkLabel(
    app,
    text="Muta Mic",
    font=ctk.CTkFont(
        size=26,
        weight="bold"
    )
)

titulo.pack(
    pady=(35,20)
)

#---Ícone---

icone = ctk.CTkLabel(
    app,
    text="🔊",
    font=ctk.CTkFont(
        size=70,
    )
)

icone.pack(
    pady=10
)

#---Status---

status = ctk.CTkLabel(
    app,
    text="",
    font=ctk.CTkFont(
        size=18,
        weight="bold"
    )
)

status.pack(
    pady=10
)

#---Botão---

botao = ctk.CTkButton(
    app,
    text="Mutar",
    width=200,
    height=50,
    font=ctk.CTkFont(
        size=21,
        weight="bold"
    ),
    command=alternar_mute,
)

botao.pack(
    pady=20
)

#---Atalho---

frame_atalho = ctk.CTkFrame(
    app,
    fg_color="transparent",
)

frame_atalho.pack(
    pady=15
)

label_atalho = ctk.CTkLabel(
    frame_atalho,
    text="Atalho:",
    font=ctk.CTkFont(
        size=14,
    )
)

label_atalho.pack(
    side="left",
    padx=5
)

tecla_atalho = ctk.CTkLabel(
    frame_atalho,
    text="F8",
    font=ctk.CTkFont(
        size=14,
        weight="bold"
    )
)

tecla_atalho.pack(
    side="left",
    padx=5
)

#---Iniciar---

keyboard.add_hotkey("f8", atalho_mute)

app.protocol("WM_DELETE_WINDOW", fechar_programa)

atualizar_interface()

app.mainloop()