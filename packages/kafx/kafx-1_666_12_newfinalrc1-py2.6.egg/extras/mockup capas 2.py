# -*- coding: utf-8 -*-
"""Este efecto muestra lo mas simple, lo basico"""
from libs import comun
from libs.draw import avanzado

class EfectoGenerico(comun.Fx):
	def EnDialogo(self, diag):
		avanzado.GrupoInicio(capa=diag._layer)
		diag.Pintar()
		avanzado.GrupoFin()
		#Luego hay que restaurar la capa base, 
		avanzado.GrupoInicio(capa=0) #esto no es importante si en cada evento cambias la capa
		#el 2º parametro opcional es la opacidad de la capa
		diag.actual.scale_x = 2.0
		diag.Pintar()
		avanzado.GrupoFin(0.8)
		
		

	def EnSilaba(self, diag):
		avanzado.GrupoInicio(capa=3)
		diag.actual.color1.CopiarDe(diag.actual.color2) #Copiamos el color secundario al color primario,
		diag.Pintar()# Pintamos la silaba en la pantalla
		#esto no se puede hacer avanzado.ModoCapa(3, 'add')
		avanzado.GrupoFin()

#Esta es la clase principal de donde kafx tomara toda la info, tiene que tener este nombre
class FxsGroup(comun.FxsGroup):
	def __init__(self):
		#Opciones principales
		self.in_ms = 150 #Milisegundos para la animacion de entrada
		self.out_ms = 250 #MS para animacion d salida
		self.sil_in_ms = 500 #ms para la animacion de entrada de cada silaba sin animar (en el dialogo actual)
		self.sil_out_ms = 200 #ms para la animacion de cada silaba muerta (en el dialogo actual)
		self.fxs = (EfectoGenerico(), EfectoGenerico())

	def EnCuadroFin(self):
		avanzado.CompactarCapas()
		#sigue siendo necesario