from iqoptionapi.stable_api import IQ_Option
from iqoptionapi.constants  import ACTIVES
from encodings.utf_8 import getregentry
from functools import reduce
import time
from configobj import ConfigObj
import json, sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate
from colorama import init, Fore, Back, Style 
from threading import Thread


init(autoreset=True)
green = Fore.GREEN
yellow = Fore.YELLOW
greenf = Back.GREEN
yellowf = Back.YELLOW
light_blue = Fore.LIGHTBLUE_EX
red = Fore.RED
redf = Back.RED
white = Fore.WHITE
whitef = Back.WHITE
cyan = Fore.CYAN
cyanf = Back.CYAN
blue = Fore.BLUE
bluef = Back.BLUE
magenta = Fore.MAGENTA
magentaf = Back.MAGENTA

print(light_blue+"\n========================================================================================================")
print(yellow + '********************************************************************************************************')
print(green+'''
            ██╗      ██████╗  ██████╗  █████╗ ███╗   ██╗    ███████╗███╗   ███╗██╗████████╗██╗  ██╗
            ██║     ██╔═══██╗██╔════╝ ██╔══██╗████╗  ██║    ██╔════╝████╗ ████║██║╚══██╔══╝██║  ██║
            ██║     ██║   ██║██║  ███╗███████║██╔██╗ ██║    ███████╗██╔████╔██║██║   ██║   ███████║
            ██║     ██║   ██║██║   ██║██╔══██║██║╚██╗██║    ╚════██║██║╚██╔╝██║██║   ██║   ██╔══██║
            ███████╗╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║    ███████║██║ ╚═╝ ██║██║   ██║   ██║  ██║
            ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚══════╝╚═╝     ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝
                                ████████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
                                ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
                                   ██║   ██████╔╝███████║██║  ██║█████╗  ██████╔╝
                                   ██║   ██╔══██╗██╔══██║██║  ██║██╔══╝  ██╔══██╗
                                   ██║   ██║  ██║██║  ██║██████╔╝███████╗██║  ██║
                                   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝'''+yellow+'''
                                                azkzero@gmail.com
''')
print(yellow + '*********************************************************************************************************')
print(light_blue+"=========================================================================================================")

config = ConfigObj()
velas = ''
tempo_restante = 0
ativos = ''
exp = 15
### CRIANDO ARQUIVO DE CONFIGURAÇÃO ####
config = ConfigObj('config.txt')
email = config['LOGIN']['email']
senha = config['LOGIN']['senha']
tipo = config['AJUSTES']['tipo']
valor_entrada = float(config['AJUSTES']['valor_entrada'])
stop_win = float(config['AJUSTES']['stop_win'])
stop_loss = float(config['AJUSTES']['stop_loss'])
pay_minimo = float(config['AJUSTES']['pay_minimo'])
lucro_total = 0
stop = True

if config['MARTINGALE']['usar_martingale'].upper() == 'S':
    martingale = int(config['MARTINGALE']['niveis_martingale'])
else:
    martingale = 0
fator_mg = float(config['MARTINGALE']['fator_martingale'])


if config['SOROS']['usar_soros'].upper() == 'S':
    soros = True
    niveis_soros = int(config['SOROS']['niveis_soros'])
    nivel_soros = 0

else:
    soros = False
    niveis_soros = 0
    nivel_soros = 0

valor_soros = 0
lucro_op_atual = 0

analise_medias = config['AJUSTES']['analise_medias']
velas_medias = int(config['AJUSTES']['velas_medias'])

print(yellow+'Iniciando Conexão com a IQ Option')
API = IQ_Option(email,senha)

### Função para conectar na Exnova ###
check, reason = API.connect()
if check:
    print('\nConectado com sucesso')
else:
    if reason == '{"code":"invalid_credentials","message":"You entered the wrong credentials. Please ensure that your login/password is correct."}':
        print('\nEmail ou senha incorreta')
        sys.exit()
        
    else:
        print('\nHouve um problema na conexão')

        print(reason)
        sys.exit()


while True:
    escolha = input(Fore.GREEN +'\n>>'+Fore.WHITE+' Qual conta deseja conectar?\n'+ Fore.GREEN+' 1 - '+ Fore.WHITE+'DEMO \n'+ Fore.GREEN+' 2 - '+ Fore.WHITE+'REAL \n'+ Fore.GREEN+'--> ')
    try:
        escolha = int(escolha)
        if escolha == 1:
            conta = 'PRACTICE'
            escolha = 'Demo'
            print(Fore.GREEN + '\n>> Conta demo selecionada')
            break
        elif escolha== 2:
            conta = 'REAL'
            escolha = 'Real'
            print(Fore.GREEN+ '\n>> Conta real selecionada')
            break

        else:
            print(Fore.RED +'>> Opção inválida - Digite 1 ou 2')
            continue
    except:
        print(Fore.RED +'>> Opção inválida - Digite 1 ou 2')
        
API.change_balance(conta)


### Função para checar stop win e loss
def check_stop():
    global stop,lucro_total
    if lucro_total <= float('-'+str(abs(stop_loss))):
        stop = False
        print(Fore.WHITE + Back.RED+'\n ######################### ')
        print(red+'  STOP LOSS BATIDO ',str(cifrao),str(lucro_total))
        print(Fore.WHITE + Back.RED+' ########################### ')
        input(' ➥  Aperte enter para sair')       

    if lucro_total >= float(abs(stop_win)):
        stop = False
        print(Fore.WHITE + Back.YELLOW+'\n ######################### ')
        print(green+'  STOP WIN BATIDO ',str(cifrao),str(lucro_total))
        print(Fore.WHITE + Back.YELLOW+' ########################### ')
        input(' ➥  Aperte enter para sair')

def payout(par):
    global profit, all_asset, pay_minimo, binary, turbo, digital

    pay_minimo = float(config["AJUSTES"]["pay_minimo"])

    try:
        if all_asset["binary"][par]["open"]:
            if profit[par]["binary"] > 0:
                binary = round(profit[par]["binary"], 2) * 100
            else:
                binary = 0
        else:
            binary = 0
    except:
        binary = 0

    try:
        if all_asset["turbo"][par]["open"]:
            if profit[par]["turbo"] > 0:
                turbo = round(profit[par]["turbo"], 2) * 100
            else:
                turbo = 0
        else:
            turbo = 0
    except:
        turbo = 0

    try:
        if all_asset["digital"][par]["open"]:
            digital = API.get_digital_payout(par)
        else:
            digital = 0
    except:
        digital = 0
    
    return binary, turbo, digital

### Função abrir ordem e checar resultado ###
def compra(ativo,valor_entrada,direcao,exp,tipo):
    global stop,lucro_total, nivel_soros, niveis_soros, valor_soros, lucro_op_atual
    print(f"Compra realizada: Ativo {melhor_par}, Entrada {valor_entrada}, Direção {direcao}, Expiração {exp}, Tipo {tipo}")
    
    if soros:
        if nivel_soros == 0:
            entrada = valor_entrada

        if nivel_soros >=1 and valor_soros > 0 and nivel_soros <= niveis_soros:
            entrada = valor_entrada + valor_soros

        if nivel_soros > niveis_soros:
            lucro_op_atual = 0
            valor_soros = 0
            entrada = valor_entrada
            nivel_soros = 0
    else:
        entrada = valor_entrada

    for i in range(martingale + 1):

        if stop == True:
        
            if tipo == 'digital':
                check, id = API.buy_digital_spot_v2(ativo,entrada,direcao,exp)
            else:
                check, id = API.buy(entrada,ativo,direcao,exp)


            if check:
                if i == 0: 
                    print('\n >> Ordem aberta \n',
                          yellow+'>> Par:',white,ativo,'\n',
                          yellow+'>> Direção:',white,direcao,'\n',
                          yellow+'>> Entrada de:',white,cifrao,entrada)
                if i >= 1:
                    print('\n >> Ordem aberta para GALE',str(i),'\n',
                          '>> Par:',ativo,'\n',
                          '>> Direção:',direcao,'\n',
                          '>> Entrada de:',cifrao,entrada)

                while True:
                    time.sleep(0.1)
                    status , resultado = API.check_win_digital_v2(id) if tipo == 'digital' else API.check_win_v4(id)

                    if status:

                        lucro_total += round(resultado,2)
                        valor_soros += round(resultado,2)
                        lucro_op_atual += round(resultado,2)
                        printar_lucro = lucro_tot(lucro_total)

                        if resultado > 0:
                            if i == 0:
                                print(green+'\n >> Resultado: WIN \n'+
                                        yellow+'\n >> Lucro: '+white+ str(round(resultado,2))+
                                        yellow+'\n >> Par: '+white+ ativo+
                                        yellow+'\n >> Lucro total: '+ printar_lucro)
                            if i >= 1:
                                    print(green+'\n >> Resultado: WIN no gale ' + str(i)+' '+
                                        yellow+'\n >> Lucro: '+white+ str(round(resultado,2))+
                                        yellow+'\n >> Par: '+white+ ativo+
                                        yellow+'\n >> Lucro total: '+ printar_lucro)

                        elif resultado == 0:
                            if i == 0:
                                print(yellow+'\n >> Resultado: EMPATE \n' +
                                        yellow+'\n >> Lucro: '+white+ str(round(resultado,2))+
                                        yellow+'\n >> Par: '+white+ ativo+
                                        yellow+'\n >> Lucro total: '+ printar_lucro)
                                
                            if i >= 1:

                                print(yellow+'\n>> Resultado: EMPATE no gale' + str(i) +' '+
                                        yellow+'\n >> Lucro: '+white+ str(round(resultado,2))+
                                        yellow+'\n >> Par: '+white+ ativo+
                                        yellow+'\n >> Lucro total: '+ printar_lucro)
                            if i+1 <= martingale:
                                gale = float(entrada)                   
                                entrada = round(abs(gale), 2)

                        else:
                            if i == 0:
                                print(red+'\n>> Resultado: LOSS ' +
                                        yellow+'\n >> Lucro: '+white+ str(round(resultado,2))+
                                        yellow+'\n >> Par: '+white+ ativo+
                                        yellow+'\n >> Lucro total: '+ printar_lucro)
                            if i >= 1:
                                print(red+'\n>> Resultado: LOSS no gale' + str(i) +' '+
                                        yellow+'\n >> Lucro: '+white+ str(round(resultado,2))+
                                        yellow+'\n >> Par: '+white+ ativo+
                                        yellow+'\n >> Lucro total: '+ printar_lucro)
                                
                            if i+1 <= martingale:
                                
                                gale = float(entrada) * float(fator_mg)                           
                                entrada = round(abs(gale), 2)

                        check_stop()

                        break
                if resultado > 0:
                    break
            else:
                print('>> Erro na abertura da ordem,', id,ativo)
    if soros:
        if lucro_op_atual > 0:
            nivel_soros += 1
            lucro_op_atual = 0
        
        else:
            valor_soros = 0
            nivel_soros = 0
            lucro_op_atual = 0

def lucro_tot(lucro_total):
    if lucro_total == 0:
        return white + cifrao + ' '+str(round(lucro_total,2))
    if lucro_total > 0:
        return green + cifrao + ' '+str(round(lucro_total,2))
    if lucro_total < 0:
        return red + cifrao + ' '+str(round(lucro_total,2))
    
### Fução que busca hora da corretora ###
def horario():
    x = API.get_server_timestamp()
    now = datetime.fromtimestamp(API.get_server_timestamp())
    
    return now

def medias(velas):
    soma = 0
    for i in velas:
        soma += i['close']
    media = soma / velas_medias

    if media > velas[-1]['close']:
        tendencia = 'put'
    else:
        tendencia = 'call'

    return tendencia

def estrategia_LSTrader_Volatility(ativos, valor_entrada, tipo):
    global timeframe, qnt_velas

    # Ler o volume mínimo da configuração
    min_volume = int(config["AJUSTES"]["min_volume"])
    volatility_threshold = 0  # Limite de volatilidade
    exp = 15 
    timeframe = 60  # Timeframe de 1 minuto
    qnt_velas = 3
    ativos = escolher_par_e_tipo_automatico(API, payout_minimo=70) # Substitua por ativos válidos
    print(yellow + '***************************************************************************************')
    print("\n>>>Iniciando Logan Smith Trader_Volatility")
    
    while True:
        time.sleep(0.1)

        timestamp_atual = API.get_server_timestamp()
        h = datetime.fromtimestamp(timestamp_atual).strftime("%d/%m/%Y %H:%M:%S")

        minutos = float(datetime.fromtimestamp(timestamp_atual).strftime("%M.%S")[1:])
        segundos = int(datetime.fromtimestamp(timestamp_atual).strftime("%S"))

        # Verificar se está no intervalo de entrada (segundos entre 30 e 00)
        entrar = segundos <= 30 or segundos == 00

        if entrar:
            print(">>>Aguardando análise", minutos, end="\r")
            
            direcao = False
            
            for ativo in ativos:
                print(yellow + '***************************************************************************************')
                print(f"\n>>>Analisando o ativo: {melhor_par}")

                try:
                    velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())
                    
                    if velas is None:
                        print(f">>>Erro ao obter velas para o ativo {melhor_par}.")
                        continue

                    # Calcular a volatilidade com base na amplitude das velas
                    amplitudes = [vela["max"] - vela["min"] for vela in velas]
                    volatilidade = np.std(amplitudes)  # Desvio padrão das amplitudes das velas
                    print(yellow + '***************************************************************************************')
                    print(f"\n>>>Volatilidade do ativo {melhor_par}: {volatilidade}, Limite de volatilidade: {volatility_threshold}")

                    if volatilidade >= volatility_threshold:
                        volume_ultima = velas[-1]["volume"]

                        if volume_ultima >= min_volume:
                            direcao = "call" if velas[-1]["close"] > velas[-2]["close"] else "put"
                            if segundos < 30:
                                print(yellow + '***************************************************************************************')
                                print(f"\n>>>Padrão de volatilidade identificado. Entrando na operação com {direcao} para o ativo {melhor_par}", h)
                                print(yellow + '***************************************************************************************')
                                print('\n')
                                puxa_candles()
                                # Função para contar o tempo até o próximo candle
                                wait_for_new_candle(API)
                                # Chama a função de compra
                                compra(ativo, valor_entrada, direcao, exp, tipo)
                                # Chama a função de Estratégia
                                estrategia_LSTrader_Volatility(ativos, valor_entrada, tipo)                                                 
                        else:
                            print(f">>>Volume insuficiente para o ativo {melhor_par}.")
                    else:
                        print(f">>>Volatilidade insuficiente para o ativo {melhor_par}.")
                
                except Exception as e:
                    print(f">>>Erro ao processar o ativo {melhor_par}: {e}")
                    
                print(yellow + '***************************************************************************************')
            if mudar_automatico == True:
                break           
        else:
            print(">> Aguardando horario para entrada", minutos, end="\r")
                                                
def catag(all_asset,API):
    global analise_result, pares_abertos

    quantidade_catalogacao = 21
    
    payout = 80
    payout = float((payout)/100)

    conf = ConfigObj("config.txt", encoding='UTF-8', list_values=False) 
    if conf['MARTINGALE']['usar_martingale'] == 'S':
        if int(conf['MARTINGALE']['niveis_martingale']) == 0:
            linha = 2
        if int(conf['MARTINGALE']['niveis_martingale']) == 1:
            linha = 3
        if int(conf['MARTINGALE']['niveis_martingale']) >= 2:
            linha = 4
        if int(conf['MARTINGALE']['niveis_martingale']) == 3:
            linha = 5
        if int(conf['MARTINGALE']['niveis_martingale']) == 4:
            linha = 6
        if int(conf['MARTINGALE']['niveis_martingale']) >= 5:
            linha = 7
        if int(conf['MARTINGALE']['niveis_martingale']) >= 6:
            linha = 8
        if int(conf['MARTINGALE']['niveis_martingale']) >= 7:
            linha = 9
        if int(conf['MARTINGALE']['niveis_martingale']) >= 8:
            linha = 10
        if int(conf['MARTINGALE']['niveis_martingale']) >= 9:
            linha = 11
        if int(conf['MARTINGALE']['niveis_martingale']) >= 10:
            linha = 12     
        martingale = int(conf['MARTINGALE']['niveis_martingale'])
    else:
        linha =2
        martingale = 0

    ############# CAPTURA PARES ABERTOS ##############

    pay_minimo = float(config["AJUSTES"]["pay_minimo"])
    
    pares_abertos = []
    pares_abertos_turbo = []
    pares_abertos_digital = []
    pares_abertos_binary = []  # Adicionar lista para binary

    if all_asset == "":
        all_asset = API.get_all_open_time()

    # Verificação dos pares no modo digital
    for par in all_asset["digital"]:
        if all_asset["digital"][par]["open"] == True:
            if par in ACTIVES:
                digital_payout = API.get_digital_payout(par)
                if digital_payout >= pay_minimo:
                    pares_abertos.append(par)
                    pares_abertos_digital.append(par)

    # Verificação dos pares no modo turbo
    for par in all_asset["turbo"]:
        if all_asset["turbo"][par]["open"] == True:
            if par in ACTIVES:
                turbo_payout = round(profit[par]["turbo"], 2) * 100
                if turbo_payout >= pay_minimo:
                    if par not in pares_abertos:
                        pares_abertos.append(par)
                        pares_abertos_turbo.append(par)  # Adicionar na lista turbo

    # Verificação dos pares no modo binary
    for par in all_asset["binary"]:
        if all_asset["binary"][par]["open"] == True:
            if par in ACTIVES:
                binary_payout = round(profit[par]["binary"], 2) * 100
                if binary_payout >= pay_minimo:
                    if par not in pares_abertos:
                        pares_abertos.append(par)
                        pares_abertos_binary.append(par)  # Adicionar na lista binary

    if "NZDUSD" in pares_abertos_binary:
        pares_abertos_binary.remove("NZDUSD")

    if "NZDUSD" in pares_abertos:
        pares_abertos.remove("NZDUSD")
    if "USOUSD" in pares_abertos:
        pares_abertos.remove("USOUSD")
    if "USDCHF" in pares_abertos:
        pares_abertos.remove("USDCHF")
    if "XAUUSD" in pares_abertos:
        pares_abertos.remove("XAUUSD")
    if "USDCHF" in pares_abertos:
        pares_abertos.remove("USDCHF")

    if "NZDUSD" in pares_abertos_digital:
        pares_abertos_digital.remove("NZDUSD")
    if "USOUSD" in pares_abertos_digital:
        pares_abertos_digital.remove("USOUSD")
    if "USDCHF" in pares_abertos_digital:
        pares_abertos_digital.remove("USDCHF")
    if "XAUUSD" in pares_abertos_digital:
        pares_abertos_digital.remove("XAUUSD")
    if "USDCHF" in pares_abertos_digital:
        pares_abertos_digital.remove("USDCHF")

    def convert(x):
        x1 =  datetime.fromtimestamp(x)
        return x1.strftime('%H:%M')

    hora =  API.get_server_timestamp()
    vela = {}
    for par in pares_abertos:
        vela[par] = {}
        data = API.get_candles(par, 60, 1000, hora)#1000 -> 240
        vela[par] = data

    def calcula_resultado(par,nome_estrategia,dicio):
        global  analise_result
        dici = dicio

        win = dici['win']
        gale1 = dici['g1']
        gale2 = dici['g2']
        gale3 = dici['g3']
        gale4 = dici['g4']
        gale5 = dici['g5']
        gale6 = dici['g6']
        gale7 = dici['g7']
        gale8 = dici['g8']
        gale9 = dici['g9']
        gale10 = dici['g10']
        loss =  dici['loss']
        
        todasentradas = win + gale1 + gale2 + gale3 + gale4 + gale5 + gale6 + gale7 + gale8 + gale9 + gale10 + loss
      
        #print(par, nome_estrategia, 'win',win ,'gale1',gale1,'gale2', gale2,'gale3',gale3,'galemax', galemax,'todas entradas', todasentradas)

        win = win
        qnt_gale1 = win + gale1
        qnt_gale2 = win + gale1 + gale2
        qnt_gale3 = win + gale1 + gale2 + gale3
        qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
        qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5
        qnt_gale6 = win + gale1 + gale2 + gale3 + gale4 + gale5 + gale6
        qnt_gale7 = win + gale1 + gale2 + gale3 + gale4 + gale5 + gale6 + gale7
        qnt_gale8 = win + gale1 + gale2 + gale3 + gale4 + gale5 + gale6 + gale7 + gale8
        qnt_gale9 = win + gale1 + gale2 + gale3 + gale4 + gale5 + gale6 + gale7 + gale8 + gale9
        qnt_gale10 = win + gale1 + gale2 + gale3 + gale4 + gale5 + gale6 + gale7 + gale8 + gale9 + gale10


        pay = 0.8
        valor_entrada = 5
        lucro_op = valor_entrada * pay
        
        if todasentradas != 0:
            assert_win = round(win/(todasentradas)*100,2)
            assert_gale1 = round(qnt_gale1/(todasentradas)*100,2)
            assert_gale2 = round(qnt_gale2/(todasentradas)*100,2)
            assert_gale3 = round(qnt_gale3/(todasentradas)*100,2)
            assert_gale4 = round(qnt_gale4/(todasentradas)*100,2)
            assert_gale5 = round(qnt_gale5/(todasentradas)*100,2)
            assert_gale6 = round(qnt_gale6/(todasentradas)*100,2)
            assert_gale7 = round(qnt_gale7/(todasentradas)*100,2)
            assert_gale8 = round(qnt_gale8/(todasentradas)*100,2)
            assert_gale9 = round(qnt_gale9/(todasentradas)*100,2)
            assert_gale10 = round(qnt_gale10/(todasentradas)*100,2)

        
        analise_result.append([nome_estrategia]+[par]+[assert_win]+[assert_gale1]+[assert_gale2]+[assert_gale3]+[assert_gale4]+[assert_gale5]+[assert_gale6]+[assert_gale7]+[assert_gale8]+[assert_gale9]+[assert_gale10])

    def contabiliza_resultado(dir,entrada,entradamax, dici_result):

        numero = 0
        while True:
            if dir == entrada[str(numero+1)]:
                if numero == 0:
                    dici_result['win'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'win', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 1 :
                    dici_result['g1'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g1', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 2 :
                    dici_result['g2'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 3 :
                    dici_result['g3'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 4 :
                    dici_result['g4'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 5 :
                    dici_result['g5'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 6 :
                    dici_result['g6'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 7 :
                    dici_result['g7'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 8 :
                    dici_result['g8'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 9 :
                    dici_result['g9'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
                elif numero == 10 :
                    dici_result['g10'] +=1
                    #if par == 'EURUSD' or  par == 'GBPUSD':
                    #print(qnt_entrada, 'g2', convert(velas[i]['from']), vela3, vela2, vela1)
                    break
            else:
            
                if martingale >= 2:
                    if  numero == 2:
                        dici_result['loss'] +=1
                        #if par == 'EURUSD' or  par == 'GBPUSD':
                        #print(qnt_entrada, 'loss', convert(velas[i]['from']), vela3, vela2, vela1)
                        break
          
            numero +=1
            if martingale >= 2:
                if numero >= 3:
                    break

        return dici_result                       
    

    def volatil(vela1):

        total = vela1
        for par in pares_abertos:
            velas = total[par]
            velas.reverse()
            qnt_entrada= 0
            dici_result = {}
            dici_result['win'] = 0
            dici_result['g1'] = 0
            dici_result['g2'] = 0
            dici_result['g3'] = 0
            dici_result['g4'] = 0
            dici_result['g5'] = 0
            dici_result['g6'] = 0
            dici_result['g7'] = 0
            dici_result['g8'] = 0
            dici_result['g9'] = 0
            dici_result['g10'] = 0
            dici_result['gmax'] = 0
            dici_result['loss'] = 0
            entrada= {}
            doji = 0
            
            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M')[1:])

                if minutos == 7 or minutos== 2:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'

                            entrada['1'] = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada['2'] = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'
                            entrada['3'] ='Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            entrada['4'] ='Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                            entrada['5'] = 'Verde' if velas[i-4]['open'] < velas[i-4]['close'] else 'Vermelha' if velas[i-4]['open'] > velas[i-4]['close'] else 'Doji'
                            entrada['6'] ='Verde' if velas[i-5]['open'] < velas[i-5]['close'] else 'Vermelha' if velas[i-5]['open'] > velas[i-5]['close'] else 'Doji'
                            entrada['7'] ='Verde' if velas[i-6]['open'] < velas[i-6]['close'] else 'Vermelha' if velas[i-6]['open'] > velas[i-6]['close'] else 'Doji'
                            entrada['8'] = 'Verde' if velas[i-7]['open'] < velas[i-7]['close'] else 'Vermelha' if velas[i-7]['open'] > velas[i-7]['close'] else 'Doji'
                            entrada['9'] ='Verde' if velas[i-8]['open'] < velas[i-8]['close'] else 'Vermelha' if velas[i-8]['open'] > velas[i-8]['close'] else 'Doji'
                            entrada['10'] ='Verde' if velas[i-9]['open'] < velas[i-9]['close'] else 'Vermelha' if velas[i-9]['open'] > velas[i-9]['close'] else 'Doji'
                            entrada['11'] ='Verde' if velas[i-10]['open'] < velas[i-10]['close'] else 'Vermelha' if velas[i-10]['open'] > velas[i-10]['close'] else 'Doji'

                            entradamax =  'Verde' if velas[i-martingale]['open'] < velas[i-martingale]['close'] else 'Vermelha' if velas[i-martingale]['open'] > velas[i-martingale]['close'] else 'Doji'
                            cores = vela1,vela2,vela3

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                qnt_entrada +=1
                                dici_result = contabiliza_resultado(dir,entrada, entradamax,dici_result)

                    except:
                        pass
                if qnt_entrada == quantidade_catalogacao:
                    break 

            calcula_resultado(par, 'VOLATILIDADE', dici_result)

    analise_result = []

    volatil(vela)
    
    if conf['MARTINGALE']['usar_martingale'] == 'S':
        if martingale <= 1:
            ordenacao = 'gale1'
            linha = 3
        if martingale == 2:
            ordenacao = 'gale2'
            linha = 4
        if martingale == 3:
            ordenacao = 'gale3'
            linha = 5
        if martingale > 4:
            ordenacao = 'gale4'
            linha = 6
        if martingale > 5:
            ordenacao = 'gale5'
            linha = 7
        if martingale > 6:
            ordenacao = 'gale6'
            linha = 8
        if martingale > 7:
            ordenacao = 'gale7'
            linha = 9
        if martingale > 8:
            ordenacao = 'gale8'
            linha = 10
        if martingale > 9:
            ordenacao = 'gale9'
            linha = 11
        if martingale > 10:
            ordenacao = 'gale10'
            linha = 12                        
    else:
        ordenacao = 'win'
        linha =2

    listaordenada = sorted(analise_result, key = lambda x: x[linha], reverse = True)

    return listaordenada, linha

perfil = json.loads(json.dumps(API.get_profile_ansyc()))
cifrao = str(perfil['currency_char'])
nome = str(perfil['name'])

valorconta = float(API.get_balance())

print(yellow + '***************************************************************************************')
print(green +'>>'+white+'  Logan Smith Trader -  Robô Volatilidade/Martingale') 
print(green +'>>'+white+'  Olá, ',nome, ' Seja bem vindo.')
print(green +'>>'+white+'  Seu Saldo na conta ',escolha, 'é de', cifrao,round(valorconta,2))
print(green +'>>'+white+'  Seu valor de entrada é de ',cifrao,round(valor_entrada,2))
print(green +'>>'+white+'  Stop win:',cifrao,round(stop_win,2))
print(green +'>>'+white+'  Stop loss:',cifrao,'-',round(stop_loss,2))
print(yellow + '***************************************************************************************')

def verifica_payouts(par):
    if tipo == 'automatico':

        if float(payouts_total['digital'][str(par)]) == 0  and float(payouts_total['turbo'][str(par)]) == 0:
            stat = False
            tipo_op = 'FECHADO'

        if float(payouts_total['digital'][str(par)]) > float(payouts_total['turbo'][str(par)]):
            if float(payouts_total['digital'][str(par)]) >= pay_minimo:
                tipo_op = 'digital'
                stat = True
            else: 
                tipo_op ='abaixo'
                stat = False

        else:
            if float(payouts_total['turbo'][str(par)]) >=pay_minimo:
                tipo_op = 'binary'
                stat = True
            else: 
                tipo_op ='abaixo'
                stat = False

    else:
        if tipo == 'binaria':
            tipo_op = 'binary'
            stat = True
        if tipo == 'digital':
            stat = True
            tipo_op = 'digital'
        try:
            if float(payouts_total['digital'][str(par)]) == 0  and float(payouts_total['turbo'][str(par)]) == 0:
                tipo_op = 'FECHADO'
                stat = False

        except:
            tipo_op = 'binary'
            stat = True

    return stat,tipo_op

def payouts():
    global payouts_total,all_asset,profit,pares_abertos

    while True:
        try:
            for par in all_asset['binary']:
                if par in ACTIVES: 
                    try:
                        if all_asset['binary'][par]['open']:
                
                            if profit[par]["binary"] > 0:
                                payouts_total['binary'][par] = round(profit[par]["binary"], 2)*100
                            else:
                                payouts_total['binary'][par] = 0
                        else:
                            payouts_total['binary'][par] = 0
                    except:
                        payouts_total['binary'][par] = 0
        except:
            pass
        try:
            for par in all_asset['turbo']:
                if par in ACTIVES:     
                    try: 
                        
                        if all_asset['turbo'][par]['open']:
                            if par not in pares_abertos:
                                pares_abertos.append(par)    
                            if profit[par]['turbo'] > 0:
                                payouts_total['turbo'][par] = round(profit[par]["turbo"], 2)*100
                            else:
                                payouts_total['turbo'][par] = 0
                        else:
                            payouts_total['turbo'][par] = 0
                    except:
                        payouts_total['turbo'][par] = 0
        except:
            pass
    
        try:
            for par in all_asset['digital']:
                if par in ACTIVES: 
                    try:    
                        if all_asset['digital'][par]['open']:
                            if par not in pares_abertos:
                                pares_abertos.append(par)    
                            payouts_total['digital'][par] = API.get_digital_payout(par)
                        else:
                            payouts_total['digital'][par] = 0
                    except:
                        payouts_total['digital'][par] = 0
        except:
            pass
        try:
            profit = API.get_all_profit()
            all_asset = API.get_all_open_time()
            time.sleep(60)
        except:
            pass
            
#        print('\npay digital')
#        for i in payouts_total['digital']:
#            if payouts_total['digital'][i] != 0:
#                print(i,payouts_total['digital'][i])
#        print('\npay binary')
#        for i in payouts_total['binary']:
#            if payouts_total['binary'][i] !=0:
#                print(i,payouts_total['binary'][i])
#        print('\npay turbo')
#        for i in payouts_total['turbo']:
#            if payouts_total['turbo'][i] !=0:
#                print(i,payouts_total['turbo'][i])
                
def payouts():
    global payouts_total, all_asset, profit, pares_abertos
print(yellow+'>> Puxando pares abertos e payouts...')

payouts_total = {}
pares_abertos = []
profit = API.get_all_profit()
all_asset = API.get_all_open_time()
payouts_total['turbo'] = {}
payouts_total['binary'] = {}
payouts_total['digital'] = {}
for par in all_asset['binary']:
    payouts_total['binary'][par] = 0
    payouts_total['turbo'][par] = 0
    payouts_total['digital'][par] = 0
for par in all_asset['turbo']:
    payouts_total['binary'][par] = 0
    payouts_total['turbo'][par] = 0
    payouts_total['digital'][par] = 0
for par in all_asset['digital']:
    payouts_total['binary'][par] = 0
    payouts_total['turbo'][par] = 0
    payouts_total['digital'][par] = 0


Thread(target=payouts).start()

def puxa_payouts():
    print('>> Puxando pares abertos        ',end = '\r')
    payouts_total = {}
    pares_abertos = []
    profit = API.get_all_profit()
    all_asset = API.get_all_open_time()
    novo = []
    payouts = []
    pares = []

    for par in all_asset['binary']:
        if all_asset['binary'][par]['open']:
            pares.append(par)

    for par in all_asset['turbo']:
        if all_asset['turbo'][par]['open']:
            if par not in pares:
                pares.append(par)
    for par in all_asset['digital']:
        if all_asset['digital'][par]['open']:
            if par not in pares:
                pares.append(par)

    for par in pares:
        print(f'>> Puxando payouts do par: {par}      ',end = '\r')
        try:
            if all_asset['binary'][par]['open']:
                bin  = round(profit[par]["binary"] * 100, 2)
            else: 
                bin = 0

            if all_asset['turbo'][par]['open']:
                turbo = round(profit[par]["turbo"] * 100 , 2)
            else:
                turbo = 0

            if all_asset['digital'][par]['open']: 
                digi = API.get_digital_payout(par)
            else:
                digi = 0

            payouts.append([par,bin,turbo,digi])
        except:
            pass
    print(tabulate(payouts,headers=['PAR','BINARY','TURBO','DIGITAL'], tablefmt="simple_grid", numalign="center"))
    
puxa_payouts()

def puxa_candles():
    """Puxa as últimas 5 velas do par EURUSD-OTC e retorna uma lista de strings ('Verde', 'Vermelha', 'Doji')."""
     
    print(f'>>> {green}PUXANDO ULTIMAS 5 VELAS DO PAR {white}{melhor_par}')
    
    velas = API.get_candles(f'{melhor_par}', 900, 5, time.time())
    hora0 = datetime.fromtimestamp(velas[-5]['from']).strftime('%H:%M')
    hora1 = datetime.fromtimestamp(velas[-4]['from']).strftime('%H:%M')
    hora2 = datetime.fromtimestamp(velas[-3]['from']).strftime('%H:%M')
    hora3 = datetime.fromtimestamp(velas[-2]['from']).strftime('%H:%M')
    hora4 = datetime.fromtimestamp(velas[-1]['from']).strftime('%H:%M')

    # Criar uma lista de strings representando as cores das velas
    cores = []
    cores.append('Verde' if velas[-5]['open'] < velas[-5]['close'] else 'Vermelha' if velas[-5]['open'] > velas[-5]['close'] else 'Doji')
    cores.append('Verde' if velas[-4]['open'] < velas[-4]['close'] else 'Vermelha' if velas[-4]['open'] > velas[-4]['close'] else 'Doji')
    cores.append('Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji')
    cores.append('Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji')
    cores.append('Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji')

    # Imprimir as velas em cores
    def cor_vela(cor):
        if cor == 'Verde':
            return Back.GREEN + '       '
        elif cor == 'Vermelha':
            return Back.RED + '       '
        elif cor == 'Doji':
            return Back.WHITE + '       '

    print('\n')
    for _ in range(7):
        print('  ', cor_vela(cores[0]), ' ', cor_vela(cores[1]), ' ', cor_vela(cores[2]), ' ', cor_vela(cores[3]), ' ', cor_vela(cores[4]))

    print('   ', str(hora0), '   ', str(hora1), '   ', str(hora2), '   ', str(hora3), '   ', str(hora4))
    print('')

    return cores  # Retorna as cores das últimas 5 velas como uma lista de strings

def escolher_par_e_tipo_automatico(API, payout_minimo=70): 
    global tipos_disponiveis, melhor_par, tempo_restante, ativo
    """ 
    Função para escolher automaticamente o par de moedas com o maior payout, 
    bloqueando os ativos que estiverem fechados, e determinar o tipo de operação 
    disponível com o maior payout entre binária e digital. 
    """ 
    # Obter todos os ativos abertos no momento

    all_assets = API.get_all_open_time() 
    all_profits = API.get_all_profit() 
    payouts = []
    pares = []
    all_asset = []
     
    ativos_excluidos = ["NZDUSD-OTC", "AUDCAD-OTC", "EURJPY-OTC", "GBPJPY-OTC", "EURGBP-OTC", "GBPUSD-OTC", "USDJPY-OTC", "USDJPY", "NZDUSD", "GBPJPY", "GBPUSD",
                        "Dollar_Index", "Yen_Index", "AUDUSD-OTC", "AUDJPY-OTC"] 
    
    # Filtrar ativos que estejam abertos e tenham payout acima do mínimo 
    ativos_disponiveis = {} 
    # Lista para catalogação dos pares em uma tabela vertical 
    catalogacao_pares = [] 
    # Verificar ativos binários abertos
    for ativo, info in all_assets['binary'].items():
        if ativo not in ativos_excluidos:  # Se o ativo não estiver na lista de excluídos 
            if info['open']:  # Verifica se o ativo está aberto 
                payout_binario = all_profits.get(ativo, {}).get('binary', 0) * 100 
                if payout_binario >= payout_minimo: 
                    ativos_disponiveis[ativo] = payout_binario 
                    # Verifica o tempo de expiração (ajuste o nome do campo conforme necessário) 
                    exp_time = info.get('expiration', 0)  # Substitua 'expiration_time' pelo campo correto 
                    if payout_binario >= payout_minimo and exp_time <= 60:  # 60 segundos = 1 minuto 
                        ativos_disponiveis[ativo] = payout_binario 
                        
                    # Adicionar ativo à catalogação para a tabela 
                    if ativo not in ["NZDUSD-OTC", "AUDCAD-OTC", "GBPJPY-OTC", "EURGBP-OTC", "GBPUSD-OTC", "EURJPY-OTC", "USDJPY-OTC", "USDJPY", "NZDUSD", "GBPJPY", "GBPUSD", 
                                     "Dollar_Index", "Yen_Index", "AUDUSD-OTC", "AUDJPY-OTC"]:
                        catalogacao_pares.append({ 
                            'Ativo': ativo, 
                            'Payout (%)': payout_binario, 
                            'Tempo Restante (s)': tempo_restante 
                        })  
         
    # Se houver ativos disponíveis com payout acima do mínimo, escolher o melhor 
    if ativos_disponiveis:
        print(f'>>> {green}Puxando pares abertos', end='\r')
        payouts = []
        pares = []

        # Verificar ativos binary e digitais abertos
        for par in all_assets['binary']:
            if ativo not in par and all_assets['binary'][par]['open']:
                pares.append(par)

        for par in all_assets['digital']:
            if ativo not in par and all_assets['digital'][par]['open']:
                if par not in pares:
                    pares.append(par)

        # Coletar payouts dos pares filtrados
        for par in pares:
            print(f'>>> {green}Puxando payouts do par: {par}', end='\r')
            try:
                bin_payout = round(all_profits.get(par, {}).get("binary", 0) * 100, 2) if all_assets['binary'].get(par, {}).get('open') else 0
                digi_payout = API.get_digital_payout(par) if all_assets['digital'].get(par, {}).get('open') else 0

                payouts.append([par, bin_payout, digi_payout])
            except:
                pass

        # Mostrar tabela de payouts
        print(tabulate(payouts, headers=['PAR', 'BINARY', 'DIGITAL'], tablefmt="double_grid", numalign="center"))
        
        # Mostrar a catalogação dos pares disponíveis em uma tabela vertical 
        df_catalogacao = pd.DataFrame(catalogacao_pares) 
        print(f"{green}Catalogação dos pares disponíveis:") 
        print(df_catalogacao)
         
        melhor_par = max(ativos_disponiveis, key=ativos_disponiveis.get) 
        print(yellow + '***************************************************************************************') 
        print(f"{green}Ativo escolhido: {melhor_par} {yellow}com payout de {ativos_disponiveis[melhor_par]:.2f}%") 
        print(yellow + '***************************************************************************************') 
        
        # Verificar disponibilidade em binária e digital, bloqueando ativos fechados 
        tipos_disponiveis = { 
            'binary': all_profits.get(melhor_par, {}).get('binary', 0) * 100 if all_assets['binary'].get(melhor_par, {}).get('open') else 0, 
            'digital': API.get_digital_payout(melhor_par) if all_assets['digital'].get(melhor_par, {}).get('open') else 0 
        } 
        
        # Filtrar os tipos com payout acima do mínimo e que estejam abertos 
        tipos_validos = {k: v for k, v in tipos_disponiveis.items() if v >= payout_minimo} 
 
        # Se houver algum tipo de operação disponível, escolher o melhor 
        if tipos_validos: 
            melhor_tipo = max(tipos_validos, key=tipos_validos.get) 
            print(f"{green}Tipo de negociação: {melhor_tipo.upper()} {yellow}com payout de {tipos_validos[melhor_tipo]:.2f}%") 
            return melhor_par, melhor_tipo 
        else: 
            print(f"{red}Nenhum tipo de negociação disponível para {melhor_par} {yellow}com payout mínimo de {payout_minimo}%.") 
            return melhor_par, None 
    else: 
        print(f"{red}Nenhum ativo disponível com {yellow}payout mínimo de {payout_minimo}%.") 
        return None, None

def wait_for_new_candle(API):
    """
    Aguarda o momento exato para o início de um novo candle de 5 minutos com precisão milimétrica.
    """
    while True:
        # Obtém o horário atual da corretora
        now = get_broker_time(API)

        # Calcula o próximo candle de 15 minutos (múltiplo de 5 no minuto, segundo 0)
        next_candle = (now + timedelta(minutes=15 - now.minute % 15)).replace(second=0, microsecond=0)

        # Aguarda até o momento exato do próximo candle
        while get_broker_time(API) < next_candle:
            # Atualiza o horário atual e a diferença para o próximo candle
            current_time = get_broker_time(API)
            time_diff = (next_candle - current_time).total_seconds()

            # Exibe o tempo restante para o próximo candle com precisão de milissegundos
            print(f"\r{green}Aguardando o próximo candle em {yellow}{time_diff:.3f} {white}segundos.", end="")

            # Aguarda 10ms para garantir uma verificação de alta precisão
            time.sleep(0.01)

        # Entrada milimétrica no novo candle
        print(f"\n{blue}Novo candle iniciado! {green}Entrando na operação.")
        break  # Sai do loop para executar a operação

def get_broker_time(API):
    """Retorna o horário atual da corretora."""
    # Obtém o timestamp do servidor da corretora
    server_timestamp = API.get_server_timestamp()
    # Converte o timestamp para um objeto datetime
    broker_time = datetime.fromtimestamp(server_timestamp)
    return broker_time

mudar_automatico = True
direcao = False
exp = 15
resposta = input("\n>> Deseja operar no melhor par? (s/n): ").strip().lower()
if resposta == 's':        
    if __name__ == "__main__":
        payout_minimo = 70  # Define o payout mínimo
        valor_entrada = float(input(f'\n>> {green}Digite o valor que você deseja operar{white}: '))
        ativos, tipo = escolher_par_e_tipo_automatico(API, payout_minimo=70)
        if ativos and tipo:
            estrategia_LSTrader_Volatility(ativos, valor_entrada, tipo)
            compra(ativo, valor_entrada, direcao, exp, tipo)  
        else:
            print("Não foi possível selecionar um ativo para operar.")       
else:
    print("\n>> Operação no melhor par ignorada.")     