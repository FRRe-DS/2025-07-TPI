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
4. [Instalación y Puesta en Marcha](#-instalación-y-puesta-en-marcha)
5. [Módulos y Funcionalidades](#-módulos-y-funcionalidades)
6. [Tecnologías](#-tecnologías)
7. [Autores](#-autores)

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

Archivo,Descripción
main.py,Punto de entrada principal. Inicializa el sistema completo.
portal.py,Interfaz de usuario para simulación de compras.
logica.py,Núcleo del sistema. Contiene las clases y funciones de validación.
Stock.py,Módulo de administración de base de datos de productos.
portalmain.py,Script para pruebas aisladas del módulo de ventas.
logicamain.py,Script para pruebas unitarias de la lógica de negocio.

<div align="center"> <sub>Desarrollo de Software - TPI 2025</sub> </div>
