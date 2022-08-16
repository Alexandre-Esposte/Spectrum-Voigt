import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import askyesno
from functools import partial
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import matplotlib.pyplot as plt
from mpl_point_clicker import clicker
from mpl_interactions import zoom_factory, panhandler
from mpl_interactions.widgets import scatter_selector_index
import mplcursors
from mpldatacursor import datacursor
from scipy.optimize import leastsq, curve_fit
from lmfit import minimize, Parameters , Minimizer, report_fit
from lmfit.models import *
from scipy import interpolate

# Some global variables
x_espec = []
y_espec = []
width_root = 1300#1020
height_root = 760#660
lines = {}
results = {}
result_replace = []
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
        if values[0] in results:
            del results[values[0]]

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
def report(result,model,id,intensidade_relativa,temperatura,pressao,delete,tp,succesful):
    text=''
    if(succesful):
        if delete:
            log_result_manual.delete('1.0', 'end')
        text = text + '\n[[Fit Statistics]]\n\n'
        text = text + f"Id: {id}\nRelative Intensity: {intensidade_relativa}\nTemperature: {temperatura}K\nPressure: {pressao}\nModel: {model}\nMethod: {result.method}\nFunction evals: {result.nfev}\nData points: {result.ndata}\nChi square: {result.chisqr}\nReduced chi square: {result.redchi}\n" \
                      f"RMSE: {np.sqrt(result.chisqr/result.ndata)}\n"
        text = text + "\n[[Fit Results]]\n\n"
        for var in result.values:
            text = text + f"{var}: {result.values[var]} (+/-) {result.params[var].stderr}  ({round(result.params[var].stderr/result.values[var] * 100,2)}%)\n\n"

        text=text + "-/"*50
    else:
        text= text+ f"\nId: {id}\n An error ocurred!! Try to fit with FIT MANUAL, please !\n\n"
        text = text + "-/" * 50

    if tp == 'manual':
        log_result_manual.insert(tk.INSERT, text)

    elif tp =='automatic':
        log_result_auto.insert(tk.INSERT, text)
    return


def interpolar(x, y, qte=3000):
    f = interpolate.interp1d(x, y, kind='cubic')

    xnew = np.linspace(x[0], x[-1], qte)
    ynew = f(xnew)

    return xnew, ynew
def separa_pontos_manual(id,intensidade_relativa):

    global x_espec,y_espec

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

    pontos_x, pontos_y = interpolar(pontos_x, pontos_y, qte=3000)

    return pontos_x, pontos_y

def fit_btn_function():

    global result_replace
   # first of all we read the entrys

    id_selected = int(id_entry.get())
    relative_intensity_selected = float(relative_intensity_entry.get().replace(',', '.'))
    temperature_selected = float(temperature_entry.get().replace(',','.'))
    pressure_selected = float(pressure_entry.get().replace(',','.'))
    model_selected = selected_profile.get()

    print(f'id: {id_selected}, int: {relative_intensity_selected}, prof: {model_selected}, {type(model_selected)}\n')

    if id_selected not in lines:
        text_t2.set("Line not found, please check the ID")
        return

    text_t2.set(f"ID {id_selected} was found and now the line is fitting by {model_selected}. Please wait !")

   # Aqui entra as funções para o ajuste

    points_x, points_y = separa_pontos_manual(id_selected, relative_intensity_selected)

    gam = np.sqrt((2 * np.log(2) * 1.38e-16 * temperature_selected) / (1.63e-24 * 3e10 * 3e10)) * float(lines[id_selected].tolist()[2])
    sig = np.sqrt((2 * np.log(2) * 1.38e-16 * temperature_selected) / (1.63e-24 * 3e10 * 3e10)) * float(lines[id_selected].tolist()[2])

    if model_selected == "Voigt":
        vgamma = True
        vsigma = False
        final, result, succesful = fit_raia(points_y, points_x, chute_centro=float(lines[id_selected].tolist()[2]),chute_sigma=float(sig), chute_gamma=float(gam), model=model_selected,vgamma=True, vsigma=True)

        erro_percentual_sigma = (result.params['sigma'].stderr / result.params['sigma'].value) * 100
        erro_gamma = result.params['gamma'].stderr
        erro_sigma = result.params['sigma'].stderr
        erro_ajuste_1 = result.chisqr
        erro_ajuste_2 = result.chisqr

        if erro_percentual_sigma > 5:
            erro_percentual_sigma = 0


        while (erro_percentual_sigma < 5):

            final, result, succesful = fit_raia(points_y, points_x, chute_centro=float(lines[id_selected].tolist()[2]),chute_sigma= float(sig), chute_gamma= float(gam), model=model_selected,vgamma=vgamma, vsigma=vsigma)

            if vgamma:
                vgamma = False
                vsigma = True
                erro_percentual_gamma = (result.params['gamma'].stderr / result.params['gamma'].value) * 100
                erro_gamma = result.params['gamma'].stderr
                erro_ajuste_1 = result.chisqr

            else:
                vgamma = True
                vsigma = False
                erro_percentual_sigma = (result.params['sigma'].stderr / result.params['sigma'].value) * 100
                erro_sigma = result.params['sigma'].stderr
                erro_ajuste_2 = result.chisqr

            gam = result.params['gamma'].value
            sig = result.params['sigma'].value

            if np.abs(erro_ajuste_2 - erro_ajuste_1) < 1e-6:
                break
    else:
        final, result, succesful = fit_raia(points_y, points_x, chute_centro=float(lines[id_selected].tolist()[2]), chute_sigma=float(sig), chute_gamma=float(gam), model=model_selected,vgamma= True, vsigma=True)

    if model_selected == "Voigt":
        # Vamos rodar novamente apenas para ajustar os restantes
        final, result, succesful = fit_raia(points_y, points_x,
                                            chute_centro=float(lines[id_selected].tolist()[2]),
                                            chute_sigma=float(sig), chute_gamma=float(gam),
                                            model=model_selected, vgamma=True, vsigma=False)
        result.params['sigma'].stderr = erro_sigma
    #print(report_fit(result))

    report(result,model_selected,id_selected,relative_intensity_selected,temperature_selected,pressure_selected,delete= True,tp='manual',succesful= succesful)

    plot_line(id_selected,model_selected,relative_intensity_selected,points_x,points_y,final,result.chisqr)

    text_t2.set("")

    result_replace = result
    return


def fit_raia(data, ex, chute_centro, chute_sigma, chute_gamma, model, vgamma, vsigma):

    data = np.array(data)
    ex = np.array(ex)

    successful = True

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

        pars['gamma'].set(value=chute_gamma, vary=vgamma, expr='')
        pars['sigma'].set(value=chute_sigma, vary=vsigma, expr='')

        pars['amplitude'].set(value=1, vary=True, expr='')
        pars['center'].set(value=chute_centro, vary=True, expr='')



    try:
        result = modelo.fit(data, pars, x=ex, nan_policy='propagate')

        final = data + result.residual

    except:
        successful = False
        final = result = 0

    return final, result, successful

def plot_line(id,profile,relative_intensity_selected,points_x,points_y,final,r2):
    fig, ax = plt.subplots(constrained_layout=True)
    ax.scatter(points_x, points_y, c='blue', linewidth=1.0, alpha=0.3, label ='Line points')
    ax.plot(points_x,final,c='black',linewidth=3.5,alpha=1, label=f'Fit by {profile} with chisqr: {r2}')
    plt.title(f"ID: {id}, profile: {profile}, Int.Rel: {relative_intensity_selected}, Points counts: {len(points_x)} ")
    plt.legend()
    plt.show()

def replace_btn():
    #result_replace

    id_selected = int(id_entry.get())
    relative_intensity_selected = float(relative_intensity_entry.get().replace(',', '.'))
    temperature_selected = float(temperature_entry.get().replace(',', '.'))
    pressure_selected = float(pressure_entry.get().replace(',', '.'))
    model_selected = selected_profile.get()

    result_list = []

    result_list =[]
    # id = line
    result_list.append(id_selected)

    #J
    result_list.append(lines[id_selected][0])

    #Branch
    result_list.append(lines[id_selected][1])

    #Wavenumber
    result_list.append(lines[id_selected][2])

    #Intensity
    result_list.append(lines[id_selected][3])

    #pressure
    result_list.append(pressure_selected)

    #temperature
    result_list.append(temperature_selected)

    #model
    result_list.append(model_selected)

    # Number of points used
    result_list.append(result_replace.ndata)

    #rms
    result_list.append(np.sqrt(result_replace.chisqr/result_replace.ndata))

    for var in result_replace.values:
        result_list.append(result_replace.values[var])
        result_list.append(result_replace.params[var].stderr)

    if model_selected != 'Voigt':
        gamma = np.nan
        gamma_std = np.nan
        result_list.insert(16,gamma)
        result_list.insert(17,gamma_std)

    results[id_selected] = result_list
    return

# *************************Functions for TAB 3 ********************************************
def result_record(result, model_selected, line, temperature, pressure,succesful):
    global results

    #[id, J, Branch, Wavenumber, Intensity, pressure, temperature, model, npoints, rms, amplitude, amplitude_std, center,center_std, sigma, sigma_std, gamma, gamma_std, fwhm, fhwm_std, height, height_std]

    result_list =[]
    # id = line
    result_list.append(line)

    if(succesful):
        #J
        result_list.append(lines[line][0])

        #Branch
        result_list.append(lines[line][1])

        #Wavenumber
        result_list.append(lines[line][2])

        #Intensity
        result_list.append(lines[line][3])

        #pressure
        result_list.append(pressure)

        #temperature
        result_list.append(temperature)

        #model
        result_list.append(model_selected)

        # Number of points used
        result_list.append(result.ndata)

        #rms
        result_list.append(np.sqrt(result.chisqr/result.ndata))

        # params
        for var in result.values:
            result_list.append(result.values[var])
            result_list.append(result.params[var].stderr)

        if model_selected != 'Voigt':
            gamma = np.nan
            gamma_std = np.nan
            result_list.insert(16,gamma)
            result_list.insert(17,gamma_std)
    else:
        for i in range(1,22):
            result_list.append(np.nan)

    results[line] = result_list
    return

def fit_btn_auto_function():

    global results

    results = {}

   #first of all we read the entrys

    acumulate_rms = 0
    if len(list(lines.keys())) == 0:
        text_t3.set("You need to select lines !!")

    relative_intensity_selected = float(relative_intensity_entry_auto.get().replace(',', '.'))
    temperature_selected = float(temperature_entry_auto.get().replace(',','.'))
    pressure_selected = float(pressure_entry_auto.get().replace(',','.'))
    model_selected = selected_profile_auto.get()
    text_t3.set(f"Fitting, please wait !")
    for line in lines:
        print(f'id: {line}, int: {relative_intensity_selected}, prof: {model_selected}, {type(model_selected)}\n')

        points_x, points_y = separa_pontos_manual(line, relative_intensity_selected)

        gam = np.sqrt((2 * np.log(2) * 1.38e-16 * temperature_selected) / (1.63e-24 * 3e10 * 3e10)) * float(lines[line].tolist()[2])
        sig = np.sqrt((2 * np.log(2) * 1.38e-16 * temperature_selected) / (1.63e-24 * 3e10 * 3e10)) * float(lines[line].tolist()[2])

        try:
            if model_selected == "Voigt":
                vgamma = True
                vsigma = False
                final, result, succesful = fit_raia(points_y, points_x, chute_centro=float(lines[line].tolist()[2]),
                                                    chute_sigma=float(sig), chute_gamma=float(gam), model=model_selected,
                                                    vgamma=True, vsigma=True)

                erro_percentual_sigma = (result.params['sigma'].stderr / result.params['sigma'].value) * 100
                erro_gamma = result.params['gamma'].stderr
                erro_sigma = result.params['sigma'].stderr
                erro_ajuste_1 = result.chisqr
                erro_ajuste_2 = result.chisqr

                if erro_percentual_sigma > 5:
                    erro_percentual_sigma = 0

                while (erro_percentual_sigma < 5):

                    final, result, succesful = fit_raia(points_y, points_x,
                                                        chute_centro=float(lines[line].tolist()[2]),
                                                        chute_sigma=float(sig), chute_gamma=float(gam),
                                                        model=model_selected, vgamma=vgamma, vsigma=vsigma)

                    if vgamma:
                        vgamma = False
                        vsigma = True
                        erro_percentual_gamma = (result.params['gamma'].stderr / result.params['gamma'].value) * 100
                        erro_gamma = result.params['gamma'].stderr
                        erro_ajuste_1 = result.chisqr

                    else:
                        vgamma = True
                        vsigma = False
                        erro_percentual_sigma = (result.params['sigma'].stderr / result.params['sigma'].value) * 100
                        erro_sigma = result.params['sigma'].stderr
                        erro_ajuste_2 = result.chisqr

                    gam = result.params['gamma'].value
                    sig = result.params['sigma'].value

                    if np.abs(erro_ajuste_2 - erro_ajuste_1) < 1e-6:
                        break

            else:
                final, result, succesful = fit_raia(points_y, points_x, chute_centro=float(lines[line].tolist()[2]), chute_sigma=float(sig), chute_gamma=float(gam), model=model_selected,vgamma = True, vsigma=True)

            if model_selected == "Voigt":
                # Vamos rodar novamente apenas para ajustar os restantes
                final, result, succesful = fit_raia(points_y, points_x,
                                                    chute_centro=float(lines[line].tolist()[2]),
                                                    chute_sigma=float(sig), chute_gamma=float(gam),
                                                    model=model_selected, vgamma=True, vsigma=False)
                result.params['sigma'].stderr = erro_sigma

            report(result, model_selected, line, relative_intensity_selected, temperature_selected, pressure_selected,delete= False,tp='automatic',succesful= succesful)

            if(succesful):
                acumulate_rms = acumulate_rms + np.sqrt(result.chisqr/result.ndata)

            # O dicionario results é similar ao dicionario lines, só que com os resultados e o conteudo da chave será uma lista em vez de um array
            # chave = Id, elementos = lista
            # lista = [id,J,Branch,Wavenumber,Intensity,pressure,temperature,model,npoints,rms,amplitude,amplitude_std,center,center_std,sigma,sigma_std,gamma,gamma_std,fwhm,fhwm_std,height,height_std]
            result_record(result, model_selected, line, temperature_selected, pressure_selected,succesful=succesful)
            print("-\-\-\-\-"*50)

            rms_average = acumulate_rms/len(list(lines.keys()))
            text_t3.set(f"Rms average {model_selected}: {rms_average}")
        except:
            report(result, model_selected, line, relative_intensity_selected, temperature_selected, pressure_selected,
                   delete=False, tp='automatic', succesful=0)
            print(f" linha id {line} deu erro ao ajustar!! \n")
    return

#***************************** FUNCTIONS FOR TAB4 ******************************************

def results_report():

    tree_log.delete(*tree_log.get_children())

    for i in results:
        list_to_insert = []
        list_to_insert.append(results[i][0])
        list_to_insert = list_to_insert + results[i][5:]
        tree_log.insert('',tk.END,values = list_to_insert)
        tree_log.yview_moveto(1)

    return
def rearrange_to_save():
    to_save = {}
    list_aux = []

    # id
    for i in results:
        list_aux.append(results[i][0])
    to_save['id'] = list_aux
    list_aux=[]

    #j
    for i in results:
        list_aux.append(results[i][1])
    to_save['j'] = list_aux
    list_aux = []

    #Branch
    for i in results:
        list_aux.append(results[i][2])
    to_save['branch'] = list_aux
    list_aux = []

    # Wavenumber
    for i in results:
        list_aux.append(results[i][3])
    to_save['wavenumber'] = list_aux
    list_aux = []

    # Intensity
    for i in results:
        list_aux.append(results[i][4])
    to_save['intensity'] = list_aux
    list_aux = []

    # Pressure
    for i in results:
        list_aux.append(results[i][5])
    to_save['pressure'] = list_aux
    list_aux = []

    # temperature
    for i in results:
        list_aux.append(results[i][6])
    to_save['temperature'] = list_aux
    list_aux = []

    # model
    for i in results:
        list_aux.append(results[i][7])
    to_save['model'] = list_aux
    list_aux = []

    # npoints
    for i in results:
        list_aux.append(results[i][8])
    to_save['npoints'] = list_aux
    list_aux = []

    # rms
    for i in results:
        list_aux.append(results[i][9])
    to_save['rms'] = list_aux
    list_aux = []

    # amplitude
    for i in results:
        list_aux.append(results[i][10])
    to_save['amplitude'] = list_aux
    list_aux = []

    # amplitude_std
    for i in results:
        list_aux.append(results[i][11])
    to_save['amplitude_std'] = list_aux
    list_aux = []

    # center
    for i in results:
        list_aux.append(results[i][12])
    to_save['center'] = list_aux
    list_aux = []

    # center_std
    for i in results:
        list_aux.append(results[i][13])
    to_save['center_std'] = list_aux
    list_aux = []

    # sigma
    for i in results:
        list_aux.append(results[i][14])
    to_save['sigma'] = list_aux
    list_aux = []

    # sigma_std
    for i in results:
        list_aux.append(results[i][15])
    to_save['sigma_std'] = list_aux
    list_aux = []

    # gamma
    for i in results:
        list_aux.append(results[i][16])
    to_save['gamma'] = list_aux
    list_aux = []

    # gamma_std
    for i in results:
        list_aux.append(results[i][17])
    to_save['gamma_std'] = list_aux
    list_aux = []

    # fwhm
    for i in results:
        list_aux.append(results[i][18])
    to_save['fwhm'] = list_aux
    list_aux = []

    # fwhm_std
    for i in results:
        list_aux.append(results[i][19])
    to_save['fwhm_std'] = list_aux
    list_aux = []

    # height
    for i in results:
        list_aux.append(results[i][20])
    to_save['height'] = list_aux
    list_aux = []

    # height_std
    for i in results:
        list_aux.append(results[i][21])
    to_save['height_std'] = list_aux
    list_aux = []

    return to_save

def save_results():

    to_save = rearrange_to_save()

    df = pd.DataFrame(to_save,index = range(1, len(to_save['id'])+1))
    files = [('All Files', '*.*'),
             ('csv', '*.csv')]
    file = asksaveasfile(mode='w', defaultextension=".csv")
    if file is None:
        return
    path = file.name
    df.to_csv(path)
    file.close()
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
tab_control.add(tab4,text="Save results")
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
submited_frame.place(relx = 0.1,rely=0.65)#y=400)
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
result_frame = tk.Frame(tab2,bg='grey')

menu_frame.place(relx=0,rely=0,relwidth=0.25,relheight=1)
text_tab2_frame.place(relx=0.25,relwidth=1,relheight=0.05)
result_frame.place(relx=0.25,rely=0.05,relwidth=1,relheight=1)

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

# pressure selection
pressure_text =tk.Label(menu_frame,text='Pressure',pady=15)
pressure_entry = tk.Entry(menu_frame,width=10)
pressure_text.pack()
pressure_entry.pack()
ttk.Separator(menu_frame,orient='horizontal').pack(fill='x',pady=5)

#  Profile selection
profile_text= tk.Label(menu_frame,text="Select profile",pady=15)
selected_profile = tk.StringVar()
profile_text.pack()
r1 = tk.Radiobutton(menu_frame, text='Gaussian', value='Gaussian', variable=selected_profile).pack(anchor='n',pady= 15)
r2 = tk.Radiobutton(menu_frame, text='Lorentz',  value='Lorentz', variable=selected_profile).pack(anchor='n',pady= 15)
r3 = tk.Radiobutton(menu_frame, text='Voigt',    value='Voigt', variable=selected_profile).pack(anchor='n',pady= 15)
ttk.Separator(menu_frame,orient='horizontal').pack(fill='x',pady=3)

# buttons
fit_btn = tk.Button(menu_frame,text='FIT',width=10,height=3,command= fit_btn_function)
#plot_fit_btn = tk.Button(menu_frame,text='PLOT FIT',width=10,height=5)
replace_btn = tk.Button(menu_frame,text='REPLACE',width=10,height=3,command= replace_btn)

fit_btn.pack(fill=tk.BOTH,anchor='n',expand=True)
replace_btn.pack(fill=tk.BOTH,anchor='n',expand=True)
#plot_fit_btn.pack(fill=tk.BOTH,anchor='s',expand=True)

# result report
log_result_manual = ScrolledText(result_frame, width= 69,height= 20,font = ("Times New Roman",12))
log_result_manual.place(relx=0,rely=0 ,relwidth=0.90,relheight=1)

# --------------------- START TAB3 ----------------------------------------------

# Aqui é onde eu faço o ajuste automático  de todas as linhas por um modelo pré selecionado
menu_auto_frame= tk.Frame(tab3)
text_tab3_frame=tk.Frame(tab3,bg='white')
result_auto_frame = tk.Frame(tab3,bg='grey')

menu_auto_frame.place(relx=0,rely=0,relwidth=0.25,relheight=1)
text_tab3_frame.place(relx=0.25,relwidth=1,relheight=0.05)
result_auto_frame.place(relx=0.25,rely=0.05,relwidth=1,relheight=1)


#text on text_tab3_frame
text_t3 = tk.StringVar()
text_tab3 = tk.Label(text_tab3_frame,textvariable=text_t3,bg='white').place(relx=0.20,rely=0.25,relheight=0.5,relwidth= 0.5)

btn_clear_auto = tk.Button(text_tab3_frame,text='Clear results log',command=lambda: log_result_auto.delete('1.0', 'end')).place(relx=0)
toco = tk.Button(text_tab3_frame,text='results',command=lambda: print(results)).place(relx=0.15)

ttk.Separator(menu_auto_frame,orient='vertical').place(relx=0.997,relheight=1)
# relative intensity selection
relative_intensity_text_auto =tk.Label(menu_auto_frame,text='Relative intensity of the line peak (%)',pady=15)
relative_intensity_entry_auto = tk.Entry(menu_auto_frame,width=10)
relative_intensity_text_auto.pack()
relative_intensity_entry_auto.pack()
ttk.Separator(menu_auto_frame,orient='horizontal').pack(fill='x',pady=5)

# temperature selection
temperature_text_auto =tk.Label(menu_auto_frame,text='Temperature (K)',pady=15)
temperature_entry_auto = tk.Entry(menu_auto_frame,width=10)
temperature_text_auto.pack()
temperature_entry_auto.pack()
ttk.Separator(menu_auto_frame,orient='horizontal').pack(fill='x',pady=5)

# pressure selection
pressure_text_auto =tk.Label(menu_auto_frame,text='Pressure',pady=15)
pressure_entry_auto = tk.Entry(menu_auto_frame,width=10)
pressure_text_auto.pack()
pressure_entry_auto.pack()
ttk.Separator(menu_auto_frame,orient='horizontal').pack(fill='x',pady=5)

#  Profile selection
profile_text_auto= tk.Label(menu_auto_frame,text="Select profile",pady=15)
selected_profile_auto = tk.StringVar()
profile_text_auto.pack()
r1_auto = tk.Radiobutton(menu_auto_frame, text='Gaussian', value='Gaussian', variable=selected_profile_auto).pack(anchor='n',pady= 15)
r2_auto = tk.Radiobutton(menu_auto_frame, text='Lorentz',  value='Lorentz', variable=selected_profile_auto).pack(anchor='n',pady= 15)
r3_auto = tk.Radiobutton(menu_auto_frame, text='Voigt',    value='Voigt', variable=selected_profile_auto).pack(anchor='n',pady= 15)
ttk.Separator(menu_auto_frame,orient='horizontal').pack(fill='x',pady=5)

# buttons
fit_btn_auto = tk.Button(menu_auto_frame,text='FIT AUTO',width=10,height=5,command= fit_btn_auto_function)
fit_btn_auto.pack(fill=tk.BOTH,anchor='n',expand=True)


# result report
log_result_auto = ScrolledText(result_auto_frame, width= 69,height= 20,font = ("Times New Roman",12))
log_result_auto.place(relx=0,rely=0 ,relwidth=0.90,relheight=1)

# --------------------- START TAB4 ----------------------------------------------
# Here i can save the results

butons_frame = tk.Frame(tab4)
butons_frame.place(relx=0, rely= 0, relwidth=1,relheight=0.1)

log_tab4_frame = tk.Frame(tab4)
log_tab4_frame.place(relx=0,rely=0.1,relwidth=1,relheight=1)

save_button = tk.Button(butons_frame,text='Save results',command=save_results)
save_button.place(relx=0,rely=0,relwidth=0.5,relheight=1)

refresh_button = tk.Button(butons_frame,text='Refresh',command=results_report)
refresh_button.place(relx=0.5,rely=0,relwidth=0.5,relheight=1)


columns_log = ('ID', 'Pres', 'Temp', 'Model', 'Npoints', 'RMS', 'Amp', 'Amp_std',
               'Center', 'Center_std', 'Sigma', 'Sigma_std', 'Gamma', 'Gamma_std', 'FWHM', 'FWHM_std', 'Height', 'Height_std')
tree_log = ttk.Treeview(log_tab4_frame, columns=columns_log, show='headings')
tree_log.heading('ID',text='ID')
'''tree_log.heading('J',text='J')
tree_log.heading('Branch',text='Branch')
tree_log.heading('Wavenumber',text='Wavenumber')
tree_log.heading('Intensity',text='Intensity')'''
tree_log.heading('Pres',text='Pres')
tree_log.heading('Temp',text='Temp')
tree_log.heading('Model',text='Model')
tree_log.heading('Npoints',text='Npoints')
tree_log.heading('RMS',text='RMS')
tree_log.heading('Amp',text='Amp')
tree_log.heading('Amp_std',text='Amp_std')
tree_log.heading('Center',text='Center')
tree_log.heading('Center_std',text='Center_std')
tree_log.heading('Sigma',text='Sigma')
tree_log.heading('Sigma_std',text='Sigma_std')
tree_log.heading('Gamma',text='Gamma')
tree_log.heading('Gamma_std',text='Gamma_std')
tree_log.heading('FWHM',text='FWHM')
tree_log.heading('FWHM_std',text='FWHM_std')
tree_log.heading('Height',text='Height')
tree_log.heading('Height_std',text='Height_std')

tree_log.column("ID",width=10)
'''tree_log.column("J",width=10)
tree_log.column("Branch",width=55)
tree_log.column("Wavenumber",width=105)
tree_log.column("Intensity",width=70)'''
tree_log.column("Pres",width=50)
tree_log.column("Temp",width=50)
tree_log.column("Model",width=60)
tree_log.column("Npoints",width=63)
tree_log.column("RMS",width=40)
tree_log.column("Amp",width=50)
tree_log.column("Amp_std",width=70)
tree_log.column("Center",width=60)
tree_log.column("Center_std",width=90)
tree_log.column("Sigma",width=60)
tree_log.column("Sigma_std",width=90)
tree_log.column("Gamma",width=60)
tree_log.column("Gamma_std",width=90)
tree_log.column("FWHM",width=60)
tree_log.column("FWHM_std",width=85)
tree_log.column("Height",width=60)
tree_log.column("Height_std",width=100)

tree_log.bind('<<TreeviewSelect>>', results_report)

scrollbar_log = ttk.Scrollbar(log_tab4_frame, orient=tk.VERTICAL, command=tree_log.yview)
tree_log.configure(yscroll=scrollbar_log.set)
#tree_log.grid(row=0, column=0,sticky='nsew')
tree_log.place(relx=0,rely=0.15,relwidth=1,relheight=1)
#scrollbar_log.grid(row=0, column=1, sticky='ns')
scrollbar_log.place(relx=0,rely=0.1)




root.mainloop()


