# XScreenCapture v 1.0
 <img width="300" height="300" alt="1f2833" src="https://github.com/user-attachments/assets/cd6c5037-2d02-4be8-8a59-11ed8595af3d" /><br><img width="296" height="519" alt="dd" src="https://github.com/user-attachments/assets/d1fff267-0e7f-4745-b3e9-4e36527a7071" />


XVCapture es una herramienta de captura de pantalla y grabación de video ligera, potente y de código abierto, diseñada con un tema oscuro moderno ("Dark Tech"). Desarrollada íntegramente en Python, ofrece un rendimiento optimizado mediante hilos separados para video y audio.



<br><b>✨ Características Principales</b>
<br><b>Grabación de Video</b>

- Multi-Monitor: Selección del monitor de origen para grabaciones multi-pantalla.
- Audio Sincronizado: Grabación de audio del micrófono con corrección automática de sincronización.
- Control de Calidad: Tres modos de grabación: Alta (30 FPS), Media (20 FPS) y Baja (10 FPS).
- Contador en Tiempo Real: Temporizador visible durante la grabación.

Captura de Imagen

    Modos de Captura Flexibles:
        Pantalla Completa: Captura instantánea del monitor seleccionado.
        Selección de Área: Herramienta interactiva para dibujar un rectángulo y capturar una zona específica.
        Ventana Específica: Sistema inteligente "Clic para capturar". Al activar esta opción, simplemente haz clic sobre cualquier ventana abierta para capturarla automáticamente (el programa trae la ventana al frente para asegurar la visibilidad).
    Temporizador (Retardo): Opciones de cuenta regresiva de 3, 4 y 5 segundos antes de capturar.

Interfaz y Diseño

    Dark Mode Elegante: Paleta de colores profesional basada en tonos oscuros (#1f2833) y acentos cian (#66FCF1).
    Organizado por Pestañas: Interfaz limpia separando las herramientas de captura y la información "Acerca de".
    Splash Screen: Pantalla de inicio con efecto de desvanecimiento.

🛠️ Tecnologías Utilizadas

Este proyecto fue construido utilizando las siguientes librerías de Python:

    GUI: tkinter (Interfaz gráfica nativa).
    Captura de Pantalla: mss (Alto rendimiento).
    Procesamiento de Video/Imagen: OpenCV (cv2), Pillow (PIL).
    Manejo de Audio: sounddevice, wave, moviepy.
    Interacción con Windows: ctypes (Para selección de ventanas).

🚀 Instalación y Uso
Requisitos Previos

Asegúrate de tener Python 3.x instalado.
1. Clonar el Repositorio

git clone https://github.com/tu-usuario/xvcapture.gitcd xvcapture

 
2. Instalar Dependencias 

Crea un entorno virtual (opcional pero recomendado) e instala las librerías necesarias: 
bash
 
  
 
pip install opencv-python mss pillow sounddevice moviepy numpy
 
 
 
3. Ejecutar la Aplicación 

Para iniciar el programa en modo desarrollo: 
bash
 
  
 
python nombre_del_archivo.py
 
 
 
📦 Compilación a .EXE (Distribución) 

Para generar un archivo ejecutable portable (.exe) utilizando pyinstaller: 

    Instala PyInstaller:
    bash
     
      
     
    pip install pyinstaller
     
     
      
    Asegúrate de tener tu archivo de imagen (ej. 1f2833.png) en la misma carpeta que el script. 
    Ejecuta el siguiente comando: 


  
 
pyinstaller --noconsole --onefile --add-data "1f2833.png;." nombre_del_archivo.py
 
 
 

El ejecutable se encontrará en la carpeta dist/. 

👨‍💻 Autor y Créditos 

Desarrollado por: Rodolfo Hernández Baz - Pr@fEs0r X 

Si tienes alguna sugerencia o encuentras un error, no dudes en abrir un Issue en este repositorio. 
📜 Licencia 

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
``` 
