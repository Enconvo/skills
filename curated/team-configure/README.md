# team-configure

End-to-end AI team member lifecycle management. Tell the AI about your company and it designs the team, creates bots, configures agents with full profiles and portraits, sets up inter-agent mesh, creates group channels, and pairs everything — fully automated.

**Fully self-contained:** Bundles enconvo-gw gateway (not publicly available), BotFather scripts (Telegram bot management), and Discord Dev scripts (Developer Portal API). Auto-installs [OpenClaw](https://github.com/nicepkg/openclaw) and walks through first-time setup of all dependencies.

## What This Skill Does

### Team Discovery & Design
- **Understand your business** — Ask about industry, company focus, team goals
- **Propose team composition** — AI suggests team size, roles, names based on your needs
- **Designate team lead** — The `main` agent coordinates the team
- **User approval** — Review and adjust before building

### Agent Identity & Profiles
- **Generate portraits** — Professional C-suite office portraits per agent, different cities/styles
- **EnConvo profiles** — Create IDENTITY.md, SOUL.md, USER.md, TOOLS.md, AGENTS.md per agent
- **OpenClaw workspaces** — TOOLS.md with role, collaborators, office setting
- **Bot profile photos** — Set portraits as Telegram/Discord bot avatars
- **EnConvo bot creation** — Custom bot with LLM model, tools, system prompt per agent

### Channel Side (Telegram & Discord)
- **Create bots** — Telegram bots via BotFather, Discord apps via Developer Portal
- **Configure bots** — Set name, description, profile photo, privacy, intents
- **Get tokens** — Extract and manage bot tokens programmatically
- **Create groups** — Create Telegram groups and Discord servers for the team
- **Add all bots** — Invite all team member bots to the group, @mention-based interaction

### AI Agent Platform Side (OpenClaw & EnConvo)
- **Create agents** — Register new agents with workspace, identity, and model config
- **Channel routing** — Bind channel accounts to specific agents via routing rules
- **Inter-agent mesh** — Configure which agents can communicate with each other (full mesh or selective)
- **Group allowlists** — Control which groups/guilds agents participate in

### Pairing (Connecting Channels to Agents)
- **Trigger pairing** — Bot sends pairing code when user sends `/start`
- **Approve pairing** — Programmatically approve pairing codes to authorize users
- **Per-user access** — Each user pairs individually with each bot

### Team Operations
- **Add member** — Ad-hoc: create bot + agent + bind + mesh update + pair, one member at a time
- **Remove member** — Clean removal across all channels and platforms
- **Full team setup** — From "I run a hedge fund" to fully operational 7-person team with portraits and live bots
- **Update mesh** — Recalculate and apply full agent-to-agent communication graph
- **Manage allowlists** — Control group/guild participation per agent

## Quick Start

```bash
# Check what's installed
bash scripts/setup.sh status

# Bootstrap everything (OpenClaw + enconvo-gw + auth checks)
bash scripts/setup.sh all

# Then use via Claude Code / OpenClaw — the SKILL.md guides the AI through any operation
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    team-configure                     │
│                                                       │
│  Channel Side              AI Platform Side           │
│  ┌──────────┐              ┌────────────┐            │
│  │ BotFather│─── tokens ──▶│  OpenClaw   │            │
│  │(Telegram)│              │  (agents,   │            │
│  └──────────┘              │  channels,  │            │
│  ┌──────────┐              │  bindings,  │            │
│  │Discord   │─── tokens ──▶│  mesh)      │            │
│  │Dev Portal│              └────────────┘            │
│  └──────────┘              ┌────────────┐            │
│                            │ enconvo-gw  │            │
│      ◀── pairing codes ──▶│ (bundled)   │            │
│                            └────────────┘            │
└─────────────────────────────────────────────────────┘
```

### Gateway Operations (enconvo-gw)
- **Claude Code agent** — Session management (`--session-id`, `--resume`, `/reset`), system prompt injection
- **Media handling** — Inbound (user uploads) and outbound (agent-generated files) with auto-upload to channels
- **DM access policies** — Open, allowlist, or pairing-based access control per bot
- **Streaming** — Progressive message editing for real-time response display
- **Discord specifics** — `MessageContent` intent, 2000-char chunking, `!reset` command
- **OpenClaw coexistence** — Rules for running alongside OpenClaw without token conflicts
- **Troubleshooting** — 10 common symptom/cause/fix scenarios

## File Structure

```
team-configure/
├── SKILL.md                    # Complete AI instructions (850+ lines)
├── README.md                   # This file
├── scripts/
│   └── setup.sh                # Bootstrap: install/update all dependencies
├── enconvo-gw/                 # Bundled gateway source (not on npm)
│   ├── bin/enconvo-gw.js       # CLI entry point
│   ├── src/                    # Node.js ESM source (20 files)
│   ├── package.json            # grammy + discord.js + commander
│   └── package-lock.json
└── skills/
    ├── botfather/              # Bundled BotFather skill (Telegram bot management)
    │   ├── botfather.py        # Python CLI (Telethon + argparse, 509 lines)
    │   ├── botfather.sh        # Shell wrapper (ensures venv + telethon)
    │   └── SKILL.md            # BotFather-specific documentation
    └── discord-dev/            # Bundled Discord Dev skill (Developer Portal API)
        ├── discord-dev.py      # Python CLI (stdlib only, no deps, 450 lines)
        ├── discord-dev.sh      # Shell wrapper
        └── SKILL.md            # Discord Dev-specific documentation
```

## Dependencies

| Dependency | Source | Installed by |
|-----------|--------|-------------|
| [OpenClaw](https://github.com/nicepkg/openclaw) | npm (public) | `setup.sh` auto-installs |
| enconvo-gw | Bundled in `enconvo-gw/` | `setup.sh` deploys to `~/enconvo-gw/` |
| BotFather scripts | Bundled in `skills/botfather/` | Used directly from skill dir |
| Discord Dev scripts | Bundled in `skills/discord-dev/` | Used directly from skill dir |
| Node.js 18+ | System | User installs |

## Requirements

- **Node.js 18+** and npm
- **Telegram account** — for BotFather API credentials (Telethon auth)
- **Discord account** — for Developer Portal token extraction (browser-based)
- **Claude Code** or **OpenClaw** — as the AI agent runtime

## Documentation

See [SKILL.md](SKILL.md) for the complete reference: bootstrap walkthrough, all CLI commands, config schemas, step-by-step workflows for every operation, and troubleshooting.

---

# team-configure [中文]

端到端 AI 团队成员生命周期管理。告诉 AI 你的公司情况，它会设计团队、创建机器人、配置完整的代理档案和肖像、建立代理间通信网络、创建群组频道并完成配对 — 全程自动化。

**完全自包含：** 内置 [enconvo-gw](../enconvo-gw/)（非公开项目），自动安装 [OpenClaw](https://github.com/nicepkg/openclaw)，并引导用户完成所有依赖的首次设置。

## 功能概览

### 团队发现与设计
- **了解业务** — 询问行业、公司重点、团队目标
- **提议团队组成** — AI 根据需求建议团队规模、角色、名称
- **指定团队负责人** — `main` 代理协调整个团队
- **用户审批** — 构建前审查和调整

### 代理身份与档案
- **生成肖像** — 每个代理的专业 C-suite 办公室肖像，不同城市/风格
- **EnConvo 档案** — 为每个代理创建 IDENTITY.md、SOUL.md、USER.md、TOOLS.md、AGENTS.md
- **OpenClaw 工作区** — 包含角色、协作者、办公环境的 TOOLS.md
- **机器人头像** — 将肖像设置为 Telegram/Discord 机器人头像
- **EnConvo 机器人创建** — 为每个代理配置自定义机器人（LLM 模型、工具、系统提示）

### 频道侧（Telegram 和 Discord）
- **创建机器人** — 通过 BotFather 创建 Telegram 机器人，通过开发者门户创建 Discord 应用
- **配置机器人** — 设置名称、描述、头像、隐私模式、权限意图
- **获取令牌** — 以编程方式提取和管理机器人令牌
- **创建群组** — 为团队创建 Telegram 群组和 Discord 服务器
- **添加所有机器人** — 邀请所有团队成员机器人加入群组，基于 @提及 交互

### AI 代理平台侧（OpenClaw 和 EnConvo）
- **创建代理** — 注册新代理，配置工作区、身份和模型
- **频道路由** — 通过路由规则将频道账户绑定到特定代理
- **代理间通信网络** — 配置代理之间的通信权限（全网格或选择性连接）
- **群组白名单** — 控制代理参与哪些群组/公会

### 配对（连接频道与代理）
- **触发配对** — 用户发送 `/start` 时机器人返回配对码
- **批准配对** — 以编程方式批准配对码以授权用户
- **逐用户授权** — 每个用户单独与每个机器人配对

### 团队操作
- **添加成员** — 临时操作：创建机器人 + 代理 + 绑定 + 网络更新 + 配对
- **移除成员** — 在所有频道和平台上彻底清除
- **从零搭建团队** — 从"我经营一家对冲基金"到拥有肖像和实时机器人的完整 7 人团队
- **更新通信网络** — 重新计算并应用完整的代理间通信图
- **管理白名单** — 按代理控制群组/公会参与权限

### 网关运维（enconvo-gw）
- **Claude Code 代理** — 会话管理（`--session-id`、`--resume`、`/reset`）、系统提示注入
- **媒体处理** — 入站（用户上传）和出站（代理生成文件）自动上传至频道
- **DM 访问策略** — 开放、白名单或配对码授权，按机器人配置
- **流式响应** — 渐进式消息编辑，实时显示回复
- **Discord 特性** — `MessageContent` 意图、2000字符分块、`!reset` 命令
- **OpenClaw 共存** — 与 OpenClaw 并行运行的令牌冲突规避规则
- **故障排查** — 10种常见问题/原因/解决方案

## 快速开始

```bash
# 检查已安装的组件
bash scripts/setup.sh status

# 引导安装所有依赖
bash scripts/setup.sh all
```

---

# team-configure [Français]

Gestion complète du cycle de vie d'une équipe IA. Décrivez votre entreprise et l'IA conçoit l'équipe, crée les bots, configure les profils complets avec portraits, établit le maillage inter-agents, crée les groupes et apparie le tout — entièrement automatisé.

**Autonome :** Inclut [enconvo-gw](../enconvo-gw/) (non disponible publiquement), installe automatiquement [OpenClaw](https://github.com/nicepkg/openclaw) et guide l'utilisateur lors de la première configuration de toutes les dépendances.

## Fonctionnalités

### Découverte et conception d'équipe
- **Comprendre l'entreprise** — Questions sur l'industrie, les objectifs
- **Proposer la composition** — Taille, rôles, noms suggérés par l'IA
- **Profils agents** — IDENTITY.md, SOUL.md, TOOLS.md, portraits par agent
- **Création bots EnConvo** — Modèle LLM, outils, prompt système par agent

### Côté canal (Telegram et Discord)
- **Créer des bots** — Bots Telegram via BotFather, applications Discord via le portail développeur
- **Configurer les bots** — Nom, description, photo, confidentialité, intents
- **Obtenir les tokens** — Extraire et gérer les tokens de bot par programmation
- **Créer des groupes** — Groupes Telegram et serveurs Discord pour l'équipe
- **Inviter tous les bots** — Interaction basée sur les @mentions

### Côté plateforme IA (OpenClaw et EnConvo)
- **Créer des agents** — Enregistrer de nouveaux agents avec espace de travail, identité et configuration de modèle
- **Routage des canaux** — Lier les comptes de canal à des agents spécifiques via des règles de routage
- **Maillage inter-agents** — Configurer la communication entre agents (maillage complet ou sélectif)
- **Listes d'autorisation de groupes** — Contrôler les groupes/guildes auxquels les agents participent

### Opérations d'équipe
- **Ajouter un membre** — Création de bot + agent + liaison + mise à jour du maillage + appairage
- **Supprimer un membre** — Suppression propre sur tous les canaux et plateformes
- **Configuration complète** — De « je dirige un fonds » à une équipe opérationnelle avec portraits et bots actifs
- **Mettre à jour le maillage** — Recalculer et appliquer le graphe de communication inter-agents

### Opérations passerelle (enconvo-gw)
- **Agent Claude Code** — Gestion de session (`--session-id`, `--resume`, `/reset`), injection de prompt système
- **Gestion des médias** — Entrants (uploads utilisateur) et sortants (fichiers générés) avec envoi automatique
- **Politiques d'accès DM** — Ouvert, liste blanche ou appairage par code
- **Streaming** — Édition progressive des messages pour un affichage en temps réel
- **Spécificités Discord** — Intent `MessageContent`, découpage 2000 caractères, commande `!reset`
- **Coexistence OpenClaw** — Règles pour éviter les conflits de tokens
- **Dépannage** — 10 scénarios problème/cause/solution courants

## Démarrage rapide

```bash
bash scripts/setup.sh status    # Vérifier l'état
bash scripts/setup.sh all       # Tout installer
```

---

# team-configure [Deutsch]

End-to-End KI-Team-Aufbau. Beschreiben Sie Ihr Unternehmen und die KI entwirft das Team, erstellt Bots, konfiguriert vollständige Profile mit Porträts, richtet das Inter-Agenten-Netzwerk ein, erstellt Gruppenkanäle und koppelt alles — vollautomatisch.

**Eigenständig:** Enthält [enconvo-gw](../enconvo-gw/) (nicht öffentlich verfügbar), installiert automatisch [OpenClaw](https://github.com/nicepkg/openclaw) und führt durch die Ersteinrichtung aller Abhängigkeiten.

## Funktionen

### Team-Entdeckung und -Design
- **Unternehmen verstehen** — Fragen zu Branche, Zielen
- **Zusammensetzung vorschlagen** — Größe, Rollen, Namen von der KI vorgeschlagen
- **Agenten-Profile** — IDENTITY.md, SOUL.md, TOOLS.md, Porträts pro Agent
- **EnConvo-Bot-Erstellung** — LLM-Modell, Tools, System-Prompt pro Agent

### Kanalseite (Telegram und Discord)
- **Bots erstellen** — Telegram-Bots über BotFather, Discord-Apps über das Entwicklerportal
- **Bots konfigurieren** — Name, Beschreibung, Profilbild, Datenschutz, Intents
- **Tokens verwalten** — Bot-Tokens programmatisch extrahieren und verwalten
- **Gruppen erstellen** — Telegram-Gruppen und Discord-Server für das Team
- **Alle Bots einladen** — @Mention-basierte Interaktion

### KI-Agenten-Plattform (OpenClaw und EnConvo)
- **Agenten erstellen** — Neue Agenten mit Arbeitsbereich, Identität und Modellkonfiguration registrieren
- **Kanal-Routing** — Kanalkonten über Routing-Regeln an bestimmte Agenten binden
- **Inter-Agenten-Netzwerk** — Kommunikation zwischen Agenten konfigurieren (Vollvernetzung oder selektiv)
- **Gruppen-Allowlists** — Steuern, an welchen Gruppen/Gilden Agenten teilnehmen

### Team-Operationen
- **Mitglied hinzufügen** — Bot + Agent + Bindung + Netzwerk-Update + Kopplung
- **Mitglied entfernen** — Saubere Entfernung über alle Kanäle und Plattformen
- **Team von Grund auf einrichten** — Von „Ich leite einen Hedgefonds" zu einem 7-köpfigen Team mit Porträts und Live-Bots
- **Netzwerk aktualisieren** — Inter-Agenten-Kommunikationsgraph neu berechnen und anwenden

### Gateway-Betrieb (enconvo-gw)
- **Claude Code Agent** — Sitzungsverwaltung (`--session-id`, `--resume`, `/reset`), System-Prompt-Injektion
- **Medienverarbeitung** — Eingehend (Benutzer-Uploads) und ausgehend (Agent-generierte Dateien) mit Auto-Upload
- **DM-Zugriffsrichtlinien** — Offen, Allowlist oder Pairing-basierte Zugriffskontrolle
- **Streaming** — Progressive Nachrichtenbearbeitung für Echtzeit-Anzeige
- **Discord-Spezifisches** — `MessageContent`-Intent, 2000-Zeichen-Chunking, `!reset`-Befehl
- **OpenClaw-Koexistenz** — Regeln zur Vermeidung von Token-Konflikten
- **Fehlerbehebung** — 10 häufige Symptom/Ursache/Lösung-Szenarien

## Schnellstart

```bash
bash scripts/setup.sh status    # Status prüfen
bash scripts/setup.sh all       # Alles installieren
```

---

# team-configure [Nederlands]

End-to-end AI-teamopbouw. Vertel de AI over uw bedrijf en het ontwerpt het team, maakt bots, configureert volledige profielen met portretten, stelt inter-agent communicatie in, maakt groepskanalen en koppelt alles — volledig geautomatiseerd.

**Zelfstandig:** Bevat [enconvo-gw](../enconvo-gw/) (niet publiek beschikbaar), installeert automatisch [OpenClaw](https://github.com/nicepkg/openclaw) en begeleidt de gebruiker door de eerste configuratie van alle afhankelijkheden.

## Functies

### Teamontdekking en -ontwerp
- **Bedrijf begrijpen** — Vragen over branche, doelen
- **Samenstelling voorstellen** — Grootte, rollen, namen voorgesteld door AI
- **Agentprofielen** — IDENTITY.md, SOUL.md, TOOLS.md, portretten per agent
- **EnConvo-botcreatie** — LLM-model, tools, systeemprompt per agent

### Kanaalkant (Telegram en Discord)
- **Bots aanmaken** — Telegram-bots via BotFather, Discord-apps via het ontwikkelaarsportaal
- **Bots configureren** — Naam, beschrijving, profielfoto, privacy, intents
- **Tokens beheren** — Bot-tokens programmatisch extraheren en beheren
- **Groepen aanmaken** — Telegram-groepen en Discord-servers voor het team
- **Alle bots uitnodigen** — @Mention-gebaseerde interactie

### AI-agentplatform (OpenClaw en EnConvo)
- **Agenten aanmaken** — Nieuwe agenten registreren met werkruimte, identiteit en modelconfiguratie
- **Kanaalroutering** — Kanaalaccounts koppelen aan specifieke agenten via routeringsregels
- **Inter-agent mesh** — Communicatie tussen agenten configureren (volledig mesh of selectief)
- **Groep-allowlists** — Bepalen aan welke groepen/guilds agenten deelnemen

### Teamoperaties
- **Lid toevoegen** — Bot + agent + binding + mesh-update + koppeling
- **Lid verwijderen** — Volledige verwijdering over alle kanalen en platformen
- **Team vanaf nul opzetten** — Van "ik run een hedgefonds" tot een volledig team met portretten en live bots
- **Mesh bijwerken** — Inter-agent communicatiegraaf herberekenen en toepassen

### Gateway-operaties (enconvo-gw)
- **Claude Code agent** — Sessiebeheer (`--session-id`, `--resume`, `/reset`), systeem-prompt injectie
- **Mediaverwerking** — Inkomend (gebruiker uploads) en uitgaand (agent-gegenereerde bestanden) met auto-upload
- **DM-toegangsbeleid** — Open, allowlist of pairing-gebaseerde toegangscontrole
- **Streaming** — Progressieve berichtbewerking voor realtime weergave
- **Discord-specifiek** — `MessageContent` intent, 2000-teken chunking, `!reset` commando
- **OpenClaw coëxistentie** — Regels om tokenconflicten te vermijden
- **Probleemoplossing** — 10 veelvoorkomende symptoom/oorzaak/oplossing-scenario's

## Snel starten

```bash
bash scripts/setup.sh status    # Status controleren
bash scripts/setup.sh all       # Alles installeren
```

---

# team-configure [Español]

Configuración integral de equipos de IA. Describa su empresa y la IA diseña el equipo, crea bots, configura perfiles completos con retratos, establece la malla inter-agentes, crea grupos y empareja todo — totalmente automatizado.

**Autónomo:** Incluye [enconvo-gw](../enconvo-gw/) (no disponible públicamente), instala automáticamente [OpenClaw](https://github.com/nicepkg/openclaw) y guía al usuario en la configuración inicial de todas las dependencias.

## Funcionalidades

### Descubrimiento y diseño de equipo
- **Entender el negocio** — Preguntas sobre industria, objetivos
- **Proponer composición** — Tamaño, roles, nombres sugeridos por la IA
- **Perfiles de agentes** — IDENTITY.md, SOUL.md, TOOLS.md, retratos por agente
- **Creación de bots EnConvo** — Modelo LLM, herramientas, prompt del sistema por agente

### Lado del canal (Telegram y Discord)
- **Crear bots** — Bots de Telegram vía BotFather, aplicaciones de Discord vía el portal de desarrolladores
- **Configurar bots** — Nombre, descripción, foto de perfil, privacidad, intents
- **Obtener tokens** — Extraer y gestionar tokens de bot programáticamente
- **Crear grupos** — Grupos de Telegram y servidores de Discord para el equipo
- **Invitar todos los bots** — Interacción basada en @menciones

### Plataforma de agentes IA (OpenClaw y EnConvo)
- **Crear agentes** — Registrar nuevos agentes con espacio de trabajo, identidad y configuración de modelo
- **Enrutamiento de canales** — Vincular cuentas de canal a agentes específicos mediante reglas de enrutamiento
- **Malla inter-agentes** — Configurar la comunicación entre agentes (malla completa o selectiva)
- **Listas de permitidos de grupos** — Controlar en qué grupos/gremios participan los agentes

### Operaciones de equipo
- **Añadir miembro** — Bot + agente + vinculación + actualización de malla + emparejamiento
- **Eliminar miembro** — Eliminación limpia en todos los canales y plataformas
- **Configuración completa** — De "dirijo un fondo" a un equipo operativo con retratos y bots activos
- **Actualizar malla** — Recalcular y aplicar el grafo de comunicación inter-agentes

### Operaciones de pasarela (enconvo-gw)
- **Agente Claude Code** — Gestión de sesiones (`--session-id`, `--resume`, `/reset`), inyección de prompt del sistema
- **Manejo de medios** — Entrantes (subidas de usuario) y salientes (archivos generados) con subida automática
- **Políticas de acceso DM** — Abierto, lista de permitidos o emparejamiento por código
- **Streaming** — Edición progresiva de mensajes para visualización en tiempo real
- **Especificidades de Discord** — Intent `MessageContent`, fragmentación de 2000 caracteres, comando `!reset`
- **Coexistencia con OpenClaw** — Reglas para evitar conflictos de tokens
- **Solución de problemas** — 10 escenarios comunes de síntoma/causa/solución

## Inicio rápido

```bash
bash scripts/setup.sh status    # Verificar estado
bash scripts/setup.sh all       # Instalar todo
```

---

# team-configure [Português]

Configuração completa de equipes de IA. Descreva sua empresa e a IA projeta a equipe, cria bots, configura perfis completos com retratos, estabelece a malha inter-agentes, cria grupos e emparelha tudo — totalmente automatizado.

**Autossuficiente:** Inclui [enconvo-gw](../enconvo-gw/) (não disponível publicamente), instala automaticamente o [OpenClaw](https://github.com/nicepkg/openclaw) e orienta o usuário na configuração inicial de todas as dependências.

## Funcionalidades

### Descoberta e design de equipe
- **Entender o negócio** — Perguntas sobre indústria, objetivos
- **Propor composição** — Tamanho, funções, nomes sugeridos pela IA
- **Perfis de agentes** — IDENTITY.md, SOUL.md, TOOLS.md, retratos por agente
- **Criação de bots EnConvo** — Modelo LLM, ferramentas, prompt do sistema por agente

### Lado do canal (Telegram e Discord)
- **Criar bots** — Bots do Telegram via BotFather, aplicativos do Discord via Portal do Desenvolvedor
- **Configurar bots** — Nome, descrição, foto de perfil, privacidade, intents
- **Obter tokens** — Extrair e gerenciar tokens de bot programaticamente
- **Criar grupos** — Grupos do Telegram e servidores do Discord para a equipe
- **Convidar todos os bots** — Interação baseada em @menções

### Plataforma de agentes IA (OpenClaw e EnConvo)
- **Criar agentes** — Registrar novos agentes com workspace, identidade e configuração de modelo
- **Roteamento de canais** — Vincular contas de canal a agentes específicos por regras de roteamento
- **Malha inter-agentes** — Configurar a comunicação entre agentes (malha completa ou seletiva)
- **Listas de permissão de grupos** — Controlar em quais grupos/guildas os agentes participam

### Operações de equipe
- **Adicionar membro** — Bot + agente + vinculação + atualização de malha + emparelhamento
- **Remover membro** — Remoção limpa em todos os canais e plataformas
- **Configuração completa** — De "eu dirijo um fundo" a uma equipe operacional com retratos e bots ativos
- **Atualizar malha** — Recalcular e aplicar o grafo de comunicação inter-agentes

### Operações de gateway (enconvo-gw)
- **Agente Claude Code** — Gerenciamento de sessão (`--session-id`, `--resume`, `/reset`), injeção de prompt do sistema
- **Manipulação de mídia** — Entrada (uploads do usuário) e saída (arquivos gerados) com upload automático
- **Políticas de acesso DM** — Aberto, lista de permitidos ou emparelhamento por código
- **Streaming** — Edição progressiva de mensagens para exibição em tempo real
- **Especificidades do Discord** — Intent `MessageContent`, fragmentação de 2000 caracteres, comando `!reset`
- **Coexistência com OpenClaw** — Regras para evitar conflitos de tokens
- **Solução de problemas** — 10 cenários comuns de sintoma/causa/solução

## Início rápido

```bash
bash scripts/setup.sh status    # Verificar status
bash scripts/setup.sh all       # Instalar tudo
```

---

## License

MIT
