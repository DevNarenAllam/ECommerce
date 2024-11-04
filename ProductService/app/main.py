from fastapi import FastAPI
from routers import product_router, product_lines_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()

app.include_router(product_router)
app.include_router(product_lines_router)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Redirect root URL to /docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
