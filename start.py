import uvicorn
from neomodel import config as neomodel_config
import config
from utils.log import get_custom_logger

logger = get_custom_logger("SERVER")

neomodel_config.DATABASE_URL = config.NEO4J_DB

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run("server:app", port=config.HTTP_PORT, host="0.0.0.0", reload=False)
    logger.info("Server running...")
