from tkinter.filedialog import askopenfilename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_point_clicker import clicker
from mpl_interactions import zoom_factory, panhandler
from mpl_interactions.widgets import scatter_selector_index
import mplcursors
from mpldatacursor import datacursor



def plot_spectrum(center_x,center_y):
    '''Está função tem como objetivo plotar o espectro bem como também
    o centro das linhas selecionadas'''

    global x_espec, y_espec

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



    fig, ax = plt.subplots(constrained_layout=True)
    lines = ax.plot(x_espec, y_espec)
    ax.scatter(center_x,center_y,c='orange',linewidths = 1.0,alpha=1)

    disconnect_zoom = zoom_factory(ax)
    pan_handler = panhandler(fig, button=3)
    mplcursors.cursor(lines, multiple='True')

    plt.title(f'{arquivo}')
    plt.show()


def load_spectrum(center_x,center_y):
    '''Está função faz o carregamento do espectro'''

    global arquivo,text

    text = 'Spectrum loaded'
    arquivo = askopenfilename()
    plot_spectrum(center_x,center_y)

def line_verification(wavenumber):

    wavenumber = float(wavenumber)
    x_espec_array = np.array(x_espec)
    y_espec_array = np.array(y_espec)
    deviation = np.abs(wavenumber - x_espec_array)
    index_min = np.where(deviation == deviation.min())[0][0]

    #print(f'Eu recebi o valor {wavenumber} , status: {wavenumber in x_espec}')
    #print(f"\nWavenumber correto: {x_espec_array[index_min]},Intensity: {y_espec_array[index_min]}, Desvio: {deviation[index_min]}")

    if(wavenumber in x_espec):
        text= f"Wavenumber selected: {wavenumber}\n\nIntensity: {y_espec[index_min]}\n\nIs in spectrum's file?: Yes "

    else:
        text= f"Wavenumber selected: {wavenumber}\n\nIs in spectrum's file?: No\n\nCorrect wavenumber: {x_espec_array[index_min]}\n\nItensity: {y_espec[index_min]}\n\nDeviation |selected wavenumber - real wavenumber|: {deviation.min()}"



    return x_espec[index_min],y_espec[index_min],text