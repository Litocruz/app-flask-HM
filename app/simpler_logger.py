import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """
    Configura un logger para que escriba en la consola y en un archivo.
    """
    # 1. Crear el directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. Configurar el formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 3. Crear el handler para el archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # 4. Crear el handler para la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 5. Crear el logger y añadir los handlers
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Uso en la aplicación:
# from app.logger import setup_logger
# logger = setup_logger('mi_app_logger', 'logs/mi_app.log')
# logger.info('Este es un mensaje de información.')