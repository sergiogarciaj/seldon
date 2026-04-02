# Proyecto BigQuery - Guía de Inicio

Este proyecto permite conectar con BigQuery utilizando la configuración y los métodos probados en el repositorio `/radar/`.

## Instrucciones de Inicio

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Autenticación**:
   Ejecuta el script de configuración para generar tus credenciales locales:
   ```bash
   python auth_setup.py
   ```
   Sigue las instrucciones en pantalla para autorizar el acceso en tu navegador. Esto creará el archivo `credentials.json`.

3. **Ejecutar el proyecto**:
   Prueba la conexión y obtén datos ejecutando:
   ```bash
   python main.py
   ```

## Estructura del Proyecto

- `main.py`: Script principal con la lógica de conexión y un ejemplo de consulta.
- `auth_setup.py`: Script para configurar la autenticación de Google Cloud.
- `requirements.txt`: Lista de librerías de Python necesarias.
- `credentials.json`: (Generado tras correr auth_setup) Almacena tus credenciales de acceso.

## Configuración de Datos
- **Proyecto GCP**: `data-exp-contactcenter`
- **Dataset**: `100x100`
- **Tabla Principal**: `third_calculated`
