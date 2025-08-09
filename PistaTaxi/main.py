# -*- coding: utf-8 -*-
import sys
import os
import requests # Importando a biblioteca requests
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
from kivy.clock import Clock
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import black, red, yellow, grey, blue
from plyer import filechooser
from kivy.uix.popup import Popup
from functools import partial

# Define fundo branco antes de qualquer coisa para evitar tela preta inicial
Window.clearcolor = (1, 1, 1, 1)

def resource_path(filename):
    """
    Retorna o caminho correto do arquivo para rodar dentro do exe ou no desenvolvimento.
    Usa o diretório do script para garantir que o caminho seja sempre o correto.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

# A linha Window.size foi removida para permitir que a janela abra maximizada.
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

class TelaSplash(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Fundo branco
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        img = Image(source=resource_path('splash.png'), allow_stretch=True, keep_ratio=True,
                    size_hint=(0.3, 0.3), 
                    pos_hint={'center_x': 0.5, 'center_y': 0.5})
        layout.add_widget(img)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


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
        self.endereco = "" # Armazena o endereço para o PDF

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
        
        # Novo campo de texto para o endereço
        self.entrada_endereco = TextInput(hint_text='Endereço (opcional)', multiline=False, size_hint=(1, 0.08))
        self.layout.add_widget(self.entrada_endereco)

        # Botão Localizador de CEP
        self.botao_cep = Button(text="Localizar CEP", size_hint=(1, 0.08), background_color=(0.1, 0.5, 0.8, 1), color=(1,1,1,1))
        self.botao_cep.bind(on_release=self.show_cep_popup)
        self.layout.add_widget(self.botao_cep)

        self.botao_calcular = Button(text="Calcular", size_hint=(1, 0.08), background_color=(0, 0.6, 0.3, 1), color=(1,1,1,1))
        self.botao_calcular.bind(on_release=self.calcular_tolerancia)
        self.layout.add_widget(self.botao_calcular)
        
        # Layout para os resultados lado a lado
        self.resultados_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.2))
        
        # Labels para os títulos das colunas de resultado
        self.resultados_layout.add_widget(Label(text="[b]Resultados Bandeira 1[/b]", markup=True, color=(0,0,0,1)))
        self.resultados_layout.add_widget(Label(text="[b]Resultados Bandeira 2[/b]", markup=True, color=(0,0,0,1)))
        
        # Labels separadas para os resultados
        self.resultado_label1 = Label(text="", halign="center", valign="middle", markup=True, color=(0,0,0,1))
        self.resultado_label2 = Label(text="", halign="center", valign="middle", markup=True, color=(0,0,0,1))
        
        self.resultados_layout.add_widget(self.resultado_label1)
        self.resultados_layout.add_widget(self.resultado_label2)
        self.layout.add_widget(self.resultados_layout)
        
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

    def show_cep_popup(self, *args):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.cep_input = TextInput(hint_text='Digite o CEP (apenas números)', multiline=False, input_filter='int')
        content.add_widget(self.cep_input)
        
        ok_button = Button(text='Buscar Endereço', size_hint=(1, 0.2))
        content.add_widget(ok_button)
        
        popup = Popup(title='Localizar CEP', content=content, size_hint=(0.7, 0.4))
        ok_button.bind(on_release=partial(self.buscar_endereco, popup))
        
        popup.open()

    def buscar_endereco(self, popup, *args):
        cep = self.cep_input.text
        if len(cep) == 8:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()
                if 'erro' not in data:
                    self.endereco = f"{data['logradouro']}, {data['bairro']}, {data['localidade']} - {data['uf']}"
                    self.entrada_endereco.text = self.endereco
                    self.resultado_label1.text = f"[color=008000]CEP encontrado com sucesso![/color]"
                    self.resultado_label2.text = f"[color=008000]CEP encontrado com sucesso![/color]"
                else:
                    self.endereco = ""
                    self.entrada_endereco.text = ""
                    self.resultado_label1.text = "[color=ff0000]CEP não encontrado.[/color]"
                    self.resultado_label2.text = "[color=ff0000]CEP não encontrado.[/color]"
            except Exception as e:
                self.endereco = ""
                self.entrada_endereco.text = ""
                self.resultado_label1.text = f"[color=ff0000]Erro na busca do CEP: {e}[/color]"
                self.resultado_label2.text = f"[color=ff0000]Erro na busca do CEP: {e}[/color]"
        else:
            self.resultado_label1.text = "[color=ff0000]CEP inválido.[/color]"
            self.resultado_label2.text = "[color=ff0000]CEP inválido.[/color]"
            self.endereco = ""
            self.entrada_endereco.text = ""
        
        popup.dismiss()

    def calcular_tolerancia(self, *args):
        # ... (código existente) ...
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
            
            # Atualiza a variável de endereço caso o usuário a tenha digitado manualmente
            self.endereco = self.entrada_endereco.text if self.entrada_endereco.text else ""

            self.resultado_label1.text = (
                f"Comp. da pista: {self.comprimento_pista1:.2f} m\n"
                f"Tarifa estimada: R$ {self.tarifa_estimativa1:.2f}\n"
                f"Tolerância permitida: ± {self.tolerancia_metros1:.2f} m"
            )
            self.resultado_label2.text = (
                f"Comp. da pista: {self.comprimento_pista2:.2f} m\n"
                f"Tarifa estimada: R$ {self.tarifa_estimativa2:.2f}\n"
                f"Tolerância permitida: ± {self.tolerancia_metros2:.2f} m"
            )

            self.botao_visualizar1.disabled = False
            self.botao_visualizar2.disabled = False
            self.botao_gerar_pdf.disabled = False
        except Exception as e:
            self.resultado_label1.text = f"[color=ff0000]Erro nos dados.[/color]"
            self.resultado_label2.text = f"[color=ff0000]Erro nos dados.[/color]"
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
            # Garante que o endereço digitado manualmente seja salvo
            self.endereco = self.entrada_endereco.text if self.entrada_endereco.text else ""
            
            file_path = filechooser.save_file(
                title='Salvar Relatório PDF',
                filters=[('PDF Documents', '*.pdf')],
            )

            if file_path:
                if isinstance(file_path, (list, tuple)):
                    file_path = file_path[0]
                self.gerar_pdf(file_path)
                self.resultado_label1.text = f"[color=008000]Relatório salvo em:[/color]\n[size=12]{file_path}[/size]"
                self.resultado_label2.text = f"[color=008000]Relatório salvo em:[/color]\n[size=12]{file_path}[/size]"
            else:
                self.resultado_label1.text = "[color=ff8c00]Geração de PDF cancelada.[/color]"
                self.resultado_label2.text = "[color=ff8c00]Geração de PDF cancelada.[/color]"

        except Exception as e:
            self.resultado_label1.text = f"[color=ff0000]Erro ao salvar o PDF: {e}[/color]"
            self.resultado_label2.text = f"[color=ff0000]Erro ao salvar o PDF: {e}[/color]"

    def gerar_pdf(self, caminho_pdf):
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        largura, altura = A4
        margem_esq = 2 * cm
        comprimento_px = 12 * cm
        altura_pista = 20
        line_thickness = 1.5
        margem_coluna = 10 * cm

        def desenhar_elementos_fixos(canvas_obj):
            logo_path = resource_path('ibametro.png')
            if not os.path.exists(logo_path):
                print(f"Erro: O arquivo de imagem '{logo_path}' não foi encontrado.")
                self.mostrar_erro_imagem(f"Erro: Imagem 'ibametro.png' não encontrada.")
                return False

            try:
                canvas_obj.setFillAlpha(0.08)  # Opacidade muito baixa
                largura_watermark = 16 * cm
                altura_watermark = 8.5 * cm 
                pos_x = (largura - largura_watermark) / 2
                pos_y = (altura - altura_watermark) / 2
                canvas_obj.drawImage(logo_path, pos_x, pos_y, width=largura_watermark, height=altura_watermark, mask='auto')
                canvas_obj.setFillAlpha(1)  # Restaura a opacidade
            except Exception as e:
                print(f"Erro ao desenhar marca d'água: {e}")
                self.mostrar_erro_imagem(f"Erro ao desenhar marca d'água: {e}")
                return False

            try:
                canvas_obj.setFillAlpha(1) # Opacidade normal
                largura_logo = 3 * cm
                altura_logo = 1.6 * cm
                pos_x_logo = largura - largura_logo - cm
                pos_y_logo = altura - altura_logo - cm
                canvas_obj.drawImage(logo_path, pos_x_logo, pos_y_logo, width=largura_logo, height=altura_logo, mask='auto')
            except Exception as e:
                print(f"Erro ao desenhar logo: {e}")
                self.mostrar_erro_imagem(f"Erro ao desenhar logo: {e}")
                return False
            
            return True

        if not desenhar_elementos_fixos(c):
            return 

        def desenhar_pista(y_top, titulo, bandeirada, valor_fracao, comprimento_pista,
                           comprimento_fracao, num_fracoes, tarifa_estimativa, tolerancia):
            # Título da Bandeira
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margem_esq, y_top, titulo)
            
            y = y_top - 1.5 * cm

            # Fórmulas
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawCentredString(margem_esq + comprimento_px / 2, y, f"Comp. da pista = {num_fracoes} × {comprimento_pista / num_fracoes:.2f}")
            c.drawCentredString(margem_esq + comprimento_px / 2, y - 0.5 * cm, f"Tarifa estimada = {bandeirada:.2f} + {num_fracoes} × {valor_fracao:.2f}")
            
            y_cota = y - 1.5 * cm
            x_ini = margem_esq
            
            # Cota de Comprimento Total (ACIMA das fórmulas)
            c.setStrokeColor(red)
            c.setLineWidth(line_thickness)
            c.line(x_ini, y_cota, x_ini + comprimento_px, y_cota)
            c.line(x_ini, y_cota - 0.15 * cm, x_ini, y_cota + 0.15 * cm)
            c.line(x_ini + comprimento_px, y_cota - 0.15 * cm, x_ini + comprimento_px, y_cota + 0.15 * cm)
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawCentredString(x_ini + comprimento_px / 2, y_cota + 0.2 * cm, f"{comprimento_pista:.2f} m")
            
            y_pista = y_cota - 2 * cm

            # Desenho da Pista
            c.setFillColor(grey)
            c.rect(x_ini, y_pista, comprimento_px, altura_pista, fill=1)
            c.setStrokeColor(yellow)
            c.setLineWidth(line_thickness)
            c.line(x_ini, y_pista + 5, x_ini + comprimento_px, y_pista + 5)
            c.line(x_ini, y_pista + 15, x_ini + comprimento_px, y_pista + 15)
            c.setStrokeColor(black)
            c.setLineWidth(line_thickness)
            c.line(x_ini, y_pista + 10, x_ini + comprimento_px, y_pista + 10)

            # Cota de Tolerância (POSICIONADA NAS EXTREMIDADES DIREITAS DA PISTA)
            tol_px = (tolerancia / comprimento_pista) * comprimento_px if comprimento_pista else 0
            x_final = x_ini + comprimento_px
            x_tol_neg = x_final - tol_px
            x_tol_pos = x_final + tol_px
            y_tol_linha = y_pista + 10
            
            c.setStrokeColor(blue)
            c.setLineWidth(line_thickness)
            c.line(x_tol_neg, y_tol_linha, x_tol_pos, y_tol_linha)
            c.line(x_tol_neg, y_tol_linha - 5, x_tol_neg, y_tol_linha + 5)
            c.line(x_tol_pos, y_tol_linha - 5, x_tol_pos, y_tol_linha + 5)
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            
            y_tol_text = y_pista - 0.5 * cm
            
            text_neg = f"-{tolerancia:.1f} m"
            text_pos = f"+{tolerancia:.1f} m"
            text_width_neg = c.stringWidth(text_neg, 'Helvetica',7)
            text_width_pos = c.stringWidth(text_pos, 'Helvetica',7)
            
            c.drawString(x_tol_neg - text_width_neg, y_tol_text, text_neg)
            c.drawString(x_tol_pos, y_tol_text, text_pos)
            
        # Cabeçalho do PDF
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(largura / 2, altura - 3 * cm, "Relatório de Demarcação da Pista")
        c.setFont("Helvetica", 12)
        c.drawCentredString(largura / 2, altura - 4 * cm, "Verificação de Taxímetro - Bandeiras 1 e 2")
        
        # Desenha a pista da Bandeira 1
        desenhar_pista(altura - 5 * cm, "Bandeira 1", self.bandeirada1, self.valor_fracao1,
                        self.comprimento_pista1, self.comprimento_fracao1, self.num_fracoes1,
                        self.tarifa_estimativa1, self.tolerancia_metros1)

        # Desenha a pista da Bandeira 2
        y_pos_bandeira2 = altura - 15 * cm
        desenhar_pista(y_pos_bandeira2, "Bandeira 2", self.bandeirada2, self.valor_fracao2,
                        self.comprimento_pista2, self.comprimento_fracao2, self.num_fracoes2,
                        self.tarifa_estimativa2, self.tolerancia_metros2)
        
        # Seção de Dados de Entrada e Resultados em Colunas
        y_dados = altura - 23 * cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margem_esq, y_dados, "Dados de Entrada e Resultados Detalhados:")
        y_dados -= 0.8 * cm

        # Cabeçalhos das colunas
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margem_esq, y_dados, "Bandeira 1")
        c.drawString(margem_esq + margem_coluna, y_dados, "Bandeira 2")
        y_dados -= 0.5 * cm

        # Dados em colunas
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq, y_dados, f"Bandeirada: R$ {self.bandeirada1:.2f}")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Bandeirada: R$ {self.bandeirada2:.2f}")
        y_dados -= 0.5 * cm
        
        c.drawString(margem_esq, y_dados, f"Valor por fração: R$ {self.valor_fracao1:.2f}")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Valor por fração: R$ {self.valor_fracao2:.2f}")
        y_dados -= 0.5 * cm
        
        c.drawString(margem_esq, y_dados, f"Número de frações: {self.num_fracoes1}")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Número de frações: {self.num_fracoes2}")
        y_dados -= 0.5 * cm
        
        c.drawString(margem_esq, y_dados, f"Comprimento da fração: {self.comprimento_fracao1:.2f} m")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Comprimento da fração: {self.comprimento_fracao2:.2f} m")
        y_dados -= 0.5 * cm
        
        c.drawString(margem_esq, y_dados, f"Comprimento total da pista: {self.comprimento_pista1:.2f} m")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Comprimento total da pista: {self.comprimento_pista2:.2f} m")
        y_dados -= 0.5 * cm
        
        c.drawString(margem_esq, y_dados, f"Tarifa estimada: R$ {self.tarifa_estimativa1:.2f}")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Tarifa estimada: R$ {self.tarifa_estimativa2:.2f}")
        y_dados -= 0.5 * cm
        
        c.drawString(margem_esq, y_dados, f"Tolerância permitida: ± {self.tolerancia_metros1:.2f} m")
        c.drawString(margem_esq + margem_coluna, y_dados, f"Tolerância permitida: ± {self.tolerancia_metros2:.2f} m")
        
        # Adiciona o endereço no rodapé do PDF
        if self.endereco:
            c.setFont("Helvetica", 10)
            c.drawCentredString(largura / 2, cm, f"Endereço: {self.endereco}")

        c.save()
    
    def mostrar_erro_imagem(self, mensagem):
        self.resultado_label1.text = f"[color=ff0000]{mensagem}[/color]"
        self.resultado_label2.text = f"[color=ff0000]{mensagem}[/color]"
        self.botao_gerar_pdf.disabled = True


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
        largura_desenhada = largura_px * 0.9
        escala = largura_desenhada / comprimento_total if comprimento_total else 1
        line_thickness = 1.5
        
        with self.canvas_area.canvas:
            # Título da Pista
            label_titulo = CoreLabel(text=f"{self.name.capitalize().replace('visual', 'Pista ')}", font_size=18, bold=True, color=(0,0,0,1))
            label_titulo.refresh()
            Rectangle(texture=label_titulo.texture, pos=((Window.width - label_titulo.texture.size[0]) / 2, y_pista + 150), size=label_titulo.texture.size)
            
            # Fórmulas
            texto1 = f"Comp. da pista = {num_fracoes} × {comprimento_total/num_fracoes:.2f}"
            texto2 = f"Tarifa estimada = {bandeirada:.2f} + {num_fracoes} × {valor_fracao:.2f}"

            label_formula1 = CoreLabel(text=texto1, font_size=14)
            label_formula1.refresh()
            Rectangle(texture=label_formula1.texture, pos=((x_inicial + largura_px)/2 - label_formula1.texture.size[0]/2, y_pista + 100), size=label_formula1.texture.size)

            label_formula2 = CoreLabel(text=texto2, font_size=14)
            label_formula2.refresh()
            Rectangle(texture=label_formula2.texture, pos=((x_inicial + largura_px)/2 - label_formula2.texture.size[0]/2, y_pista + 70), size=label_formula2.texture.size)

            # Cota comprimento total (ACIMA das fórmulas)
            Color(1, 0, 0, 1) # Red
            y_cota = y_pista + 50
            x_final_desenhado = x_inicial + largura_desenhada
            Line(points=[x_inicial, y_cota, x_final_desenhado, y_cota], width=line_thickness)
            Line(points=[x_inicial, y_cota - 5, x_inicial, y_cota + 5], width=line_thickness)
            Line(points=[x_final_desenhado, y_cota - 5, x_final_desenhado, y_cota + 5], width=line_thickness)

            label_ct = CoreLabel(text=f"{comprimento_total:.2f} m", font_size=14, color=(1, 0, 0, 1))
            label_ct.refresh()
            Rectangle(texture=label_ct.texture, pos=((x_inicial + x_final_desenhado) / 2 - label_ct.texture.size[0] / 2, y_cota + 5), size=label_ct.texture.size)

            # Pista
            Color(0.8, 0.8, 0.8, 1) # Grey
            y_pista_desenhada = y_cota - 50
            Rectangle(pos=(x_inicial, y_pista_desenhada - altura_pista / 2), size=(largura_desenhada, altura_pista))

            faixa_offset = altura_pista / 3
            Color(1, 1, 0, 1) # Yellow
            Line(points=[x_inicial, y_pista_desenhada - faixa_offset, x_final_desenhado, y_pista_desenhada - faixa_offset], width=line_thickness)
            Line(points=[x_inicial, y_pista_desenhada + faixa_offset, x_final_desenhado, y_pista_desenhada + faixa_offset], width=line_thickness)

            Color(0, 0, 0, 1) # Black
            Line(points=[x_inicial, y_pista_desenhada, x_final_desenhado, y_pista_desenhada], width=line_thickness)
            
            # Cota tolerância (POSICIONADA NAS EXTREMIDADES DIREITAS DA PISTA)
            tol_px = tolerancia_m * escala
            x_final = x_inicial + largura_desenhada
            x_tol_neg = x_final - tol_px
            x_tol_pos = x_final + tol_px
            y_tol_linha = y_pista_desenhada + 10  # Na altura da linha central da pista
            
            Color(0, 0, 1, 1) # Blue
            Line(points=[x_tol_neg, y_tol_linha, x_tol_pos, y_tol_linha], width=line_thickness)
            Line(points=[x_tol_neg, y_tol_linha - 5, x_tol_neg, y_tol_linha + 5], width=line_thickness)
            Line(points=[x_tol_pos, y_tol_linha - 5, x_tol_pos, y_tol_linha + 5], width=line_thickness)
            
            # Desenha textos de tolerância
            y_tol_text = y_pista_desenhada - 40 # Nova posição para os textos
            label_tol_neg = CoreLabel(text=f"-{tolerancia_m:.2f}", font_size=14, color=(0,0,1,1))
            label_tol_neg.refresh()
            Rectangle(texture=label_tol_neg.texture, pos=(x_tol_neg - label_tol_neg.texture.size[0]/2, y_tol_text), size=label_tol_neg.texture.size)
            
            label_tol_pos = CoreLabel(text=f"+{tolerancia_m:.2f}", font_size=14, color=(0,0,1,1))
            label_tol_pos.refresh()
            Rectangle(texture=label_tol_pos.texture, pos=(x_tol_pos - label_tol_pos.texture.size[0]/2, y_tol_text), size=label_tol_pos.texture.size)

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
        sm = ScreenManager()
        sm.add_widget(TelaSplash(name='splash'))
        sm.add_widget(TelaInicial(name='inicial'))
        self.entrada = TelaEntradaDados(name='entrada')
        self.visual_pista1 = TelaVisualPista1(name='visual1')
        self.visual_pista2 = TelaVisualPista2(name='visual2')
        sm.add_widget(self.entrada)
        sm.add_widget(self.visual_pista1)
        sm.add_widget(self.visual_pista2)

        sm.current = 'splash'
        Clock.schedule_once(lambda dt: self.mudar_tela(sm), 7)

        return sm
    
    def on_start(self):
        # Maximiza a janela na inicialização, após o build ter sido concluído
        Window.maximize()

    def mudar_tela(self, sm):
        sm.current = 'inicial'

if __name__ == '__main__':
    MeuApp().run()