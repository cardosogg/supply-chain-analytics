import logging
import os


def setup_logger(name="doghouse_logger"):
  # Cria a pasta de logs se não existir
  log_dir = "logs"
  os.makedirs(log_dir, exist_ok=True)
  log_file = os.path.join(log_dir, "pipeline.log")

  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)

  # Evita duplicidade de handlers caso o logger seja chamado várias vezes
  if not logger.handlers:
    # Handler para arquivo (grava histórico detalhado)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Handler para o console (exibe no terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formato padrão corporativo: [Data/Hora] - [Nível] - [Mensagem]
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

  return logger