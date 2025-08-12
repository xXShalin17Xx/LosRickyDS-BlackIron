import sqlite3

conn =sqlite3.connect("BlackIron.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuario(
    NumUsuario INT PRIMARY KEY AUTOINCREMENT ,
    Nombre VARCHAR(50),
    Apellido VARCHAR(50),
    Email VARCHAR(50)
);
''')

cursor.execute('''  
               
    CREATE TABLE IF NOT EXISTS MetodoDePago(
    CVC/CVV int,
    Num_T int,
    fecha_vencimiento DATE,
    nombreTitular VARCHAR(50)
    apellidoTitular VARCHAR(50)
    FOREING KEY (nombreTitular) references Usuario(Nombre),
    FOREING KEY (apellidoTitular) references Usuario(Apellido)
    
               
);            
 ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Producto(
    GTIN INT PRIMARY KEY AUTOINCREMENT,
    Nombre VARCHAR(50),
    Familia VARCHAR(50),
    Caracteristica VARCHAR(50),
    Precio DECIMAL(10,2),
    CantStock INT 
);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Pedido(
    IDPedido INT PRIMARY KEY AUTOINCREMENT,
    Producto VARCHAR(50),
    NumUsuario INT,
    NombreUsu VARCHAR(50),
    ApellidoUsu VARCHAR(50),
    Precio DECIMAL(10,2),
    FOREIGN KEY (Producto) references Producto(Nombre),
    FOREIGN KEY (NumUsuario) references Usuario(NumUsuario)
    FOREIGN KEY (NombreUsu) references Usuario(Nombre),
    FOREIGN KEY (ApellidoUsu) references Usuario(Apellido)
    
);
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS PedidoKITS(
    IDPedido INT PRIMARY KEY AUTOINCREMENT,
    ProductosEnKit VARCHAR(50),
    NumUsuario INT,
    NombreUsu VARCHAR(50),
    ApellidoUsu VARCHAR(50),
    Precio DECIMAL(10,2),
    FOREIGN KEY (Producto) references Producto(Nombre),
    FOREIGN KEY (NumUsuario) references Usuario(NumUsuario)
    FOREIGN KEY (NombreUsu) references Usuario(Nombre),
    FOREIGN KEY (ApellidoUsu) references Usuario(Apellido)
    
);
''')


cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS Facturacion(
    IDFactura INT PRIMARY KEY AUTOINCREMENT,
    IDPedido INT
    NombreUsu VARCHAR(50),
    ApellidoUsu VARCHAR(50),
    Tipo VARCHAR(10),
    PrecioBruto DECIMAL(10,2),
    PrecioNeto DECIMAL(10,2)
);
 ''')

def Pedido():
    cursor.execute(''' Select Nombre, Familia, Caracteristica, Precio from Producto ''')
    productos = cursor.fetchall() 
    if productos(bool) is False:
        print("No hay productos en stock")
    else:
        for producto in productos:
            print(f'''
    -------------------------------------------------------------------------------------
    | Producto: {producto[0]} | Familia: {producto[1]} | Caracteristica: {producto[2]} | Precio: { producto[3]} |
    -------------------------------------------------------------------------------------
    ''')

     

    Nombre = input("Ingrese su nombre")
    Apellido = input("ingrese su apellido")
    Email = input("Ingrese su correo electronico")
    cursor.execute(''' 
    INSERT INTO Usuario (Nombre, Apellido, Email)
 ''',Nombre, Apellido, Email)
    
    NumTarjeta = int(input("Ingrese los números de su tarjeta"))
    CVCoCVV = int(input("Ingrese la clave CVC/CVV"))
    if NumTarjeta <13 or NumTarjeta >19:
        print("El número de la tarjeta es invalido")
    else:
        if CVCoCVV >4 or CVCoCVV <3:
            print("Clave CVC/CVV")
        else:
            cursor.execute(''' 
        INSERT INTO MetodoDePago(CVC/CVV, Num_T, fecha_vencimiento, nombreTitular, apellidoTitular)
     ''',NumTarjeta,CVCoCVV, Nombre, Apellido)
