import sqlite3
import hashlib


conn =sqlite3.connect("BlackIron.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuario(
    NumUsuario INTEGER PRIMARY KEY AUTOINCREMENT ,
    Nombre TEXT,
    Apellido TEXT,
    Email TEXT,
    Hash TEXT
);
''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS Administrador (
    Usuario TEXT PRIMARY KEY,
    Hash TEXT
);

''')

cursor.execute('''  
               
    CREATE TABLE IF NOT EXISTS MetodoDePago(
    CVCoCVV INTEGER,
    NumTarjeta INTEGER PRIMARY KEY,
    fecha_vencimiento DATE,
    Titular TEXT

    
               
);            
 ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Producto(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    Familia TEXT,
    Caracteristica TEXT,
    Precio DECIMAL(10,2) NOT NULL,
    CantStock INTEGER DEFAULT 0

);
''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS Kit  (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT,
    Precio REAL
);
 ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS KitProducto  (
    IDKit INTEGER,
    IDProducto INTEGER,
    Cantidad INTEGER,
    FOREIGN KEY (IDKit) REFERENCES Kit(ID),
    FOREIGN KEY (IDProducto) REFERENCES Producto(ID)
);
 ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Pedido(
    IDPedido INTEGER PRIMARY KEY AUTOINCREMENT,
    Producto TEXT,
    NumUsuario INTEGER,
    Precio DECIMAL(10,2),
    Cantidad INTEGER,
    NumTarjeta INTEGER, 
    FOREIGN KEY (Producto) references Producto(Nombre),
    FOREIGN KEY (NumUsuario) references Usuario(NumUsuario),
    FOREIGN KEY (NumTarjeta) references MetodoDePago(Num_T)
    
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS DetallePedidoProducto (
    IDDetalle INTEGER PRIMARY KEY AUTOINCREMENT,
    IDPedido INTEGER NOT NULL,
    IDProducto INTEGER NOT NULL,
    Cantidad INTEGER NOT NULL,
    PrecioUnitario REAL NOT NULL,
    FOREIGN KEY (IDPedido) REFERENCES Pedido(IDPedido),
    FOREIGN KEY (IDProducto) REFERENCES Producto(ID)
);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS PedidoKITS(
    IDPedido INTEGER PRIMARY KEY AUTOINCREMENT,
    IDKit INTEGER,
    NumUsuario INTEGER,
    Precio DECIMAL(10,2),
    Cantidad INTEGER,
    NumTarjeta INTEGER,
    FOREIGN KEY (IDKit) references Kit(ID),
    FOREIGN KEY (NumUsuario) references Usuario(NumUsuario),
    FOREIGN KEY (NumTarjeta) references MetodoDePago(Num_T)
    
);
''')

cursor.execute(''' 
CREATE TABLE IF NOT EXISTS DetallePedidoKit (
    IDDetalle INTEGER PRIMARY KEY AUTOINCREMENT,
    IDPedido INTEGER NOT NULL,
    IDProducto INTEGER NOT NULL,
    Cantidad INTEGER NOT NULL,
    PrecioUnitario REAL NOT NULL,
    FOREIGN KEY (IDPedido) REFERENCES PedidoKITS(IDPedido),
    FOREIGN KEY (IDProducto) REFERENCES Producto(ID)
);
 ''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS Facturacion(
    IDFactura INTEGER PRIMARY KEY AUTOINCREMENT,
    IDPedido INTEGER,
    NombreUsu TEXT,
    ApellidoUsu TEXT,
    Tipo TEXT CHECK(Tipo IN ('Producto', 'Kit')),
    PrecioBruto DECIMAL(10,2),
    PrecioNeto DECIMAL(10,2),
    Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
 ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Devolucion (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    IDPedido INTEGER,
    Tipo TEXT CHECK(Tipo IN ('Producto', 'Kit')),
    Fecha TEXT,
    Cantidad INTEGER,
    Motivo TEXT,
    FOREIGN KEY(IDPedido) REFERENCES Pedido(ID)
);
 ''')

def encriptar_contraseña(contraseña):
    return hashlib.sha256(contraseña.encode()).hexdigest()

def verificar_contraseña(contraseña_ingresada, hash_guardado):
    return encriptar_contraseña(contraseña_ingresada) == hash_guardado

import sqlite3

def registrar_admin_seguro():
    clave_maestra = "BlackIron2025"  
    clave_ingresada = input("Ingrese la clave maestra para registrar administrador: ")

    if clave_ingresada != clave_maestra:
        print("Clave incorrecta. Acceso denegado.")
        return

    usuario = input("Nuevo usuario administrador: ")
    contraseña = input("Contraseña: ")
    resultado = registrar_admin(usuario, contraseña, db_path="BlackIron.db")
    print(resultado)

def registrar_admin(usuario, contraseña, db_path="mi_base.db"):
    if not usuario or not contraseña:
        return "Usuario y contraseña requeridos."

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM Administrador WHERE Usuario = ?", (usuario,))
    if cursor.fetchone():
        conn.close()
        return f"El administrador '{usuario}' ya existe."

    hash = encriptar_contraseña(contraseña)
    cursor.execute("INSERT INTO Administrador (Usuario, Hash) VALUES (?, ?)", (usuario, hash))
    conn.commit()
    conn.close()
    return f"Administrador '{usuario}' registrado con éxito."

def login_admin(usuario, contraseña, db_path="mi_base.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT Hash FROM Administrador WHERE Usuario = ?", (usuario,))
    fila = cursor.fetchone()
    conn.close()

    if fila and verificar_contraseña(contraseña, fila[0]):
        return f"Login exitoso como administrador '{usuario}'."
    return "Credenciales inválidas."

def registrar_tarjeta_si_no_existe(NumTarjeta, CVCoCVV, fecha_vencimiento, Titular):
    try:
        cursor.execute('SELECT NumTarjeta FROM MetodoDePago WHERE NumTarjeta = ?', (NumTarjeta,))
        tarjeta_existente = cursor.fetchone()

        if not tarjeta_existente:
            cursor.execute('''
                INSERT INTO MetodoDePago (CVCoCVV, NumTarjeta, fecha_vencimiento, Titular)
                VALUES (?, ?, ?, ?)
            ''', (CVCoCVV, NumTarjeta, fecha_vencimiento, Titular))
            conn.commit()
            print("Tarjeta registrada correctamente.")
        else:
            print("La tarjeta ya está registrada. Se usará la información existente.")
    except Exception as e:
        conn.rollback()
        print("Error al registrar la tarjeta:", e)

def validar_datos_tarjeta(NumTarjeta, CVCoCVV):
    if not (13 <= len(NumTarjeta) <= 19):
        print("El número de la tarjeta es inválido.")
        return False
    if not (3 <= len(CVCoCVV) <= 4):
        print("Clave CVC/CVV inválida.")
        return False
    return True

def procesar_tarjeta(NumTarjeta, CVCoCVV, fecha_vencimiento, Titular):
    if not validar_datos_tarjeta(NumTarjeta, CVCoCVV):
        return False
    registrar_tarjeta_si_no_existe(NumTarjeta, CVCoCVV, fecha_vencimiento, Titular)
    return True

def Registrar():
    Nombre = input("Ingrese su nombre: ")
    Apellido = input("Ingrese su apellido: ")
    Email = input("Ingrese su correo electrónico: ").lower()
    Contraseña = input("Ingrese su contraseña: ")

    cursor.execute('''SELECT * FROM Usuario WHERE Email = ?''', (Email,))
    check = cursor.fetchall()

    if check:
        print("Email ya registrado, inicie sesión.")
        return None
    else:
        hash = encriptar_contraseña(Contraseña)
        cursor.execute('''
            INSERT INTO Usuario (Nombre, Apellido, Email, Hash)
            VALUES (?, ?, ?, ?)
        ''', (Nombre, Apellido, Email, hash))
        conn.commit()
        print("Usuario registrado.")

        cursor.execute('''SELECT NumUsuario FROM Usuario WHERE Email = ?''', (Email,))
        idUsuario = cursor.fetchone()[0]
        return idUsuario

def Login():
    Email = input("Ingrese su Email registrado: ").lower()
    ContraseñaIngresada = input("Ingrese su contraseña: ")

    cursor.execute('''SELECT Hash FROM Usuario WHERE Email = ?''', (Email,))
    fila = cursor.fetchone()

    if not fila:
        print("Usuario no encontrado, revise la información ingresada.")
        return None

    hash_guardado = fila[0]
    if verificar_contraseña(ContraseñaIngresada, hash_guardado):
        print("¡Sesión iniciada correctamente!")
    else:
        print("Contraseña incorrecta. Intente nuevamente.")
        return None

    cursor.execute('''SELECT NumUsuario FROM Usuario WHERE Email = ?''', (Email,))
    idUsuario = cursor.fetchone()[0]
    print('''
        ----------------------------
       | ¡RECUERDA!                  |
       |   TU NÚMERO DE USUARIO ES:  |
        ----------------------------
    ''')
    return idUsuario

def obtener_id_pedido(tabla, campo, valor, usuario):
    cursor.execute(f'''
        SELECT IDPedido FROM {tabla}
        WHERE {campo} = ? AND NumUsuario = ?
        ORDER BY IDPedido DESC LIMIT 1
    ''', (valor, usuario))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def mostrar_factura(IDPedido):
    cursor.execute('SELECT * FROM Facturacion WHERE IDPedido = ?', (IDPedido,))
    factura = cursor.fetchone()
    print("Factura:", factura)

def facturar_producto(IDPedido, NumUsuario):
    cursor.execute('SELECT Nombre, Apellido FROM Usuario WHERE NumUsuario = ?', (NumUsuario,))
    NombreUsu, ApellidoUsu = cursor.fetchone()

    cursor.execute('SELECT Precio, Cantidad FROM Pedido WHERE IDPedido = ?', (IDPedido,))
    Precio, Cantidad = cursor.fetchone()

    PrecioBruto = Precio * Cantidad
    PrecioNeto = round(PrecioBruto * 1.21, 2)

    cursor.execute('''
        INSERT INTO Facturacion (IDPedido, NombreUsu, ApellidoUsu, Tipo, PrecioBruto, PrecioNeto)
        VALUES (?, ?, ?, 'Producto', ?, ?)
    ''', (IDPedido, NombreUsu, ApellidoUsu, PrecioBruto, PrecioNeto))
    conn.commit()
    mostrar_factura(IDPedido)
        
def facturar_kit(IDPedido, NumUsuario):
    cursor.execute('SELECT Nombre, Apellido FROM Usuario WHERE NumUsuario = ?', (NumUsuario,))
    NombreUsu, ApellidoUsu = cursor.fetchone()

    cursor.execute('SELECT Precio, Cantidad FROM PedidoKITS WHERE IDPedido = ?', (IDPedido,))
    Precio, Cantidad = cursor.fetchone()

    PrecioBruto = Precio * Cantidad
    PrecioNeto = round(PrecioBruto * 1.21, 2)

    cursor.execute('''
        INSERT INTO Facturacion (IDPedido, NombreUsu, ApellidoUsu, Tipo, PrecioBruto, PrecioNeto)
        VALUES (?, ?, ?, 'Kit', ?, ?)
    ''', (IDPedido, NombreUsu, ApellidoUsu, PrecioBruto, PrecioNeto))
    conn.commit()
    mostrar_factura(IDPedido)

def registrar_detalle_pedido_kit(IDPedido, componentes, cantidad):
    for IDProducto, cantidad_por_kit in componentes:
        cantidad_total = cantidad_por_kit * cantidad
        cursor.execute('SELECT Precio FROM Producto WHERE ID = ?', (IDProducto,))
        precio_unitario = cursor.fetchone()[0]

        cursor.execute('''
            INSERT INTO DetallePedidoKit (IDPedido, IDProducto, Cantidad, PrecioUnitario)
            VALUES (?, ?, ?, ?)
        ''', (IDPedido, IDProducto, cantidad_total, precio_unitario))
    conn.commit()

def registrar_detalle_pedido_producto(IDPedido, IDProducto, cantidad):
    cursor.execute('SELECT Precio FROM Producto WHERE ID = ?', (IDProducto,))
    precio_unitario = cursor.fetchone()[0]

    cursor.execute('''
        INSERT INTO DetallePedidoProducto (IDPedido, IDProducto, Cantidad, PrecioUnitario)
        VALUES (?, ?, ?, ?)
    ''', (IDPedido, IDProducto, cantidad, precio_unitario))
    conn.commit()

def actualizar_stock_kit(componentes, cantidad):
    for IDProducto, cantidad_por_kit in componentes:
        cantidad_total = cantidad_por_kit * cantidad
        cursor.execute('''
            UPDATE Producto SET CantStock = CantStock - ? WHERE ID = ?
        ''', (cantidad_total, IDProducto))
    conn.commit()

def actualizar_stock_producto(prod, cantidad):
    cursor.execute('''
        UPDATE Producto SET CantStock = CantStock - ? WHERE ID = ?
    ''', (cantidad, prod))
    conn.commit()

def validar_stock_kit(componentes, cantidad):
    for IDProducto, cantidad_por_kit in componentes:
        cantidad_total = cantidad_por_kit * cantidad
        cursor.execute('SELECT CantStock FROM Producto WHERE ID = ?', (IDProducto,))
        stock_actual = cursor.fetchone()[0]
        if cantidad_total > stock_actual:
            return False
    return True

def validar_stock_producto(prod, cantidad):
    cursor.execute('SELECT CantStock FROM Producto WHERE ID = ?', (prod,))
    stock_actual = cursor.fetchone()[0]
    return cantidad <= stock_actual

def agregar_al_carrito(Carrito, IDPedido, tipo, nombre, cantidad, precio_unitario):
    Carrito.append({
        "IDPedido": IDPedido,
        "Tipo": tipo,
        "Nombre": nombre,
        "Cantidad": cantidad,
        "PrecioUnitario": precio_unitario,
        "PrecioTotal": precio_unitario * cantidad
    })

def mostrar_resumen_carrito(Carrito):
    print("\nResumen del carrito:")
    Total = 0
    for item in Carrito:
        print(f"Pedido #{item['IDPedido']} | Tipo: {item['Tipo']} | {item['Nombre']} x{item['Cantidad']} → ${item['PrecioTotal']:.2f}")
        Total += item['PrecioTotal']
    print(f"Total a pagar: ${Total:.2f}")

def CargarProducto():
    print("\n--- CARGA DE PRODUCTO ---")
    nombre = input("Nombre del producto: ")
    familia = input("Familia del producto: ")
    caracteristica = input("Característica: ")
    precio = float(input("Precio unitario: "))
    cantidad = int(input("Cantidad a ingresar al stock: "))

    
    cursor.execute('SELECT ID FROM Producto WHERE Nombre = ?', (nombre,))
    existente = cursor.fetchone()

    if existente:
        
        cursor.execute('''
            UPDATE Producto
            SET CantStock = CantStock + ?, Precio = ?
            WHERE ID = ?
        ''', (cantidad, precio, existente[0]))
        print(f"Producto existente actualizado. Stock sumado: {cantidad}")
    else:
        
        cursor.execute('''
            INSERT INTO Producto (Nombre, Familia, Caracteristica, Precio, CantStock)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, familia, caracteristica, precio, cantidad))
        print(f"Producto nuevo cargado: {nombre} x{cantidad}")

    conn.commit()

def CargarKit():
    print("\n--- CARGA DE KIT ---")
    nombre = input("Nombre del kit: ")
    precio = float(input("Precio del kit: "))
    cantidad = int(input("Cantidad de kits a ingresar: "))

    cursor.execute('''
        INSERT INTO Kit (Nombre, Precio)
        VALUES (?, ?)
    ''', (nombre, precio))
    conn.commit()

    cursor.execute('SELECT ID FROM Kit WHERE Nombre = ? ORDER BY ID DESC LIMIT 1', (nombre,))
    IDKit = cursor.fetchone()[0]

    print("Ahora definí los componentes del kit:")
    while True:
        IDProducto = int(input("ID del producto componente: "))
        cantidad_por_kit = int(input("Cantidad por kit: "))

        cursor.execute('''
            INSERT INTO KitProducto (IDKit, IDProducto, Cantidad)
            VALUES (?, ?, ?)
        ''', (IDKit, IDProducto, cantidad_por_kit))

        continuar = input("¿Agregar otro componente? (Si/No): ").lower()
        if continuar not in ["si", "s"]:
            break

    conn.commit()
    print(f"Kit '{nombre}' cargado con éxito.")

def VerStockProductos():
    print("\n--- STOCK DE PRODUCTOS ---")
    cursor.execute('''
        SELECT ID, Nombre, Familia, Caracteristica, Precio, CantStock
        FROM Producto
        ORDER BY Nombre
    ''')
    productos = cursor.fetchall()

    if not productos:
        print("No hay productos cargados.")
        return

    for p in productos:
        print(f'''
    ------------------------------------------------------------
    | ID: {p[0]} | {p[1]} | Familia: {p[2]} | {p[3]} | Precio: ${p[4]:.2f} | Stock: {p[5]} |
    ------------------------------------------------------------
        ''')

def VerStockKits():
    print("\n--- KITS DEFINIDOS ---")
    cursor.execute('''
        SELECT k.ID, k.Nombre, k.Precio
        FROM Kit k
        ORDER BY k.Nombre
    ''')
    kits = cursor.fetchall()

    if not kits:
        print("No hay kits definidos.")
        return

    for k in kits:
        print(f"\nKit ID: {k[0]} | Nombre: {k[1]} | Precio: ${k[2]:.2f}")
        print("Componentes:")
        cursor.execute('''
            SELECT p.Nombre, kp.Cantidad
            FROM KitProducto kp
            JOIN Producto p ON kp.IDProducto = p.ID
            WHERE kp.IDKit = ?
        ''', (k[0],))
        componentes = cursor.fetchall()
        for nombre, cantidad in componentes:
            print(f"  - {nombre} x{cantidad}")

def ReporteEscasezStock(umbral=5):
    print(f"\n--- REPORTE DE ESCASEZ DE STOCK (umbral: {umbral}) ---")
    cursor.execute('''
        SELECT ID, Nombre, Familia, Caracteristica, CantStock
        FROM Producto
        WHERE CantStock < ?
        ORDER BY CantStock ASC
    ''', (umbral,))
    productos = cursor.fetchall()

    if not productos:
        print("No hay productos con stock bajo.")
        return

    for p in productos:
        print(f'''
    --------------------------------------------------------
    | ID: {p[0]} | {p[1]} | Familia: {p[2]} | {p[3]} | Stock actual: {p[4]} unidades |
    --------------------------------------------------------
        ''')

def PedidoProducto():
    cursor.execute('SELECT ID, Nombre, Familia, Caracteristica, Precio FROM Producto')
    productos = cursor.fetchall()

    if not productos:
        print("No hay productos en stock")
        return

    for producto in productos:
        print(f'''
    -------------------------------------------------------------------------------------
    | ID: {producto[0]} | Producto: {producto[1]} | Familia: {producto[2]} | Caracteristica: {producto[3]} | Precio: {producto[4]} |
    -------------------------------------------------------------------------------------
    ''')

    ans = input("¿Está usted registrado en BlackIron? (Si/No) ").lower()
    if ans == "si":
        NumUsuario = Login()
    else:
        NumUsuario = Registrar()

    Carrito = []
    Total = 0
    continuar = "Si"

    while continuar.lower() in ["si", "s"]:
        try:
            prod = int(input("Ingrese el número del producto a comprar: "))
            cantidad = int(input("¿Cuántos ejemplares desea comprar?: "))

            if not validar_stock_producto(prod, cantidad):
                print("No hay suficiente stock para este producto.")
                return

            cursor.execute('SELECT Precio, Nombre FROM Producto WHERE ID = ?', (prod,))
            resultado = cursor.fetchone()

            if not resultado:
                print("Producto no encontrado.")
                continuar = input("¿Desea agregar otro producto al carrito? (Si/No): ")
                continue

            Precio, NombreProducto = resultado

            NumTarjeta = input("Ingrese los números de su tarjeta: ")
            CVCoCVV = input("Ingrese la clave CVC/CVV: ")
            fecha_vencimiento = input("Ingrese la fecha de vencimiento: ")
            Titular = input("Ingrese el Titular como aparece en la tarjeta: ")

            if not procesar_tarjeta(NumTarjeta, CVCoCVV, fecha_vencimiento, Titular):
                continue

            try:
                cursor.execute('''
                    INSERT INTO Pedido (Producto, NumUsuario, Precio, Cantidad, NumTarjeta)
                    VALUES (?, ?, ?, ?, ?)
                ''', (NombreProducto, NumUsuario, Precio, cantidad, NumTarjeta))

                conn.commit()

                IDPedido = obtener_id_pedido("Pedido", "Producto", NombreProducto, NumUsuario)

                registrar_detalle_pedido_producto(IDPedido, prod, cantidad)
                actualizar_stock_producto(prod, cantidad)
                facturar_producto(IDPedido, NumUsuario)

                Total += Precio * cantidad
                agregar_al_carrito(Carrito, IDPedido, "Producto", NombreProducto, cantidad, Precio)

                print("Producto agregado al carrito correctamente.")

            except Exception as e:
                conn.rollback()
                print("Error al procesar el pedido:", e)

        except ValueError:
            print("Entrada inválida. Intente nuevamente.")

        continuar = input("¿Desea agregar otro producto al carrito? (Si/No): ")

    mostrar_resumen_carrito(Carrito)

    

    
                
def PedidoKit():
    cursor.execute('SELECT * FROM Kit')
    kits = cursor.fetchall()

    if not kits:
        print("No hay kits en stock")
        return

    for kit in kits:
        print(f'''
    -------------------------------------------------------------------------------------
    | ID: {kit[0]} | Producto1: {kit[1]} | Producto2: {kit[2]} |
    -------------------------------------------------------------------------------------
    ''')

    ans = input("¿Está usted registrado en BlackIron? (Si/No) ").lower()
    if ans == "si":
        NumUsuario = Login()
    else:
        NumUsuario = Registrar()

    Carrito = []
    Total = 0
    continuar = "Si"

    while continuar.lower() in ["si", "s"]:
        try:
            kit_id = int(input("Ingrese el número del kit a comprar: "))
            cantidad = int(input("¿Cuántos ejemplares desea comprar?: "))

            cursor.execute('SELECT IDProducto, Cantidad FROM KitProducto WHERE IDKit = ?', (kit_id,))
            componentes = cursor.fetchall()

            cursor.execute('SELECT Precio, Nombre FROM Kit WHERE ID = ?', (kit_id,))
            resultado = cursor.fetchone()

            if not resultado:
                print("Kit no encontrado.")
                continuar = input("¿Desea agregar otro kit al carrito? (Si/No): ")
                continue

            Precio, NombreKit = resultado

            NumTarjeta = input("Ingrese los números de su tarjeta: ")
            CVCoCVV = input("Ingrese la clave CVC/CVV: ")
            fecha_vencimiento = input("Ingrese la fecha de vencimiento: ")
            Titular = input("Ingrese el Titular como aparece en la tarjeta: ")

            if not procesar_tarjeta(NumTarjeta, CVCoCVV, fecha_vencimiento, Titular):
                continue

            try:
                cursor.execute('''
                    INSERT INTO PedidoKITS (IDKit, NumUsuario, Precio, Cantidad, NumTarjeta)
                    VALUES (?, ?, ?, ?, ?)
                ''', (kit_id, NumUsuario, Precio, cantidad, NumTarjeta))

                conn.commit()

                IDPedido = obtener_id_pedido("PedidoKITS", "IDKit", kit_id, NumUsuario)

                registrar_detalle_pedido_kit(IDPedido, componentes, cantidad)
                actualizar_stock_kit(componentes, cantidad)
                facturar_kit(IDPedido, NumUsuario)

                Total += Precio * cantidad
                agregar_al_carrito(Carrito, IDPedido, "Kit", NombreKit, cantidad, Precio)

                print("Kit agregado al carrito correctamente.")

            except Exception as e:
                conn.rollback()
                print("Error al procesar el pedido:", e)

        except ValueError:
            print("Entrada inválida. Intente nuevamente.")

        continuar = input("¿Desea agregar otro kit al carrito? (Si/No): ")

    mostrar_resumen_carrito(Carrito)


def DevolverProducto():
    NumUsuario = Login()
    if NumUsuario is None:
        return

    cursor.execute('''
        SELECT p.IDPedido, p.Producto, p.Cantidad, p.Precio
        FROM Pedido p
        WHERE p.NumUsuario = ?
    ''', (NumUsuario,))
    pedidos = cursor.fetchall()

    if not pedidos:
        print("No hay pedidos de productos registrados para devolución.")
        return

    for p in pedidos:
        print(f"IDPedido: {p[0]} | Producto: {p[1]} | Cantidad comprada: {p[2]} | Precio unitario: ${p[3]}")

    try:
        IDPedido = int(input("Ingrese el ID del pedido de producto a devolver: "))
        cantidad_devolver = int(input("¿Cuántos productos desea devolver?: "))
        motivo = input("Motivo de la devolución: ")

        cursor.execute('SELECT IDProducto, Cantidad FROM DetallePedidoProducto WHERE IDPedido = ?', (IDPedido,))
        resultado = cursor.fetchone()

        if not resultado:
            print("Pedido no válido o sin detalle registrado.")
            return

        IDProducto, cantidad_comprada = resultado

        if cantidad_devolver > cantidad_comprada:
            print("No puede devolver más productos de los que compró.")
            return

        cursor.execute('''
            INSERT INTO Devolucion (IDPedido, Tipo, Fecha, Cantidad, Motivo)
            VALUES (?, 'Producto', datetime('now'), ?, ?)
        ''', (IDPedido, cantidad_devolver, motivo))

        cursor.execute('''
            UPDATE Producto SET CantStock = CantStock + ? WHERE ID = ?
        ''', (cantidad_devolver, IDProducto))

        conn.commit()
        print("Devolución de producto registrada correctamente.")

    except Exception as e:
        conn.rollback()
        print("Error al procesar la devolución:", e)
    
def DevolverKit():
    NumUsuario = Login()
    if NumUsuario is None:
        return

    cursor.execute('''
        SELECT pk.IDPedido, k.Nombre, pk.Cantidad, pk.Precio
        FROM PedidoKITS pk
        JOIN Kit k ON pk.IDKit = k.ID
        WHERE pk.NumUsuario = ?
    ''', (NumUsuario,))
    pedidos = cursor.fetchall()

    if not pedidos:
        print("No hay pedidos de kits registrados para devolución.")
        return

    for p in pedidos:
        print(f"IDPedido: {p[0]} | Kit: {p[1]} | Cantidad comprada: {p[2]} | Precio unitario: ${p[3]}")

    try:
        IDPedido = int(input("Ingrese el ID del pedido de kit a devolver: "))
        cantidad_devolver = int(input("¿Cuántos kits desea devolver?: "))
        motivo = input("Motivo de la devolución: ")

        cursor.execute('SELECT IDKit, Cantidad FROM PedidoKITS WHERE IDPedido = ? AND NumUsuario = ?', (IDPedido, NumUsuario))
        resultado = cursor.fetchone()

        if not resultado:
            print("Pedido no válido.")
            return

        IDKit, cantidad_comprada = resultado

        if cantidad_devolver > cantidad_comprada:
            print("No puede devolver más kits de los que compró.")
            return

        cursor.execute('SELECT IDProducto, Cantidad FROM KitProducto WHERE IDKit = ?', (IDKit,))
        componentes = cursor.fetchall()

        cursor.execute('''
            INSERT INTO Devolucion (IDPedido, Tipo, Fecha, Cantidad, Motivo)
            VALUES (?, 'Kit', datetime('now'), ?, ?)
        ''', (IDPedido, cantidad_devolver, motivo))

        for IDProducto, cantidad_por_kit in componentes:
            cantidad_total = cantidad_por_kit * cantidad_devolver
            cursor.execute('''
                UPDATE Producto SET CantStock = CantStock + ? WHERE ID = ?
            ''', (cantidad_total, IDProducto))

        conn.commit()
        print("Devolución de kit registrada correctamente.")

    except Exception as e:
        conn.rollback()
        print("Error al procesar la devolución:", e)

def menu_principal():
    while True:
        print("""
        -------------------------------------
        |         BLACKIRON SYSTEM          |
        -------------------------------------
        1. Iniciar sesión como usuario
        2. Registrar nuevo usuario
        3. Iniciar sesión como administrador
        4. Registrar nuevo administrador
        5. Salir
        """)
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            idUsuario = Login()
            if idUsuario:
                menu_usuario(idUsuario)
        elif opcion == "2":
            idUsuario = Registrar()
            if idUsuario:
                menu_usuario(idUsuario)
        elif opcion == "3":
            admin = input("Usuario administrador: ")
            contraseña = input("Contraseña: ")
            resultado = login_admin(admin, contraseña, db_path="BlackIron.db")
            if "exitoso" in resultado:
                print(resultado)
                menu_admin()
            else:
                print("Acceso denegado.")
        elif opcion == "4":
            registrar_admin_seguro()
        elif opcion == "5":
            print("Gracias por usar BlackIron. ¡Hasta pronto!")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

def menu_usuario(idUsuario):
    while True:
        print(f"""
        -------------------------------------
        |     MENÚ DE USUARIO #{idUsuario}     |
        -------------------------------------
        1. Realizar pedido de producto
        2. Realizar pedido de kit
        3. Devolver producto
        4. Devolver kit
        5. Ver stock disponible
        6. Ver kits disponibles
        7. Ver reporte de escasez
        8. Volver al menú principal
        """)
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            PedidoProducto()
        elif opcion == "2":
            PedidoKit()
        elif opcion == "3":
            DevolverProducto()
        elif opcion == "4":
            DevolverKit()
        elif opcion == "5":
            VerStockProductos()
        elif opcion == "6":
            VerStockKits()
        elif opcion == "7":
            ReporteEscasezStock()
        elif opcion == "8":
            break
        else:
            print("Opción inválida.")

def menu_admin():
    while True:
        print("""
        -------------------------------------
        |       MENÚ DE ADMINISTRADOR       |
        -------------------------------------
        1. Cargar nuevo producto
        2. Cargar nuevo kit
        3. Ver stock de productos
        4. Ver kits definidos
        5. Ver reporte de escasez
        6. Volver al menú principal
        """)
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            CargarProducto()
        elif opcion == "2":
            CargarKit()
        elif opcion == "3":
            VerStockProductos()
        elif opcion == "4":
            VerStockKits()
        elif opcion == "5":
            ReporteEscasezStock()
        elif opcion == "6":
            break
        else:
            print("Opción inválida.")

menu_principal()

