#import modules
 
from tkinter import *
from tkinter import messagebox,filedialog,ttk
import os
import requests
import json

# Designing window for login 
def login():
    main_screen.withdraw()
    global login_screen
    login_screen = Toplevel(main_screen)
    login_screen.title("Login")
    login_screen.geometry("300x350")
    Label(login_screen, text="").pack()
 
    global username_verify
    global password_verify
    global ip_verify
 
    username_verify = StringVar()
    password_verify = StringVar()
    ip_verify = StringVar()

    Label(login_screen, text="Username: ", font=('bold', 14)).pack()
    Entry(login_screen, textvariable=username_verify).pack()
    Label(login_screen, text="").pack()
    Label(login_screen, text="Password: ", font=('bold', 14)).pack()
    Entry(login_screen, textvariable=password_verify, show= '*').pack()
    Label(login_screen, text="").pack()
    Label(login_screen, text="Server ip: ", font=('bold', 14)).pack()
    Entry(login_screen, textvariable=ip_verify).pack()
    Label(login_screen, text="").pack()
    Button(login_screen, text="Login", width=10, height=1, command = login_verify).pack()
    Button(login_screen, text="back", width=10, height=1, fg="red", command=lambda: voltar(login_screen,main_screen)).pack(side=RIGHT, expand=1)


# Implementing event on login button 
def login_verify():
#get username and password
    global username1
    global password1
    global ip 

    username1 = username_verify.get()
    password1 = password_verify.get()
    ip = ip_verify.get()
# this will delete the entry after login button is pressed
    username_verify.set("")
    password_verify.set("")
    ip_verify.set("")
   
    ####### hardcoded#######
    ip = '192.168.117.163'
    username1 = 'demo'
    password1 = 'secret'
    ########################
    
#Cria um token para o utilizador (já criado)
    url_token = 'http://'+ip+'/identity/v3/auth/tokens'
    myobj={"auth":{"identity":{"methods":["password"],"password":{"user":{"name":username1,"domain":{"name":"Default"},"password":password1}}}}}
    response_API = requests.post(url_token, json = myobj)

    if response_API.status_code != 201: 
        messagebox.showerror('ERROR', 'Incorrect Username or Password')
        return

    global usr_token
    usr_token = response_API.headers['X-Subject-Token']
    login_screen.withdraw()
    projeto()

    #print the token in command so I don't have to always aquire it via postname because I am lazy
    print(f"{usr_token=}")

def projeto():
    global proj_screen
    proj_screen = Toplevel(login_screen)
    proj_screen.title("Projetos")
    proj_screen.geometry("300x250")

    # Project List (Listbox)
    
    global Lista_proj
    Lista_proj = Listbox(proj_screen,bg = "pink", bd = 5, fg = "black")  
    yscroll = Scrollbar(proj_screen, command=Lista_proj.yview)

    yscroll.pack(side=RIGHT, fill=Y)
    Lista_proj.pack(fill=BOTH)

    Lista_proj.config(yscrollcommand=yscroll.set)
    
    # Bind select
    Lista_proj.bind('<<ListboxSelect>>', select_proj)

    Button(proj_screen, text="Log Out", width=10, height=1, fg="red", command=lambda: voltar(proj_screen,login_screen) ).pack(side=RIGHT)
    Button(proj_screen, text="Continuar", width=10, height=1, fg="green", command=instancias).pack(side=RIGHT)


    url_projetos = 'http://'+ip+'/identity/v3/auth/projects'
    projetos_API = requests.get(url_projetos, headers = {"x-auth-token": usr_token})

    projetos_json = projetos_API.json()
    projetos_resposta = projetos_json['projects']        

    global store_list

    store_list = []
    for item in projetos_resposta:
        store_details = {"name":None, "id":None}
        store_details['name'] = item['name']
        store_details['id'] = item['id']
        store_list.append(store_details)
        i = 1
        Lista_proj.insert(i, store_details['name'])
        i += 1
    

def select_proj(event):

    index = Lista_proj.curselection()[0]
    seltext = Lista_proj.get(index)

    global proj_id

    for i in store_list:
        if i['name'] == seltext:
            proj_id = i['id']

    

def instancias():
    #caso nao tenha sido selecionado nenhum projeto a aplicacao nao avança
    try:
        proj_id
    except:
        messagebox.showerror('ERROR', 'Selecione um Projeto')
        return

    global inst_screen
    inst_screen = Toplevel(proj_screen)
    inst_screen.title("Instancias")
    inst_screen.geometry("400x350")
    
    global Lista_inst


    # Project List (Listbox)    
    Lista_inst = Listbox(inst_screen,bg = "pink", bd = 5, fg = "black")
    yscroll = Scrollbar(inst_screen, command=Lista_inst.yview)

    yscroll.pack(side=RIGHT, fill=Y)
    Lista_inst.pack(fill=BOTH)

    Lista_inst.config(yscrollcommand=yscroll.set)
    
    # Bind select
    Lista_inst.bind('<<ListboxSelect>>', select_inst)

    
    #butoes da janelas das instancias/ instance buttons
    Button(inst_screen, text="Voltar", width=10, height=1, fg="red", command=lambda: voltar(inst_screen,proj_screen) ).pack(side=BOTTOM)
    Button(inst_screen, text="Create Volume", width=14, height=1, command=create_vol).pack(side=BOTTOM)
    #Button(inst_screen, text="Adicionar imagem", width=14, fg="white", bg="#263D42", command=add_img).pack(side=BOTTOM)
    Button(inst_screen, text="Adicionar imagem", width=14, fg="white", bg="#263D42", command=create_img).pack(side=BOTTOM)
    Button(inst_screen, text="Lista de Imagens", width=14, height=1, command=lista_images).pack(side=BOTTOM)
    Button(inst_screen, text="Remover", width=10, height=1, command=remover_inst).pack(side=RIGHT)
    Button(inst_screen, text="Alterar", width=10, height=1, command=update_inst).pack(side=RIGHT)
    Button(inst_screen, text="Create Instance", width=14, height=1, command=criar_inst).pack(side=RIGHT)
    
    url_token = 'http://'+ip+'/identity/v3/auth/tokens'
    myobj={"auth":{"identity":{"methods":["password"],"password":{"user":{"name":username1,"domain":{"name":"Default"},"password":password1}}},"scope":{"project":{"id":proj_id}}}}
    response_API = requests.post(url_token, json = myobj)
    global scoped_usr_token
    scoped_usr_token = response_API.headers['X-Subject-Token']

    url_instances = 'http://'+ip+'/compute/v2.1/servers'
    instances_API = requests.get(url_instances, headers = {"x-auth-token": scoped_usr_token})
    instances_json = instances_API.json() 
    inst_resposta = instances_json['servers']
    
    global store_list_instances

    store_list_instances = []
    for item in inst_resposta:
        store_details = {"name":None, "id":None}
        store_details['name'] = item['name']
        store_details['id'] = item['id']
        store_list_instances.append(store_details)
        i = 1
        Lista_inst.insert(i, store_details['name'])
        i += 1

def lista_images():
    global lista_img_screen
    lista_img_screen = Toplevel(inst_screen)
    lista_img_screen.title("Lista de Imagens")
    lista_img_screen.geometry("1100x500")

    url_images = 'http://' + ip + '/image/v2/images'
    images_API = requests.get(url_images, headers={"x-auth-token": scoped_usr_token})
    imagens_json = images_API.json()
    img_respota = imagens_json['images']

    imagem_table= ttk.Treeview(lista_img_screen)
    #Colunas
    imagem_table['columns'] = ("name","ID", "Type", "file_exten", "MinDisk", "MinRAM")
    imagem_table.column("#0", width=0, stretch=NO)
    imagem_table.column("name", width=70, anchor=W)
    imagem_table.column("ID", width=70, anchor=CENTER)
    imagem_table.column("Type", width=70, anchor=W)
    imagem_table.column("file_exten", width=100, anchor=CENTER)
    imagem_table.column("MinDisk", width=100, anchor=CENTER)
    imagem_table.column("MinRAM", width=100, anchor=CENTER)

    #Texto nas colunas
    imagem_table.heading("#0", text="", anchor=W)
    imagem_table.heading("name", text="Nome", anchor=W)
    imagem_table.heading("ID",text="Id", anchor=CENTER)
    imagem_table.heading("Type",text="Tipo", anchor=W)
    imagem_table.heading("file_exten",text="Extensão do ficheiro", anchor=CENTER)
    imagem_table.heading("MinDisk",text="Min. Disco Alocado", anchor=CENTER)
    imagem_table.heading("MinRAM",text="Min. RAM Alocada", anchor=CENTER)

    aux_list_img = []
    list_img = []

    for item in img_respota:
        store_details = {"name": None, "id": None, "status": None,"min_disk": None, "min_ram": None,  "disk_format": None}
        store_details['name'] = item['name']
        store_details['id'] = item['id']
        store_details['status'] = item['status']
        store_details['min_disk'] = item['min_disk']
        store_details['min_ram'] = item['min_ram']
        store_details['disk_format'] = item['disk_format']
        aux_list_img.append(store_details)
        list_img.append(store_details['name'])

    #linhas com a informação das imagens
    for i in aux_list_img:
        imagem_table.insert(parent='',index='end', iid=i,values=(i['name'],i['id'],i['status'],i['disk_format'], i['min_disk'], i['min_ram']))

    imagem_table.pack(pady=10)
def add_img():
    global filename
    global img_filename
    filename = StringVar()

    # pop-up da janela para selecionar o ficheiro
    filename= filedialog.askopenfilename(initialdir="/", title="Seleccione a imagem: ",
             filetypes=(("executables", "*.iso"), ("all files", "*.*")))
    #print(filename)
    img_filename.set(filename)


def create_img():
    global create_img_screen
    create_img_screen = Toplevel(inst_screen)
    create_img_screen.title("Criar Imagem")
    create_img_screen.geometry("350x350")

    global container_format
    global disk_format
    global name_imagem
    global img_id
    global min_disk
    global min_ram
    global img_filename

    name_imagem = StringVar()
    img_id = StringVar()
    disk_format = StringVar()
    list_disk_format = ['ami', 'aki', 'ari', 'vhd', 'vhdx', 'vmdk', 'raw', 'qcow2', 'vdi', 'ploop', 'iso']
    container_format = StringVar()
    #list_container_format = ['ami', 'aki', 'ari', 'bare', 'ovf', 'ova', 'docker']
    img_filename = StringVar()
    min_disk = IntVar()
    min_ram = IntVar()

    #labels and buttons to add parameters of an image
    Label(create_img_screen, text="Nome da Imagem: ", font=('bold', 14)).pack()
    Entry(create_img_screen, textvariable=name_imagem).pack()
    Label(create_img_screen, text="Extensão do ficheiro: ", font=('bold', 14)).pack()
    OptionMenu(create_img_screen, disk_format,*list_disk_format).pack()
    #Label(create_img_screen, text="Formato do container ", font=('bold', 14)).pack()
    #OptionMenu(create_img_screen, container_format, *list_container_format).pack()
    Label(create_img_screen, text="Minimo de espaço de disco: ", font=('bold', 14)).pack()
    Entry(create_img_screen, textvariable=min_disk).pack()
    Label(create_img_screen, text="Minimo de RAM: ", font=('bold', 14)).pack()
    Entry(create_img_screen, textvariable=min_ram).pack()
    Button(create_img_screen,text="Escolha o ficheiro", width=14, fg="white", bg="#263D42", command=add_img).pack()
    Label(create_img_screen, textvariable=img_filename, font=(10)).pack()

    Button(create_img_screen, text="Registar Imagem", width=14, fg="white", bg="#263D42", command=registar_img).pack()

    disk_format.set(list_disk_format[0])
    #container_format.set(list_container_format[0])

def registar_img():
    print(name_imagem.get())
    print(filename)

    #POST Request para criar a imagem
    url_img = 'http://' + ip + '/image/v2/images'
    my_obj = {"disk_format": disk_format.get(), "name": name_imagem.get(), "min_disk": min_disk.get(), "min_ram": min_ram.get()}
    images_API = requests.post(url_img, json=my_obj, headers={"x-auth-token": scoped_usr_token})
    imagens_json = images_API.json()

    # PUT request para dar upload do ficheiro da imagem
    image_respota = imagens_json['id']
    url_upload = 'http://' + ip + '/image/v2/images/'+image_respota+'/file'
    #print(filename)
    img_upload_API = requests.put(url_upload, headers={"content-type": "application/octet-stream", "x-auth-token": scoped_usr_token}, data={ 'image_file': filename})
    print(image_respota)

def create_vol():
    global create_vol_screen
    create_vol_screen = Toplevel(inst_screen)
    create_vol_screen.title("Criar Volume")
    create_vol_screen.geometry("300x250")

    global vol_size
    global vol_name
    global vol_desc

    vol_name = StringVar()  
    vol_size = IntVar()
    vol_desc = StringVar()

    Label(create_vol_screen, text="Nome do Volume: ", font=('bold', 14)).pack()
    Entry(create_vol_screen, textvariable=vol_name).pack()
    Label(create_vol_screen, text="Tamanho: ", font=('bold', 14)).pack()
    Entry(create_vol_screen, textvariable=vol_size).pack()
    Label(create_vol_screen, text="Descricao: ", font=('bold', 14)).pack()
    Entry(create_vol_screen, textvariable=vol_desc).pack()

    Button(create_vol_screen, text="voltar", width=10, height=1, fg="red", command=lambda: voltar(create_vol_screen,inst_screen) ).pack(side=RIGHT)
    Button(create_vol_screen, text="Update", width=10, height=1, fg="green", command=create_vol_verify).pack(side=RIGHT)

def create_vol_verify():
    size_vol = vol_size.get()
    name_vol = vol_name.get()
    description_vol = vol_desc.get()

    url_vols = 'http://'+ip+'/volume/v3/'+proj_id+'/volumes'
    myobj={"volume":{"size":size_vol,"availability_zone":"nova","name":name_vol,"description":description_vol,"volume_type":"lvmdriver-1"}}
    vols_API = requests.post(url_vols, json = myobj, headers = {"x-auth-token": scoped_usr_token})
    print(vols_API.status_code)

def select_inst(event):
    global index1
    index1 = Lista_inst.curselection()[0]
    seltext = Lista_inst.get(index1)
    
    global inst_id

    for i in store_list_instances:
        if i['name'] == seltext:
            inst_id = i['id']

def update_inst():
    try:
        inst_id
    except:
        messagebox.showerror('ERROR', 'Selecione uma instancia')
        return

    global update_screen
    update_screen = Toplevel(inst_screen)
    update_screen.title("Criar Instancia")
    update_screen.geometry("300x150")

    url_instance = 'http://192.168.254.129/compute/v2.1/servers/'+inst_id
    instance_API = requests.get(url_instance, headers = {"x-auth-token": scoped_usr_token})
    instance_json = instance_API.json()
    instance_respota = instance_json['server']
    name = instance_respota['name']


    global nome_inst_put
    nome_inst_put = StringVar()  
    nome_inst_put.set(name)

    Label(update_screen, text="Nome da instancia: ", font=('bold', 14)).pack()
    Entry(update_screen, textvariable=nome_inst_put).pack()

    Button(update_screen, text="voltar", width=10, height=1, fg="red", command=lambda: voltar(update_screen,inst_screen) ).pack(side=RIGHT)
    Button(update_screen, text="Update", width=10, height=1, fg="green", command=confirmar_update).pack(side=RIGHT)

def confirmar_update():
    nome_update = nome_inst_put.get()
    url_update = 'http://'+ip+'/compute/v2.1/servers/'+inst_id
    myobj={"server":{"name":nome_update}}
    response_API = requests.put(url_update, json = myobj, headers = {"x-auth-token": scoped_usr_token})
    print("update ",response_API.status_code)

def criar_inst():
    global criar_screen
    criar_screen = Toplevel(inst_screen)
    criar_screen.title("Criar Instancia")
    criar_screen.geometry("300x310")

    url_flavors = 'http://'+ip+'/compute/v2.1/flavors'
    flavors_API = requests.get(url_flavors, headers = {"x-auth-token": scoped_usr_token})
    flavors_json = flavors_API.json()
    flv_respota = flavors_json['flavors']

    url_images = 'http://'+ip+'/image/v2/images'
    images_API = requests.get(url_images, headers = {"x-auth-token": scoped_usr_token})
    imagens_json = images_API.json()
    img_respota = imagens_json['images']

    print(f"{img_respota=}")


    url_network = 'http://'+ip+':9696/v2.0/networks'
    network_API = requests.get(url_network, headers = {"x-auth-token": scoped_usr_token})
    network_json = network_API.json()
    net_respota = network_json['networks']

    #TODO fix keypair
    url_keypair = 'http://' + ip + '/compute/v2.1/os-keypairs'
    keypair_API = requests.get(url_keypair, headers = {"x-auth-token": scoped_usr_token})
    keypair_json = keypair_API.json()
    #keypair_json = json.loads(keypair_API)
    print(f"{keypair_json=}")
    keypair_respota = keypair_json['keypairs']
    print(f"{keypair_respota[0]=}")
    print(f"{keypair_respota[1]=}")
    #print(keypair_respota.keys())
    #print(help(keypair_respota))




    global store_list_flv

    store_list_flv = []
    list_flv = []
    for item in flv_respota:
        store_details = {"name":None, "id":None}
        store_details['name'] = item['name']
        store_details['id'] = item['id']
        store_list_flv.append(store_details)
        list_flv.append(store_details['name'])

    
    global store_list_img

    store_list_img = []
    list_img = []
    for item in img_respota:
        store_details = {"name":None, "id":None}
        store_details['name'] = item['name']
        store_details['id'] = item['id']
        store_list_img.append(store_details)
        list_img.append(store_details['name'])

    global store_list_net

    store_list_net = []
    list_net = []
    for item in net_respota:
        store_details = {"name":None, "id":None}
        store_details['name'] = item['name']
        store_details['id'] = item['id']
        store_list_net.append(store_details)
        list_net.append(store_details['name'])


    global store_list_keypair

    #TODO get keypair working properly
    store_list_keypair = []
    list_keypair = []
    for item in keypair_respota:
        #o keypair vai ser apenas identificado pelo seu nome
        #preciso de entrar no nome dentro do keypair
        store_details = {"keypair": None}
        store_details['kaypair'] = item['keypair']
        store_list_keypair.append(store_details)
        list_keypair.append(store_details['keypair'])


    global nome_inst
    global imagem
    global network
    global flavor
    global keypair

    nome_inst = StringVar()
    imagem = StringVar()
    network = StringVar()
    flavor = StringVar()
    keypair = StringVar()
    

    Label(criar_screen, text="Nome da instancia: ", font=('bold', 14)).pack()
    Entry(criar_screen, textvariable=nome_inst).pack()
    Label(criar_screen, text="Imagem: ", font=('bold', 14)).pack()
    OptionMenu(criar_screen, imagem, *list_img).pack()   
    Label(criar_screen, text="Network: ", font=('bold', 14)).pack()
    OptionMenu(criar_screen, network, *list_net).pack()
    Label(criar_screen, text="Flavour: ", font=('bold', 14)).pack()
    OptionMenu(criar_screen, flavor, *list_flv).pack()
    Label(criar_screen, text="keypair: ", font=('bold', 14)).pack()
    OptionMenu(criar_screen, keypair, *list_keypair).pack()

    imagem.set(list_img[0])
    network.set(list_net[0])
    flavor.set(list_flv[0])
    keypair.set(list_keypair[0])
    
    Button(criar_screen, text="voltar", width=10, height=1, fg="red", command=lambda: voltar(criar_screen,inst_screen) ).pack(side=RIGHT)
    Button(criar_screen, text="Criar", width=10, height=1, fg="green", command=confirmar_criacao).pack(side=RIGHT)

    

def confirmar_criacao():
    nome = nome_inst.get()

    for i in store_list_img:
        if i['name'] == imagem.get():
            img_id = i['id']

    for i in store_list_net:
        if i['name'] == network.get():
            net_id = i['id']

    for i in store_list_flv:
        if i['name'] == flavor.get():
            flv_id = i['id']

#o keypair nao tem id, só é identificado pelo seu key_name/name
    for i in store_list_keypair:
        if i['name'] == keypair.get():
            key_name = i['name']

    #print(imagem.get(),network.get(),flavor.get())
    url_token = 'http://'+ip+'/compute/v2.1/servers'
    myobj= {"server":{"name":nome,"imageRef":img_id,"flavorRef":flv_id,
                      "networks":[{"uuid":net_id}],"availability_zone":"nova",
                      "keypairRef":key_name}}
    
    response_API = requests.post(url_token, headers = {"x-auth-token": scoped_usr_token}, json = myobj)
    
    print("criacao ",response_API.status_code)

def remover_inst():
    try:
        inst_id
    except:
        messagebox.showerror('ERROR', 'Selecione uma instancia')
        return

    url_instance = 'http://'+ip+'/compute/v2.1/servers/'+inst_id
    instance_API = requests.delete(url_instance, headers = {"x-auth-token": scoped_usr_token})
    print("remocao ",instance_API.status_code)
    Lista_inst.delete(index1)


def voltar(destroy,deiconify):
    destroy.destroy()
    deiconify.deiconify()

def exit_app():
    exit(0)


# Designing Main(first) window
def main_account_screen():
    global main_screen
    main_screen = Tk()
    main_screen.geometry("300x200")
    main_screen.title("Account Login")

    Label(text="TRABALHO DE LTI", width="300", height="2", font=("Bold", 18)).pack()
    
    Button(text="Sair", height="2", width="30", command = exit_app, foreground="black", background='#ff7b8d').pack(side=BOTTOM, expand=1)
    Button(text="Login", height="2", width="30", command = login, foreground="black", background='#abfeff').pack(side=BOTTOM, expand=1)

    main_screen.mainloop()
    

main_account_screen()