import discord
from discord.ext import commands
from discord import app_commands
from config import COLORS
from functions import get_timestamp, save_verification_message, get_verification_message


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def setup_verification(self):
        """Setup für das Verification System - wird vom starter.py aufgerufen"""
        try:
            # Registriere die VerificationView als persistent view
            self.bot.add_view(VerificationView())
            print("✅ VerificationView als persistent view registriert!")
            
            # Zeige die aktuelle Message ID an
            current_message_id = get_verification_message()
            if current_message_id:
                print(f"📝 Aktuelle Verification Message ID: {current_message_id}")
                
                # Versuche die Message zu fetchen und die View wiederherzustellen
                await self.restore_verification_message(current_message_id)
            else:
                print("⚠️ Keine Verification Message ID gespeichert!")
                
        except Exception as e:
            print(f"❌ Fehler beim Setup der VerificationView: {e}")

    async def restore_verification_message(self, message_id):
        """Stellt die Verification Message wieder her"""
        try:
            # Hole alle Guilds des Bots
            for guild in self.bot.guilds:
                # Suche in allen Channels nach der Message
                for channel in guild.text_channels:
                    try:
                        message = await channel.fetch_message(message_id)
                        if message:
                            print(f"✅ Verification Message gefunden in #{channel.name}")
                            
                            # Erstelle ein neues Embed falls nötig
                            embed = discord.Embed(
                                title="✅ Verifizierung",
                                description="Klicke auf den Button unten, um dich zu verifizieren.",
                                color=COLORS["green"],
                                timestamp=get_timestamp()
                            )
                            
                            # Erstelle die View
                            view = VerificationView()
                            
                            # Bearbeite die Message
                            await message.edit(embed=embed, view=view)
                            print(f"✅ Verification Message in #{channel.name} wiederhergestellt!")
                            return
                    except discord.NotFound:
                        continue
                    except Exception as e:
                        print(f"⚠️ Fehler beim Bearbeiten der Message in #{channel.name}: {e}")
                        continue
            
            print("⚠️ Verification Message konnte nicht gefunden werden!")
            
        except Exception as e:
            print(f"❌ Fehler beim Wiederherstellen der Verification Message: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Wird ausgeführt, wenn ein neues Mitglied dem Server beitritt"""
        embed = discord.Embed(
            title="Willkommen auf dem Server!",
            description=f"Willkommen {member.mention} auf {member.guild.name}!",
            color=COLORS["green"],
            timestamp=get_timestamp()
        )
        embed.set_author(name=f"{member.name} ist das neue Mitglied", icon_url="https://flimando.com/logo.png")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📋 Erste Schritte", value="• Lies die Regeln\n• Stelle dich vor\n• Hab Spaß!", inline=False)
        embed.set_footer(text=f"Mitglied #{len(member.guild.members)}")
        channel = member.guild.get_channel(1029006771148312626)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Wird ausgeführt, wenn ein Mitglied den Server verlässt"""
        embed = discord.Embed(
            title="Verabschiedung",
            description=f"{member.mention} hat den Server verlassen.",
            color=COLORS["red"],
            timestamp=get_timestamp()
        )
        embed.set_author(name=f"{member.name} hat den Server verlassen", icon_url="https://flimando.com/logo.png")
        embed.set_thumbnail(url=member.display_avatar.url)
        channel = member.guild.get_channel(1029006771148312626)
        await channel.send(embed=embed)

    @app_commands.command(
        name="verification-setup",
        description="Setup the verification system"
    )
    async def verification_setup(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            # Erstelle ein Embed für die Verifizierung
            embed = discord.Embed(
                title="✅ Verifizierung",
                description="Klicke auf den Button unten, um dich zu verifizieren.",
                color=COLORS["green"],
                timestamp=get_timestamp()
            )
            
            # Erstelle die View mit dem Button
            view = VerificationView()
            
            # Sende das Embed mit dem Button
            message = await interaction.response.send_message(embed=embed, view=view)
            
            # Speichere die Message ID in der data.json
            save_verification_message(message.id)
            print(f"📝 Neue Verification Message ID gespeichert: {message.id}")
            
        else:
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen!", ephemeral=True)

    @app_commands.command(
        name="set-verification-message",
        description="Setze die Message ID für das Verification System"
    )
    async def set_verification_message(self, interaction: discord.Interaction, message_id: str):
        if interaction.user.guild_permissions.administrator:
            try:
                # Validiere die Message ID
                message_id_int = int(message_id)
                
                # Speichere die Message ID in der data.json
                save_verification_message(message_id_int)
                
                await interaction.response.send_message(
                    f"✅ Verification Message ID auf {message_id_int} gesetzt und in data.json gespeichert!",
                    ephemeral=True
                )
                
            except ValueError:
                await interaction.response.send_message("❌ Ungültige Message ID!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen!", ephemeral=True)

    @app_commands.command(
        name="get-verification-message",
        description="Zeige die aktuelle Verification Message ID"
    )
    async def get_verification_message_cmd(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            message_id = get_verification_message()
            if message_id:
                await interaction.response.send_message(
                    f"📝 Aktuelle Verification Message ID: `{message_id}`",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "⚠️ Keine Verification Message ID gespeichert!",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen!", ephemeral=True)

    @app_commands.command(
        name="restore-verification",
        description="Stelle die Verification Message wieder her"
    )
    async def restore_verification_cmd(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            message_id = get_verification_message()
            if message_id:
                await interaction.response.send_message(
                    "🔄 Versuche Verification Message wiederherzustellen...",
                    ephemeral=True
                )
                
                # Stelle die Message wieder her
                await self.restore_verification_message(message_id)
                
                await interaction.followup.send(
                    "✅ Verification Message Wiederherstellung abgeschlossen!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "⚠️ Keine Verification Message ID gespeichert!",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen!", ephemeral=True)


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        style=discord.ButtonStyle.success,
        label="Verifizieren",
        custom_id="verify_button"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Hole die Verified Rolle
            verified_role = interaction.guild.get_role(1028686037968506890)
            
            if verified_role is None:
                await interaction.response.send_message("❌ Verified Rolle nicht gefunden!", ephemeral=True)
                return
            
            # Prüfe ob User bereits die Rolle hat
            if verified_role in interaction.user.roles:
                await interaction.response.send_message("✅ Du bist bereits verifiziert!", ephemeral=True)
                return
            
            # Füge die Rolle dem User hinzu
            await interaction.user.add_roles(verified_role)
            
            # Bestätige die Verifizierung
            await interaction.response.send_message("✅ Du wurdest erfolgreich verifiziert!", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Fehler bei der Verifizierung: {str(e)}", ephemeral=True)


async def setup(bot):
    welcome_cog = Welcome(bot)
    await bot.add_cog(welcome_cog)
    
    # Setup Verification System nach dem Laden der Extension
    await welcome_cog.setup_verification()
    
    print("Welcome Extension Loaded!")