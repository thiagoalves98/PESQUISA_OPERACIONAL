# -*- coding: utf-8 -*-

import pulp
import numpy

#Cria uma matriz de zeros
def Matriz(n, m):
	Matriz = []

	for i in range(n):
		n = []

		for j in range(m):
			n.append(0)

		Matriz.append(n)

	return Matriz

#Abre os arquivos com as instâncias
def Open(Name):

	if(Name == 'Dados'):
		arq = open('Dados.txt','r')
		dado = arq.read()
		arq.close()
		matriz_dado = dado.split( )
		return matriz_dado

	elif(Name == 'Demandas_cidades'):
		arq = open('Demandas_cidades.txt','r')
		demanda = arq.read()
		arq.close()
		matriz_demanda = demanda.split( )
		return matriz_demanda

	elif(Name == 'Distancias_Fabricas_Cidades'):
		arq = open('Distancias_Fabricas_Cidades.txt','r')
		f_c = arq.read()
		arq.close()
		matriz_f_c = f_c.split( )
		return matriz_f_c

	elif(Name == 'Distancias_Fabricas_Centros'):
		arq = open('Distancias_Fabricas_Centros.txt','r')
		f_cd = arq.read()
		arq.close()
		matriz_f_cd = f_cd.split( )
		return matriz_f_cd

	elif(Name == 'Distancias_Centro_Cidades'):
		arq = open('Distancias_Centros_Cidades.txt','r')
		c_cd = arq.read()
		arq.close()
		matriz_c_cd = c_cd.split( )
		return matriz_c_cd

	else:
		print("Arquivo não encontrado")

def main():

	matriz_dado 	= Open('Dados')

	#Dados de entrada
	F 	= int(matriz_dado.pop(0))		#Número de fabricas
	C 	= int(matriz_dado.pop(0))		#Número de cidades
	CD 	= int(matriz_dado.pop(0))		#Número de centros de distribuicao
	p 	= float(matriz_dado.pop(0))		#Preço do cimento
	cc 	= float(matriz_dado.pop(0))		#Custo de transporte por caminhão
	cf 	= float(matriz_dado.pop(0))		#Custo de transporte por ferrovia

	#Cria os vetores de matrizes
	y = Matriz(CD, 0)
	z = Matriz(F, 0)
	x = Matriz(F, C)
	g = Matriz(F, CD)
	q = Matriz(CD,C)
	c = Matriz(F,0)
	d = Matriz(C, 0)
	f = Matriz(CD, 0)
	cap = Matriz(F,0)

	distij = Matriz(F, C)
	distkj = Matriz(CD, C)
	distik = Matriz(F, CD)

	#Capacidade da fabrica i
	for i in range(F):
		cap[i] = float(matriz_dado.pop(0))

	#Custo da fabrica i
	for i in range(F):
		c[i] = float(matriz_dado.pop(0))

	#Taxa anual
	for k in range(CD):
		f[k] = float(matriz_dado.pop(0))

	matriz_demanda 	= Open('Demandas_cidades')

	#Demanda da cidade
	for j in range(C):
		d[j] = float(matriz_demanda.pop(0))


	matriz_f_c 		= Open('Distancias_Fabricas_Cidades')
	matriz_f_cd 	= Open('Distancias_Fabricas_Centros')
	matriz_c_cd 	= Open('Distancias_Centro_Cidades')

	#Distancias das fabricas para as cidades
	for i in range(F):
		for j in range(C):
			distij[i][j] = float(matriz_f_c.pop(0))

	#Distancias dos centros de distribuição para as cidades
	for k in range(CD):
		for j in range(C):
			distkj[k][j] = float(matriz_c_cd.pop(0))

	#Distancias das dabricas para os centros de distribuição
	for i in range(F):
		for k in range(CD):
			distik[i][k] = float(matriz_f_cd.pop(0))


	#Cria um problema de maximazação
	opt_model = pulp.LpProblem("Cadeia de Suprimento", pulp.LpMaximize)


	### VARIAVEIS DE DECISAO

	for k in range(CD):
	    y[k] = pulp.LpVariable('y'+str(k), lowBound=0, upBound=1, cat='Binary')

	for i in range(F):
	    z[i] = pulp.LpVariable('z'+str(i), lowBound=0, upBound=1, cat='Binary')
	    
	for i in range(F):
		for j in range(C):
			x[i][j] = pulp.LpVariable('x'+str(i)+str(j), lowBound=0, cat='Continuous')
	    
	for i in range(F):
		for k in range(CD):
			g[i][k] = pulp.LpVariable('g'+str(i)+str(k), lowBound=0, cat='Continuous')
	        
	for k in range(CD):
		for j in range(C):
			q[k][j] = pulp.LpVariable('q'+str(k)+str(j), lowBound=0, cat='Continuous')

	
	###FUNÇÃO OBJETIVO

	opt_model += p*(pulp.lpSum(x[i][j] for i in range(F) for j in range(C))) + p*(pulp.lpSum(g[i][k] for i in range(F) for k in range(CD))) - (pulp.lpSum(c[i] * z[i] for i in range(F))) - (pulp.lpSum(f[k] * y[k] for k in range(CD))) - cc * (pulp.lpSum(x[i][j] * distij[i][j] for i in range(F) for j in range(C))) - cf * (pulp.lpSum([g[i][k] * distik[i][k] for i in range(F) for k in range(CD)])) - cc * (pulp.lpSum(q[k][j] * distkj[k][j] for k in range(CD) for j in range(C))) 
	

	### RESTRIÇÕES

	#Restricao 1
	for j in range(C):
		opt_model += (pulp.lpSum(x[i][j] for i in range(F) for j in range(C))) + (pulp.lpSum(q[k][j] for k in range(CD) for j in range(C))) <= d[j]

	#Restricao 2
	for k in range(CD):
		opt_model += (pulp.lpSum(q[k][j] for j in range(C))) <= (pulp.lpSum(cap[i] for i in range(F))) * y[k]

	#Restricao 3
	for i in range(F):
		opt_model += (pulp.lpSum(g[i][k] for k in range(CD))) + (pulp.lpSum(x[i][j] for j in range(C))) <= cap[i] * z[i]

	#Escreve o modelo na pasta raiz
	opt_model.writeLP('Resricoes.txt')


	#Solve
	while True:

	    opt_model.solve()
	  
	    if(pulp.LpStatus[opt_model.status] == "Optimal"):

	    	print("\nSOLUCAO OTIMA ENCONTRADA ########\n")

	        print('Lucro Total = ' + str(pulp.value(opt_model.objective)))

	        break

	    else:
	        print("SOLUCAO OTIMA NAO ENCONTRADA")

if __name__=="__main__":
	main()
    
    
    
    
    
    
    
    