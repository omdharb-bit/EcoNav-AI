
# 🌱 EcoNav AI

**AI-powered environmental decision intelligence system for low-exposure route optimization**

---

## 🚀 Problem

Urban commuters unknowingly expose themselves to harmful air pollution (AQI) while choosing routes based only on time or distance.

---

## 💡 Solution

EcoNav AI recommends **health-aware routes** by combining:
- Real-time / simulated AQI data
- Route graph analysis
- Exposure scoring system
- AI-based decision policies

---

## ⚙️ How It Works

1. User inputs:
   - Source
   - Destination
   - Preference (fastest / cleanest)

2. System pipeline:
   - Generate routes (graph engine)
   - Enrich with AQI data
   - Compute exposure per route
   - Score routes using reward function
   - Select optimal route via agent

---

## 🧠 Architecture

- **env-core** → environment simulation (routes + AQI)
- **exposure-engine** → exposure calculation system
- **agent-engine** → decision-making logic
- **backend (FastAPI)** → orchestrates pipeline
- **frontend (Streamlit)** → user interface

---

## 🏗️ Tech Stack

- Python
- FastAPI
- Streamlit
- Docker
- Graph-based routing
- AI/ML-ready architecture

---

---

## 🔥 Key Features

- 🌿 Green route optimization  
- 🧪 Exposure scoring system  
- 🤖 AI-based decision engine  
- 📊 Simulation-ready environment  
- ⚡ Modular monorepo architecture  

---
## 📂 Project Structure

- apps/ → frontend, backend, simulator
- packages/ → env-core, exposure-engine, agent-engine
- infra/ → docker & deployment
- data/ → AQI datasets
---

## 🚀 Future Scope

- Real-time AQI API integration  
- Reinforcement Learning agent  
- City-wide pollution heatmaps  
- Personal exposure tracking  

---



---

## ⭐ Vision

> "Not just faster routes — smarter, healthier decisions."

