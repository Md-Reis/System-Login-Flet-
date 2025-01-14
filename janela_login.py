import sqlite3
import flet as ft
import win32com.client as win32
import re

from flet import *
from time import sleep

global local, bd

local = './data_base/' #Pasta do Banco de Dados
bd = 'BD.db' #Nome do Banco de Dados
audio_on = True

class DataBase(): #Acessa o Banco de Dados SQlite3
    def __init__(self):
        super().__init__()
    def conecta(self):
        try:
            name = f"{local}{bd}"
            self.connection = sqlite3.connect(name)
        except:
            conn = sqlite3.connect('BD.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    senha TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
    def desconecta(self):
        try:
            self.connection.close()
        except:
            pass
        
class Back_End(DataBase):
    #Back do sistema e com todo o codigo fonte de validação de login, registro de novo usuario e recuperação de senha
    def __init__(self, func, tela, id, name, senha, loading, t1, t2, t3):
        super().__init__()
        self.func = func
        self.tela = tela
        self.id_user = id
        self.name_user = name
        self.senha = senha
        self.loading = loading
        self.info = t1
        self.alerta = t2
        self.info2 = t3
        
        if self.func == 'valida':
            self.valida_usuario()
        elif self.func == 'new':
            self.cadastra_usuario()
        else:
            self.email_recuperação()
    def sounds(audio, page): #Função para reproduzir audio
        if audio_on == True:
            def play_sound():
                play = ft.Audio(src=audio, autoplay=True)
                page.overlay.append(play)
                page.update()
            return play_sound()
        else:
            page.overlay.clear()
            page.update()
    def valida_usuario(self): #Validação de usuario através do Bando de Dados do SQlite3
        if audio_on:
            Back_End.sounds("./sounds/cg.mp3", self.tela)
        if self.id_user.value == '':
            self.alerta.visible = True
            self.alerta.value = 'Insira o ID do usuario'
            self.tela.update()
            sleep(3)
            self.alerta.visible = False
            self.tela.update()
        elif self.id_user.value:
            self.conecta()
            sql = 'select * from usuarios;'
            self.cursor = self.connection.cursor()
            self.cursor.execute(sql)
            self.buscaruser = self.cursor.fetchall()
            user = 0
            for i in self.buscaruser:
                if self.id_user.value == str(i[0]):
                    self.name_user.disable=False
                    self.tela.update()
                    self.name_user.value = i[1]
                    self.name_user.disable=True
                    self.tela.update()
                    user = 1
                    if self.senha.value != "":
                        if self.senha.value == i[2]:
                            sql1 = f"""select * from usuarios where id = {i[0]} """
                            self.cursor = self.connection.cursor()
                            self.cursor.execute(sql1)
                            self.dadosvendedor = self.cursor.fetchall()
                            self.usuario_login = self.dadosvendedor[0][1]
                            self.usuario_status = self.dadosvendedor[0][3]
                            self.nome_banco_dados = self.cursor.fetchone()
                            global vend, status
                            status = self.usuario_status
                            vend = self.usuario_login
                            
                            self.info.value = f'{self.name_user.value.capitalize()}, Seja muito bem vindo!'
                            self.info.visible = True
                            self.loading.visible = True                            
                            self.tela.controls.clear()
                            
                            body_loading = ft.Container(
                                ft.Column(
                                    [ft.Image('./assets/load.gif'),
                                    ft.Row([self.loading],ft.MainAxisAlignment.CENTER)]),
                                padding=ft.Padding(top=100, right=0, left=0, bottom=0),
                                visible=True,
                                width=400,
                                height=470,
                                border_radius=40,
                                bgcolor = 'black',
                                opacity=0.9
                            )

                            body_log = ft.Container(
                                ft.Stack([
                                    ft.Image('./assets/bg.gif', fit=ft.ImageFit.COVER, left= -60, top= 130),
                                    ft.Container(
                                        ft.Column([
                                                ft.Row([self.loading],ft.MainAxisAlignment.CENTER),
                                                ft.Row([self.info],ft.MainAxisAlignment.CENTER),
                                                ]),
                                            width=400,
                                            height=470,
                                            top=0,
                                            left=0,
                                            bgcolor = ft.Colors.TRANSPARENT,
                                            border_radius=30,
                                            opacity=0.9),
                                        ]),visible=True,
                                            width=400,
                                            height=470,
                                            border_radius=30,
                                            border=ft.Border(
                                                top=ft.BorderSide(width=2, color=ft.Colors.WHITE30),
                                                right=ft.BorderSide(width=2, color=ft.Colors.WHITE30)
                                    ),
                                            bgcolor = 'black',
                                            opacity=0.9
                                    )
                            self.tela.add(body_loading)
                            self.tela.update()
                            sleep(3)
                            self.tela.controls.clear()
                            self.tela.add(body_log)
                            self.tela.update()
                            sleep(5)
                            self.tela.window.close()
                        else:
                            self.alerta.visible = True
                            self.alerta.value = 'Por favor verifique o ID e senha digitados'
                            self.tela.update()
                            sleep(2)
                            self.alerta.visible = False
                            self.tela.update()
            if user == 0:
                self.alerta.visible = True
                self.alerta.value = 'Usuário nao encontrado!'
                self.tela.update()
                sleep(3)
                self.alerta.visible = False
                self.tela.update()
            self.desconecta()
    def cadastra_usuario(self): #Função para Cadastrar novos usuarios
        self.conecta()
        sql = f'insert INTO usuarios (nome, senha, email, telefone) VALUES("{self.name_user.value}", "{self.senha.value}", "{self.alerta.value.lower()}" ,"{self.info.value}");'
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()
        self.desconecta()
        
        self.tela.controls.clear()
        self.loading.visible = True
        self.info2.value = f'Usuário {self.name_user.value.capitalize()}'
        self.info2.visible = True
        self.info3 = ft.Text(value='Cadastrado com Sucesso!',size=18,color= '#17ffee',height= 50)
        self.tela.update()
        body_cadastrado = ft.Container(
                ft.Stack([
                    ft.Container(
                        ft.Column([
                            ft.Row([self.loading], ft.MainAxisAlignment.CENTER),
                            ft.Row([self.info2],ft.MainAxisAlignment.CENTER),
                            ft.Row([self.info3],ft.MainAxisAlignment.CENTER),
                            ]),
                            width=400,
                            height=470,
                            top=40,
                            left=0,
                            bgcolor = ft.Colors.TRANSPARENT,
                            border_radius=30,
                            opacity=0.9),
                    ]),visible=True,
                        width=400,
                        height=470,
                        border_radius=30,
                        border=ft.Border(
                            top=ft.BorderSide(width=2, color=ft.Colors.WHITE30),
                            right=ft.BorderSide(width=2, color=ft.Colors.WHITE30)
                                    ),
                        bgcolor = 'black',
                        opacity=0.9
        )
        self.tela.add(body_cadastrado)
        self.tela.update()
        sleep(5)
        self.tela.window.close()
    def email_recuperação(self): #Função de recuperação de email (Padrão Outlook)
        email_recover = self.info.value.lower()
        
        self.conecta()
        sql =f"select id, nome, senha FROM usuarios where email = '{email_recover}';"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()
        self.senha = cursor.fetchall()
        self.desconecta()
        
        if  len(self.senha) == 0:
            self.alerta.visible = True
            self.info.value = ""
            self.tela.update()
            sleep(2)
            self.alerta.visible = False
            self.tela.update()
        else:    
            outlook = win32.Dispatch("Outlook.Application")
            message = outlook.CreateItem(0)
            message.Display()
            message.Subject = "E-mail de Recuperação de Senha"
            message.To = email_recover
            texto = f"Olá,<br>Conforme solicitado, segue a recuperação dos seus dados<br><br>ID de usuário: {self.senha[0][0]}<br>Nome do usuário: {self.senha[0][1]}<br>Senha cadastrada: {self.senha[0][2]}"
            message.HtmlBody = texto
            message.Send()
            
            info = ft.Text(
                value=f'E-mail enviado para:',
                size=15,
                height=18,
                color= 'white',
                visible=True
            )
            
            info1 = ft.Text(
                value=f'{email_recover}',
                size=15,
                height=18,
                weight='bold',
                color= '#17ffee',
                visible=True
            )
            self.loading.visible = True                            
            self.tela.controls.clear()
            
            body_loading = ft.Container(
                                ft.Row([self.loading],ft.MainAxisAlignment.CENTER),
                                visible=True,
                                width=400,
                                height=470,
                                border_radius=40,
                                bgcolor = 'black',
                                opacity=0.9
                            )
            body_log = ft.Container(
                ft.Stack([
                    ft.Image('./assets/bg.gif', left= -60, top=60),
                    ft.Container(
                        ft.Column([
                                ft.Row([info],ft.MainAxisAlignment.CENTER),
                                ft.Row([info1],ft.MainAxisAlignment.CENTER),
                                ]),
                                width=400,
                                height=470,
                                top=0,
                                left=0,
                                bgcolor = ft.Colors.TRANSPARENT,
                                border_radius=30,
                                opacity=0.9),
                        ]),visible=True,
                            width=400,
                            height=470,
                            border_radius=30,
                            border=ft.Border(
                                top=ft.BorderSide(width=2, color=ft.Colors.WHITE30),
                                right=ft.BorderSide(width=2, color=ft.Colors.WHITE30)
                                    ),
                            bgcolor = 'black',
                            opacity=0.9
            )
            self.tela.add(body_loading)
            self.tela.update()
            sleep(2)
            self.tela.controls.clear()
            self.tela.add(body_log)
            self.tela.update()
            sleep(5)
            self.tela.window.close()
            
class Front_End():
    #Front do sistema e interface de login, registro e recuperação de senha
    def main(page:ft.Page):
        page.window.width = 400 #largura
        page.window.height = 470 #altura
        page.window.center()
        page.window.bgcolor = ft.Colors.TRANSPARENT
        page.window.frameless = True
        page.window.maximizable = False
        
        page.title='Login'
        page.bgcolor = ft.Colors.TRANSPARENT
        page.horizontal_alignment = 'center'
        page.vertical_alignment = 'center'
        page.padding = 0
        
        def start():
            Back_End.sounds("./sounds/gm.mp3", page)
            
        def page_init(page): #Pagina inicial da aplicação
            Back_End.sounds("./sounds/cg.mp3", page)
            
            #Chama o Back End para validar as informações de Login
            def call_back_end_init(e):
                func = 'valida'
                Back_End(func, page, id_user, name_user, password, loading, t1, t2, forget_pass)
            
            #Função para desligar e ligar o som
            def mute_soud(e):
                global audio_on
                if soundeffect.visible == True:
                    audio_on = False
                    page.overlay.clear()
                    soundeffect.visible = False
                    page.update()
                else:
                    audio_on = True
                    soundeffect.visible = True
                    page.update()
            
            icon = ft.Image(
                src=f'./assets/load_icon.gif',
                width=80,
                visible=True,
                scale=1.4
            )
            
            loading = ft.Image(
            src= f'./assets/load_icon.gif',
            width= 150,
            visible= False
            )

            t1 = ft.Text(
                value='Digite seu ID e Senha',
                size=18,
                color= '#17ffee'
            )

            t2 = ft.Text(
                value='Informações de confirmação!',
                size=15,
                bgcolor= '',
                color= '',
                visible= False
            )

            id_user = ft.TextField(
                label= 'ID',
                width= 50,
                height= 70,
                color= '#ffffff',
                border_width= 2,
                border_radius= 15,
                border_color= '#17ffee',
                on_blur=call_back_end_init, on_submit=call_back_end_init,
                focused_border_color= '#17ffee',
                visible= True
            )
            
            name_user = ft.TextField(
                label= 'Usuário',
                width= 140,
                height= 70,
                color= '#ffffff',
                border_width= 2,
                border_radius= 15,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                disabled=True,
                visible=True
            )

            password = ft.TextField(
                label= 'Password',
                width= 200,
                height= 50,
                color= '#ffffff',
                border_radius= 15,
                border_width= 2,
                password= True,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                on_submit=call_back_end_init,
                can_reveal_password=True,
                visible= True
            )
            
            #Altera a rota para o layout de recuperação de senha
            forget_pass = ft.TextButton(
                "Esqueceu a senha?",
                on_click=lambda e :page_recover(page),
                visible=True,
            )
            
            btn_confirm = ft.ElevatedButton(
                text= 'E N T E R',
                width= 200,
                height= 40,
                bgcolor= '#17ffee',
                color= '#3d423c',
                on_click= call_back_end_init,
                visible= True
            )
        
            #Altera a rota para o layout de cadastro de usuario
            t3 = ft.Row([
                    ft.Text(
                    "Ainda não tem cadastro?",
                    color= 'white'),
                            ft.TextButton(
                            "Criar Conta",
                            on_click = lambda e :page_register(page)),
            ], visible=True)
            
            #Desliga e liga os audios do sistema
            sound_bt = ft.Container(
                content=ft.Image(src='./assets/soundonoff.gif', width=75, height=75, scale=0.5),
                on_click=lambda e: mute_soud(soundeffect),
                visible=True,
            )
            
            soundeffect = ft.Container(
                content=ft.Image(src='./assets/soundeffect.gif', width=85, height=85, scale=2.2),
            ) 
            if audio_on:
                soundeffect.visible = True
            else:
                soundeffect.visible = False
            
            #Fecha a janela principal
            btn_close = ft.Container(
                content=ft.Image(src='./assets/power.gif', width=65, height=65),
                on_click=lambda e: page.window.close(),
                visible=True,
                bgcolor = ft.Colors.TRANSPARENT,
            )
            
            #Layout do sistema de login
            body_init = ft.Container(
                content=ft.Stack([
                    ft.Image('./assets/bg.gif', fit=ft.ImageFit.COVER, left= -60, top= 100),
                    ft.Container(
                        ft.Column([
                            ft.Row([t1,icon], alignment=ft.MainAxisAlignment.SPACE_EVENLY), loading,
                            ft.Row([t2, loading], ft.MainAxisAlignment.CENTER),
                            ft.Row([id_user, name_user], ft.MainAxisAlignment.CENTER),
                            ft.Row([password],ft.MainAxisAlignment.CENTER),
                            ft.Row([ft.Container(content=forget_pass, padding=ft.Padding(left=160, top=0, right=0, bottom=0))], alignment=ft.MainAxisAlignment.START),
                            ft.Row([btn_confirm],ft.MainAxisAlignment.CENTER, height=40),
                            ft.Row([t3], ft.MainAxisAlignment.CENTER),
                            ft.Row([
                                ft.Stack([
                                    ft.Container(content=soundeffect, padding=ft.Padding(left=160, top=10, right=0, bottom=0)),
                                    ft.Row([ft.Container(content=sound_bt, padding=ft.Padding(left=0, top=20, right=0, bottom=0)),
                                            ft.Container(content=btn_close, padding=ft.Padding(left=75, top=20, right=0, bottom=0))], alignment=ft.MainAxisAlignment.START, spacing=180)
                                        ])
                                    ])
                        ]),
                        width=400,
                        height=470,
                        top=0,
                        left=0,
                        bgcolor = ft.Colors.TRANSPARENT,
                        border_radius=30,
                        opacity=0.9
                    ),
                  ]),
                    visible=True,
                    width=400,
                    height=470,
                    border=ft.Border(
                        top=ft.BorderSide(width=2, color=ft.Colors.WHITE30),
                        right=ft.BorderSide(width=2, color=ft.Colors.WHITE30)
                                    ),
                    border_radius=30,
                    bgcolor = 'black',
                    opacity=0.9
            )
            page.clean()
            page.add(body_init)
        
        def page_register(page): #Pagina de cadastro de usuarios
            Back_End.sounds("./sounds/cg.mp3", page)
            #Chama o Back End para registrar novo usuaio
            def call_back_end_new(e):
                if not format_email(email.value):
                    t2.value = "Insira um e-mail valido!"
                    t2.visible = True
                    page.update()
                    sleep(2)
                    t2.visible = False
                    page.update()
                else:
                    if password.value != confirm_password.value:
                        t2.value = "As senhas estão divergentes!"
                        t2.visible = True
                        page.update()
                        sleep(2)
                        t2.visible = False
                        page.update()
                    else:
                        func = 'new'
                        Back_End(func, page, None, name_user, password, loading, telefone, email, t1)
            
            #Formatação do numero de celular
            def format_tel(e):
                numero = ''.join(filter(str.isdigit, telefone.value))
                if len(numero) >= 0:
                    numero_formatado = f"({numero[:2]}) {numero[2:7]}-{numero[7:11]}"
                else:
                    numero_formatado = numero
                telefone.value = numero_formatado
                telefone.update()
                def check_num(tel):
                    if len(tel) < 11:
                        t2.value = "Verifique o numero de Celular Digitado!"
                        t2.visible = True
                        page.update()
                        sleep(2)
                        t2.visible = False
                        page.update()
                telefone.on_blur = lambda e :check_num(telefone.value)
            #Validação de e-mail real
            def format_email(e):
                padrao_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                if re.match(padrao_email, email.value):
                    return True
                else:
                    return False
            
            loading = ft.Image(
            src= f'./assets/load_icon.gif',
            width= 100,
            visible= False
            )

            t1 = ft.Text(
                value='Cadastro de Usuários',
                size=18,
                color= '#17ffee',
                height= 50
            )

            t2 = ft.Text(
                value='Informações de confirmação!',
                size=15,
                bgcolor= '',
                color= '',
                visible= False
            )

            id_user = ft.TextField(
                label= 'ID',
                width= 50,
                height= 80,
                color= '#ffffff',
                border_width= 2,
                border_radius= 15,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                disabled=True,
                visible= True
            )
            
            name_user = ft.TextField(
                label= 'Nome',
                width= 200,
                height= 80,
                color= '#ffffff',
                border_width= 2,
                border_radius= 15,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                visible=True
            )

            password = ft.TextField(
                label= 'Senha',
                width= 150,
                height= 50,
                color= '#ffffff',
                border_radius= 15,
                border_width= 2,
                password= True,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                can_reveal_password=True,
                visible= True,
            )
            
            confirm_password = ft.TextField(
                label= 'Repetir Senha',
                width= 150,
                height= 50,
                color= '#ffffff',
                border_radius= 15,
                border_width= 2,
                password= True,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                can_reveal_password=True,
                visible= True,
            )
            
            email = ft.TextField(
                label= 'E-mail',
                width= 150,
                height= 50,
                color= '#ffffff',
                border_radius= 15,
                border_width= 2,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                visible= True,
            )
            
            telefone = ft.TextField(
                label= 'Telefone',
                width= 150,
                height= 50,
                color= '#ffffff',
                border_radius= 15,
                border_width= 2,
                border_color= '#17ffee',
                focused_border_color= '#17ffee',
                visible= True,
                on_change = format_tel
            )
            
            btn_confirm = ft.ElevatedButton(
                text= 'C A D A S T R A R',
                width= 200,
                height= 40,
                on_click=call_back_end_new,
                bgcolor= '#17ffee',
                color= '#3d423c',
                
                visible= True
            )
        
            back = ft.ElevatedButton(
                text= '<',
                width= 40,
                height= 40,
                bgcolor= '#17ffee',
                color= '#3d423c',
                on_click= lambda e :page_init(page),
                visible= True
            )
            
            body_new_user = ft.Container(
                ft.Stack([
                    ft.Image('./assets/bg.gif', left= -60, top= 100),
                    ft.Container(
                        ft.Column([
                            ft.Row([t1], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([t2, loading], ft.MainAxisAlignment.CENTER),
                            ft.Row([id_user, name_user], ft.MainAxisAlignment.CENTER),
                            ft.Row([password, confirm_password],ft.MainAxisAlignment.CENTER),
                            ft.Row([email, telefone],ft.MainAxisAlignment.CENTER),
                            ft.Row([btn_confirm],ft.MainAxisAlignment.CENTER, height=70),
                            ft.Row([back],ft.MainAxisAlignment.CENTER),
                            ]),
                            width=400,
                            height=470,
                            top=20,
                            left=0,
                            bgcolor = ft.Colors.TRANSPARENT,
                            border_radius=30,
                            opacity=0.9),
                    ]),visible=True,
                        width=400,
                        height=470,
                        border_radius=30,
                        border=ft.Border(
                            top=ft.BorderSide(width=2, color=ft.Colors.WHITE30),
                            right=ft.BorderSide(width=2, color=ft.Colors.WHITE30)
                                    ),
                        bgcolor = 'black',
                        opacity=0.9
                )
            page.clean()            
            page.add(body_new_user)  
    
        def page_recover(page): #Pagina de recuperação de senha
            Back_End.sounds("./sounds/cg.mp3", page)
            
            #Chama o Back End para recuperar a senha por email
            def call_back_end_recover(e):
                func = 'recover'
                Back_End(func, page, None, None, None, loading, email, t2, None)

            loading = ft.Image(
            src= f'./assets/load_icon.gif',
            width= 100,
            visible= False
            )

            t1 = ft.Text(
                value='Redefinir Senha',
                size=26,
                height=40,
                weight='bold',
                color= '#17ffee',
                visible=True
            )
            
            t2 = ft.Text(
                value='E-mail nao cadastrado no banco de dados!',
                size=15,
                bgcolor= '',
                color= '',
                visible= False
            )

            email = ft.TextField(
                label = 'E-mail',
                width = 200,
                height = 50,
                color = '#ffffff',
                border_radius = 15,
                border_width = 2,
                border_color = '#17ffee',
                focused_border_color= '#17ffee',
                visible = True,
                prefix_icon= ft.Icon(ft.Icons.EMAIL),
            )
            
            btn_confirm = ft.ElevatedButton(
                text= 'Enviar E-mail',
                width= 200,
                height= 40,
                bgcolor= '#17ffee',
                color= '#3d423c',
                on_click=call_back_end_recover,
                visible= True
            )
            
            back = ft.ElevatedButton(
                text= '<',
                width= 40,
                height= 40,
                bgcolor= '#17ffee',
                color= '#3d423c',
                on_click= lambda e :page_init(page),
                visible= True
            )
        
            body_recover = ft.Container(
                ft.Stack([
                    ft.Image('./assets/bg.gif', left= -60, top= 100),
                    ft.Container(
                            ft.Column([
                            ft.Row([t1],ft.MainAxisAlignment.CENTER),
                            ft.Row([t2],ft.MainAxisAlignment.CENTER),
                            ft.Row([loading], ft.MainAxisAlignment.CENTER),
                            ft.Row([email],ft.MainAxisAlignment.CENTER),
                            ft.Row([btn_confirm],ft.MainAxisAlignment.CENTER, height=80),
                            ft.Row([back],ft.MainAxisAlignment.CENTER),
                            ]),
                            width=400,
                            height=470,
                            top=100,
                            left=0,
                            bgcolor = ft.Colors.TRANSPARENT,
                            border_radius=30,
                            opacity=0.9
                            ),
                    ]),visible=True,
                        width=400,
                        height=470,
                        border_radius=30,
                        border=ft.Border(
                            top=ft.BorderSide(width=2, color=ft.Colors.WHITE30),
                            right=ft.BorderSide(width=2, color=ft.Colors.WHITE30)
                                    ),
                        bgcolor = 'black',
                        opacity=0.9
                )
            page.clean()
            page.add(body_recover)  
    
        page_init(page)
        sleep(1)
        start()
    app(target=main)

Front_End()
