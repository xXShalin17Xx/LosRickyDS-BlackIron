CREATE DATABASE BlackIron;

USE BlackIron;

CREATE TABLE Usuario(
    NumUsuario INT PRIMARY KEY,
    Nombre VARCHAR(50),
    Apellido VARCHAR(50),
    Email VARCHAR(50)
);

CREATE TABLE Producto(
    GTIN INT PRIMARY KEY,
    Nombre VARCHAR(50),
    Familia VARCHAR(50),
    Caracteristica VARCHAR(50),
    Precio DECIMAL(10,2),
    CantStock INT 
);

CREATE TABLE Pedido(
    IDPedido INT PRIMARY KEY,
    NumUsuario INT,
    Producto VARCHAR(50),
    NombreUsu VARCHAR(50),
    ApellidoUsu VARCHAR(50),
    Tipo VARCHAR(10),
    Precio DECIMAL(10,2),
    FOREIGN KEY Producto references Producto(Nombre),
    FOREIGN KEY NumUsuario references Usuario(NumUsuario)
    FOREIGN KEY NombreUsu references Usuario(Nombre),
    FOREIGN KEY ApellidoUsu references Usuario(Apellido)
    
);

CREATE TABLE Facturacion(
    IDFactura INT PRIMARY KEY,
    IDPedido INT
    NombreUsu VARCHAR(50),
    ApellidoUsu VARCHAR(50),
    Tipo VARCHAR(10),
    PrecioBruto DECIMAL(10,2),
    PrecioNeto DECIMAL(10,2)
);

