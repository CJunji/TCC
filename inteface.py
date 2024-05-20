import customtkinter as ctm
import tkinter
import serial
import threading
import time
import serial.tools.list_ports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter.ttk import *
import xlsxwriter
import sys

arduino = 0
conexao = False
tempo = 0

peltier1_st = 0
peltier2_st = 0
default_data = [[0,0,0,0,0,0,0,0,0,0]]

planilha = pd.DataFrame(default_data, columns=['Tempo', 'Estado', 'Tf',
                                                'Tq', u'\u0394' + 'T','V', 'I', 'R', 'P', 'S'])
fig = plt.plot(planilha.get('Tempo'), planilha.get('V'))

port_available = []
for port in serial.tools.list_ports.comports():
    port_available.append(port.name)

baud = 115200

def arduino_conect():
    global conexao, arduino, planilha, tempo
    
    if(conexao == False):
        tempo = 0
        planilha = planilha.iloc[0]

        port_use = port_connect.get()

        arduino = serial.Serial(port_use, baud, timeout=0)
        time.sleep(2)
        #arduino.close()
        #time.sleep(0.5)
        #arduino.open()
        #time.sleep(0.5)
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        connect_bt.configure(text = "Desconectar")
        ard_signal.configure(fg_color = 'green')

        conexao = True
        sendArduino("connect")
        if(t1.is_alive() == False):
            t1.start()

    else:
        conexao = False
        sendArduino("10 50 5 0")
        time.sleep(2)
        sendArduino("desconnect")
        time.sleep(2)
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        time.sleep(2)
        arduino.close()
        connect_bt.configure(text = "Conectar")
        ard_signal.configure(fg_color = 'red')
        arduino = 0

def encerramento():
    global conexao, arduino

    if(conexao == True):
        arduino_conect()
    
    time.sleep(0.2)
    screen.destroy()
    screen.quit()
    sys.exit()

def readArduino():
    global conexao, arduino
    while True:
        if conexao:
            data = arduino.readline()
            time.sleep(0.3)
            arduino.reset_output_buffer()   
            data_sensor = data.decode('utf-8')
            if(data_sensor != ''):
                print(data_sensor)
                refresh_data(data_sensor)
        else:
            pass

def sendArduino(data_send):
    print(data_send)
    arduino.write(data_send.encode('utf-8'))
    time.sleep(0.3)
    arduino.reset_input_buffer()
    arduino.reset_input_buffer()
    time.sleep(0.3)

def window_save():
    def salvar():
        if(ext_file.get() == "CSV"):
            planilha.to_csv(nome_file.get() + '.csv', encoding='utf-8', index=True,  sep='\t')
        elif(ext_file.get() == "EXCEL"):
            writer = pd.ExcelWriter(nome_file.get() + ".xlsx", engine="xlsxwriter")
            planilha.to_excel(writer, sheet_name="Ensaio")
            writer.close()
        salvarWindow.destroy()
     
    salvarWindow = Toplevel()
    salvarWindow.title("Salvar como")
    salvarWindow.geometry("400x200")
 
    salvar_label = ctm.CTkLabel(salvarWindow, 
                                text ="Salvar arquivo como: ",
                                text_color='black')
    salvar_label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

    nome_label = ctm.CTkLabel(salvarWindow,
                             text="Nome do arquivo: ",
                             text_color='black')
    nome_label.place(relx=0.2, rely=0.3, anchor=tkinter.CENTER)

    nome_file = ctm.CTkEntry(salvarWindow,
                             text_color='black')
    nome_file.place(relx=0.7, rely=0.3, anchor=tkinter.CENTER)

    ext_label = ctm.CTkLabel(salvarWindow,
                             text="Tipo de arquivo: ",
                             text_color='black')
    ext_label.place(relx=0.2, rely=0.6, anchor=tkinter.CENTER)

    ext_file = ctm.StringVar(value="CSV")
    extension_file = ctm.CTkOptionMenu(master=salvarWindow,
                                       values=["CSV", "EXCEL"],
                                       variable=ext_file,
                                       width=80,
                                       height=30,
                                       corner_radius=50,
                                       text_color="black")
    extension_file.place(relx=0.7, rely=0.6, anchor=tkinter.CENTER)

    att_bt = ctm.CTkButton(master=salvarWindow,
                           text='Salvar',
                           text_color='black',
                           command=salvar)
    att_bt.place(relx=0.5, rely=0.9, anchor=tkinter.CENTER)

tensao = "0.0"
corrente = "0.0"
temperatura1 = "0.0"
temperatura2 = "0.0"
difTemp = "0.0"
resistencia = "0.0"
potencia = "0.0"
seebeck = "0.0"

screen = ctm.CTk()

screen.title("Equipamento Peltier - Gráficos")
screen.geometry("1200x560")
screen.resizable(False, False)

def save_csv():
    planilha.to_csv('Leitura.csv', encoding='utf-8', index=True,  sep='\t')

def save_excel():
    planilha.to_excel('Leitura.csv', encoding='utf-8', index=True,  sep='\t')

config_frame = ctm.CTkFrame(master=screen,
                            width=430,
                            height=260,
                            fg_color="gray")
config_frame.place(x=760, y=10)

peltier1_frame = ctm.CTkFrame(master=config_frame,
                              width=200,
                              height=100,
                              fg_color="cyan")
peltier1_frame.place(x=10, y=115)

peltier2_frame = ctm.CTkFrame(master=config_frame,
                              width=200,
                              height=100,
                              fg_color="#ff4000")
peltier2_frame.place(x=220, y=115)

reading_frame = ctm.CTkFrame(master=screen,
                             width=430,
                             height=150,
                             fg_color="gray")
reading_frame.place(x=760, y=280)

tabview_frame = ctm.CTkFrame(master=screen,
                             width=740,
                             height=540)
tabview_frame.place(x=10, y=10)

feedback_frame = ctm.CTkFrame(master=screen,
                              width=430,
                              height=110,
                              fg_color="gray")
feedback_frame.place(x=760, y=440)

def enviar():
    if(peltier1.get() == ''):
        data = "10 "
    else:
        data = peltier1.get() + " "

    if(peltier2.get() == ''):
        data += '50 '
    else:
        data += peltier2.get() + " "
    
    if(pt1_sw.get() == "1" and pt2_sw.get() == "1"):
        if(waveform.get() == "Constante"):
            data += "1 "
        elif(waveform.get() == "Quadrada"):
            data += "2 "
    
    if(pt1_sw.get() == "1" and pt2_sw.get() == "0"):
        data += "3 "
    
    if(pt1_sw.get() == "0" and pt2_sw.get() == "1"):
        data += "4 "
    
    if(pt1_sw.get() == "0" and pt2_sw.get() == "0"):
        data += "5 "

    if(pt1_sw.get() == "1" and pt2_sw.get() == "1" and waveform.get() == "Quadrada"):
        if(periodo.get() == ''):
            data += "120"
        else:
            data += periodo.get()
    else:
        data += "0"

    print(data)
    sendArduino(data_send=data)

salvar_bt = ctm.CTkButton(master=reading_frame,
                          text="Salvar",
                          text_color="BLACK",
                          command=window_save)
fechar_bt = ctm.CTkButton(master=reading_frame,
                          text="Fechar",
                          text_color="BLACK",
                          command=encerramento)
atualizar_bt = ctm.CTkButton(master=config_frame,
                             text="Atualizar",
                             text_color="BLACK",
                             command=enviar)

connect_bt = ctm.CTkButton(master=config_frame,
                          text="Conectar",
                          text_color="BLACK",
                          command=arduino_conect)

atualizar_bt.place(relx=0.5, rely=0.92, anchor=tkinter.CENTER)
salvar_bt.place(relx=0.25, rely=0.85, anchor=tkinter.CENTER)
fechar_bt.place(relx=0.75, rely=0.85, anchor=tkinter.CENTER)
connect_bt.place(relx=0.7, rely=0.20, anchor=tkinter.CENTER)

tabview = ctm.CTkTabview(master=tabview_frame,
                         width=740,
                         height=520,
                         segmented_button_unselected_color="blue",
                         segmented_button_selected_color="green",
                         fg_color='white')
tabview.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

tensao_tabview = tabview.add("Tensão(mV)")
corrente_tabview = tabview.add("Corrente(mA)")
resistencia_tabview = tabview.add("Resistência(ohms)")
seebeck_tabview = tabview.add("Seebeck(mV/K)")

tabview.tab("Tensão(mV)").grid_columnconfigure(0,weight=1)
tabview.tab("Corrente(mA)").grid_columnconfigure(0,weight=1)
tabview.tab("Resistência(ohms)").grid_columnconfigure(0,weight=1)
tabview.tab("Seebeck(mV/K)").grid_columnconfigure(0,weight=1)

peltier1 = ctm.CTkEntry(master=peltier1_frame, width=50, placeholder_text="10")
peltier1.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

peltier2 = ctm.CTkEntry(master=peltier2_frame, width=50, placeholder_text="50")
peltier2.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

periodo_label = ctm.CTkLabel(master=config_frame,
                             text="Periodo(s): ",
                             text_color='black')
periodo_label.place(relx=0.65, rely=0.35, anchor=tkinter.CENTER)

periodo = ctm.CTkEntry(master=config_frame, width=50, placeholder_text="120")
periodo.place(relx=0.80, rely= 0.35, anchor=tkinter.CENTER)

pt1_sw = ctm.StringVar(value=0)
peltier1_sw = ctm.CTkSwitch(master=peltier1_frame,
                            text="Desligado/Ligado",
                            width=100,
                            height=20,
                            variable=pt1_sw,
                            onvalue=1,
                            offvalue=0,
                            text_color="BLACK")
peltier1_sw.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)

pt2_sw = ctm.StringVar(value="0")
peltier2_sw = ctm.CTkSwitch(master=peltier2_frame,
                            text="Desligado/Ligado",
                            width=100,
                            height=20,
                            variable=pt2_sw,
                            onvalue="1",
                            offvalue="0",
                            text_color="BLACK")
peltier2_sw.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)

config_label = ctm.CTkLabel(config_frame,
                            text="CONFIGURAÇÃO",
                            text_color="BLACK")
config_label.place(relx=0.5, rely=0.05, anchor=tkinter.CENTER)

peltier1_label = ctm.CTkLabel(peltier1_frame,
                            text="Temperatura Fria(ºC)",
                            text_color="BLACK")
peltier1_label.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)

peltier2_label = ctm.CTkLabel(peltier2_frame,
                            text="Temperatura Quente(ºC)",
                            text_color="BLACK")
peltier2_label.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)

waveform = ctm.StringVar(value="Constante")
wave_menu = ctm.CTkOptionMenu(master=config_frame,
                              values=["Constante", "Quadrada"],
                              variable=waveform,
                              width=40,
                              height=30,
                              corner_radius=50,
                              text_color="BLACK")
wave_menu.place(relx=0.25, rely=0.35, anchor=tkinter.CENTER)

port_connect = ctm.StringVar(value="Conectar porta")
port_menu = ctm.CTkOptionMenu(master=config_frame,
                              values=port_available,
                              variable=port_connect,
                              width=40,
                              height=30,
                              corner_radius=50,
                              text_color="BLACK")
port_menu.place(relx=0.3, rely=0.2, anchor=tkinter.CENTER)

reading_label = ctm.CTkLabel(master=reading_frame,
                             text="ÚLTIMA LEITURA",
                             text_color="BLACK")
reading_label.place(relx=0.5, rely=0.07, anchor=tkinter.CENTER)

temperatura1_label = ctm.CTkLabel(master=reading_frame,
                                  text="Tf: " + str(temperatura1) + " ºC",
                                  text_color="BLACK",)
temperatura2_label = ctm.CTkLabel(master=reading_frame,
                                  text="Tq: " + str(temperatura2) + " ºC",
                                  text_color="BLACK")
difTemp_label = ctm.CTkLabel(master=reading_frame,
                             text=u'\u0394' + "T : " + str(difTemp) + " K",
                             text_color="BLACK")
voltage_label = ctm.CTkLabel(master=reading_frame,
                             text="V: " + str(tensao) + " mV",
                             text_color="BLACK")
current_label = ctm.CTkLabel(master=reading_frame,
                             text="I: " + str(corrente) + " mA",
                             text_color="BLACK")
resistencia_label = ctm.CTkLabel(master=reading_frame,
                           text="R: " + str(resistencia) + " " + u'\u03a9',
                           text_color="BLACK")
potencia_label = ctm.CTkLabel(master=reading_frame,
                           text="P : " + str(potencia) + " " + u'\u03BC' + "W",
                           text_color="BLACK")
seebeck_label = ctm.CTkLabel(master=reading_frame,
                             text="S: " + str(seebeck) + " mV/K",
                             text_color="BLACK")

temperatura1_label.place(relx=0.1, rely=0.12)
temperatura2_label.place(relx=0.6, rely=0.12)
voltage_label.place(relx=0.1, rely=0.27)
current_label.place(relx=0.6, rely=0.27)
resistencia_label.place(relx=0.1, rely=0.42)
potencia_label.place(relx=0.6, rely=0.42)
difTemp_label.place(relx=0.1, rely=0.57)
seebeck_label.place(relx=0.6, rely=0.57)

monitor_label = ctm.CTkLabel(master=feedback_frame,
                             text="MONITOR",
                             text_color="BLACK")
monitor_label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

monitor_peltier1 = ctm.CTkLabel(master=feedback_frame,
                                text="Peltier Fria",
                                text_color="BLACK")
monitor_peltier1.place(relx=0.20, rely=0.3, anchor=tkinter.CENTER)

monitor_peltier2 = ctm.CTkLabel(master=feedback_frame,
                                text="Peltier Quente",
                                text_color="BLACK")
monitor_peltier2.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)

monitor_comunication = ctm.CTkLabel(master=feedback_frame,
                                text="Comunicação",
                                text_color="BLACK")
monitor_comunication.place(relx=0.80, rely=0.3, anchor=tkinter.CENTER)

peltier1_sinal = ctm.CTkFrame(master=feedback_frame,
                              width=50,
                              height=50,
                              corner_radius=90,
                              fg_color="red")
peltier1_sinal.place(relx=0.20, rely=0.65, anchor=tkinter.CENTER)

peltier2_sinal = ctm.CTkFrame(master=feedback_frame,
                              width=50,
                              height=50,
                              corner_radius=90,
                              fg_color="red")
peltier2_sinal.place(relx=0.5, rely=0.65, anchor=tkinter.CENTER)

ard_signal = ctm.CTkFrame(master=feedback_frame,
                              width=50,
                              height=50,
                              corner_radius=90,
                              fg_color="red")
ard_signal.place(relx=0.80, rely=0.65, anchor=tkinter.CENTER)


def refresh_data(data_sensor):
    global planilha, tempo
    resistencia = 0.0
    seebeck = 0.0
    potencia = 0.0

    data_splited = data_sensor.split(" ")
    tempo += 1
    
    if (len(data_splited) != 5):
        return

    stRun = float(data_splited[0])
    temperatura1 = float(data_splited[1])
    temperatura2 = float(data_splited[2])
    tensao = float(data_splited[3])
    if(tensao == ''):
        tensao = 0.0
    corrente = float(data_splited[4])
    if(corrente == ''):
        corrente = 0.0

    difTemp = float(temperatura2) - float(temperatura1)
    potencia = tensao * corrente

    if(float(corrente) != 0):
        resistencia = (tensao / corrente) - 0.4

    if(float(difTemp) != 0):
        seebeck = (tensao / difTemp)

    if(stRun == 1):
        peltier1_sinal.configure(fg_color="green")
        peltier2_sinal.configure(fg_color="green")
    elif(stRun == 2):
        peltier1_sinal.configure(fg_color="green")
        peltier2_sinal.configure(fg_color="green")
    elif(stRun == 3):
        peltier1_sinal.configure(fg_color="green")
        peltier2_sinal.configure(fg_color="red")
    elif(stRun == 4):
        peltier1_sinal.configure(fg_color="red")
        peltier2_sinal.configure(fg_color="green")
    elif(stRun == 5):
        peltier1_sinal.configure(fg_color="red")
        peltier2_sinal.configure(fg_color="red")

    temperatura1_label.configure(text="Tf: " + '%.2f' % temperatura1 + " ºC")
    temperatura2_label.configure(text="Tq: " + '%.2f' % temperatura2 + " ºC")
    difTemp_label.configure(text=u'\u0394' + "T : " + '%.2f' % difTemp + " K")
    voltage_label.configure(text="V: " + '%.2f' % tensao + " mV")
    current_label.configure(text="I: " + '%.2f' % corrente + " mA")
    resistencia_label.configure(text="R: " + '%.2f' % resistencia + " " + u'\u03a9')

    if(potencia < 1000):
        potencia_label.configure(text="P : " + '%.2f' % potencia + " " + u'\u03BC' + "W")
    else:
        potencia_label.configure(text="P : " + '%.2f' % (potencia / 1000) + " " + "mW")

    seebeck_label.configure(text="S: " + '%.2f' % seebeck + " mV/K")
    
    data_aux = [[tempo, stRun, temperatura1, temperatura2,
                difTemp, tensao, corrente, resistencia, potencia, seebeck]]

    aux_dataFrame = pd.DataFrame(data_aux, columns=['Tempo', 'State', 'Tf', 'Tq', u'\u0394' + 'T','V', 'I',
                                                      'R', 'P', 'S'])

    planilha = pd.concat([planilha, aux_dataFrame], ignore_index=True)
    voltage_plot()
    corrente_plot()
    resistencia_plot()
    seebeck_plot()

fig_voltage = plt.figure()

def voltage_plot():
    fig_voltage.clear()
    ax1 = fig_voltage.add_subplot(111)
    ax1.clear()
    x1_data = planilha.get('Tempo')
    y1_data = planilha.get('V')
    ax1.plot(x1_data, y1_data)
    ax1.set_ylabel('Tensão (mV)')

    ax5 = ax1.twinx()
    y5_data = planilha.get(u'\u0394' + 'T')
    ax5.plot(x1_data, y5_data, 'r-')
    ax5.set_ylabel(u'\u0394' + 'T (ºC)', color = 'r')
    for tl in ax5.get_yticklabels():
        tl.set_color('r')
    
    voltage_slide.draw()

voltage_slide = FigureCanvasTkAgg(fig_voltage, master=tensao_tabview)
voltage_slide.get_tk_widget().pack(fill='both', padx=(75,85))

fig_corrente, ax2 = plt.subplots()

def corrente_plot():
    ax2.clear()

    ax2.set(xlabel='Tempo(s)', ylabel='Corrente (mA)')
    x2_data = planilha.get('Tempo')
    y2_data = planilha.get('I')

    ax2.plot(x2_data, y2_data)
    corrente_slide.draw()

corrente_slide = FigureCanvasTkAgg(fig_corrente, master=corrente_tabview)
corrente_slide.get_tk_widget().pack(fill='both', padx=(50,10))

fig_resistencia, ax3 = plt.subplots()

def resistencia_plot():
    ax3.clear()

    ax3.set(xlabel='Tempo(s)', ylabel='Resistência (' + u'\u03a9' + ')')
    x3_data = planilha.get('Tempo')
    y3_data = planilha.get('R')

    ax3.plot(x3_data, y3_data)
    resistencia_slide.draw()

resistencia_slide = FigureCanvasTkAgg(fig_resistencia, master=resistencia_tabview)
resistencia_slide.get_tk_widget().pack(fill='both', padx=(45,10))

fig_seebeck, ax4 = plt.subplots()

def seebeck_plot():
    ax4.clear()

    ax4.set(xlabel='Tempo(s)', ylabel='Coeficiente de Seebeck (mV/K)')
    x4_data = planilha.get('Tempo')
    y4_data = planilha.get('S')

    ax4.plot(x4_data, y4_data)
    seebeck_slide.draw()

seebeck_slide = FigureCanvasTkAgg(fig_seebeck, master=seebeck_tabview)
seebeck_slide.get_tk_widget().pack(fill='both', padx=(40,10))

t1 = threading.Thread(target=readArduino)

screen.protocol("WM_DELETE_WINDOW", encerramento)
screen.mainloop()
