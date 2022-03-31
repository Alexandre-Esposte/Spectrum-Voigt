import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno
from funcoes import *
from functools import partial
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from mpl_point_clicker import clicker
from mpl_interactions import zoom_factory, panhandler
from mpl_interactions.widgets import scatter_selector_index
import mplcursors
from mpldatacursor import datacursor
from scipy.optimize import leastsq, curve_fit
from lmfit import minimize, Parameters , Minimizer, report_fit
from lmfit.models import *

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


#************************Functions for TAB 1*************************************
def read_spectrum():
    global arquivo,x_espec,y_espec

    print(f"Nome do arquivo: {arquivo}")

    df = pd.read_csv(arquivo)

    x = df['LinePosition(cm-1)']

    y = df['Intensity']

    x = list(x)
    y = list(y)

    resultado = {}
    aux = dict(zip(x, y))

    x = sorted(x)

    for i in x:
        resultado[i] = aux[i]

    x_espec = list(resultado.keys())
    y_espec = list(resultado.values())
    plot_spectrum()

def load_spectrum(center_x,center_y):
    '''Está função faz o carregamento do espectro'''

    global arquivo
    arquivo = askopenfilename()
    read_spectrum()

def plot_spectrum():
    '''Está função tem como objetivo plotar o espectro bem como também
    o centro das linhas selecionadas'''

    global center_x,center_y,arquivo,x_espec,y_espec

    print(f"{len(x_espec)}")
    fig, ax = plt.subplots(constrained_layout=True)
    lines = ax.plot(x_espec, y_espec)
    ax.scatter(center_x,center_y,c='orange',linewidths = 1.0,alpha=1)

    disconnect_zoom = zoom_factory(ax)
    pan_handler = panhandler(fig, button=3)
    mplcursors.cursor(lines, multiple='True')

    plt.title(f'{arquivo}')
    plt.show()


def line_verification(wavenumber):

    wavenumber = float(wavenumber)
    x_espec_array = np.array(x_espec)
    y_espec_array = np.array(y_espec)
    deviation = np.abs(wavenumber - x_espec_array)
    index_min = np.where(deviation == deviation.min())[0][0]


    if(wavenumber in x_espec):
        text= f"Wavenumber selected: {wavenumber}\n\nIntensity: {y_espec[index_min]}\n\nIs in spectrum's file?: Yes "

    else:
        text= f"Wavenumber selected: {wavenumber}\n\nIs in spectrum's file?: No\n\nCorrect wavenumber: {x_espec_array[index_min]}\n\nItensity: {y_espec[index_min]}\n\nDeviation |selected wavenumber - real wavenumber|: {deviation.min()}"



    return x_espec[index_min],y_espec[index_min],text

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


# *********************Functions for TAB 2**************************************
def separa_pontos_manual(id,intensidade_relativa):

    global x_espec,y_espec

    #x_espec,y_espec = load_spec2()

    linha = lines[id].tolist()

    centro = float(linha[2])

    pontosx = []
    pontosy = []

    # intensidade do centro e dos pontos adjacentes
    icentro = float(linha[3])
    iponto = float(linha[3] )# só inicializando a variável, preciso disso para entrar no while (1 > intensidade_relativa)

    esquerda_x = []
    esquerda_y = []

    direita_x = []
    direita_y = []


    i = 1

    # para a esquerda
    while (iponto / icentro >= intensidade_relativa):

        # aqui é de fato o valor da intensidade dos pontos adjacentes
        iponto = y_espec[y_espec.index(icentro) - i]

        if iponto / icentro >= intensidade_relativa:
            esquerda_x.insert(-i, x_espec[x_espec.index(centro) - i])
            esquerda_y.insert(-i, y_espec[y_espec.index(icentro) - i])

        # print(i,iponto/icentro)
        i = i + 1

    # Para direita
    icentro = float(linha[3])
    iponto  = float(linha[3])
    i = 1
    while (iponto / icentro >= intensidade_relativa):

        iponto = y_espec[y_espec.index(icentro) + i]

        if iponto / icentro >= intensidade_relativa:
            direita_x.insert(i, x_espec[x_espec.index(centro) + i])
            direita_y.insert(i, y_espec[y_espec.index(icentro) + i])

        i = i + 1

    pontos_x = esquerda_x + [centro] + direita_x

    pontos_y = esquerda_y + [icentro] + direita_y

    return pontos_x, pontos_y

def fit_btn_function():

   # first of all we read the entrys

    id_selected = int(id_entry.get())
    relative_intensity_selected = float(relative_intensity_entry.get().replace(',', '.'))
    temperature_selected = float(temperature_entry.get().replace(',','.'))

    #aux = list(lines.keys())
    print(f'id: {id_selected}, int: {relative_intensity_selected}, prof: {selected_profile.get()}, {type(selected_profile.get())}\n')

    if id_selected not in lines:
        text_t2.set("Line not found, please check the ID")
        return

    text_t2.set(f"ID {id_selected} was found and now the line is fitting by {selected_profile.get()}. Please wait !")

   # Aqui entra as funções para o ajuste

    points_x, points_y = separa_pontos_manual(id_selected, relative_intensity_selected)



    gam = np.sqrt((2 * np.log(2) * 1.38e-16 * temperature_selected) / (1.63e-24 * 3e10 * 3e10)) * float(lines[id_selected].tolist()[2])
    sig = np.sqrt((2 * np.log(2) * 1.38e-16 * temperature_selected) / (1.63e-24 * 3e10 * 3e10)) * float(lines[id_selected].tolist()[2])



    final, result = fit_raia(points_y, points_x, chute_centro=float(lines[id_selected].tolist()[2]), chute_sigma=float(sig), chute_gamma=float(gam), model=selected_profile.get())

    print(report_fit(result))
    plot_line(id_selected,selected_profile.get(),relative_intensity_selected,points_x,points_y,final,result.chisqr)


    text_t2.set("")
    return


def fit_raia(data, ex, chute_centro, chute_sigma, chute_gamma, model):

    data = np.array(data)
    ex = np.array(ex)

    print(f"data: {type(data)}, ex: {type(ex)}, chute_centro: {type(chute_centro)}, chute_sigma: {type(chute_sigma)}, chute_gama: {type(chute_gamma)},model: {type(model)}")

    if model == 'Gaussian':
        print("Ajustando com a Gaussiana")
        modelo = GaussianModel()
        pars = modelo.guess(data, x=ex)

        pars['sigma'].set(value=chute_sigma, vary=True, expr='')
        pars['amplitude'].set(value=1, vary=True, expr='')
        pars['center'].set(value=chute_centro, vary=True, expr='')

    elif model == 'Lorentz':
        print("Ajustando com a Lorentz")
        modelo = LorentzianModel()
        pars = modelo.guess(data, x=ex)

        pars['sigma'].set(value=chute_sigma, vary=True, expr='')
        pars['amplitude'].set(value=1, vary=True, expr='')
        pars['center'].set(value=chute_centro, vary=True, expr='')

    elif model == 'Voigt':
        print("Ajustando com a Voigt")
        modelo = VoigtModel()
        pars = modelo.guess(data, x=ex)

        pars['gamma'].set(value=chute_gamma, vary=True, expr='')
        pars['sigma'].set(value=chute_sigma, vary=True, expr='')

        pars['amplitude'].set(value=1, vary=True, expr='')
        pars['center'].set(value=chute_centro, vary=True, expr='')


    result = modelo.fit(data, pars, x=ex)

    final = data + result.residual

    return final, result

def plot_line(id,profile,relative_intensity_selected,points_x,points_y,final,r2):
    fig, ax = plt.subplots(constrained_layout=True)
    ax.scatter(points_x, points_y, c='blue', linewidth=1.0, alpha=0.3, label ='Line points')
    ax.plot(points_x,final,c='black',linewidth=3.5,alpha=1, label=f'Fit by {profile} with chisqr: {r2}')
    plt.title(f"ID: {id}, profile: {profile}, Int.Rel: {relative_intensity_selected}, Points counts: {len(points_x)} ")
    plt.legend()
    plt.show()
#------------------------------FUNCTIONS END-----------------------------------------------


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
tab_control.add(tab2,text="Manual Fit")
tab_control.add(tab3,text="Auto Fit")
tab_control.add(tab4,text="Credits")
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
plot_spec_button = ttk.Button(load_frame, text='Plot / Replot  spectrum', command= plot_spectrum)
plot_spec_button.pack(fill=tk.X)



#---------------------- ENTRY CENTER FRAME WIDGETS--------------------------------------------------------

wavenumber_label = tk.Label(entry_center_frame, text='Wavenumber (x)',fg='black',font=14)
wavenumber_entry = tk.Entry(entry_center_frame)
wavenumber_entry.focus()


J_label = tk.Label(entry_center_frame, text='Rotational Quantum number (J)',font=14)
J_entry = tk.Entry(entry_center_frame)

branch_label = tk.Label(entry_center_frame, text='Branch (Q, P, R)',font=14)
branch_entry = tk.Entry(entry_center_frame)


submit_button = tk.Button(entry_center_frame, text='Submit', command=submited)

tk.Frame(entry_center_frame, height=50).pack()

wavenumber_label.pack()
wavenumber_entry.pack(fill='x', padx=40)
tk.Frame(entry_center_frame, height=30).pack()

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
log.place(relx=0,rely=0.1)
log.insert(tk.INSERT,'Here you can see information about the selected lines')
log_update("")

# --------------------- START TAB2 ----------------------------------------------
# Na aba2 é onde faço a separação e ajuste de uma única linha selecionada.

# frames
menu_frame= tk.Frame(tab2)
text_tab2_frame=tk.Frame(tab2,bg='white')

menu_frame.place(relx=0,rely=0,relwidth=0.25,relheight=1)
text_tab2_frame.place(relx=0.25,relwidth=1,relheight=0.05)

# widgets

#text on text_tab2_frame
text_t2 = tk.StringVar()
text_tab2 = tk.Label(text_tab2_frame,textvariable=text_t2,bg='white').place(relx=0,rely=0.25,relheight=0.5,relwidth= 0.5)

# line id selection
ttk.Separator(menu_frame,orient='vertical').place(relx=0.997,relheight=1)
id_text = tk.Label(menu_frame,text="Line identification (id)",pady=15)
id_entry =tk.Entry(menu_frame,width= 10)
id_text.pack()
id_entry.pack()
ttk.Separator(menu_frame,orient='horizontal').pack(fill='x',pady=5)

# relative intensity selection
relative_intensity_text =tk.Label(menu_frame,text='Relative intensity of the line peak (%)',pady=15)
relative_intensity_entry = tk.Entry(menu_frame,width=10)
relative_intensity_text.pack()
relative_intensity_entry.pack()
ttk.Separator(menu_frame,orient='horizontal').pack(fill='x',pady=5)

# temperature selection
temperature_text =tk.Label(menu_frame,text='Temperature (K)',pady=15)
temperature_entry = tk.Entry(menu_frame,width=10)
temperature_text.pack()
temperature_entry.pack()
ttk.Separator(menu_frame,orient='horizontal').pack(fill='x',pady=5)

#  Profile selection
profile_text= tk.Label(menu_frame,text="Select profile",pady=15)
selected_profile = tk.StringVar()
profile_text.pack()
r1 = tk.Radiobutton(menu_frame, text='Gaussian', value='Gaussian', variable=selected_profile).pack(anchor='n',pady= 15)
r2 = tk.Radiobutton(menu_frame, text='Lorentz',  value='Lorentz', variable=selected_profile).pack(anchor='n',pady= 15)
r3 = tk.Radiobutton(menu_frame, text='Voigt',    value='Voigt', variable=selected_profile).pack(anchor='n',pady= 15)
ttk.Separator(menu_frame,orient='horizontal').pack(fill='x',pady=5)

# buttons
fit_btn = tk.Button(menu_frame,text='FIT',width=10,height=5,command= fit_btn_function)
#plot_fit_btn = tk.Button(menu_frame,text='PLOT FIT',width=10,height=5)

fit_btn.pack(fill=tk.BOTH,anchor='n',expand=True)
#plot_fit_btn.pack(fill=tk.BOTH,anchor='s',expand=True)



# --------------------- START TAB3 ----------------------------------------------
# Aqui é onde eu faço o ajuste automático  de todas as linhas por um modelo pré selecionado



# --------------------- START TAB4 ----------------------------------------------


root.mainloop()
