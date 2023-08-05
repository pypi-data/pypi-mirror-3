# -*- coding: utf-8 -*-
"""Este efecto muestra lo mas simple, lo basico"""
from libs import comun
from libs.draw import avanzado



class EfectoGenerico(comun.Fx):
	def EnDialogo(self, diag):
		avanzado.ActivarCapa(diag._layer)
		#el parametro puede ser un numero, o un nombre, se crean cuando los activas
		#pej
		#avanzado.ActivarCapa("Cosas feas")
		#avanzado.ActivarCapa(1)
		#avanzado.ActivarCapa(0)#capa base
		diag.Pintar()
		#Luego hay que restaurar la capa base, 
		avanzado.ActivarCapa(0, 0.8) #esto no es importante si en cada evento cambias la capa
		#el 2º parametro opcional es la opacidad de la capa
		diag.actual.scale_x = 2.0
		diag.Pintar()
		
		

	def EnSilaba(self, diag):
		avanzado.ActivarCapa(3)
		diag.actual.color1.CopiarDe(diag.actual.color2) #Copiamos el color secundario al color primario,
		diag.Pintar()# Pintamos la silaba en la pantalla

		#tambien podriamos usar un modo de pintado por cada capa, al mejor estilo photoshop
		#seria dificil de entender y haria mas lento la compactacion de capas, pero permitiria mucha mas flexibilidad
		#pej
		avanzado.ModoCapa(3, 'add')
		#entonces, podes dibujar todo lo que quieras en la capa 3, usando over, y cuando compactas la capa, queda con modo add

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
		#muy importante, 
		#recien acá se pintan las capas una encima de otra, y se aplican los modos de pintado de cada CAPA
		#pej la capa 3 quedaria con modo add, el resto con over.