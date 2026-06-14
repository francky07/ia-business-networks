#!/usr/bin/env python3
import asyncio, random, json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime

class DirectorAgent:
    def __init__(self, brain_logger=None):
        self.logger = brain_logger
        self.contrats_en_cours = []
        self.pipeline = []

    def log(self, msg):
        if self.logger:
            self.logger(msg)
        else:
            print(f"[{datetime.now()}] {msg}")

    async def prospecter(self):
        """Cherche des offres sur une plateforme (ex: Freelancer.com via RSS)"""
        self.log("🔍 Recherche de missions...")
        # Simulé : à remplacer par appel API ou scraping réel
        offres_simulees = [
            {"titre": "Création d'un bot Telegram", "budget": 300, "contact_email": "client1@mail.com", "score": 75},
            {"titre": "Automatisation de trading crypto", "budget": 1500, "contact_email": "client2@mail.com", "score": 90}
        ]
        # Ici vous feriez un vrai scraping ou appel API
        return offres_simulees

    async def qualifier(self, offre):
        # Calcule un score basé sur budget et mots-clés
        score = 0
        if offre.get("budget", 0) > 200: score += 40
        if any(kw in offre.get("titre", "").lower() for kw in ["ia", "automatisation", "bot"]): score += 30
        score += random.randint(0, 30)
        offre["score"] = score
        return offre

    async def postuler(self, offre):
        if offre["score"] < 50:
            self.log(f"⏩ Offre ignorée (score {offre['score']}) : {offre['titre']}")
            return
        self.log(f"📧 Candidature à {offre['titre']} (budget {offre['budget']} USD) - score {offre['score']}")
        # Envoyer email de proposition (à connecter à votre SMTP)
        # Exemple : await self.envoyer_email(offre['contact_email'], "Proposition", "Notre IA peut réaliser...")
        self.pipeline.append(offre)

    async def run(self):
        self.log("🚀 Agent Directeur activé")
        while True:
            offres = await self.prospecter()
            for offre in offres:
                offre = await self.qualifier(offre)
                await self.postuler(offre)
            await asyncio.sleep(300)  # toutes les 5 minutes

if __name__ == "__main__":
    agent = DirectorAgent()
    asyncio.run(agent.run())
