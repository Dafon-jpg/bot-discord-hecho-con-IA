"""
=============================================================================
  UBA Discord Server Bot - Setup + Persistente
=============================================================================

  GUÍA PARA CREAR EL BOT EN DISCORD DEVELOPER PORTAL
  ====================================================

  1. Andá a https://discord.com/developers/applications
  2. Hacé clic en "New Application" y ponele un nombre (ej: "UBA Bot")
  3. En el menú izquierdo, andá a "Bot"
  4. Hacé clic en "Reset Token" y COPIÁ el token (se muestra una sola vez)
  5. En "Privileged Gateway Intents", activá los tres:
     - PRESENCE INTENT
     - SERVER MEMBERS INTENT
     - MESSAGE CONTENT INTENT
  6. En el menú izquierdo, andá a "OAuth2" > "URL Generator"
  7. En "Scopes", seleccioná: bot, applications.commands
  8. En "Bot Permissions", seleccioná: Administrator
  9. Copiá la URL generada abajo, abrila en el navegador e invitá al bot
  10. Creá un archivo .env en esta misma carpeta con:
      DISCORD_TOKEN=tu_token_aqui
  11. Ejecutá: pip install -r requirements.txt
  12. Ejecutá: python setup_server.py
  13. En tu servidor de Discord, escribí: !setup
"""

import discord
from discord.ext import commands
from discord import ui, PermissionOverwrite, SelectOption, Embed, Colour
from dotenv import load_dotenv
import os
import re
import asyncio
from datetime import datetime


# =============================================================================
# CONFIGURACIÓN DE ROLES
# =============================================================================

ROLES_CONFIG = [
    {"name": "Admin", "color": 0xFF0000, "permissions": discord.Permissions(administrator=True), "hoist": True},
    {"name": "Exactas", "color": 0x3498DB, "permissions": discord.Permissions.none(), "hoist": True},
    {"name": "Derecho", "color": 0xF1C40F, "permissions": discord.Permissions.none(), "hoist": True},
    {"name": "Ingeniería", "color": 0xE67E22, "permissions": discord.Permissions.none(), "hoist": True},
    {"name": "Estudiante CBC", "color": 0x2ECC71, "permissions": discord.Permissions.none(), "hoist": True},
    {"name": "Estudiante general", "color": 0x99AAB5, "permissions": discord.Permissions.none(), "hoist": False},
]


# =============================================================================
# CONFIGURACIÓN DE CATEGORÍAS Y CANALES
# =============================================================================

CATEGORIES_CONFIG = [
    {
        "name": "🌐 RECEPCIÓN",
        "overwrites_type": "announcement",  # read-only para @everyone excepto auto-roles embed
        "channels": [
            {"name": "📋rules-y-faq", "type": "text", "topic": "📜 Normas de convivencia del servidor. Leé antes de participar.", "read_only": True},
            {"name": "🎭auto-roles", "type": "text", "topic": "🎯 Elegí tu carrera y materias con los menús desplegables.", "read_only": True},
            {"name": "📢anuncios-uba", "type": "text", "topic": "📅 Fechas de inscripción, feriados académicos y novedades UBA.", "read_only": True},
            {"name": "📌difusion-importante", "type": "text", "topic": "🔔 Mensajes de difusión prioritaria."},
            {"name": "📚biblioteca-general", "type": "text", "topic": "📖 Biblioteca automática — aquí se recopilan todos los recursos compartidos en el servidor."},
        ],
    },
    {
        "name": "🏫 EL CAMPUS",
        "overwrites_type": "open",
        "channels": [
            {"name": "💬charla-general", "type": "text", "topic": "☕ Para hablar de cualquier cosa."},
            {"name": "📱grupos-whatsapp", "type": "text", "topic": "🔗 Links a grupos de WhatsApp no oficiales hechos por alumnos."},
            {"name": "🛒market-pueblo", "type": "text", "topic": "💰 Compra/venta de apuntes, libros, calculadoras, teclados y más."},
            {"name": "💻vsc-y-tech", "type": "text", "topic": "🖥️ Dudas de programación, setup, IDEs y herramientas tech."},
        ],
    },
    {
        "name": "🎓 CBC - CICLO BÁSICO COMÚN",
        "overwrites_type": "open",
        "channels": [
            {"name": "📖ipc-40", "type": "text", "topic": "🧠 Introducción al Pensamiento Científico (40) — Común a todas las carreras"},
            {"name": "🏛sociedad-y-estado-24", "type": "text", "topic": "📜 ICSE - Introducción al Conocimiento de la Sociedad y Estado (24) — Común a todas las carreras"},
            {"name": "📐analisis-matematico-66", "type": "text", "topic": "📊 Análisis Matemático (66) — Exactas / Ingeniería"},
            {"name": "🔢algebra-62", "type": "text", "topic": "➗ Álgebra (62) — Exactas / Ingeniería"},
            {"name": "⚡fisica-03", "type": "text", "topic": "🔭 Física (03) — Exactas / Ingeniería"},
            {"name": "🧪quimica-05", "type": "text", "topic": "⚗️ Química (05) — Exactas / Ingeniería"},
            {"name": "👥sociologia-14", "type": "text", "topic": "🏘️ Sociología (14) — Derecho"},
            {"name": "🏛ciencia-politica-22", "type": "text", "topic": "🗳️ Ciencia Política (22) — Derecho"},
            {"name": "💰economia-21", "type": "text", "topic": "📈 Economía (21) — Derecho"},
            {"name": "⚖derecho-latinoamericano-33", "type": "text", "topic": "📕 Principios Generales del Derecho Latinoamericano (33) — Derecho"},
        ],
    },
    {
        "name": "🔬 EXACTAS / INGENIERÍA",
        "overwrites_type": "private_exactas",
        "channels": [
            {"name": "📚biblioteca-digital", "type": "text", "topic": "📂 PDFs, links a Drives, apuntes de 'El Altillo' y recursos digitales."},
            {"name": "📐algebra-1", "type": "text", "topic": "🔢 Álgebra I — Parciales, apuntes, consultas y resolución de ejercicios."},
            {"name": "📊analisis-1", "type": "text", "topic": "📈 Análisis Matemático I — Parciales, apuntes y consultas."},
            {"name": "💻algoritmos-1", "type": "text", "topic": "🖥️ Algoritmos y Estructuras de Datos I — Código, debugging y consultas."},
        ],
    },
    {
        "name": "⚖️ DERECHO",
        "overwrites_type": "private_derecho",
        "channels": [
            {"name": "📜jurisprudencia-y-fallos", "type": "text", "topic": "⚖️ Archivos de jurisprudencia, fallos y casos de estudio."},
            {"name": "📚bibliografia-derecho", "type": "text", "topic": "📖 Libros, códigos actualizados y material de estudio."},
        ],
    },
    {
        "name": "🎮 RECREO & BOTS",
        "overwrites_type": "open",
        "channels": [
            {"name": "🤖comandos-apps", "type": "text", "topic": "🕹️ Canal exclusivo para usar bots y apps: Chess, Sudoku, Rythm, Wordle, Watch Together."},
            {"name": "🎮gaming-chat", "type": "text", "topic": "🎲 Coordiná partidas de Ajedrez, Sudoku y más."},
        ],
    },
    {
        "name": "🔊 BIBLIOTECA DE VOZ",
        "overwrites_type": "open",
        "channels": [
            {"name": "🔇 Estudio Silencioso", "type": "voice", "muted": True},
            {"name": "📚 Sala de Estudio A", "type": "voice"},
            {"name": "📚 Sala de Estudio B", "type": "voice"},
            {"name": "☕ El Buffet", "type": "voice"},
        ],
    },
]


# =============================================================================
# REGEX PARA DETECCIÓN DE RECURSOS (BIBLIOTECA AUTOMÁTICA)
# =============================================================================

RESOURCE_PATTERN = re.compile(
    r'https?://\S+'                          # Cualquier URL
    r'|www\.\S+'                             # URLs sin protocolo
    r'|drive\.google\.com/\S+'               # Google Drive
    r'|mega\.nz/\S+'                         # Mega
    r'|dropbox\.com/\S+'                     # Dropbox
    r'|onedrive\.live\.com/\S+',             # OneDrive
    re.IGNORECASE
)

FILE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.xls', '.zip', '.rar'}

# Colores por categoría para los embeds de biblioteca
CATEGORY_COLORS = {
    "🌐 RECEPCIÓN": 0x3498DB,
    "🏫 EL CAMPUS": 0x2ECC71,
    "🎓 CBC - CICLO BÁSICO COMÚN": 0xE67E22,
    "🔬 EXACTAS / INGENIERÍA": 0x9B59B6,
    "⚖️ DERECHO": 0xF1C40F,
    "🎮 RECREO & BOTS": 0xE91E63,
    "🔊 BIBLIOTECA DE VOZ": 0x607D8B,
}


# =============================================================================
# VIEWS PERSISTENTES - SISTEMA AUTO-ROLES (ESTILO SAPPHIRE)
# =============================================================================

class CareerSelectView(discord.ui.View):
    """Menú desplegable para seleccionar carrera. Persistente entre reinicios."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="uba_career_role_select",
        placeholder="🎓 Seleccioná tu carrera...",
        min_values=1,
        max_values=3,
        options=[
            SelectOption(
                label="Exactas",
                value="Exactas",
                emoji="🔬",
                description="Fac. de Ciencias Exactas y Naturales"
            ),
            SelectOption(
                label="Derecho",
                value="Derecho",
                emoji="⚖️",
                description="Facultad de Derecho"
            ),
            SelectOption(
                label="Ingeniería",
                value="Ingeniería",
                emoji="⚙️",
                description="Facultad de Ingeniería"
            ),
        ]
    )
    async def career_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        member = interaction.user

        added = []
        removed = []

        for value in select.values:
            role = discord.utils.get(guild.roles, name=value)
            if role is None:
                continue

            if role in member.roles:
                await member.remove_roles(role)
                removed.append(role.name)
            else:
                await member.add_roles(role)
                added.append(role.name)

        # Construir mensaje de respuesta
        parts = []
        if added:
            parts.append(f"✅ **Roles agregados:** {', '.join(added)}")
        if removed:
            parts.append(f"❌ **Roles removidos:** {', '.join(removed)}")
        if not parts:
            parts.append("⚠️ No se encontraron los roles. Pedile a un admin que ejecute `!setup`.")

        await interaction.response.send_message("\n".join(parts), ephemeral=True)


class CBCSelectView(discord.ui.View):
    """Menú desplegable para identificarse como estudiante CBC."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="uba_cbc_select",
        placeholder="📖 ¿Estás cursando el CBC?",
        min_values=1,
        max_values=1,
        options=[
            SelectOption(
                label="Sí, curso el CBC",
                value="cbc_si",
                emoji="🎓",
                description="Asignarme el rol Estudiante CBC"
            ),
            SelectOption(
                label="Ya terminé el CBC",
                value="cbc_no",
                emoji="✅",
                description="Remover el rol Estudiante CBC"
            ),
            SelectOption(
                label="Estudiante general",
                value="general",
                emoji="📋",
                description="Solo quiero el rol de Estudiante general"
            ),
        ]
    )
    async def cbc_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        member = interaction.user
        value = select.values[0]

        cbc_role = discord.utils.get(guild.roles, name="Estudiante CBC")
        general_role = discord.utils.get(guild.roles, name="Estudiante general")

        if value == "cbc_si":
            if cbc_role:
                await member.add_roles(cbc_role)
            msg = "✅ **Rol asignado:** Estudiante CBC"
        elif value == "cbc_no":
            if cbc_role and cbc_role in member.roles:
                await member.remove_roles(cbc_role)
            msg = "❌ **Rol removido:** Estudiante CBC"
        elif value == "general":
            if general_role:
                await member.add_roles(general_role)
            msg = "✅ **Rol asignado:** Estudiante general"
        else:
            msg = "⚠️ Opción no reconocida."

        await interaction.response.send_message(msg, ephemeral=True)


# =============================================================================
# BOT PRINCIPAL
# =============================================================================

class UBABot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """Registra views persistentes al iniciar (sobreviven reinicios)."""
        self.add_view(CareerSelectView())
        self.add_view(CBCSelectView())


bot = UBABot()


# =============================================================================
# EVENTOS
# =============================================================================

@bot.event
async def on_ready():
    print(f"{'='*50}")
    print(f"  Bot conectado como: {bot.user}")
    print(f"  Servidores: {[g.name for g in bot.guilds]}")
    print(f"  Ejecutá !setup en tu servidor para configurarlo")
    print(f"{'='*50}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    """Setup automático cuando el bot se une a un nuevo servidor."""
    print(f"Bot agregado al servidor: {guild.name}")
    # Buscar un canal donde enviar el mensaje de bienvenida
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                "👋 **¡Hola!** Soy el bot de configuración UBA.\n"
                "Un **administrador** puede ejecutar `!setup` para configurar el servidor completo."
            )
            break


# =============================================================================
# BIBLIOTECA AUTOMÁTICA - DETECCIÓN DE RECURSOS
# =============================================================================

@bot.event
async def on_message(message: discord.Message):
    # Ignorar mensajes del propio bot
    if message.author.bot:
        return

    # No procesar mensajes de DMs
    if message.guild is None:
        await bot.process_commands(message)
        return

    # Detectar recursos (archivos adjuntos o links)
    has_files = len(message.attachments) > 0
    has_links = bool(RESOURCE_PATTERN.search(message.content or ""))

    # Verificar extensiones de archivos adjuntos
    has_resource_files = any(
        os.path.splitext(att.filename)[1].lower() in FILE_EXTENSIONS
        for att in message.attachments
    )

    if has_files or has_links:
        # No recopilar del propio canal biblioteca
        if "biblioteca-general" not in (message.channel.name or ""):
            await mirror_to_biblioteca(message, has_resource_files, has_links)

    # IMPORTANTE: procesar comandos después
    await bot.process_commands(message)


async def mirror_to_biblioteca(message: discord.Message, has_files: bool, has_links: bool):
    """Copia un mensaje con recursos al canal #biblioteca-general."""
    biblioteca = discord.utils.get(message.guild.text_channels, name="📚biblioteca-general")
    if biblioteca is None:
        # Intentar buscar sin emoji (Discord sanitiza nombres)
        biblioteca = discord.utils.find(
            lambda c: "biblioteca-general" in c.name,
            message.guild.text_channels
        )
    if biblioteca is None:
        return

    # Determinar color del embed según categoría
    cat_name = message.channel.category.name if message.channel.category else "Sin categoría"
    color = CATEGORY_COLORS.get(cat_name, 0x95A5A6)

    # Construir embed
    embed = Embed(
        title="📚 Nuevo recurso compartido",
        color=color,
        timestamp=message.created_at
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.display_avatar.url if message.author.display_avatar else None
    )
    embed.add_field(
        name="📍 Canal de origen",
        value=f"**{cat_name}** → #{message.channel.name}",
        inline=False
    )
    embed.add_field(
        name="🔗 Ir al mensaje",
        value=f"[Click aquí]({message.jump_url})",
        inline=True
    )

    # Contenido del mensaje (truncado)
    if message.content:
        content_preview = message.content[:300]
        if len(message.content) > 300:
            content_preview += "..."
        embed.add_field(name="💬 Contenido", value=content_preview, inline=False)

    # Listar archivos adjuntos
    if message.attachments:
        file_list = []
        for att in message.attachments:
            size_mb = att.size / (1024 * 1024)
            file_list.append(f"📎 **{att.filename}** ({size_mb:.1f} MB)")
        embed.add_field(name="📁 Archivos", value="\n".join(file_list), inline=False)

    # Extraer links del mensaje
    if has_links and message.content:
        links = RESOURCE_PATTERN.findall(message.content)
        if links:
            link_list = [f"🔗 {link}" for link in links[:5]]  # Max 5 links
            if len(links) > 5:
                link_list.append(f"_...y {len(links) - 5} más_")
            embed.add_field(name="🌐 Enlaces", value="\n".join(link_list), inline=False)

    embed.set_footer(text=f"Recopilado automáticamente de #{message.channel.name}")

    try:
        await biblioteca.send(embed=embed)

        # Re-subir archivos si son menores a 25MB
        files_to_send = []
        for att in message.attachments:
            if att.size < 25 * 1024 * 1024:  # 25MB límite de Discord
                try:
                    file = await att.to_file()
                    files_to_send.append(file)
                except Exception:
                    pass

        if files_to_send:
            await biblioteca.send(files=files_to_send)

    except discord.HTTPException as e:
        print(f"Error al enviar a biblioteca: {e}")


# =============================================================================
# FUNCIÓN PRINCIPAL DE SETUP
# =============================================================================

async def setup_server(guild: discord.Guild, status_channel=None):
    """
    Configura el servidor completo: roles, categorías, canales y embeds.
    Idempotente: verifica existencia antes de crear.
    """

    async def send_status(msg):
        if status_channel:
            try:
                await status_channel.send(msg)
            except Exception:
                pass
        print(msg)

    await send_status("⏳ **Iniciando configuración del servidor...**")

    # ─── FASE 0: LIMPIAR CANALES DEL TEMPLATE ─────────────────────────
    await send_status("🧹 Limpiando canales del template de Discord...")
    template_channels = [
        "welcome-and-rules", "announcements", "resources",
        "general", "meeting-plans", "off-topic",
    ]
    template_voice = ["Lounge", "Meeting Room 1", "Meeting Room 2"]
    template_categories = ["Information", "Text Channels", "Voice Channels"]

    for ch in guild.text_channels:
        if ch.name in template_channels:
            try:
                await ch.delete(reason="Limpieza de template para setup UBA")
                await send_status(f"  🗑️ Canal eliminado: **#{ch.name}**")
                await asyncio.sleep(0.3)
            except discord.HTTPException:
                pass

    for vc in guild.voice_channels:
        if vc.name in template_voice:
            try:
                await vc.delete(reason="Limpieza de template para setup UBA")
                await send_status(f"  🗑️ Canal de voz eliminado: **{vc.name}**")
                await asyncio.sleep(0.3)
            except discord.HTTPException:
                pass

    for cat in guild.categories:
        if cat.name in template_categories:
            try:
                await cat.delete(reason="Limpieza de template para setup UBA")
                await send_status(f"  🗑️ Categoría eliminada: **{cat.name}**")
                await asyncio.sleep(0.3)
            except discord.HTTPException:
                pass

    # ─── FASE 1: CREAR ROLES ───────────────────────────────────────────
    await send_status("🎨 Creando roles...")
    roles = {}

    for role_cfg in ROLES_CONFIG:
        existing = discord.utils.get(guild.roles, name=role_cfg["name"])
        if existing is None:
            try:
                role = await guild.create_role(
                    name=role_cfg["name"],
                    colour=discord.Colour(role_cfg["color"]),
                    permissions=role_cfg["permissions"],
                    hoist=role_cfg["hoist"],
                    mentionable=True
                )
                roles[role_cfg["name"]] = role
                await send_status(f"  ✅ Rol creado: **{role_cfg['name']}**")
                await asyncio.sleep(0.3)
            except discord.HTTPException as e:
                await send_status(f"  ❌ Error creando rol {role_cfg['name']}: {e}")
        else:
            roles[role_cfg["name"]] = existing
            await send_status(f"  ⏩ Rol ya existe: **{role_cfg['name']}**")

    # ─── FASE 2: CREAR CATEGORÍAS Y CANALES ────────────────────────────
    await send_status("📂 Creando categorías y canales...")

    auto_roles_channel = None
    comandos_channel = None

    for cat_cfg in CATEGORIES_CONFIG:
        cat_name = cat_cfg["name"]

        # Construir overwrites de la categoría
        overwrites = build_category_overwrites(guild, roles, cat_cfg["overwrites_type"])

        # Verificar si la categoría ya existe
        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if existing_cat is None:
            try:
                cat_kwargs = {"name": cat_name}
                if overwrites:
                    cat_kwargs["overwrites"] = overwrites
                category = await guild.create_category(**cat_kwargs)
                await send_status(f"  📁 Categoría creada: **{cat_name}**")
                await asyncio.sleep(0.3)
            except discord.HTTPException as e:
                await send_status(f"  ❌ Error creando categoría {cat_name}: {e}")
                continue
        else:
            category = existing_cat
            await send_status(f"  ⏩ Categoría ya existe: **{cat_name}**")

        # Crear canales dentro de la categoría
        for ch_cfg in cat_cfg["channels"]:
            ch_name = ch_cfg["name"]
            ch_type = ch_cfg["type"]

            # Verificar si el canal ya existe en esta categoría
            if ch_type == "text":
                existing_ch = discord.utils.find(
                    lambda c, n=ch_name: n.lower().replace(" ", "-") in c.name.lower() or c.name == n,
                    category.text_channels
                )
            else:
                existing_ch = discord.utils.find(
                    lambda c, n=ch_name: n.lower() in c.name.lower() or c.name == n,
                    category.voice_channels
                )

            if existing_ch is not None:
                # Guardar referencia a canales especiales
                if "auto-roles" in existing_ch.name:
                    auto_roles_channel = existing_ch
                if "comandos-apps" in existing_ch.name:
                    comandos_channel = existing_ch
                continue

            try:
                if ch_type == "text":
                    # Kwargs para la creación del canal
                    kwargs = {"name": ch_name, "topic": ch_cfg.get("topic", "")}

                    if ch_cfg.get("read_only"):
                        ch_overwrites = {
                            guild.default_role: PermissionOverwrite(send_messages=False),
                            guild.me: PermissionOverwrite(send_messages=True),
                        }
                        # Mantener overwrites de la categoría si es privada
                        if cat_cfg["overwrites_type"].startswith("private"):
                            for role_key, perm in overwrites.items():
                                if role_key not in ch_overwrites:
                                    ch_overwrites[role_key] = perm
                        kwargs["overwrites"] = ch_overwrites

                    channel = await category.create_text_channel(**kwargs)

                    # Guardar referencia a canales especiales
                    if "auto-roles" in channel.name:
                        auto_roles_channel = channel
                    if "comandos-apps" in channel.name:
                        comandos_channel = channel

                else:  # voice
                    kwargs = {"name": ch_name}

                    if ch_cfg.get("muted"):
                        kwargs["overwrites"] = {
                            guild.default_role: PermissionOverwrite(
                                connect=True,
                                speak=False,
                                stream=False
                            ),
                            guild.me: PermissionOverwrite(
                                connect=True,
                                speak=True
                            ),
                        }

                    channel = await category.create_voice_channel(**kwargs)

                await send_status(f"    📌 Canal creado: **{ch_name}**")
                await asyncio.sleep(0.3)

            except discord.HTTPException as e:
                await send_status(f"    ❌ Error creando canal {ch_name}: {e}")

    # ─── FASE 3: ENVIAR EMBEDS DE AUTO-ROLES ───────────────────────────
    if auto_roles_channel:
        await send_status("🎭 Configurando sistema de auto-roles...")
        await setup_auto_roles(auto_roles_channel)

    # ─── FASE 4: ENVIAR GUÍA DE COMANDOS ───────────────────────────────
    if comandos_channel:
        await send_status("🤖 Enviando guía de comandos y apps...")
        await setup_commands_guide(comandos_channel)

    # ─── FASE 5: ENVIAR REGLAS ──────────────────────────────────────────
    rules_channel = discord.utils.find(
        lambda c: "rules" in c.name,
        guild.text_channels
    )
    if rules_channel:
        await send_status("📋 Configurando canal de reglas...")
        await setup_rules(rules_channel)

    await send_status("✅ **¡Servidor configurado exitosamente!** 🎉")


def build_category_overwrites(guild, roles, overwrites_type):
    """Construye los permission overwrites según el tipo de categoría."""
    if overwrites_type == "private_exactas":
        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
            guild.me: PermissionOverwrite(view_channel=True),
        }
        if "Exactas" in roles:
            overwrites[roles["Exactas"]] = PermissionOverwrite(view_channel=True)
        if "Ingeniería" in roles:
            overwrites[roles["Ingeniería"]] = PermissionOverwrite(view_channel=True)
        if "Admin" in roles:
            overwrites[roles["Admin"]] = PermissionOverwrite(view_channel=True)
        return overwrites

    elif overwrites_type == "private_derecho":
        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
            guild.me: PermissionOverwrite(view_channel=True),
        }
        if "Derecho" in roles:
            overwrites[roles["Derecho"]] = PermissionOverwrite(view_channel=True)
        if "Admin" in roles:
            overwrites[roles["Admin"]] = PermissionOverwrite(view_channel=True)
        return overwrites

    elif overwrites_type == "announcement":
        return {
            guild.default_role: PermissionOverwrite(view_channel=True, send_messages=False),
            guild.me: PermissionOverwrite(view_channel=True, send_messages=True),
        }

    else:  # "open"
        return {}


# =============================================================================
# SETUP DE EMBEDS ESPECIALES
# =============================================================================

async def setup_auto_roles(channel: discord.TextChannel):
    """Envía los embeds con select menus en #auto-roles si no existen."""
    # Verificar si ya se enviaron
    async for msg in channel.history(limit=20):
        if msg.author == channel.guild.me and msg.embeds:
            print("  ⏩ Embeds de auto-roles ya existen.")
            return

    # Embed de bienvenida
    welcome_embed = Embed(
        title="🎓 ¡Bienvenido al servidor UBA!",
        description=(
            "Usá los **menús desplegables** de abajo para configurar tu perfil.\n\n"
            "**Paso 1:** Seleccioná tu carrera (podés elegir más de una)\n"
            "**Paso 2:** Indicá si estás cursando el CBC\n\n"
            "Esto te dará acceso a los canales específicos de tu facultad "
            "y te conectará con compañeros de las mismas materias. 📚"
        ),
        color=Colour.blue()
    )
    welcome_embed.set_footer(text="Los roles se pueden cambiar en cualquier momento")
    await channel.send(embed=welcome_embed)
    await asyncio.sleep(0.5)

    # Embed + Select Menu de Carrera
    career_embed = Embed(
        title="🏛️ Seleccioná tu Facultad",
        description=(
            "Elegí una o más carreras del menú desplegable.\n"
            "Si ya tenés un rol y lo seleccionás de nuevo, **se remueve** (toggle).\n\n"
            "🔬 **Exactas** — Ciencias Exactas y Naturales\n"
            "⚖️ **Derecho** — Facultad de Derecho\n"
            "⚙️ **Ingeniería** — Facultad de Ingeniería"
        ),
        color=Colour.gold()
    )
    await channel.send(embed=career_embed, view=CareerSelectView())
    await asyncio.sleep(0.5)

    # Embed + Select Menu de CBC
    cbc_embed = Embed(
        title="📖 Ciclo Básico Común",
        description=(
            "¿Estás cursando el CBC actualmente?\n"
            "Este rol te identificará como estudiante del Ciclo Básico Común."
        ),
        color=Colour.green()
    )
    await channel.send(embed=cbc_embed, view=CBCSelectView())


async def setup_commands_guide(channel: discord.TextChannel):
    """Envía la guía de comandos de apps integradas en #comandos-apps."""
    # Verificar si ya se envió
    async for msg in channel.history(limit=10):
        if msg.author == channel.guild.me and msg.embeds:
            return

    embed = Embed(
        title="🕹️ Apps y Actividades del Servidor",
        description="Acá podés usar todas las apps integradas sin molestar en otros canales.",
        color=Colour.purple()
    )

    embed.add_field(
        name="♟️ Chess in the Park",
        value=(
            "Partidas de ajedrez dentro de Discord.\n"
            "Iniciá una actividad en un **canal de voz** → "
            "botón de cohete 🚀 → Chess in the Park"
        ),
        inline=False
    )
    embed.add_field(
        name="🔢 Daily Sudoku Together",
        value=(
            "Sudoku cooperativo diario.\n"
            "Iniciá desde un **canal de voz** → "
            "botón de cohete 🚀 → Sudoku Together"
        ),
        inline=False
    )
    embed.add_field(
        name="🎵 Rythm",
        value=(
            "Música en canales de voz.\n"
            "`!play <canción o URL>` — Reproducir música\n"
            "`!skip` — Saltar canción\n"
            "`!queue` — Ver cola de reproducción\n"
            "`!disconnect` — Desconectar el bot"
        ),
        inline=False
    )
    embed.add_field(
        name="📝 Wordle",
        value=(
            "El clásico juego de palabras.\n"
            "Iniciá desde un **canal de voz** → "
            "botón de cohete 🚀 → Wordle"
        ),
        inline=False
    )
    embed.add_field(
        name="📺 Watch Together (YouTube)",
        value=(
            "Mirá videos de YouTube en grupo.\n"
            "Iniciá desde un **canal de voz** → "
            "botón de cohete 🚀 → Watch Together"
        ),
        inline=False
    )

    embed.set_footer(text="💡 Las actividades se inician desde canales de voz con el botón de Activities (🚀)")
    await channel.send(embed=embed)


async def setup_rules(channel: discord.TextChannel):
    """Envía las reglas del servidor en #rules-y-faq."""
    # Verificar si ya se enviaron
    async for msg in channel.history(limit=10):
        if msg.author == channel.guild.me and msg.embeds:
            return

    embed = Embed(
        title="📜 Reglas y FAQ del Servidor",
        description="Lee atentamente antes de participar.",
        color=Colour.red()
    )

    embed.add_field(
        name="1️⃣ Respeto mutuo",
        value="Tratá a todos con respeto. No se toleran insultos, discriminación ni acoso de ningún tipo.",
        inline=False
    )
    embed.add_field(
        name="2️⃣ Contenido apropiado",
        value="No compartas contenido NSFW, ilegal o que viole derechos de autor de forma malintencionada.",
        inline=False
    )
    embed.add_field(
        name="3️⃣ Usá los canales correctos",
        value="Cada canal tiene un propósito específico. Revisá el topic del canal antes de postear.",
        inline=False
    )
    embed.add_field(
        name="4️⃣ No spam",
        value="Evitá mensajes repetitivos, flood de emojis o publicidad no autorizada.",
        inline=False
    )
    embed.add_field(
        name="5️⃣ Auto-roles",
        value="Configurá tus roles en 🎭auto-roles para ver los canales de tu carrera.",
        inline=False
    )
    embed.add_field(
        name="6️⃣ Market Pueblo",
        value="Publicá en 🛒market-pueblo solo ventas reales. No estafas.",
        inline=False
    )
    embed.add_field(
        name="7️⃣ Recursos académicos",
        value="Todo material que compartas se recopila automáticamente en 📚biblioteca-general.",
        inline=False
    )

    embed.set_footer(text="El incumplimiento de las reglas puede resultar en warn, mute o ban.")
    await channel.send(embed=embed)


# =============================================================================
# COMANDO !SETUP
# =============================================================================

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_command(ctx: commands.Context):
    """Configura el servidor completo. Solo para administradores."""
    await setup_server(ctx.guild, status_channel=ctx.channel)


@setup_command.error
async def setup_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Necesitás permisos de **Administrador** para ejecutar este comando.")
    else:
        await ctx.send(f"❌ Error inesperado: {error}")
        print(f"Error en !setup: {error}")


# =============================================================================
# INICIO DEL BOT
# =============================================================================

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("=" * 50)
        print("  ERROR: No se encontró DISCORD_TOKEN")
        print("=" * 50)
        print()
        print("  Seguí estos pasos:")
        print("  1. Andá a https://discord.com/developers/applications")
        print("  2. Creá una aplicación y un bot")
        print("  3. Copiá el token del bot")
        print("  4. Creá un archivo .env con: DISCORD_TOKEN=tu_token")
        print("  5. Ejecutá de nuevo: python setup_server.py")
        print()
        exit(1)

    print("Iniciando bot UBA...")
    bot.run(token)
