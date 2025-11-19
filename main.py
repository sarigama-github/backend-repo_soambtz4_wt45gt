import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from database import create_document, get_documents, db

app = FastAPI(title="O'Plaisir API", description="Backend for O'Plaisir concept store")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr

class ProductFilter(BaseModel):
    tag: Optional[str] = None
    category: Optional[str] = None
    limit: Optional[int] = Field(default=8, ge=1, le=50)

@app.get("/")
def read_root():
    return {"message": "O'Plaisir API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Bienvenue sur l'API O'Plaisir"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "Unknown"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ------- Content Endpoints -------

@app.get("/api/occasions")
def get_occasions():
    return [
        {"key": "noel", "label": "Noël"},
        {"key": "ramadan", "label": "Ramadan"},
        {"key": "paques", "label": "Pâques"},
        {"key": "saintvalentin", "label": "Saint-Valentin"},
        {"key": "anniversaire", "label": "Anniversaires"},
        {"key": "mariage", "label": "Mariages & Naissances"},
    ]

@app.post("/api/newsletter/subscribe")
def subscribe_newsletter(payload: NewsletterSubscribeRequest):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        # ensure unique email
        existing = db["newslettersubscriber"].find_one({"email": payload.email})
        if existing:
            return {"status": "exists", "message": "Déjà inscrit"}
        create_document("newslettersubscriber", {"email": payload.email})
        return {"status": "ok", "message": "Merci pour votre inscription !"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/bestsellers")
def get_bestsellers(filter: ProductFilter):
    if db is None:
        # Return a tiny curated sample for preview if DB missing
        sample = [
            {
                "_id": "demo1",
                "title": "Panier Chocolat Signature",
                "price": 89.0,
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=1200&auto=format&fit=crop",
                "tag": "bestseller",
            },
            {
                "_id": "demo2",
                "title": "Coffret Méditerranéen Prestige",
                "price": 119.0,
                "image": "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?q=80&w=1200&auto=format&fit=crop",
                "tag": "bestseller",
            },
            {
                "_id": "demo3",
                "title": "Assortiment Découverte",
                "price": 59.0,
                "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop",
                "tag": "bestseller",
            },
        ]
        return sample[: filter.limit or 8]
    qry = {}
    if filter.tag:
        qry["tag"] = filter.tag
    if filter.category:
        qry["category"] = filter.category
    docs = get_documents("product", qry, limit=filter.limit)
    # Map images if missing
    for d in docs:
        d.setdefault("image", "https://images.unsplash.com/photo-1542838686-73ca0c37d0e3?q=80&w=1200&auto=format&fit=crop")
    return docs

@app.get("/api/testimonials")
def get_testimonials():
    if db is None:
        return [
            {"name": "Sofia", "message": "Des créations sublimes et un service impeccable.", "rating": 5},
            {"name": "Karim", "message": "Le panier Ramadan a fait sensation dans ma famille.", "rating": 5},
            {"name": "Lina", "message": "Personnalisation parfaite pour notre mariage.", "rating": 4},
        ]
    docs = get_documents("testimonial", {}, limit=12)
    return [{"name": d.get("name"), "message": d.get("message"), "rating": d.get("rating", 5)} for d in docs]

# Simple seed route (optional)
@app.post("/api/seed")
def seed():
    if db is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        # Insert a few products if none
        if db["product"].count_documents({}) == 0:
            items = [
                {"title": "Panier Chocolat Premium", "description": "Truffes et pralinés artisanaux", "price": 89.0, "category": "paniers", "tag": "bestseller", "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=1200&auto=format&fit=crop"},
                {"title": "Coffret Méditerranéen", "description": "Huile d'olive, nougat, miel", "price": 119.0, "category": "paniers", "tag": "bestseller", "image": "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?q=80&w=1200&auto=format&fit=crop"},
                {"title": "Panier Découverte", "description": "Sélection du chef", "price": 59.0, "category": "paniers", "tag": "nouveau", "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop"},
            ]
            for it in items:
                create_document("product", it)
        # Testimonials
        if db["testimonial"].count_documents({}) == 0:
            for t in [
                {"name": "Sofia", "message": "Des créations sublimes et un service impeccable.", "rating": 5},
                {"name": "Karim", "message": "Le panier Ramadan a fait sensation dans ma famille.", "rating": 5},
            ]:
                create_document("testimonial", t)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
