import discord
from discord.ext import commands
from discord.ui import Button, View
from colorthief import ColorThief
from io import BytesIO
import aiohttp

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variável global para armazenar o ID do canal
channel_ids = {}

user_stats = {}
message_cache = {}  # Armazena os IDs das mensagens para atualizações

def is_admin(ctx):
    return any(role.permissions.administrator for role in ctx.author.roles)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    guild_id = message.guild.id

    if guild_id in channel_ids and message.channel.id != channel_ids[guild_id]:
        await message.channel.send(f"Você não pode usar comandos aqui {message.author.mention}, bobinho(a)!")
        return

    await bot.process_commands(message)

@bot.command()
@commands.check(is_admin)
async def set(ctx, channel: discord.TextChannel = None):
    guild_id = ctx.guild.id
    if channel:
        channel_ids[guild_id] = channel.id
        await ctx.send(f"Canal definido para {channel.mention}.")
    else:
        await ctx.send("Por favor, mencione um canal válido.")

@bot.command()
@commands.check(is_admin)
async def add(ctx, stat_type: str, member: discord.Member = None, value: int = 0):
    if member is None:
        member = ctx.author

    if member.id not in user_stats:
        user_stats[member.id] = {'wins': 0, 'mvps': 0, 'defeats': 0, 'games': 0, 'x1': 0, 'x2': 0, 'x3': 0, 'x4': 0, 'total_titles': 0}

    if stat_type == 'w':
        user_stats[member.id]['wins'] += value
        await ctx.send(f"Adicionado {value} vitórias ao usuário {member.display_name}.")
    elif stat_type == 'm':
        user_stats[member.id]['mvps'] += value
        await ctx.send(f"Adicionado {value} MVPs ao usuário {member.display_name}.")
    elif stat_type == 'd':
        user_stats[member.id]['defeats'] += value
        await ctx.send(f"Adicionado {value} derrotas ao usuário {member.display_name}.")
    elif stat_type == 'p':
        user_stats[member.id]['games'] += value
        await ctx.send(f"Adicionado {value} partidas ao usuário {member.display_name}.")
    elif stat_type in ['x1', 'x2', 'x3', 'x4']:
        user_stats[member.id][stat_type] += value
        user_stats[member.id]['total_titles'] = sum(user_stats[member.id][key] for key in ['x1', 'x2', 'x3', 'x4'])
        await ctx.send(f"Adicionado {value} ao {stat_type} do usuário {member.display_name}.")
    else:
        await ctx.send("Tipo de estatística inválido. Use 'w' para vitórias, 'm' para MVPs, 'd' para derrotas, 'p' para partidas, 'x1', 'x2', 'x3' ou 'x4'.")

    # Atualiza a embed do usuário após adicionar
    await update_camps_embed(ctx, member.id)

@bot.command()
@commands.check(is_admin)
async def rem(ctx, stat_type: str, member: discord.Member = None, value: int = 0):
    if member is None:
        member = ctx.author

    if member.id not in user_stats:
        user_stats[member.id] = {'wins': 0, 'mvps': 0, 'defeats': 0, 'games': 0, 'x1': 0, 'x2': 0, 'x3': 0, 'x4': 0, 'total_titles': 0}

    if stat_type == 'w':
        user_stats[member.id]['wins'] = max(0, user_stats[member.id]['wins'] - value)
        await ctx.send(f"Removido {value} vitórias do usuário {member.display_name}.")
    elif stat_type == 'm':
        user_stats[member.id]['mvps'] = max(0, user_stats[member.id]['mvps'] - value)
        await ctx.send(f"Removido {value} MVPs do usuário {member.display_name}.")
    elif stat_type == 'd':
        user_stats[member.id]['defeats'] = max(0, user_stats[member.id]['defeats'] - value)
        await ctx.send(f"Removido {value} derrotas do usuário {member.display_name}.")
    elif stat_type == 'p':
        user_stats[member.id]['games'] = max(0, user_stats[member.id]['games'] - value)
        await ctx.send(f"Removido {value} partidas do usuário {member.display_name}.")
    elif stat_type in ['x1', 'x2', 'x3', 'x4']:
        user_stats[member.id][stat_type] = max(0, user_stats[member.id][stat_type] - value)
        user_stats[member.id]['total_titles'] = sum(user_stats[member.id][key] for key in ['x1', 'x2', 'x3', 'x4'])
        await ctx.send(f"Removido {value} ao {stat_type} do usuário {member.display_name}.")
    else:
        await ctx.send("Tipo de estatística inválido. Use 'w' para vitórias, 'm' para MVPs, 'd' para derrotas, 'p' para partidas, 'x1', 'x2', 'x3' ou 'x4'.")

    # Atualiza a embed do usuário após remover
    await update_camps_embed(ctx, member.id)

async def get_dominant_color(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    image_data = BytesIO(await resp.read())
                    color_thief = ColorThief(image_data)
                    dominant_color = color_thief.get_color(quality=1)
                    return discord.Color.from_rgb(*dominant_color)
    except Exception as e:
        print(f"Error getting dominant color: {e}")
    return discord.Color.default()

@bot.command()
async def p(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    highest_role = max(member.roles, key=lambda role: role.position, default=None)
    highest_role_mention = highest_role.mention if highest_role else "Nenhum cargo"

    stats = user_stats.get(member.id, {'wins': 0, 'mvps': 0, 'defeats': 0, 'games': 0, 'x1': 0, 'x2': 0, 'x3': 0, 'x4': 0, 'total_titles': 0})

    banner_color = discord.Color.default()
    if member.banner:
        banner_url = member.banner.url
        banner_color = await get_dominant_color(banner_url)
    else:
        avatar_url = member.avatar.url
        banner_color = await get_dominant_color(avatar_url)
    
    embed = discord.Embed(
        title=f"Perfil de {member.display_name}",
        color=banner_color
    )
    
    emoji_vitorias = "<a:trofeuanim2:1265140462822494301>"  # Substitua com o ID do seu emoji
    emoji_mvps = "<a:fogin:1265879088879501425>"   # Substitua com o ID do seu emoji
    emoji_derrotas = "<a:losee:1265879018935291904>"  # Substitua com o ID do seu emoji
    emoji_partidas = "<a:rocket:1265879126481567828>" # Substitua com o ID do seu emoji

    stats_str = (
        f"{emoji_vitorias} **Vitórias:** {stats['wins']}\n"
        f"{emoji_mvps} **Mvps:** {stats['mvps']}\n"
        f"{emoji_derrotas} **Derrotas:** {stats['defeats']}\n"
        f"{emoji_partidas} **Partidas Totais:** {stats['games']}\n\n"
        f"**Cargo mais alto:** {highest_role_mention}"
    )
    
    embed.description = stats_str
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)

    # Quem sabe em breve ... 
    # custom_emoji = discord.PartialEmoji(name="trofeuanim", id=1265140462822494301)  # Substitua com o nome e ID do seu emoji personalizado

    # view = View()
    # camps_button = Button(
    #     label="Camps", 
    #     style=discord.ButtonStyle.success, 
    #     custom_id="camps_button",
    #     emoji=custom_emoji
    # )
    # rank_button = Button(
    #     label="Rank", 
    #     style=discord.ButtonStyle.success, 
    #     custom_id="rank_button",
    #     emoji=custom_emoji
    # )

    # view.add_item(camps_button)
    # view.add_item(rank_button)

    await ctx.send(embed=embed,)

@bot.command()
async def camps(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    custom_emoji = "<a:crownk1ng:1265254021178982574>"  # Substitua com o ID do seu emoji personalizado para o troféu
    custom_emoji2 = "<a:medal1:1265152625834332293>"  # Substitua com o ID do seu emoji personalizado
    custom_emoji3 = "<a:trofeuanim2:1265251026689069109>"  # Substitua com o ID do seu emoji personalizado

    stats_data = user_stats.get(member.id, {'x1': 0, 'x2': 0, 'x3': 0, 'x4': 0, 'total_titles': 0})

    embed = discord.Embed(
        title=f"Perfil de {member.display_name} {custom_emoji}",
        color=await get_dominant_color(member.avatar.url)
    )
    
    embed.description = (
        f"{custom_emoji2} **x1:** {stats_data.get('x1', 0)}\n"
        f"{custom_emoji2} **x2:** {stats_data.get('x2', 0)}\n"
        f"{custom_emoji2} **x3:** {stats_data.get('x3', 0)}\n"
        f"{custom_emoji2} **x4:** {stats_data.get('x4', 0)}\n\n"
        f"{custom_emoji3} **Títulos Totais:** {stats_data.get('total_titles', 0)}"
    )

    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)

    await ctx.send(embed=embed)
    
@bot.command()
async def rank(ctx, category: str = None, member: discord.Member = None):
    if member is None:
        member = ctx.author

    if category and category not in ['x1', 'x2', 'x3', 'x4']:
        await ctx.send("Categoria inválida. Escolha entre 'x1', 'x2', 'x3' ou 'x4'.")
        return

    sorted_users = sorted(user_stats.items(), key=lambda item: item[1].get(category, 0) if category else item[1]['total_titles'], reverse=True)

    if not sorted_users:
        await ctx.send("Nenhum dado de usuário encontrado.")
        return

    emoji_trofeu = "<a:crownmvp:1265254037566259201>"  # Substitua com o ID do seu emoji personalizado para o troféu
    emoji_top1 = "<a:medal1:1265152625834332293>"  # Substitua com o ID do seu emoji personalizado para o top 1
    emoji_top2 = "<a:silvermedal:1265152665826885715>"  # Substitua com o ID do seu emoji personalizado para o top 2
    emoji_top3 = "<a:copermedal:1265152688123805808>"  # Substitua com o ID do seu emoji personalizado para o top 3
    
    embed_description = ""
    top1_member = None
    for i, (user_id, stats) in enumerate(sorted_users[:10]):
        user_member = ctx.guild.get_member(user_id)
        if not user_member:
            continue
        
        rank_position = i + 1
        position_str = f"**{rank_position}º**"  # Formatação da posição em negrito
        
        if i == 0:
            top1_member = user_member
            embed_description += f"{emoji_top1} {position_str} - {user_member.mention} - {stats.get(category, stats['total_titles'])} títulos\n"
        elif i == 1:
            embed_description += f"{emoji_top2} {position_str} - {user_member.mention} - {stats.get(category, stats['total_titles'])} títulos\n"
        elif i == 2:
            embed_description += f"{emoji_top3} {position_str} - {user_member.mention} - {stats.get(category, stats['total_titles'])} títulos\n\n"
        else:
            embed_description += f"{position_str} - {user_member.mention} - {stats.get(category, stats['total_titles'])} títulos\n"
    
    user_rank = next((i + 1 for i, (user_id, stats) in enumerate(sorted_users) if user_id == member.id), None)
    if user_rank:
        embed_description += f"\n**Suas Estatísticas:**\nSua Posição: **{user_rank}º**"
    else:
        embed_description += "\n**Suas Estatísticas:**\nVocê não está no rank!"

    embed_color = discord.Color.default()
    if top1_member:
        avatar_url = top1_member.avatar.url
        embed_color = await get_dominant_color(avatar_url)
    
    embed = discord.Embed(
        title=f"{emoji_trofeu} | Ranking Top — {'Títulos' if category is None else category}",
        color=embed_color
    )
    
    embed.description = embed_description
    if top1_member:
        embed.set_thumbnail(url=top1_member.avatar.url)
    embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)

    await ctx.send(embed=embed)

@bot.command()
async def ajuda(ctx):
    # Emojis para os títulos
    emoji_disponiveis = "<:engrenagem:1265887332867768331>"
    emoji_admin = "<a:graycrown:1265895426016673844>"
    emoji_usuario = "<:usercinza:1265887284465504286>"
    
    admin_commands = {
        "!set <canal>": "Define o canal onde os comandos podem ser usados.",
        "!add <tipo> <membro> <valor>": "Adiciona estatísticas ao usuário (tipos: w, m, d, p, x1, x2, x3, x4).",
        "!rem <tipo> <membro> <valor>": "Remove estatísticas do usuário (tipos: w, m, d, p, x1, x2, x3, x4)."
    }
    
    user_commands = {
        "!p <membro>": "Mostra o perfil e estatísticas do usuário.",
        "!camps <membro>": "Mostra os campeonatos ganhos pelo usuário.",
        "!rank <categoria> <membro>": "Mostra o ranking dos usuários (categorias: x1, x2, x3, x4, total_titles)."
    }
    
    embed = discord.Embed(
        title=f"Comandos Disponíveis  {emoji_disponiveis}",
        color=discord.Color.from_rgb(169, 169, 169)  # Cor cinza claro
    )
    
    embed.add_field(
        name=f"Comandos para Administradores  {emoji_admin}",
        value="\n".join([f"**{cmd}**: {desc}" for cmd, desc in admin_commands.items()]),
        inline=False
    )
    
    embed.add_field(
        name=f"Comandos para Usuários  {emoji_usuario}",
        value="\n".join([f"**{cmd}**: {desc}" for cmd, desc in user_commands.items()]),
        inline=False
    )
    
    await ctx.send(embed=embed)

bot.run('SEU_BOT_TOKEN_AQUI')