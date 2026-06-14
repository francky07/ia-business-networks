#!/usr/bin/env python3
import asyncio, subprocess

async def main():
    print("💰 Département ventes – PayPal (lien direct)")
    logfile = open("ventes.log", "a")
    while True:
# # # # # #         subprocess.run(["python", "sell_emails_paypal.py"], stdout=logfile, stderr=subprocess.STDOUT)  # PayPal désactivé par diagnostic  # PayPal désactivé par diagnostic  # PayPal désactivé  # PayPal désactivé
        logfile.flush()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
