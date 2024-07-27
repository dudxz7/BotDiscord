<h1 align="center">Bot de Estatísticas para Discord 🤖</h1>

Este projeto é um bot para Discord desenvolvido em Python usando a biblioteca `discord.py`. O bot foi criado para o stremar de jogos @magnusxff, com o intuito de gerenciar e visualizar estatísticas de usuários em um servidor. Ele oferece uma variedade de comandos para adicionar, remover e exibir estatísticas, bem como recursos interativos para facilitar a interação dos usuários com o bot.

#### Funcionalidades Principais

1. **Gerenciamento de Canal de Comandos**:
    - **`!set <canal>`**: Define um canal específico onde os comandos do bot podem ser utilizados. Apenas administradores podem definir o canal.

2. **Adição e Remoção de Estatísticas**:
    - **`!add <tipo> <membro> <valor>`**: Adiciona estatísticas ao usuário. Tipos de estatísticas incluem vitórias (`w`), MVPs (`m`), derrotas (`d`), partidas (`p`), e títulos de campeonatos (`x1`, `x2`, `x3`, `x4`).
    - **`!rem <tipo> <membro> <valor>`**: Remove estatísticas do usuário com os mesmos tipos acima. Apenas administradores podem adicionar ou remover estatísticas.

3. **Visualização de Estatísticas de Usuários**:
    - **`!p <membro>`**: Mostra o perfil e estatísticas do usuário, incluindo vitórias, MVPs, derrotas, partidas e o cargo mais alto no servidor.
    - **`!camps <membro>`**: Exibe os campeonatos ganhos pelo usuário, divididos nas categorias `x1`, `x2`, `x3` e `x4`, além do total de títulos.
    - **`!rank <categoria>`**: Exibe o ranking dos usuários baseado na categoria selecionada (`x1`, `x2`, `x3`, `x4` ou `total_titles`). Mostra os 10 melhores jogadores e a posição do usuário que executou o comando.

4. **Comando de Ajuda**:
    - **`!ajuda`**: Exibe uma lista de comandos disponíveis para administradores e usuários, com emojis para melhorar a visualização e organização das informações.

#### Recursos Adicionais

- **Emojis Personalizados**: O bot utiliza emojis personalizados para representar diferentes tipos de estatísticas e ações, tornando a interface mais atraente e intuitiva.
- **Atualização Dinâmica de Embeds**: Após adicionar ou remover estatísticas, as embeds do perfil do usuário são atualizadas automaticamente para refletir as mudanças.
- **Cores Dominantes em Imagens**: O bot utiliza a biblioteca `colorthief` para extrair a cor dominante do avatar ou banner dos usuários, aplicando essa cor às embeds para uma apresentação visualmente coerente.

#### Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **discord.py**: Biblioteca para interagir com a API do Discord.
- **aiohttp**: Biblioteca para realizar requisições HTTP assíncronas.
- **colorthief**: Biblioteca para extrair a cor dominante de imagens.

#### Como Executar

1. **Pré-requisitos**:
    - Python 3.8 ou superior
    - Bibliotecas: `discord.py`, `aiohttp`, `colorthief`
    
2. **Instalação**:
    - Clone o repositório.
    - Instale as dependências com `pip install -r requirements.txt`.
    
3. **Configuração**:
    - Insira seu token de bot do Discord na função `bot.run('SEU_TOKEN_DO_DISCORD')`.

4. **Execução**:
    - Execute o script Python com `python bot.py`.

Este bot foi projetado para ser uma ferramenta útil e divertida para servidores do Discord, incentivando a competição amigável entre os membros através do acompanhamento de estatísticas e rankings personalizados.
