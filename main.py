from src.pipeline.logging_setup import setup_logging
from loguru import logger
from pathlib import Path
import yaml

from config.config_models import PipelineConfig

def load_and_validate_config(yaml_path: Path, campaign_key: str) -> PipelineConfig:
    logger.info(f"Leyendo archivo de configurarion: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as file:
        raw_data = yaml.safe_load(file)
        

    if not isinstance(raw_data, dict) or campaign_key not in raw_data:
        raise KeyError(
            f"No se encontro la clave raiz '{campaign_key}' en el archivo Yaml"
        )

    config = PipelineConfig(**raw_data[campaign_key])
    logger.success(
        f"Configuracion '{campaign_key} validada correctamente. "
        f"Total columnas mapeadas: {len(config.sheet_name.columns)}"
    )
    return config

if __name__ == "__main__":

    path_yaml = Path("config/Popular_Castigo.yaml")

    pipeline = load_and_validate_config(path_yaml, "popular_castigo")
    print(pipeline)