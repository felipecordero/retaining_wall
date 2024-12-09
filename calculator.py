# from io import StringIO
import math

import numpy

from flexvigas import flexion

# import svgwrite
import plotly.graph_objects as go
import shapely as shp

# Common names

rectangulos = ["rectMuro", 
                "rectFund", 
                "rectDiente"]

class Structural_Model:

    def __init__(self, 
                #  ka, 
                 hd, 
                 hm, 
                 hf, 
                #  kae, 
                 kv,
                 kh, 
                 qsc,
                 l1,
                 l2,
                 e,
                 e_top,
                 beta,
                 phi,
                 mu,
                 fy,
                 fc,
                 rec,
                 pp_tierra = 1.8,

                 ) -> None:

        # Parametros basicos (inputs)

        self.ka: float
        self.hd: float = hd
        self.hm: float = hm
        self.hf: float = hf
        self.kae: float
        self.kv: float = kv
        self.kh: float = kh
        self.qsc: float = qsc
        self.l1: float = l1
        self.l2: float = l2
        self.hd: float = hd
        self.e: float = e
        self.e_top: float = e_top
        self.beta: float = beta
        self.pp_tierra: float = pp_tierra # ton / m3
        self.pp_concrete: float = 2.5 # ton/m3
        self.phi = phi
        self.mu = mu
        self.fy = fy
        self.fc = fc
        self.rec = rec

        # Parametros compuestos

        self.wMuro: float
        self.fRoce: float

        self.tensiones_layout = go.Figure()

        self.tensiones_layout.update_layout(
                hovermode=False,
                yaxis=dict(scaleanchor='x',
                        scaleratio=1,
                        showgrid=False, 
                        showline=False,
                        showticklabels=False
                ),
                height=150,
                xaxis=dict(showgrid=False, 
                           showline=False,
                           showticklabels=False
                ),
                margin=dict(l=0,  # Left margin
                            r=0,  # Right margin
                            b=0,  # Bottom margin
                            t=0,  # Top margin
                            pad=0   # Padding between the plotting area and the axis lines
                ),
                showlegend=False
            )

        # dibujar la linea que representa el relleno tras muro
        self.y: float = l2 * math.tan(math.radians(beta))

        self.calcularKaeKa()

        self.create_tierra_polygon()
        self.create_wall_polygon()

        self.n: float

        self.calcular_E_activo()
        self.calcular_E_sc()
        self.calcular_E_sismo()
        self.calcularMresistenteyRoce()
        self.calcularMvolcante()
        self.calcularTensiones()
        self.calcularPasivo()
        self.calcularFS()
        self.calcularAs()

    def calcularKaeKa(self):
        phi = math.radians(self.phi)
        theta = 0.0
        beta = math.radians(self.beta)
        kh = self.kh
        kv = self.kv
        ten = math.atan(kh / (1 - kv))
        delta = phi / 2
        # calculo de Kae
        a = (math.cos(phi - theta - ten)) ** 2
        b = math.cos(ten) * (math.cos(theta) ** 2) * math.cos(delta + theta + ten)
        c = math.sin(delta + phi) * math.sin(phi - beta - ten)
        d = math.cos(delta + theta + ten) * math.cos(beta - theta)
        self.kae = a / (b * ( 1 + (c / d) ** 0.5) ** 2 )

        # calculo de Ka
        ten = 0.0
        a = (math.cos(phi - theta - ten)) ** 2
        b = math.cos(ten) * (math.cos(theta) ** 2) * math.cos(delta + theta + ten)
        c = math.sin(delta + phi) * math.sin(phi - beta - ten)
        d = math.cos(delta + theta + ten) * math.cos(beta - theta)
        self.ka = a / (b * ( 1 + (c / d) ** 0.5) ** 2 )
        
    def calcular_E_activo(self):
        ka = self.ka
        pp_tierra = self.pp_tierra
        h = self.hm + self.hf
        self.eActivo = 0.5 * ka * pp_tierra * h ** 2
        self.bActivo = h / 3
        self.mActivo = self.eActivo * self.bActivo

        self.e_activo_polygon = shp.Polygon([
            (0, 0),
            (self.eActivo * 0.5, 0),
            (0, h)
        ])

    def calcular_E_sismo(self):
        kae = self.kae
        pp_tierra = self.pp_tierra
        h = self.hm + self.hf
        kv = self.kv
        pae = 0.5 * kae * pp_tierra * h ** 2 * (1 - kv)
        self.eSismo = pae - self.eActivo
        self.bSismo = 2 / 3 * h
        self.mSismo = self.eSismo * self.bSismo

        self.e_sismo_polygon = shp.Polygon([
            (0, 0),
            (self.eSismo * 0.5, h),
            (0, h)
        ])

    def calcular_E_sc(self):
        ka = self.ka
        h = self.hm + self.hf
        qsc = self.qsc
        self.eSC = ka * qsc * h
        self.bSC = h * 0.5
        self.mSC = self.eSC * self.bSC

        self.e_sc_polygon = shp.Polygon([
            (0, 0),
            (self.eSC / h / 2, 0),
            (self.eSC / h / 2, h),
            (0, h)
        ])

    def calcularPasivo(self):
        # parametros generales
        hd = self.hd
        phi = math.radians(self.phi)
        ang = math.tan(math.radians(45.0) + phi / 2)
        c  = hd * ang
        kp = ang ** 2
        l_fund = self.aBase

        # empuje estatico pasivo
        hd = self.sPPSC1
        b = self.sPPSC2
        s2 = 0.0
        if b <= 0.0:
            s2 = hd - c * (hd + b) / l_fund
        else:
            s2 = b + (l_fund - c) / l_fund * (hd - b)
        sPasivo = c * (hd + s2) / 2
        self.ePasivoEst = kp * sPasivo

        # empuje sismico del pasivo
        hd = self.sPPSIS1
        b = self.sPPSIS2
        s2 = 0.0
        if b <= 0.0:
            s2 = hd - c * (hd + b) / l_fund
        else:
            s2 = b + (l_fund - c) / l_fund * (hd - b)
        sPasivo = c * (hd + s2) / 2
        self.ePasivoSis = kp * sPasivo
        self.kp = kp

    def calcularMresistenteyRoce(self):
        mu = self.mu
        self.wSCresistente = self.qsc * self.l2
        n = self.n = self.wMuro + self.wTierra + self.wSCresistente
        self.mMuro = self.wMuro * self.wall_centroide_x
        self.mTierra = self.wTierra * self.tierra_centroide_x
        self.bSCresistente = self.l1 + self.e + self.l2 / 2
        self.mSCresistente = self.wSCresistente * self.bSCresistente
        self.mResistente = self.mMuro + self.mTierra + self.mSCresistente
        self.fRoce = mu * n

    def calcularMvolcante(self):
        m1 = self.mActivo + self.mSismo
        m2 = self.mActivo + self.mSC
        self.mVocante = max(m1,m2)

    def calcularTensiones(self):
        self.aBase =  self.l1 + self.l2 + self.e
        self.omegaMuro = self.aBase ** 2 / 6
        levanteEst = 0.0
        levanteSis = 0.0
        nPPSC = self.wMuro + self.wTierra + self.wSCresistente
        nPPSIS = self.wMuro + self.wTierra
        mPPSC = self.mActivo + self.mSC + \
                - self.wMuro * (self.wall_centroide_x - self.aBase / 2) + \
                - self.wTierra * (self.tierra_centroide_x - self.aBase / 2)
        mPPSIS = self.mActivo + self.mSismo + \
                 - self.wMuro * (self.wall_centroide_x - self.aBase / 2) + \
                 - self.wTierra * (self.tierra_centroide_x - self.aBase / 2)
        # calculo de las tensiones minimas:
        if mPPSC / nPPSC > self.aBase / 6:
            self.sPPSC1 = 2 / 3 * nPPSC / ((self.aBase / 2 - mPPSC / nPPSC) * self.aBase)
            self.sPPSC2 = 0.0
            levanteEst = 3 * mPPSC / nPPSC - self.aBase / 2
        else:
            self.sPPSC1 = nPPSC / self.aBase + mPPSC / self.omegaMuro
            self.sPPSC2 = nPPSC / self.aBase - mPPSC / self.omegaMuro

        if mPPSIS / nPPSIS > self.aBase / 6:
            self.sPPSIS1 = 2 / 3 * nPPSIS / ((self.aBase / 2 - mPPSIS / nPPSIS) * self.aBase)
            self.sPPSIS2 = 0.0
            levanteSis = 3 * mPPSIS / nPPSIS - self.aBase / 2
        else:
            self.sPPSIS1 = nPPSIS / self.aBase + mPPSIS / self.omegaMuro
            self.sPPSIS2 = nPPSIS / self.aBase - mPPSIS / self.omegaMuro
            
        # poligono para tensiones estaticas
        self.tensiones_estaticas_polygon = shp.Polygon([
            (0.0, 0.0),
            (0.0, -self.sPPSC1 * 0.1),
            ((self.aBase - levanteEst), -self.sPPSC2 * 0.1),
            ((self.aBase - levanteEst), 0.0),
        ])
        
        # poligono para tensiones sismicas
        self.tensiones_sismicas_polygon = shp.Polygon([
            (0.0, 0.0),
            (0.0, - self.sPPSIS1 * 0.1),
            ((self.aBase - levanteSis), - self.sPPSIS2 * 0.1),
            ((self.aBase - levanteSis), 0.0)
        ])

        self.levanteEst = levanteEst
        self.levanteSis = levanteSis

    def calcularFS(self):
        self.fsPPSCD = (self.fRoce + self.ePasivoEst) / (self.eActivo + self.eSC)
        self.fsPPSCV = self.mResistente / (self.mActivo + self.mSC)
        self.fsPPSISD = (self.fRoce + self.ePasivoSis - self.mu * self.wSCresistente)\
                         / (self.eActivo + self.eSismo)
        self.fsPPSISV = (self.mResistente - self.mSCresistente) / (self.mActivo + self.mSismo)

    def calcularAs(self):
        hm = self.hm
        ka = self.ka
        sc = self.qsc
        d = self.pp_tierra
        mSC = ka * sc * hm * hm / 2
        mEa = ka * d * hm * hm / 2 * hm / 3
##        mEs = kh * d * hf * hm * hm / 2 + kh * d * hm * hm / 2 * 2 / 3 * hm
        mEs = self.mSismo
        mu = 1.5 * max(mSC + mEa, mEs + mEa)
        h = self.e * 100
        b = 1.0 * 100
        rec = self.rec
        fc = self.fc
        fy = self.fy
        pu = 0.0
        a = flexion(h,b,rec,fc,fy,mu,pu)[0]

        return {
            "Mu [ton m / m] : ": mu,
            "As [cm² / m] : ": a
        }
    
    def create_wall_polygon(self):

        l1 = self.l1
        l2 = self.l2
        hf = self.hf
        hd = self.hd
        hm = self.hm
        e = self.e
        e_top = self.e_top

        self.muro_polygon = shp.Polygon([
            (l1, hf),
            (l1 + e, hf),
            (l1 + e, hf + hm),
            (l1 + e - e_top, hf + hm)
        ])

        self.fund_polygon = shp.Polygon([
            (0, hf),
            (l1 + e + l2, hf),
            (l1 + e + l2, 0),
            (0, 0)
        ])

        self.diente_polygon = shp.Polygon([
            (l1, 0),
            (l1 + e, 0),
            (l1 + e, - hd),
            (l1, - hd)

        ])

        muro = self.wall_polygon = shp.union_all([self.muro_polygon,
                                                   self.fund_polygon,
                                                   self.diente_polygon])

        self.wall_area = muro.area
        self.wall_centroide_x = muro.centroid.x

        self.wMuro = 2.5 * self.wall_area

    def create_tierra_polygon(self):
        l1 = self.l1
        l2 = self.l2
        hf = self.hf
        hm = self.hm
        e = self.e
        y = self.y
        tierra = self.tierra_polygon = shp.Polygon([
            (l1 + e, hf),
            (l1 + e + l2, hf),
            (l1 + e + l2, hf + hm + y),
            (l1 + e, hf + hm)]
        )
        self.tierra_centroide_x = tierra.centroid.x
        self.tierra_area = tierra.area
        self.wTierra = self.pp_tierra * tierra.area

    # def update_drawing(self):

    def create_drawing(self):
        l1 = self.l1
        l2 = self.l2
        hf = self.hf
        hm = self.hm
        e = self.e
        e_top = self.e_top
        y = self.y
        hd = self.hd
        beta = self.beta

        # using plotly

        fig = go.Figure()
        x, y = numpy.array(self.wall_polygon.exterior.coords.xy)

        muro_scatter = go.Scattergl(x=x, 
                                     y=y, 
                                     fill="toself",
                                     fillcolor="lightgray",
                                     showlegend=False,
                                     mode="lines",
                                    line=dict(width=1,
                                              color='black'))
        
        x, y = numpy.array(self.tierra_polygon.exterior.coords.xy)
        
        tierra_scatter = go.Scattergl(x=x, 
                                      y=y, 
                                      fill="toself", fillcolor="antiquewhite", showlegend=False,
                                      mode="lines",
                                      line=dict(width=1,
                                                color='black'))

        fig.add_traces([muro_scatter, tierra_scatter])

        # Dibujar los empujes

        # e_activo
        e_activo_polygon = shp.affinity.translate(self.e_activo_polygon,
                                                  xoff=l1 + l2 + e + 0.5)
        
        x, y = numpy.array(e_activo_polygon.exterior.coords.xy)

        e_activo_scatter = go.Scattergl(x=x, 
                                        y=y, 
                                        name="E_activo",
                                        mode="lines"
                                        )

        # e_sismo

        minx, _, maxx, _ = self.e_activo_polygon.bounds

        e_sismo_polygon = shp.affinity.translate(self.e_sismo_polygon,
                                                  xoff=l1 + l2 + e + 0.5 + 0.5 + maxx - minx)
        
        x, y = numpy.array(e_sismo_polygon.exterior.coords.xy)

        e_sismo_scatter = go.Scattergl(x=x, 
                                       y=y, 
                                       name="E_Sismo", 
                                       mode="lines")

        # e_sc

        minx, _, maxx, _ = shp.union_all([e_activo_polygon, 
                                          e_sismo_polygon]).bounds

        e_sc_polygon = shp.affinity.translate(self.e_sc_polygon,
                                                  xoff=l1 + l2 + e + 0.5 + 0.5 + maxx - minx)
        
        x, y = numpy.array(e_sc_polygon.exterior.coords.xy)

        e_sc_scatter = go.Scattergl(x=x, 
                                    y=y, 
                                    name="SC", 
                                    mode="lines")

        # Agregando los empujes a la escena

        fig.add_traces([e_activo_scatter, 
                            e_sismo_scatter,
                            e_sc_scatter])
        
        fig.update_layout(
            hovermode=False,
            yaxis=dict(scaleanchor='x',
                       scaleratio=1,
                       showgrid=False, 
                        showline=False,
                        showticklabels=False
                       ),
            xaxis=dict(scaleanchor='x',
                       scaleratio=1,
                       showgrid=False, 
                        showline=False,
                        showticklabels=False
                       ),
            margin=dict(l=0,  # Left margin
                        r=0,  # Right margin
                        b=0,  # Bottom margin
                        t=0,  # Top margin
                        pad=0   # Padding between the plotting area and the axis lines
            ),

        )

        # Dimensions anotations

        # hf
        fig.add_annotation(x=l1 + e + l2, 
                           y=hf / 2,
                           showarrow=False,
                           textangle=-90,
                           xshift=10,
                           text=f"Hf = {round(hf, 2)} [m]")

        # hm
        fig.add_annotation(x=l1, 
                           y=hf + hm / 2,
                           showarrow=False,
                           textangle=-90,
                           xshift=-12, 
                           text=f"Hm = {round(hm, 2)} [m]")

        # e bottom
        fig.add_annotation(x=l1 + e / 2, 
                           y=hf,
                           showarrow=True,
                           textangle=0,
                        #    xshift=20,
                        #    yshift=11,
                           text=f"e bottom = {round(e, 2)} [m]")

        # e top
        fig.add_annotation(x=l1 + e_top / 2, 
                           y=hf + hm,
                           showarrow=False,
                           textangle=0,
                           yshift=11,
                           text=f"e top = {round(e_top, 2)} [m]")

        # l1
        fig.add_annotation(x=l1 / 2, 
                           y=hf,
                           showarrow=False,
                           textangle=0,
                            xshift=-20,
                            yshift=10,
                           text=f"L1 = {round(l1, 2)} [m]")

        # l2
        fig.add_annotation(x=l1 + e + l2 / 2, 
                           y=0,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=-11,
                           text=f"L2 = {round(l2, 2)} [m]")

        # hd
        if hd:
            text_hd = f"Hd = {round(hd, 2)} [m]"
        else:
            text_hd = "No Hd defined"
        fig.add_annotation(x=l1 + e / 2, 
                           y=0 - hd,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=-11,
                           text=text_hd)
        
        # beta
        fig.add_annotation(x=l1 + e + l2 / 2, 
                           y=hf + hm,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=11,
                           text=f"β = {round(beta, 2)} °")
        

        # empuje activo
        minx, _, maxx, _ = e_activo_polygon.bounds
        fig.add_annotation(x=minx + (maxx - minx) / 2, 
                           y=0,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=-11,
                           text=f"Max σ Active = {round(self.eActivo / (hm + hf) * 2, 2)} [ton/m²]")
        
        # empuje sismo
        minx, _, maxx, _ = e_sismo_polygon.bounds
        fig.add_annotation(x=minx + (maxx - minx) / 2, 
                           y=hf + hm,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=11,
                           text=f"Max σ Seismic = {round(self.eSismo / (hm + hf) * 2, 2)} [ton/m²]")
        
        # empuje sc
        minx, _, maxx, _ = e_sc_polygon.bounds
        fig.add_annotation(x=minx + (maxx - minx) / 2, 
                           y=0,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=-11,
                           text=f"Max σ Live Load = {round(self.eSC / (hf + hm), 2)} [ton/m²]")
        
        # empuje pasivo Estatico
        fig.add_annotation(x=-0.5, 
                           y=0,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=-11,
                           text=f"E Pasive (static) = {round(self.ePasivoEst, 1)} [ton]")
        
        # empuje pasivo Seismic
        fig.add_annotation(x=-0.5, 
                           y=0,
                           showarrow=False,
                           textangle=0,
                            # xshift=-20,
                            yshift=-30,
                           text=f"E Pasive (seismic) = {round(self.ePasivoSis, 1)} [ton]")

        return fig
    
        # svg approach

        # width = (self.l1 + self.l2 + self.e) * 1.2
        # height = (self.hd + self.hf + self.hm) * 1.2

        # dwg_wall = svgwrite.Drawing(size = (width,
        #                                     height))
        
        # dwg_wall.viewbox(width=width, height=height)
        
        # # Add a group with a transform to invert the y-axis
        # group = dwg_wall.g(transform=f'scale(1, -1) translate(0, -{height})')

        # group.add(dwg_wall.polygon([i for i in self.wall_polygon.exterior.coords], fill='lightgray', stroke='black', stroke_width=0.01))

        # group.add(dwg_wall.polygon([i for i in self.tierra_polygon.exterior.coords], fill='burlywood', stroke='black', stroke_width=0.01))

        # dwg_wall.add(group)

        # return buffer_wall.getvalue()
    
    def draw_tensiones_estaticas(self):

        # zapata
        x, y = numpy.array(self.fund_polygon.exterior.coords.xy)
        fund_scatter = go.Scattergl(x=x,
                                    y=y,
                                    fill="toself",
                                    fillcolor="lightgray",
                                    mode="lines",
                                    line=dict(width=1,
                                                color='black'))

        # tensiones

        x, y = numpy.array(self.tensiones_estaticas_polygon.exterior.coords.xy)
        tensiones_scatter = go.Scattergl(x=x,
                                    y=y,
                                    fill="toself",
                                    fillcolor="paleturquoise",
                                    mode="lines",
                                    line=dict(width=1,
                                                color='black'))
        
        fig = go.Figure()

        fig.add_traces([fund_scatter, tensiones_scatter])

        fig.update_layout(self.tensiones_layout.layout)

        # anotations

        minx, miny, maxx, maxy = self.tensiones_estaticas_polygon.bounds

        fig.add_annotation(
            x=minx, 
            y=0, 
            text=f"{round(self.sPPSC1, 1)}",
            showarrow=False,
            textangle=-90,
            xshift=-10,
            yshift=-15
            # font=dict(
            #     size=16,
            #     color="#ffffff"
            # ),
            # bgcolor="#ff7f0e",
            # bordercolor="#c7c7c7",
            # borderwidth=2,
            # borderpad=4,
            )
        fig.add_annotation(
            x=maxx, 
            y=0, 
            text=f"{round(self.sPPSC2, 1)}",
            showarrow=False,
            textangle=-90,
            xshift=10,
            yshift=-15
        )

        return fig
    
    def draw_tensiones_sismicas(self):

        # zapata
        x, y = numpy.array(self.fund_polygon.exterior.coords.xy)
        fund_scatter = go.Scattergl(x=x,
                                    y=y,
                                    fill="toself",
                                    fillcolor="lightgray",
                                    mode="lines",
                                      line=dict(width=1,
                                                color='black'))

        # tensiones

        x, y = numpy.array(self.tensiones_sismicas_polygon.exterior.coords.xy)
        tensiones_scatter = go.Scattergl(x=x,
                                    y=y,
                                    fill="toself",
                                    fillcolor="paleturquoise",
                                    mode="lines",
                                      line=dict(width=1,
                                                color='black'))
        
        fig = go.Figure()

        fig.add_traces([fund_scatter, tensiones_scatter])

        fig.update_layout(self.tensiones_layout.layout)

        # anotations

        minx, miny, maxx, maxy = self.tensiones_sismicas_polygon.bounds

        fig.add_annotation(
            x=minx, 
            y=0, 
            text=f"{round(self.sPPSIS1, 1)}",
            showarrow=False,
            textangle=-90,
            xshift=-10,
            yshift=-15
            )
        fig.add_annotation(
            x=maxx, 
            y=0, 
            text=f"{round(self.sPPSIS2, 1)}",
            showarrow=False,
            textangle=-90,
            xshift=10,
            yshift=-15
            )

        return fig
    
    def get_lifting(self):
        return self.levanteEst, self.levanteSis
    
    def get_results(self):
        return {
            "K active [adim]": self.ka,
            "K ae [adim]": self.kae,
            # "K pasive [adim]": self.kp,
            "W_Concrete [ton/m]" : self.wMuro,
            "W_Soil [ton/m]": self.wTierra,
            "M_resistent [ton m /m]": self.mResistente,
            "M_overturning [ton m /m]": self.mVocante,
            "E_active [ton/m2 /m]": self.eActivo,
            "E_seismic [ton/m2 /m]": self.eSismo,
            "E_Live_Load [ton/m2 /m]": self.eSC,
            "Frictional Force [ton /m]": self.fRoce,
        }
    
    def get_fs(self):
        return {
            "SF Sliding Static": self.fsPPSCD,
            "SF Overturning Static": self.fsPPSCV,
            "SF Sliding Dynamic": self.fsPPSISD,
            "SF Overturning Dynamic": self.fsPPSISV
        }