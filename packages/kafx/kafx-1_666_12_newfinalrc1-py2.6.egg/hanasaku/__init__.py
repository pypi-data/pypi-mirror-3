# -*- coding: utf-8 -*-
from libs import comun, video
from libs.draw import avanzado, extra
import math, random, cairo
from math import pi, sin, cos

t1 = extra.CargarTextura('hanasaku/barra3.png', extend=cairo.EXTEND_REFLECT) #salida
t2 = extra.CargarTextura('hanasaku/p2.png', extend=cairo.EXTEND_REFLECT) #base g1
t3 = extra.CargarTextura('hanasaku/barra4.png', extend=cairo.EXTEND_REFLECT) #entrada
t4 = extra.CargarTextura('hanasaku/g1.png', extend=cairo.EXTEND_REFLECT) #base 2

class FX1(comun.Fx):


	def EnDialogoEntra(self, d):
		d.MoverDe((0+(comun.Interpolar(d.progreso, (random.randint(10, 10)),0, comun.i_b_backstart))) ,(0))
		global t3, t2
		d.texturas[d.PART_RELLENO] = t2
		d.actual.modo_relleno = d.P_TEXTURA
		avanzado.GrupoInicio()
		d.Pintar()
		texto = avanzado.GrupoFin(0)
		avanzado.GrupoInicio()
		d.texturas[d.PART_RELLENO] = t3
		d.actual.modo_relleno = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso,-1480, -450) , 50, parte = d.PART_RELLENO)
		d.texturas[d.PART_BORDE] = t3
		d.actual.modo_borde = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso,-1480, -450) , 50, parte = d.PART_BORDE)
		d.Pintar()
		mascara = avanzado.GrupoFin(0)
		video.cf.ctx.set_source(texto)
		video.cf.ctx.mask(mascara)

	def EnDialogoSale(self, d):
		d.MoverA((0+(comun.Interpolar(d.progreso, 0,(random.randint(10, 10)), comun.i_b_backstart))) ,(0))
		global t1, t4
		d.texturas[d.PART_RELLENO] = t4
		d.actual.modo_relleno = d.P_TEXTURA
		avanzado.GrupoInicio()
		d.Pintar()
		texto = avanzado.GrupoFin(0)
		avanzado.GrupoInicio()
		d.texturas[d.PART_RELLENO] = t1
		d.actual.modo_relleno = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso, -2400, -1300) , 50, parte = d.PART_RELLENO )
		d.texturas[d.PART_BORDE] = t1
		d.actual.modo_borde = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso, -2400, -1300) , 50, parte = d.PART_BORDE )
		d.Pintar()
		mascara = avanzado.GrupoFin(0)
		video.cf.ctx.set_source(texto)
		video.cf.ctx.mask(mascara)

	def EnSilabaDorm(self, d):
		global t2
		d.texturas[d.PART_RELLENO] = t2
		d.actual.modo_relleno = d.P_TEXTURA
		d.Pintar()
	def EnSilabaMuerta(self, sil):
		global t4
		sil.texturas[sil.PART_RELLENO] = t4
		sil.actual.modo_relleno = sil.P_TEXTURA
		sil.Pintar()

	def EnSilaba(self, sil):
		global t4, t2
		sil.actual.sombra = 1
		sil.actual.borde = 0
		sil.Escalar(1, comun.Interpolar(sil.progreso, 2, 1, comun.i_b_boing))
		sil.Pintar()
		sil.texturas[sil.PART_RELLENO] = t2

		sil.actual.modo_relleno = sil.P_TEXTURA
		avanzado.GrupoInicio()
		sil.Pintar()
		avanzado.fGlow(1, 0.2+(sin(pi*sil.progreso)/6.0))
		avanzado.GrupoFin(comun.Interpolar(sil.progreso, 1, 0, comun.i_accel))
		sil.actual.borde = 0
		sil.texturas[sil.PART_RELLENO] = t4
		sil.actual.modo_relleno = sil.P_TEXTURA
		avanzado.GrupoInicio()
		sil.Pintar()
		avanzado.fGlow(1, 0.2+(sin(pi*sil.progreso)/6.0))
		avanzado.GrupoFin(comun.Interpolar(sil.progreso, 0, 1, comun.i_accel))



class FX2(comun.Fx):
	def EnDialogoEntra(self, d):
		global t3, t2
		d.texturas[d.PART_RELLENO] = t2
		d.actual.modo_relleno = d.P_TEXTURA
		d.Mover((d.actual.pos_x+615 ,d.actual.pos_y+(comun.Interpolar(d.progreso, (random.randint(10, 10)),0, comun.i_b_backstart) ) ), (d.actual.pos_x+615 , d.actual.pos_y) )

		avanzado.GrupoInicio()
		d.Pintar()
		texto = avanzado.GrupoFin(0)

		avanzado.GrupoInicio()
		d.texturas[d.PART_RELLENO] = t3
		d.actual.modo_relleno = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso,-1480, -850) , 50, parte = d.PART_RELLENO)
		d.texturas[d.PART_BORDE] = t3
		d.actual.modo_borde = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso,-1480, -850) , 50, parte = d.PART_BORDE)
		d.Pintar()
		mascara = avanzado.GrupoFin(0)

		video.cf.ctx.set_source(texto)
		video.cf.ctx.mask(mascara)

	def EnSilabaDorm(self, d):
		d.actual.pos_x = d.actual.pos_x+615
		global t2
		d.texturas[d.PART_RELLENO] = t2
		d.actual.modo_relleno = d.P_TEXTURA
		d.Pintar()

	def EnSilabaMuerta(self, d):
		d.actual.pos_x = d.actual.pos_x+615
		global t4
		d.texturas[d.PART_RELLENO] = t4
		d.actual.modo_relleno = d.P_TEXTURA
		d.Pintar()

	def EnDialogoSale(self, d):
		global t1, t4
		d.texturas[d.PART_RELLENO] = t4
		d.actual.modo_relleno = d.P_TEXTURA
		d.Mover((d.actual.pos_x+615 , d.actual.pos_y), (d.actual.pos_x+615 ,d.actual.pos_y+(comun.Interpolar(d.progreso, (random.randint(10, 10)),0, comun.i_b_backstart) ) ))

		avanzado.GrupoInicio()
		d.Pintar()
		texto = avanzado.GrupoFin(0)

		avanzado.GrupoInicio()
		d.texturas[d.PART_RELLENO] = t1
		d.actual.modo_relleno = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso, -2400, -1800) , 50, parte = d.PART_RELLENO )
		d.texturas[d.PART_BORDE] = t1
		d.actual.modo_borde = d.P_TEXTURA
		d.MoverTextura( comun.Interpolar(d.progreso, -2400, -1800) , 50, parte = d.PART_BORDE )
		d.Pintar()

		mascara = avanzado.GrupoFin(0)
		video.cf.ctx.set_source(texto)
		video.cf.ctx.mask(mascara)

	def EnSilaba(self, sil):
		global t4, t2
		sil.actual.sombra = 1
		sil.actual.borde = 0
		sil.Escalar(1, comun.Interpolar(sil.progreso, 1.30, 1, comun.i_b_boing))
		sil.actual.pos_x = sil.actual.pos_x+615
		sil.Pintar()
		sil.texturas[sil.PART_RELLENO] = t2
		sil.actual.modo_relleno = sil.P_TEXTURA

		avanzado.GrupoInicio()
		sil.Pintar()
		avanzado.fGlow(1, 0.2+(sin(pi*sil.progreso)/6.0))
		avanzado.GrupoFin(comun.Interpolar(sil.progreso, 1, 0, comun.i_accel))

		sil.actual.borde = 0
		sil.texturas[sil.PART_RELLENO] = t4
		sil.actual.modo_relleno = sil.P_TEXTURA

		avanzado.GrupoInicio()
		sil.Pintar()
		avanzado.fGlow(1, 0.2+(sin(pi*sil.progreso)/6.0))
		avanzado.GrupoFin(comun.Interpolar(sil.progreso, 0, 1, comun.i_accel))




class FxsGroup(comun.FxsGroup):
	def __init__(self):
		self.in_ms = 400
		self.out_ms = 400
		self.fxs = (FX1(), FX2())