from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.backend.api.route import router as eco_router

# ✅ CREATE APP FIRST
app = FastAPI()

# ✅ ADD CORS (FOR FRONTEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTER ROUTES
app.include_router(eco_router)


# OPTIONAL: root endpoint
@app.get("/")
def root():
    return {"message": "EcoNav AI running 🚀"}