import os
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

token = os.getenv("GITHUB_TOKEN")
print("Token:", token)
if token:
    logger.info(f"GITHUB_TOKEN loaded, starts with: {token[:6]}... and length: {len(token)}")
else:
    logger.error("GITHUB_TOKEN not set in environment")
