import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno
from funcoes import *
from functools import partial
from tkinter.scrolledtext import ScrolledText

def log_update(text):

    log.insert(tk.INSERT, text)
    log.insert(tk.INSERT,"\n"+"_"*69+"\n")
    log.yview(tk.END)

def item_selected(event):
    '''Esta função remove as linhas selecionadas da lista de submetidos'''
    global lines
    global center_x
    global center_y


    item = tree.item(tree.selection())
    values = item['values']
    #print(f'Identification {values[0]} and line values = {values[1:]}')


    answer = askyesno(title='Confirmation',message=f'Are you sure that you want to remove line {values[0]}?')

    if answer:
        tree.delete(tree.selection())
        lines.pop(values[0])
        showinfo(title='Sucess',message=f'The line {values[0]} was deleted !!')
        center_x.remove(float(values[3]))
        center_y.remove(float(values[4]))



def submited():
    ''' Esta função obtém os valores preenchidos nos campos de entrada , trata-os e os coloca na lista de submetidos.
        São postos também no dicionario lines do tipo id:line_array para utilização futura'''

    global lines
    global id
    global center_x
    global center_y


    # OBTENDO AS ENTRADAS DOS CAMPOS EM BRANCO
    J = J_entry.get()

    branch = branch_entry.get()

    wavenumber = wavenumber_entry.get()

    #intensity = intensity_entry.get()

    # ARRUMANDO AS ENTRADAS
    branch = branch.upper()

    wavenumber = wavenumber.replace(',' , '.')

    #intensity = intensity.replace(',' , '.')

    # Nessa função eu verifico o centro da linha, caso seja o errado ele é arrumado
    # Caso certo é retornado o valor da intensidade
    # Caso errado é retornado o valor da intensidade e do centro correto

    wavenumber,intensity,text = line_verification(wavenumber)
    log_update(f'Line ID: {id}\n\n'+text)
    #intensity = intensity.replace(',', '.')
    #line_verification(wavenumber)

    # Aqui eu crio uma lista somente com os centros
    center_x.append(float(wavenumber))
    center_y.append(float(intensity))

    array = np.array([J,branch,wavenumber,intensity])


    # APAGANDO O CAMPO DE ENTRADA PARA MAIOR COMODIDADE DO USUARIO
    J_entry.delete(0,tk.END)
    branch_entry.delete(0,tk.END)
    wavenumber_entry.delete(0,tk.END)
    #intensity_entry.delete(0,tk.END)

    # ADICIONANDO O ARRAY QUE REPRESENTA A LINHA NO DICIONARIO LINES
    # A CHAVE É O ID E O ELEMENTO É A LINHA CONTIDA NO ARRAY ID:LINE_ARRAY
    lines[id] = array

    # ADICIONANDO A LINHA LIDA NA JANELA APOIO AO FINAL DO ROOT
    tree.insert('',tk.END,values = [id,J,branch,wavenumber,intensity])
    tree.yview_moveto(1)

    # INCREMENTANDO A VARIÁVEL DE IDENTIFICAÇÃO
    id += 1




# Some global variables
x_espec = []
y_espec = []
width_root = 1020
height_root = 660
lines = {}
id = 1
arquivo= None
center_x = []
center_y = []

# Root frame
root = tk.Tk()
root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='icone.png'))
root.title('Spectrum Voigt')
root.geometry(f'{width_root}x{height_root}')

# TABS
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)
tab_control.add(tab1,text="Line Selection")
tab_control.add(tab2,text="Line Validation")
tab_control.add(tab3,text="Auto Fit")
tab_control.add(tab4,text="Manual Fit")
tab_control.pack(expand=1,fill='both')

#  ------------------ TAB 1 -----------------------------------------------------------
# Na aba1 se encontra os widgets responsaveis por capturar as linhas

# Entry frame settings
entry_center_frame = tk.Frame(tab1, width=200,height = 300)

# load frame settings
load_frame = tk.Frame(tab1, width=200, height=300,pady=25)

# submited frame settings
submited_frame = tk.Frame(tab1, width=650,height=300,bg = 'white')

# Log frame settings
log_frame = tk.Frame(tab1,width= 570,height= 385)

# putting the frames
load_frame.place(relx=0)
entry_center_frame.place(relx=0.73,rely=0.05)
submited_frame.place(relx = 0,rely=0.65)#y=400)
log_frame.place(relx=0.16,rely=0.015)

#---------------------- LOAD FRAME WIDGETS--------------------------------------------------------

load_spec_button = ttk.Button(load_frame, text='Load spectrum', command=partial(load_spectrum,center_x,center_y))
load_spec_button.pack(fill=tk.X)

ttk.Frame(root, height=10).pack()
plot_spec_button = ttk.Button(load_frame, text='Plot / Replot  spectrum', command= partial(plot_spectrum,center_x,center_y))
plot_spec_button.pack(fill=tk.X)



#---------------------- ENTRY CENTER FRAME WIDGETS--------------------------------------------------------

wavenumber_label = tk.Label(entry_center_frame, text='Wavenumber (x)',fg='black',font=14)
wavenumber_entry = tk.Entry(entry_center_frame)
wavenumber_entry.focus()

#intensity_label = tk.Label(entry_center_frame, text='Intensity (y)',font=14)
#intensity_entry = tk.Entry(entry_center_frame)

J_label = tk.Label(entry_center_frame, text='Rotational Quantum number (J)',font=14)
J_entry = tk.Entry(entry_center_frame)

branch_label = tk.Label(entry_center_frame, text='Branch (Q, P, R)',font=14)
branch_entry = tk.Entry(entry_center_frame)


submit_button = tk.Button(entry_center_frame, text='Submit', command=submited)

tk.Frame(entry_center_frame, height=50).pack()

wavenumber_label.pack()
wavenumber_entry.pack(fill='x', padx=40)
tk.Frame(entry_center_frame, height=30).pack()

#intensity_label.pack()
#intensity_entry.pack(fill=tk.X, padx=40)
tk.Frame(entry_center_frame, height=30).pack()

J_label.pack()
J_entry.pack(fill=tk.X, padx=40)
tk.Frame(entry_center_frame, height=30).pack()

branch_label.pack()
branch_entry.pack(fill=tk.X, padx=40)

tk.Frame(entry_center_frame, height=30).pack()
submit_button.pack()

#---------------------- SUBMITED FRAME WIDGETS--------------------------------------------------------

columns = ('ID','J','Branch' ,'Wavenumber', 'Intensity')
tree = ttk.Treeview(submited_frame, columns=columns, show='headings')
tree.heading('ID',text='ID')
tree.heading('J',text='J')
tree.heading('Branch',text='Branch')
tree.heading('Wavenumber',text='Wavenumber')
tree.heading('Intensity',text='Intensity')
tree.bind('<<TreeviewSelect>>', item_selected)



scrollbar = ttk.Scrollbar(submited_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
tree.grid(row=0, column=0,sticky='nsew')
scrollbar.grid(row=0, column=1, sticky='ns')



# ------------------ LOG FRAME WIDGETS --------------------
log = ScrolledText(log_frame, width= 69,height= 20,font = ("Times New Roman",12))
log.place(relx=0,rely=0)
log.insert(tk.INSERT,'Here you can see information about the selected lines')
log_update("")

# --------------------- START TAB2 ----------------------------------------------
# Na aba2 se encontra a parte de validação dos centros das linhas, aqui é faço uma validação cruzada com as linhas selecionadas
# e os pontos contidas no arquivo do espectro para verificar se batem

# frames
line_validation_btn_frame = tk.Frame(tab2, width=200,height = 300,bg='pink')
line_validation_report_frame = tk.Frame(tab2, width=200,height = 400,bg='white')
line_validation_btn_frame.place(relx= 0)
line_validation_report_frame.place(relx= 0.5)




# --------------------- START TAB3 ----------------------------------------------
# Aqui é onde eu faço o ajuste automático  de todas alinhas por um modelo pré selecionado



# --------------------- START TAB4 ----------------------------------------------
# Aqui é o ajuste manual apenas para fins de verificação em suma é parecido com o automatico só que com a liberdade
# de selecionar a linha uma por uma para analises aprofundadas

root.mainloop()
