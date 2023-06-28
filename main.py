from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from scan import scaner
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
import mysql.connector


class LoginScreen(Screen):
	pass
class ScanScreen(Screen):
	pass
class PesagemScreen(Screen):
	pass
class Ensaio(MDCard):
	pass
class WindowManager(ScreenManager):
	pass

sm = ScreenManager()
sm.add_widget(LoginScreen(name = 'loginscreen'))
sm.add_widget(ScanScreen(name = 'scanscreen'))
sm.add_widget(PesagemScreen(name = 'pesagemscreen'))

class Ensaio(MDCard):
    codEnsaio = StringProperty('...')
    nomeEnsaio = StringProperty('...')
    idEnsaio = StringProperty('...')

class MainApp(MDApp):

	db = mysql.connector.connect(host='localhost', user='root', password='teste', database='lanali')
	cursor = db.cursor() 

	def build(self):
		self.theme_cls.theme_style = "Light"
		self.strng = Builder.load_file('login.kv')
		return self.strng
	
	def mudaTema(self):
		if self.theme_cls.theme_style == "Dark":
			self.theme_cls.theme_style = "Light"
			self.strng.get_screen('scanscreen').ids.mudatema.text = 'Tema Escuro'
			self.strng.get_screen('pesagemscreen').ids.mudatema.text = 'Tema Escuro'
		else:
			self.theme_cls.theme_style = "Dark"	
			self.strng.get_screen('scanscreen').ids.mudatema.text = 'Tema Claro'
			self.strng.get_screen('pesagemscreen').ids.mudatema.text = 'Tema Claro'

	def confirma(self, pesagem, codEnsaio):
		self.codEnsaio = codEnsaio
		self.pesagem = pesagem
		self.dialog = MDDialog(
			title = "Confirmar Pesagem",
			text = "Deseja confirmar a pesagem?",
			buttons = [
				MDRectangleFlatButton(
					text = "SALVAR", text_color = self.theme_cls.primary_color, on_release = self.grava
				),
				MDFlatButton(
					text = "CANCELAR", text_color = self.theme_cls.primary_color, on_release = self.fechaMensagem
					),
			]
		)
		self.dialog.open()

	def fechaMensagem(self, obj):
		self.dialog.dismiss()	

	def grava(self, obj):
		self.cursor.execute('''INSERT INTO mvt_rastreabilidade_ensaio 
								(idMvtRastreabilidadeEnsaio, idRQ, idFuncionario, dataHora, status, 
								codEnsaio, idItemEnsaio, valorDinamico) 
								VALUES(0, 84, 1, "", "Pesagem feita", "{}", {}, "Pesagem: {}")
								'''.format(self.codEnsaio, self.idEnsaio, self.pesagem))
		self.dialog.dismiss()

	def login(self, usuario, senha):
		self.cursor.execute('''SELECT login, senha, nome 
							FROM adm_funcionario_credencial
							INNER JOIN cad_funcionario using(idfuncionario)''')
		usuario_list = []
		for i in self.cursor.fetchall():
			usuario_list.append(i[0])
		if usuario in usuario_list and usuario != "":
			self.cursor.execute(f"SELECT senha from adm_funcionario_credencial WHERE login = '{usuario}'")
			for j in self.cursor:
				if senha == j[0]:
					self.strng.get_screen('scanscreen').manager.transition = NoTransition()
					self.strng.get_screen('scanscreen').manager.current = 'scanscreen'
					self.strng.get_screen('scanscreen').ids.usuarioMenuScan.text = usuario
					self.strng.get_screen('pesagemscreen').ids.usuarioMenuPesagem.text = usuario
				else:
					self.dialog = MDDialog(title = "Senha Incorreta", text = "Insira uma senha válida para esse usuário")
					self.dialog.open()
		else:
			self.dialog = MDDialog(title = "Usuário Incorreto", text = "Insira um usuário válido")
			self.dialog.open()

	def sair(self):	
		self.strng.get_screen('loginscreen').manager.transition = NoTransition()
		self.strng.get_screen('loginscreen').manager.current = 'loginscreen'
		self.strng.get_screen('loginscreen').ids.usuario.text = ''
		self.strng.get_screen('loginscreen').ids.senha.text = ''

	def scan(self):
		self.strng.get_screen('pesagemscreen').manager.transition = NoTransition()
		self.strng.get_screen('pesagemscreen').manager.current = 'pesagemscreen'
		resultado = scaner()
		for reg in resultado:
			self.idEnsaio = reg['idItemEnsaio']
			self.strng.get_screen('pesagemscreen').ids.pesagemTopBar.title = 'Solicitação: {}'.format(str(self.idEnsaio))
			self.strng.get_screen('pesagemscreen').ids.listaEnsaio.add_widget(				
				MDAnchorLayout(	
					Ensaio(
			        line_color=(0.2, 0.2, 0.2, 0.8),
			        nomeEnsaio= reg['descricao'],
			        codEnsaio = reg['codEnsaio'],
					idEnsaio = str(reg['idItemEnsaio']),
		    		size = (dp(400), dp(150)),
					size_hint = (.9, None),
					),
					size = (dp(500), dp(160)),
	                anchor_x = "center",
                	anchor_y =  "top",
					size_hint = (.1, None),
				),				
			)
    	
MainApp().run()       
