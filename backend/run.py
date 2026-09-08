import os
import uvicorn
from backend.app.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
