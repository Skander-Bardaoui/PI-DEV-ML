<p align="center">
  <img src="docs/banner.svg" width="100%" alt="NovaEntra ML banner" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=7C3AED&center=true&vCenter=true&width=760&lines=Predict+what+to+buy+next;FastAPI+%2B+scikit-learn;Trends%2C+seasonality%2C+confidence" alt="Typing tagline" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/languages/top/Skander-Bardaoui/PI-DEV-ML?style=flat-square&color=7C3AED" alt="" />
  <img src="https://img.shields.io/github/stars/Skander-Bardaoui/PI-DEV-ML?style=flat-square&color=7C3AED" alt="" />
  <img src="https://img.shields.io/github/last-commit/Skander-Bardaoui/PI-DEV-ML?style=flat-square&color=A78BFA" alt="" />
  <img src="https://img.shields.io/badge/status-Active-7C3AED?style=flat-square" alt="" />
</p>

## Overview

A machine-learning microservice that forecasts future purchasing needs from order history. It predicts order quantity and the best order date, returns a confidence score, detects trend and seasonality, and produces recommendations with urgency levels. Exposed as a documented FastAPI REST service.

## Highlights

- Order-quantity and optimal-order-date prediction
- Confidence score from 0 to 100% for every prediction
- Trend and seasonality detection
- Urgency-aware purchasing recommendations
- Batch predictions for multiple products
- Docker image, Kubernetes manifests and Render deployment guides

## Tech stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,docker,kubernetes,git,githubactions&theme=dark&perline=8" alt="Tech stack" />
</p>

## Getting started

**Prerequisites:** Python 3.11+ and a trained model bundle.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --port 8001 --reload
```

## Project structure

```text
app/        FastAPI application and ML pipelines
tests/      unit tests
k8s/        deployment manifests
render.yaml deployment blueprint
```

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:7C3AED,100:0A0A0C&height=110&section=footer" alt="footer" width="100%" />
</p>

<p align="center">
  Built by <a href="https://github.com/Skander-Bardaoui"><b>Skander Bardaoui</b></a> ·
  <a href="https://skander-bardaoui.netlify.app/">Portfolio</a> ·
  <a href="https://github.com/Skander-Bardaoui?tab=repositories">All repositories</a>
</p>
