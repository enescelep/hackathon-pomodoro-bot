import json
import discord
import requests
from discord.ext import commands
from time import sleep

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
token = "" # Kendi token'inizi giriniz :)

#Her mola'da özlü ses buluyor. Bulduğu fonksiyon burada
def get_quote(get=requests.get("https://zenquotes.io/api/random")):
    response = get
    json_data = json.loads(response.text)
    quote = [json_data[0]['q'], json_data[0]['a']]
    return quote

#Yardım komutu, bilgi amaçlı eklendi.
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="Pomodoro Yardım", description="Pomodoro Komutu Hakkında Bilgi")  # ,color=Hex code
    embed.add_field(name="!pomodoro [süre(dakika)] [bildirim süresi(saniye)] [seans sayısı]",
                    value="Örnek kullanım: !pomodoro 15 10 3 | 15 dakika, 10 saniyede bir bildirim, 3 seans")
    await ctx.send(embed=embed)


@bot.command()
async def pomodoro(ctx, sure: int, bildirim: int, seansSayisi: int):
    if sure <= 0 or bildirim <= 0 or seansSayisi <= 0:
        await ctx.send(f"""```{ctx.message.author.name} girilen bütün değerler 0'dan büyük girilmelidir 😡```""")
    else:
        mola_sayisi = seansSayisi - 1
        # Seans sayısı kadar çalışıyor
        baslangic = await ctx.send("""```yaml\nPomodoro başlamak üzere ✍🏻```""")
        mesaj = await ctx.send(
            f"""```yaml\nPomodoro Bilgisi:\nÇalışma süresi: {sure} dakika\nBildirim süresi: {bildirim} saniye\nSeans sayısı: {seansSayisi}```""")

        quote = get_quote()[0]
        author = get_quote()[1]
        # Ünlü kişilerden alıntılar (motivasyon amaçlı)
        inspire = await ctx.send(f'''```{quote} - {author}```''')

        for i in range(5, -1, -1):
            sleep(1)
            await baslangic.edit(content=f"""```yaml\nPomodoro başlamasına kalan süre: {i} ```""")

        await baslangic.edit(content=f"""```Pomodoro başladı, iyi çalışmalar 👌🏻```""")
        sleep(2)

        while seansSayisi > 0:
            saniye_sure = int(sure * 60)

            # Pomodoro sayacı
            while saniye_sure > 0:
                dakika = int(saniye_sure / 60)
                saniye = int(saniye_sure % 60)

                # Yazılması için dakika ve saniye kontrolü
                if saniye > 0 and dakika > 0:
                    await mesaj.edit(content=f'''```yaml\nPomodoro: {dakika} dakika, {saniye} saniye kaldı.```''')
                elif saniye <= 0:
                    await mesaj.edit(content=f'''```yaml\nPomodoro: {dakika} dakika kaldı.```''')
                elif dakika <= 0:
                    await mesaj.edit(content=f'''```yaml\nPomodoro: {saniye} saniye kaldı.```''')

                sleep(bildirim)
                saniye_sure -= bildirim

                if saniye_sure <= 0 and mola_sayisi > 0:
                    await mesaj.edit(content=f"""```Süre bitti, şimdi 5 dakikalık mola zamanı```""")
                    sleep(5)

            # Mola sayacı
            mola_suresi = 5
            mola_suresi_saniye = mola_suresi * 60
            while mola_suresi_saniye > 0 and mola_sayisi > 0:

                dakika = int(mola_suresi_saniye / 60)
                saniye = int(mola_suresi_saniye % 60)

                # Yazılması için dakika ve saniye kontrolü

                if saniye > 0 and dakika > 0:
                    await mesaj.edit(content=f'''```yaml\nMola: {dakika} dakika {saniye} saniye kaldı.```''')
                elif dakika <= 0:
                    await mesaj.edit(content=f'''```yaml\nMola: {saniye} saniye kaldı.```''')
                elif saniye <= 0:
                    await mesaj.edit(content=f'''```yaml\nMola: {dakika} dakika kaldı.```''')

                # Ünlü kişilerden alıntılar (motivasyon amaçlı)
                await inspire.edit(content=f'''```{quote} - {author}```''')
                if mola_suresi_saniye <= 0:
                    await mesaj.edit(content=f"""```Mola bitti, {sure} dakikalık çalışma zamanı```""")
                    sleep(5)

                sleep(bildirim)
                mola_suresi_saniye -= bildirim
            mola_sayisi -= 1
            seansSayisi -= 1
        await inspire.delete()
        await baslangic.delete()
        await mesaj.edit(content=f"""```Bütün seanslar bitti, tebrikler 🎉```""")


@bot.event
# Pomodoro adlı bir yazı kanalı oluşturun. Kanalın ID'sini pomodoro_channel'daki bot.get_channel() içine yapıştırın.
# Bot sunucuya eklendiğinde bot hakkında ufak bir bilgi veriyor.
async def on_guild_join(guild):
    pomodoro_channel = bot.get_channel()  # Oluşturduğunuz ID'yi buraya kopyalayın.
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(title="Pomodoro Bot", description="Merhabalar ben Pomodoro Bot👋", color=0x00ffd2)
            embed.add_field(name="Kullanabileceğin komutlar:", value="!yardim ve !pomodoro", inline=False)
            embed.add_field(name="Aklında bir soru mu var?",
                            value="Komutları nasıl kullanabileceğini öğrenmek istiyorsan !yardim yazarak bilgi edinebilirsin🤗",
                            inline=False)
            embed.set_footer(text=f"Bot yapımcıları: Enes05 ve Bt238")
            embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6XuZyU12-y0ofUswNOI_XTeb9qNNwz7l8J3TKZmGJKeROIdnMnUpnd0Sr9St2qidk3-s&usqp=CAU")
            await pomodoro_channel.send(embed=embed)
        break


@bot.event
async def on_ready():
    # Easter Egg :)
    await bot.change_presence(
        activity=discord.Streaming(name="Testing Pomodoro Bot", url="https://www.youtube.com/watch?v=b48HJQL5Hoo"))
    print("{0.user} olarak giriş yapıldı".format(bot))


bot.run(token)
