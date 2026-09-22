import customtkinter as ctk
import keyboard
import winsound
import json
import os

from pycaw.constants import DEVICE_STATE

from pycaw.pycaw import AudioUtilities, EDataFlow

#---Configuração---

arquivo_config= "config.json"

config = {
    "microfone": "",
    "atalho": "f8"
}

def carregar_config():
    global config

    if not os.path.exists(arquivo_config):
        return

    try:
        with open(arquivo_config, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()

            if not conteudo:
                return

            dados = json.loads(conteudo)
            config.update(dados)

    except (json.JSONDecodeError, OSError) as error:
        print("Falha ao carregar config:", error)

def salvar_config():
    try:
        with open(arquivo_config, "w", encoding="utf-8") as arquivo:
            json.dump(
                config,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    except Exception as erro:
        print("Falha ao salvar config: ", erro)

carregar_config()

#---Microfone---

microfones = {}
microfone = None


def listar_microfones():
    dispositivos = AudioUtilities.GetAllDevices(
        data_flow=EDataFlow.eCapture.value,
        device_state=DEVICE_STATE.ACTIVE.value
    )

    resultado = {}

    for dispositivo in dispositivos:
        try:
            nome = dispositivo.FriendlyName

            volume = dispositivo.EndpointVolume

            if nome:
                resultado[nome] = {
                    "dispositivo": dispositivo,
                    "volume": volume
                }

        except Exception as erro:
            print(
                f"Microfone ignorado ({dispositivo.FriendlyName}):",
                erro
            )

    return resultado


def atualizar_lista_microfones():
    global microfones

    microfones = listar_microfones()

    nomes = list(microfones.keys())

    combo_microfone.configure(values=nomes)

    if not nomes:
        combo_microfone.set("Nenhum microfone encontrado")
        return

    if config["microfone"] in microfones:

        nome = config["microfone"]

    else:

        nome = nomes[0]

    combo_microfone.set(nome)

    selecionar_microfone(nome)


def selecionar_microfone(nome):
    global microfone

    if nome not in microfones:
        return

    try:
        microfone = microfones[nome]["volume"]

        estado = bool(
            microfone.GetMute()
        )

        config["microfone"] = nome

        salvar_config()

        atualizar_interface()

        print()
        print("Microfone selecionado:", nome)
        print("Mutado:", estado)

    except Exception as erro:

        microfone = None

        print(
            "Erro ao selecionar microfone:",
            repr(erro)
        )

        atualizar_interface()

#---Interface---

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("Muta Mic")
app.geometry("470x620")
app.resizable(False, False)
app.iconbitmap("assets/icon.ico")

#---Inteface - Atualizar Status---

def atualizar_interface():

    if microfone is None:
        icone.configure(text="?")
        status.configure(
            text="Nenhum Microfone",
            text_color="gray"
        )

        botao.configure(
            state="disabled"
        )

        return

    try:
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

    except Exception as erro:
        print("Erro ao atualizar interface: ", erro)

#---Microfone - Mute---

def alternar_mute():
    if microfone is None:
        return

    try:
        mutado = bool(microfone.GetMute())
        if mutado:
            microfone.SetMute(0, None)
            winsound.PlaySound('assets/unmute.wav', winsound.SND_FILENAME)

        else:
            microfone.SetMute(1, None)
            winsound.PlaySound('assets/mute.wav', winsound.SND_FILENAME)

        app.after(
            0,
            atualizar_interface
        )

    except Exception as erro:
        print("Erro ao alterar mute: ", erro)

#---Encerrar programa---

def fechar_programa():
    global atalho_captura

    try:
        keyboard.unhook_all()

    except:
        pass

    atalho_captura = None

    app.destroy()

#---Atalho---

atalho_registrado = None
capturando_atalho = False
atalho_captura = None

def registrar_atalho():
    global atalho_registrado

    if atalho_registrado is not None:
        try:
            keyboard.remove_hotkey(
                atalho_registrado
            )

        except:
            pass

    try:
        atalho_registrado = keyboard.add_hotkey(
            config["atalho"],
            alternar_mute
        )

        label_atalho.configure(
            text=config["atalho"]
        )

    except Exception as erro:
        print("Erro ao registrar atalho: ", erro)

def iniciar_captura_atalho():
    global capturando_atalho
    global atalho_captura

    if capturando_atalho:
        return

    capturando_atalho = True

    botao_atalho.configure(
        text="Precione uma tecla...",
    )

    if atalho_registrado is not None:
        try:
            keyboard.remove_hotkey(
                atalho_registrado
            )

        except:
            pass

    atalho_captura = keyboard.on_press(
        capturar_tecla
    )

def capturar_tecla(evento):
    global capturando_atalho
    global atalho_captura

    if not capturando_atalho:
        return

    tecla = evento.name

    if tecla in [
        "shift",
        "ctrl",
        "alt",
        "windows"
    ]:
        return

    capturando_atalho = False

    if atalho_captura is not None:
        try:
            keyboard.unhook(atalho_captura)

        except (KeyError, ValueError):
            pass

        atalho_captura = None

    config["atalho"] = tecla
    salvar_config()

    app.after(
        0,
        finalizar_captura_atalho
    )

def finalizar_captura_atalho():

    botao_atalho.configure(
        text="Alterar"
    )

    registrar_atalho()

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

#---Interface - Microfone---

label_microfone = ctk.CTkLabel(
    app,
    text="Microfone",
    font=ctk.CTkFont(
        size=14,
        weight="bold"
    )
)

label_microfone.pack(
    pady=(10,5)
)

combo_microfone = ctk.CTkComboBox(
    app,
    width=370,
    command=selecionar_microfone,
    state="readonly"
)

combo_microfone.pack(
    pady=5
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

#---Botão Mute---

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
    width=370,
    height=100
)

frame_atalho.pack(
    pady=15
)

frame_atalho.pack_propagate(
    False
)

texto_atalho = ctk.CTkLabel(
    frame_atalho,
    text="Atalho:",
    font=ctk.CTkFont(
        size=14,
    )
)

texto_atalho.place(
    x=20,
    y=18
)

label_atalho = ctk.CTkLabel(
    frame_atalho,
    text=config["atalho"].upper(),
    font=ctk.CTkFont(
        size=18,
        weight="bold"
    )
)

label_atalho.place(
    x=20,
    y=50
)

botao_atalho = ctk.CTkButton(
    frame_atalho,
    text="Aterar",
    width=130,
    command=iniciar_captura_atalho
)

botao_atalho.place(
    x=215,
    y=35
)

#---Iniciar---

atualizar_lista_microfones()

registrar_atalho()

app.protocol("WM_DELETE_WINDOW", fechar_programa)

atualizar_interface()

app.mainloop()