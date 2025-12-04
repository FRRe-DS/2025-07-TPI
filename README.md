# 2025-07-TPI
# Trabajo Práctico Integrador - Grupo 07

<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Estado](https://img.shields.io/badge/Estado-Finalizado-success?style=for-the-badge)
![UTN](https://img.shields.io/badge/UTN-FRRe-blue?style=for-the-badge)

**Sistema Modular de Gestión de Stock y Portal de Ventas** Desarrollo de Software 2025

[Reportar Bug](https://github.com/FRRe-DS/2025-07-TPI/issues) · [Solicitar Feature](https://github.com/FRRe-DS/2025-07-TPI/issues)

</div>

---

## 📑 Tabla de Contenidos

1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Arquitectura del Sistema](#-arquitectura-del-sistema)
3. [Estructura del Repositorio](#-estructura-del-repositorio)
4. [Instalación y Despliegue](#-instalación-y-despliegue)
5. [Módulos y Funcionalidades](#-módulos-y-funcionalidades)
6. [Tecnologías](#-tecnologías)

---

## 📖 Descripción del Proyecto

Este proyecto implementa un sistema integral para la administración de inventarios y la gestión de pedidos de clientes. Diseñado bajo un enfoque modular, el sistema permite desacoplar la lógica de negocio de la interfaz de usuario y la persistencia de datos.

El objetivo principal es simular un entorno real de e-commerce donde interactúan múltiples componentes: un portal de cara al cliente, un validador de reglas de negocio y un gestor de almacén.

---

## 🏗 Arquitectura del Sistema

El diseño sigue una arquitectura en capas para asegurar la escalabilidad y mantenibilidad del código.

Archivo,Descripción
main.py,Punto de entrada principal. Inicializa el sistema completo.
portal.py,Interfaz de usuario para simulación de compras.
logica.py,Núcleo del sistema. Contiene las clases y funciones de validación.
Stock.py,Módulo de administración de base de datos de productos.
portalmain.py,Script para pruebas aisladas del módulo de ventas.
logicamain.py,Script para pruebas unitarias de la lógica de negocio.

##🚀 Instalación y Despliegue Ofrecemos dos formas de ejecutar el proyecto: localmente con Python o mediante Docker.Opción A: Ejecución con Docker (Recomendada)Asegúrate de tener Docker instalado y corriendo.Construir la imagen:Bashcd "Trabajo TP"
docker build -t grupo07-tpi .
Correr el contenedor:Bashdocker run -it --rm grupo07-tpi
Opción B: Ejecución Local (Python)Clonar el repositorio:Bashgit clone -b Tercer-Entrega [https://github.com/FRRe-DS/2025-07-TPI.git](https://github.com/FRRe-DS/2025-07-TPI.git)
cd 2025-07-TPI
Crear entorno virtual:Bashpython -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
Ejecutar:Bashpython main.py
🛠 TecnologíasCategoríaTecnologíaUsoLenguajeLógica de backend y scripts.InfraestructuraContainerización y entorno reproducible.Control de VersionesGestión del código fuente.
🧩 Módulos y Funcionalidades
🛒 Portal de Ventas
Permite a los usuarios visualizar el catálogo de productos disponibles y realizar pedidos. Se comunica exclusivamente con la capa lógica para confirmar transacciones.

📦 Gestión de Stock
Módulo encargado de mantener la integridad del inventario. Sus funciones incluyen:

Control de stock mínimo.

Actualización de cantidades post-venta.

Gestión de precios.

⚙️ Lógica de Negocio
Actúa como intermediario (Middleware) asegurando que:

No se vendan productos sin stock.

Los precios sean correctos.

Las transacciones se registren adecuadamente.

🛠 Tecnologías
El proyecto ha sido construido utilizando:

Python: Lenguaje principal para backend y lógica.

Git: Control de versiones.



<div align="center"> <sub>Desarrollo de Software - TPI 2025</sub> </div>
