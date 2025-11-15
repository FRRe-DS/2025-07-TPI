# **📘 Guía Rápida: Base de Datos y Entorno Docker**

Esta guía explica cómo levantar el proyecto y la base de datos PostgreSQL en tu computadora local utilizando Docker.

### **1\. Requisitos Previos**

* Tener instalado **Docker Desktop** (y que esté abierto/corriendo).  
* Tener **Git** instalado.

### **2\. Configuración Inicial (Solo la primera vez)**

Como las contraseñas no se suben a Git por seguridad, cada uno debe crear su propio archivo de configuración.

1. Crea un archivo llamado `.env` en la carpeta raíz del proyecto (al lado de `docker-compose.yml`).  
2. Copia y pega el siguiente contenido dentro:

Fragmento de código  
\# Configuración de Base de Datos  
DB\_NAME=portal\_db  
DB\_USER=portal\_user  
DB\_PASS=portal\_password  
DB\_HOST=db  
DB\_PORT=5432

**Nota:** `DB_HOST=db` es vital para que Docker funcione. Si corres Django fuera de Docker, cambia eso por `127.0.0.1`.

### **3\. Levantar el Proyecto**

Abre la terminal en la carpeta del proyecto y ejecuta:

Bash  
docker-compose up \-d \--build

* Esto descarga PostgreSQL, instala las librerías de Python y levanta el servidor.  
* Espera a que termine. Si todo salió bien, verás los contenedores corriendo en Docker Desktop.

### **4\. Preparar la Base de Datos (¡Importante\!)**

Cuando descargas el proyecto, **la base de datos viene vacía** (sin tablas). Debes ejecutar estos comandos una sola vez para crear la estructura:

**A. Crear las tablas (Migraciones):**

Bash  
docker-compose exec web python manage.py migrate

**B. Crear un usuario administrador (Para entrar al panel):**

Bash  
docker-compose exec web python manage.py createsuperuser

*(Sigue las instrucciones para poner usuario y contraseña)*.

### **5\. ¿Cómo trabajar día a día?**

* **Para iniciar todo:** `docker-compose up -d`  
* **Para detener todo:** `docker-compose down`  
* **Si instalaste una librería nueva:** `docker-compose up -d --build`  
* **Si hiciste cambios en los modelos (BD):**  
  1. `docker-compose exec web python manage.py makemigrations`  
  2. `docker-compose exec web python manage.py migrate`

