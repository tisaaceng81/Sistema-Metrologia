# -*- coding: utf-8 -*-
import sys
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import Label as CoreLabel
from kivy.utils import platform
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import black, red, yellow, grey
from plyer import filechooser

def resource_path(filename):
    """Retorna o caminho correto do arquivo para rodar dentro do exe ou no desenvolvimento."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

# Configurações da janela
Window.size = (360, 640)
Window.title = "Demarcação de Pista para Verificação de Taxímetro"

def criar_titulo():
    """Cria um widget Label para o título do aplicativo."""
    return Label(
        text="Demarcação de Pista para Verificação de Taxímetro",
        size_hint=(1, 0.1),
        font_size=16,
        bold=True,
        color=(0, 0, 0, 1),
        halign='center',
        valign='middle'
    )

class TelaInicial(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Fundo branco para a tela
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(criar_titulo())

        # Logo com caminho seguro
        logo = Image(source=resource_path('ibametro.png'), size_hint=(1, 0.5))
        layout.add_widget(logo)

        botao = Button(
            text="Iniciar",
            size_hint=(1, 0.1),
            font_size=20,
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        botao.bind(on_release=self.ir_para_proxima)
        layout.add_widget(botao)

        rodape = Label(
            text="Desenvolvido por Tiago Carneiro",
            size_hint=(1, 0.1),
            font_size=14,
            color=(0, 0, 0, 1)
        )
        layout.add_widget(rodape)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def ir_para_proxima(self, *args):
        self.manager.current = 'entrada'

class TelaEntradaDados(Screen):
    """
    Tela para o usuário inserir os dados referentes às bandeiras 1 e 2 do taxímetro.
    Calcula os resultados e permite visualizar as pistas ou gerar um PDF.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=8)

        # Fundo branco
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout.add_widget(criar_titulo())

        grid = GridLayout(cols=2, spacing=6, size_hint=(1, 0.65))

        # Bandeira 1 inputs
        self.entrada_bandeirada1 = TextInput(hint_text='B 1 (R$)', input_filter='float', multiline=False)
        self.entrada_valor_faccao1 = TextInput(hint_text='Valor por Fração 1 (R$)', input_filter='float', multiline=False)
        self.entrada_num_fracoes1 = TextInput(hint_text='Nº de frações 1', input_filter='int', multiline=False)
        self.entrada_comprimento_fracao1 = TextInput(hint_text='Comp. da fração 1 (m)', input_filter='float', multiline=False)

        grid.add_widget(Label(text="B 1 (R$):", color=(0,0,0,1)))
        grid.add_widget(self.entrada_bandeirada1)
        grid.add_widget(Label(text="Valor por fração 1 (R$):", color=(0,0,0,1)))
        grid.add_widget(self.entrada_valor_faccao1)
        grid.add_widget(Label(text="Nº de frações 1:", color=(0,0,0,1)))
        grid.add_widget(self.entrada_num_fracoes1)
        grid.add_widget(Label(text="Comp. da fração 1 (m):", color=(0,0,0,1)))
        grid.add_widget(self.entrada_comprimento_fracao1)

        grid.add_widget(Label(text=""))  # espaçador
        grid.add_widget(Label(text=""))  # espaçador

        # Bandeira 2 inputs
        self.entrada_bandeirada2 = TextInput(hint_text='B 2 (R$)', input_filter='float', multiline=False)
        self.entrada_valor_faccao2 = TextInput(hint_text='Valor por Fração 2 (R$)', input_filter='float', multiline=False)
        self.entrada_num_fracoes2 = TextInput(hint_text='Nº de frações 2', input_filter='int', multiline=False)
        self.entrada_comprimento_fracao2 = TextInput(hint_text='Comp. da fração 2 (m)', input_filter='float', multiline=False)

        grid.add_widget(Label(text="B 2 (R$):", color=(0,0,0,1)))
        grid.add_widget(self.entrada_bandeirada2)
        grid.add_widget(Label(text="Valor por fração 2 (R$):", color=(0,0,0,1)))
        grid.add_widget(self.entrada_valor_faccao2)
        grid.add_widget(Label(text="Nº de frações 2:", color=(0,0,0,1)))
        grid.add_widget(self.entrada_num_fracoes2)
        grid.add_widget(Label(text="Comp. da fração 2 (m):", color=(0,0,0,1)))
        grid.add_widget(self.entrada_comprimento_fracao2)

        self.layout.add_widget(grid)

        self.botao_calcular = Button(text="Calcular", size_hint=(1, 0.08), background_color=(0, 0.6, 0.3, 1), color=(1,1,1,1))
        self.botao_calcular.bind(on_release=self.calcular_tolerancia)
        self.layout.add_widget(self.botao_calcular)

        self.resultado_label = Label(text="", halign="center", valign="middle", size_hint=(1, 0.2), markup=True, color=(0,0,0,1))
        self.layout.add_widget(self.resultado_label)

        botoes_finais = BoxLayout(size_hint=(0.8, 0.08), spacing=5, pos_hint={'center_x': 0.5})

        self.botao_visualizar1 = Button(text="Pista 1", disabled=True, background_color=(0.2, 0.5, 0.8, 1), color=(1,1,1,1))
        self.botao_visualizar1.bind(on_release=self.ir_para_pista1)

        self.botao_visualizar2 = Button(text="Pista 2", disabled=True, background_color=(0.1, 0.4, 0.6, 1), color=(1,1,1,1))
        self.botao_visualizar2.bind(on_release=self.ir_para_pista2)
        
        self.botao_gerar_pdf = Button(text="Gerar PDF", disabled=True, background_color=(0.8, 0.2, 0.2, 1), color=(1,1,1,1))
        self.botao_gerar_pdf.bind(on_release=self.gerar_pdf_report)

        self.botao_voltar = Button(text="Voltar", background_color=(0.6, 0, 0, 1), color=(1,1,1,1))
        self.botao_voltar.bind(on_release=self.voltar_inicio)

        botoes_finais.add_widget(self.botao_voltar)
        botoes_finais.add_widget(self.botao_visualizar1)
        botoes_finais.add_widget(self.botao_visualizar2)
        botoes_finais.add_widget(self.botao_gerar_pdf)

        self.layout.add_widget(botoes_finais)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def calcular_tolerancia(self, *args):
        try:
            self.bandeirada1 = float(self.entrada_bandeirada1.text)
            self.valor_fracao1 = float(self.entrada_valor_faccao1.text)
            self.num_fracoes1 = int(self.entrada_num_fracoes1.text)
            self.comprimento_fracao1 = float(self.entrada_comprimento_fracao1.text)
            self.comprimento_pista1 = self.num_fracoes1 * self.comprimento_fracao1
            self.tarifa_estimativa1 = self.bandeirada1 + self.num_fracoes1 * self.valor_fracao1
            self.tolerancia_metros1 = self.comprimento_pista1 * 0.02

            self.bandeirada2 = float(self.entrada_bandeirada2.text)
            self.valor_fracao2 = float(self.entrada_valor_faccao2.text)
            self.num_fracoes2 = int(self.entrada_num_fracoes2.text)
            self.comprimento_fracao2 = float(self.entrada_comprimento_fracao2.text)
            self.comprimento_pista2 = self.num_fracoes2 * self.comprimento_fracao2
            self.tarifa_estimativa2 = self.bandeirada2 + self.num_fracoes2 * self.valor_fracao2
            self.tolerancia_metros2 = self.comprimento_pista2 * 0.02

            self.resultado_label.text = (
                "[b]Resultados Bandeira 1:[/b]\n"
                f"Comprimento da pista: {self.comprimento_pista1:.2f} m\n"
                f"Tarifa estimada: R$ {self.tarifa_estimativa1:.2f}\n"
                f"Tolerância permitida: ± {self.tolerancia_metros1:.2f} m\n"
                "[b]Resultados Bandeira 2:[/b]\n"
                f"Comprimento da pista: {self.comprimento_pista2:.2f} m\n"
                f"Tarifa estimada: R$ {self.tarifa_estimativa2:.2f}\n"
                f"Tolerância permitida: ± {self.tolerancia_metros2:.2f} m"
            )
            self.botao_visualizar1.disabled = False
            self.botao_visualizar2.disabled = False
            self.botao_gerar_pdf.disabled = False
        except Exception as e:
            self.resultado_label.text = f"[color=ff0000]Erro nos dados inseridos.[/color]\n{e}"
            self.botao_visualizar1.disabled = True
            self.botao_visualizar2.disabled = True
            self.botao_gerar_pdf.disabled = True

    def ir_para_pista1(self, *args):
        app = App.get_running_app()
        app.visual_pista1.atualizar_desenho(
            self.num_fracoes1,
            self.comprimento_pista1,
            self.comprimento_fracao1,
            self.tolerancia_metros1,
            self.bandeirada1,
            self.valor_fracao1
        )
        self.manager.current = 'visual1'

    def ir_para_pista2(self, *args):
        app = App.get_running_app()
        app.visual_pista2.atualizar_desenho(
            self.num_fracoes2,
            self.comprimento_pista2,
            self.comprimento_fracao2,
            self.tolerancia_metros2,
            self.bandeirada2,
            self.valor_fracao2
        )
        self.manager.current = 'visual2'

    def voltar_inicio(self, *args):
        self.manager.current = 'inicial'

    def gerar_pdf_report(self, *args):
        try:
            file_path = filechooser.save_file(
                title='Salvar Relatório PDF',
                filters=[('PDF Documents', '*.pdf')],
                # path=os.path.expanduser("~")  # opcional
            )

            if file_path:
                if isinstance(file_path, (list, tuple)):
                    file_path = file_path[0]
                self.gerar_pdf(file_path)
                self.resultado_label.text = f"[color=008000]Relatório salvo em:[/color]\n[size=12]{file_path}[/size]"
            else:
                self.resultado_label.text = "[color=ff8c00]Geração de PDF cancelada.[/color]"

        except Exception as e:
            self.resultado_label.text = f"[color=ff0000]Erro ao salvar o PDF: {e}[/color]"

    def gerar_pdf(self, caminho_pdf):
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        largura, altura = A4
        margem_esq = 2 * cm
        comprimento_px = 12 * cm
        altura_pista = 20

        def desenhar_pista(y_top, titulo, bandeirada, valor_fracao, comprimento_pista,
                           comprimento_fracao, num_fracoes, tarifa_estimativa, tolerancia):
            espacamento_texto = 18

            c.setFont("Helvetica-Bold", 14)
            c.drawString(margem_esq, y_top, titulo)
            y = y_top - espacamento_texto

            c.setFont("Helvetica", 12)
            c.drawString(margem_esq, y, f"Bandeirada: R$ {bandeirada:.2f}")
            y -= espacamento_texto
            c.drawString(margem_esq, y, f"Valor por fração: R$ {valor_fracao:.2f}")
            y -= espacamento_texto
            c.drawString(margem_esq, y, f"Número de frações: {num_fracoes}")
            y -= espacamento_texto
            c.drawString(margem_esq, y, f"Comprimento da fração: {comprimento_fracao:.2f} m")
            y -= espacamento_texto
            c.drawString(margem_esq, y, f"Comprimento da pista: {comprimento_pista:.2f} m")
            y -= espacamento_texto
            c.drawString(margem_esq, y, f"Tarifa estimada: R$ {tarifa_estimativa:.2f}")
            y -= espacamento_texto
            c.drawString(margem_esq, y, f"Tolerância permitida: ± {tolerancia:.2f} m")

            y_pista = y - 50
            x_ini = margem_esq

            c.setFillColor(grey)
            c.rect(x_ini, y_pista, comprimento_px, altura_pista, fill=1)
            c.setStrokeColor(yellow)
            c.setLineWidth(1.5)
            c.line(x_ini, y_pista + 5, x_ini + comprimento_px, y_pista + 5)
            c.line(x_ini, y_pista + 15, x_ini + comprimento_px, y_pista + 15)
            c.setStrokeColor(black)
            c.setLineWidth(2)
            c.line(x_ini, y_pista + 10, x_ini + comprimento_px, y_pista + 10)

            c.setStrokeColor(red)
            y_cota = y_pista + 30
            c.line(x_ini, y_cota, x_ini + comprimento_px, y_cota)
            c.line(x_ini, y_cota - 3, x_ini, y_cota + 3)
            c.line(x_ini + comprimento_px, y_cota - 3, x_ini + comprimento_px, y_cota + 3)
            c.setFont("Helvetica", 10)
            c.drawCentredString(x_ini + comprimento_px / 2, y_cota + 5, f"{comprimento_pista:.2f} m")

            tol_px = (tolerancia / comprimento_pista) * comprimento_px if comprimento_pista else 0
            x_centro = x_ini + comprimento_px / 2
            y_tol = y_pista - 15
            c.line(x_centro - tol_px, y_tol, x_centro + tol_px, y_tol)
            c.line(x_centro - tol_px, y_tol - 3, x_centro - tol_px, y_tol + 3)
            c.line(x_centro + tol_px, y_tol - 3, x_centro + tol_px, y_tol + 3)
            c.drawCentredString(x_centro, y_tol - 10, f"± {tolerancia:.2f} m")

            y_formula_base = y_tol - 30
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawCentredString(x_centro, y_formula_base + 10, "Comp. da pista = Nº de frações × Comp. da fração")
            c.drawCentredString(x_centro, y_formula_base - 5, f"Tarifa estimada = {bandeirada:.2f} + {num_fracoes} x {valor_fracao:.2f}")

            return y_formula_base - 25

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(largura / 2, altura - 2 * cm, "Demarcação de Pista para Verificação de Taxímetro")

        y_atual = altura - 3 * cm
        y_atual = desenhar_pista(
            y_atual,
            "Bandeira 1:",
            self.bandeirada1,
            self.valor_fracao1,
            self.comprimento_pista1,
            self.comprimento_fracao1,
            self.num_fracoes1,
            self.tarifa_estimativa1,
            self.tolerancia_metros1
        )

        desenhar_pista(
            y_atual,
            "Bandeira 2:",
            self.bandeirada2,
            self.valor_fracao2,
            self.comprimento_pista2,
            self.comprimento_fracao2,
            self.num_fracoes2,
            self.tarifa_estimativa2,
            self.tolerancia_metros2
        )

        c.save()

# (AQUI você pode ter a definição das telas VisualPista1, VisualPista2, o gerenciador e o App principal)


class TelaVisualPistaBase(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

        with self.canvas.before:
            Color(1, 1, 1, 1)  # Fundo branco
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Área para desenho da pista
        self.canvas_area = FloatLayout()
        self.layout.add_widget(self.canvas_area)

        # Botão Voltar criado uma vez
        self.botao_voltar = Button(text="Voltar", size_hint=(1, 0.1),
                                   background_color=(0.6, 0, 0, 1), color=(1, 1, 1, 1))
        self.botao_voltar.bind(on_release=self.voltar_para_entrada)
        self.layout.add_widget(self.botao_voltar)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def desenhar_pista(self, x_inicial, y_pista, altura_pista,
                       comprimento_total, tolerancia_m, bandeirada,
                       valor_fracao, num_fracoes):
        # Limpa canvas antes de desenhar
        self.canvas_area.canvas.clear()

        largura_px = Window.width - 2 * x_inicial
        escala = largura_px / comprimento_total if comprimento_total else 1

        with self.canvas_area.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=(x_inicial, y_pista - altura_pista / 2), size=(largura_px, altura_pista))

            faixa_offset = altura_pista / 3
            Color(1, 1, 0, 1)
            Line(points=[x_inicial, y_pista - faixa_offset, x_inicial + largura_px, y_pista - faixa_offset], width=2)
            Line(points=[x_inicial, y_pista + faixa_offset, x_inicial + largura_px, y_pista + faixa_offset], width=2)

            Color(0, 0, 0, 1)
            Line(points=[x_inicial, y_pista, x_inicial + largura_px, y_pista], width=3)

            # Cota comprimento total
            Color(1, 0, 0, 1)
            seta_offset = 20
            y_cota = y_pista + altura_pista / 2 + seta_offset
            x_final = x_inicial + largura_px
            Line(points=[x_inicial, y_cota, x_final, y_cota], width=1.5)
            Line(points=[x_inicial, y_cota - 5, x_inicial, y_cota + 5], width=1.5)
            Line(points=[x_final, y_cota - 5, x_final, y_cota + 5], width=1.5)

            label_ct = CoreLabel(text=f"{comprimento_total:.2f} m", font_size=14, color=(1, 0, 0, 1))
            label_ct.refresh()
            texture = label_ct.texture
            Rectangle(texture=texture, pos=((x_inicial + x_final) / 2 - texture.size[0] / 2, y_cota + 5), size=texture.size)

            # Cota tolerância
            y_tol = y_pista - altura_pista / 2 - seta_offset
            x_centro = (x_inicial + x_final) / 2
            x_tol_ini = x_centro - tolerancia_m * escala
            x_tol_fim = x_centro + tolerancia_m * escala
            Line(points=[x_tol_ini, y_tol, x_tol_fim, y_tol], width=1.5)
            Line(points=[x_tol_ini, y_tol - 5, x_tol_ini, y_tol + 5], width=1.5)
            Line(points=[x_tol_fim, y_tol - 5, x_tol_fim, y_tol + 5], width=1.5)

            label_tol = CoreLabel(text=f"± {tolerancia_m:.2f} m", font_size=14, color=(1, 0, 0, 1))
            label_tol.refresh()
            Rectangle(texture=label_tol.texture, pos=(x_centro - label_tol.texture.size[0]/2, y_tol - 20), size=label_tol.texture.size)

            # Fórmulas
            texto1 = f"Comp. da pista = {num_fracoes} × {comprimento_total/num_fracoes:.2f}"
            texto2 = f"Tarifa estimada = {bandeirada:.2f} + {num_fracoes} × {valor_fracao:.2f}"

            y_formula_2 = y_pista + altura_pista / 2 + 50
            y_formula_1 = y_formula_2 + 40

            label_formula1 = CoreLabel(text=texto1, font_size=14)
            label_formula1.refresh()
            Rectangle(texture=label_formula1.texture, pos=((x_inicial + x_final)/2 - label_formula1.texture.size[0]/2, y_formula_1), size=label_formula1.texture.size)

            label_formula2 = CoreLabel(text=texto2, font_size=14)
            label_formula2.refresh()
            Rectangle(texture=label_formula2.texture, pos=((x_inicial + x_final)/2 - label_formula2.texture.size[0]/2, y_formula_2), size=label_formula2.texture.size)

    def atualizar_desenho(self, num_fracoes, comprimento_total, comprimento_fracao, tolerancia_m, bandeirada=None, valor_fracao=None):
        margem = 40
        y_pista = Window.height / 2
        altura_pista = 60
        x_inicial = margem
        self.desenhar_pista(x_inicial, y_pista, altura_pista,
                            comprimento_total, tolerancia_m, bandeirada,
                            valor_fracao, num_fracoes)

    def voltar_para_entrada(self, instance):
        self.manager.current = 'entrada'


class TelaVisualPista1(TelaVisualPistaBase):
    """Tela de visualização específica para a Bandeira 1."""
    pass

class TelaVisualPista2(TelaVisualPistaBase):
    """Tela de visualização específica para a Bandeira 2."""
    pass

class MeuApp(App):
    """
    Classe principal do aplicativo Kivy.
    Gerencia as diferentes telas do aplicativo.
    """
    def build(self):
        sm = ScreenManager() # Gerenciador de telas
        sm.add_widget(TelaInicial(name='inicial')) # Adiciona a tela inicial
        self.entrada = TelaEntradaDados(name='entrada') # Instancia a tela de entrada de dados
        self.visual_pista1 = TelaVisualPista1(name='visual1') # Instancia a tela de visualização da pista 1
        self.visual_pista2 = TelaVisualPista2(name='visual2') # Instancia a tela de visualização da pista 2
        sm.add_widget(self.entrada)
        sm.add_widget(self.visual_pista1)
        sm.add_widget(self.visual_pista2)
        return sm

if __name__ == '__main__':
    MeuApp().run() # Inicia o aplicativo Kivy