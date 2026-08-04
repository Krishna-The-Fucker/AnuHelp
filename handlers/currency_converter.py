# ============================================================
# 💱 CURRENCY CONVERTER UTILITIES (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "💱 ᴄᴜʀʀᴇɴᴄʏ"

__help__ = """
*💱 ᴄᴜʀʀᴇɴᴄʏ ᴄᴏɴᴠᴇʀᴛᴇʀ* — Instantly convert amounts between different world currencies using live exchange rates!

• `/convert [amount] [from_curr] [to_curr]` — Convert currency (e.g., `/convert 100 USD INR`)
• `/rates [currency]` — Check live exchange rates relative to major base currencies
"""

from pyrogram import filters
from pyrogram.types import Message
import aiohttp
import logging

def register_currency_system(app):

    # ============================================================
    # 💱 CONVERT CURRENCY (`/convert`)
    # ============================================================
    @app.on_message(filters.command("convert"))
    async def convert_currency_cmd(client, message: Message):
        args = message.command
        if len(args) < 4:
            return await message.reply(
                "⚠️ **Invalid format!**\n\n"
                "📌 **Usage:** `/convert [amount] [from] [to]`\n"
                "💡 **Example:** `/convert 50 USD INR`"
            )

        try:
            amount = float(args[1])
            from_curr = args[2].upper()
            to_curr = args[3].upper()
        except ValueError:
            return await message.reply("❌ **Invalid amount provided! Please specify a valid number.**")

        status_msg = await message.reply("💱 **Fetching live exchange rates and converting...**")

        try:
            # Using free open exchangerates API endpoint
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await status_msg.edit_text("❌ **Failed to fetch exchange rates. Check currency codes!**")
                    
                    data = await resp.json()
                    rates = data.get("rates", {})
                    
                    if to_curr not in rates:
                        return await status_msg.edit_text(f"❌ **Currency code `{to_curr}` not found or unsupported!**")

                    rate = rates[to_curr]
                    converted_amount = amount * rate

                    await status_msg.edit_text(
                        f"💱 **Currency Conversion Result**\n\n"
                        f"🔹 **From:** `{amount:,.2f} {from_curr}`\n"
                        f"🔸 **To:** `{converted_amount:,.2f} {to_curr}`\n"
                        f"📈 **Exchange Rate:** `1 {from_curr} = {rate:,.4f} {to_curr}`"
                    )

        except Exception as e:
            logging.error(f"[Currency Convert Error]: {e}")
            await status_msg.edit_text(f"❌ **An error occurred during conversion:** `{str(e)}`")

    # ============================================================
    # 📈 CHECK RATES (`/rates`)
    # ============================================================
    @app.on_message(filters.command("rates"))
    async def check_rates_cmd(client, message: Message):
        args = message.command
        base = args[1].upper() if len(args) > 1 else "USD"

        status_msg = await message.reply(f"📈 **Fetching live exchange rates for base `{base}`...**")

        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await status_msg.edit_text("❌ **Invalid base currency code or API error.**")
                    
                    data = await resp.json()
                    rates = data.get("rates", {})
                    
                    # Pick major popular currencies for quick display
                    popular = ["INR", "EUR", "GBP", "CAD", "AUD", "JPY", "AED"]
                    rate_lines = [f"• `1 {base} = {rates.get(cur):,.4f} {cur}`" for cur in popular if cur in rates]

                    output = (
                        f"📊 **Live Exchange Rates (Base: {base})**\n\n" +
                        "\n".join(rate_lines) if rate_lines else "❌ **No rates available.**"
                    )

                    await status_msg.edit_text(output)

        except Exception as e:
            logging.error(f"[Rates Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to fetch rates:** `{str(e)}`")
