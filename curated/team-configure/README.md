# team-configure

End-to-end AI team member lifecycle management. Create channel bots, configure AI agents, pair them together, set up inter-agent communication mesh — from a single skill.

**Fully self-contained:** Bundles enconvo-gw gateway (not publicly available), BotFather scripts (Telegram bot management), and Discord Dev scripts (Developer Portal API). Auto-installs [OpenClaw](https://github.com/nicepkg/openclaw) and walks through first-time setup of all dependencies.

## What This Skill Does

### Channel Side (Telegram & Discord)
- **Create bots** — Telegram bots via BotFather, Discord apps via Developer Portal
- **Configure bots** — Set name, description, profile photo, privacy, intents
- **Get tokens** — Extract and manage bot tokens programmatically
- **Invite to servers/groups** — Add bots to Discord servers and Telegram groups

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
- **Full team setup** — From absolute scratch: install dependencies, create all bots, configure all agents, mesh everyone, pair all
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

端到端 AI 团队成员生命周期管理。创建频道机器人、配置 AI 代理、配对连接、设置代理间通信网络 — 一个技能搞定一切。

**完全自包含：** 内置 [enconvo-gw](../enconvo-gw/)（非公开项目），自动安装 [OpenClaw](https://github.com/nicepkg/openclaw)，并引导用户完成所有依赖的首次设置。

## 功能概览

### 频道侧（Telegram 和 Discord）
- **创建机器人** — 通过 BotFather 创建 Telegram 机器人，通过开发者门户创建 Discord 应用
- **配置机器人** — 设置名称、描述、头像、隐私模式、权限意图
- **获取令牌** — 以编程方式提取和管理机器人令牌
- **邀请加入** — 将机器人添加到 Discord 服务器和 Telegram 群组

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
- **从零搭建团队** — 完全从头开始：安装依赖、创建所有机器人、配置所有代理、建立通信网络、完成所有配对
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

Gestion complète du cycle de vie des membres d'une équipe IA. Créez des bots de messagerie, configurez des agents IA, associez-les, mettez en place la communication inter-agents — le tout depuis un seul skill.

**Autonome :** Inclut [enconvo-gw](../enconvo-gw/) (non disponible publiquement), installe automatiquement [OpenClaw](https://github.com/nicepkg/openclaw) et guide l'utilisateur lors de la première configuration de toutes les dépendances.

## Fonctionnalités

### Côté canal (Telegram et Discord)
- **Créer des bots** — Bots Telegram via BotFather, applications Discord via le portail développeur
- **Configurer les bots** — Nom, description, photo, confidentialité, intents
- **Obtenir les tokens** — Extraire et gérer les tokens de bot par programmation
- **Inviter dans les serveurs/groupes** — Ajouter des bots aux serveurs Discord et groupes Telegram

### Côté plateforme IA (OpenClaw et EnConvo)
- **Créer des agents** — Enregistrer de nouveaux agents avec espace de travail, identité et configuration de modèle
- **Routage des canaux** — Lier les comptes de canal à des agents spécifiques via des règles de routage
- **Maillage inter-agents** — Configurer la communication entre agents (maillage complet ou sélectif)
- **Listes d'autorisation de groupes** — Contrôler les groupes/guildes auxquels les agents participent

### Opérations d'équipe
- **Ajouter un membre** — Création de bot + agent + liaison + mise à jour du maillage + appairage
- **Supprimer un membre** — Suppression propre sur tous les canaux et plateformes
- **Configuration complète** — Depuis zéro : installer les dépendances, créer tous les bots, configurer tous les agents, mailler, appairer
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

End-to-End-Lebenszyklusverwaltung für KI-Teammitglieder. Erstellen Sie Kanal-Bots, konfigurieren Sie KI-Agenten, koppeln Sie sie miteinander und richten Sie die Inter-Agenten-Kommunikation ein — alles mit einem einzigen Skill.

**Eigenständig:** Enthält [enconvo-gw](../enconvo-gw/) (nicht öffentlich verfügbar), installiert automatisch [OpenClaw](https://github.com/nicepkg/openclaw) und führt durch die Ersteinrichtung aller Abhängigkeiten.

## Funktionen

### Kanalseite (Telegram und Discord)
- **Bots erstellen** — Telegram-Bots über BotFather, Discord-Apps über das Entwicklerportal
- **Bots konfigurieren** — Name, Beschreibung, Profilbild, Datenschutz, Intents
- **Tokens verwalten** — Bot-Tokens programmatisch extrahieren und verwalten
- **Zu Servern/Gruppen einladen** — Bots zu Discord-Servern und Telegram-Gruppen hinzufügen

### KI-Agenten-Plattform (OpenClaw und EnConvo)
- **Agenten erstellen** — Neue Agenten mit Arbeitsbereich, Identität und Modellkonfiguration registrieren
- **Kanal-Routing** — Kanalkonten über Routing-Regeln an bestimmte Agenten binden
- **Inter-Agenten-Netzwerk** — Kommunikation zwischen Agenten konfigurieren (Vollvernetzung oder selektiv)
- **Gruppen-Allowlists** — Steuern, an welchen Gruppen/Gilden Agenten teilnehmen

### Team-Operationen
- **Mitglied hinzufügen** — Bot + Agent + Bindung + Netzwerk-Update + Kopplung
- **Mitglied entfernen** — Saubere Entfernung über alle Kanäle und Plattformen
- **Team von Grund auf einrichten** — Komplett neu: Abhängigkeiten installieren, alle Bots erstellen, alle Agenten konfigurieren, vernetzen, koppeln
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

End-to-end levenscyclusbeheer voor AI-teamleden. Maak kanaal-bots, configureer AI-agenten, koppel ze aan elkaar en stel inter-agent communicatie in — vanuit één enkele skill.

**Zelfstandig:** Bevat [enconvo-gw](../enconvo-gw/) (niet publiek beschikbaar), installeert automatisch [OpenClaw](https://github.com/nicepkg/openclaw) en begeleidt de gebruiker door de eerste configuratie van alle afhankelijkheden.

## Functies

### Kanaalkant (Telegram en Discord)
- **Bots aanmaken** — Telegram-bots via BotFather, Discord-apps via het ontwikkelaarsportaal
- **Bots configureren** — Naam, beschrijving, profielfoto, privacy, intents
- **Tokens beheren** — Bot-tokens programmatisch extraheren en beheren
- **Uitnodigen voor servers/groepen** — Bots toevoegen aan Discord-servers en Telegram-groepen

### AI-agentplatform (OpenClaw en EnConvo)
- **Agenten aanmaken** — Nieuwe agenten registreren met werkruimte, identiteit en modelconfiguratie
- **Kanaalroutering** — Kanaalaccounts koppelen aan specifieke agenten via routeringsregels
- **Inter-agent mesh** — Communicatie tussen agenten configureren (volledig mesh of selectief)
- **Groep-allowlists** — Bepalen aan welke groepen/guilds agenten deelnemen

### Teamoperaties
- **Lid toevoegen** — Bot + agent + binding + mesh-update + koppeling
- **Lid verwijderen** — Volledige verwijdering over alle kanalen en platformen
- **Team vanaf nul opzetten** — Helemaal opnieuw: afhankelijkheden installeren, alle bots maken, alle agenten configureren, mesh opzetten, koppelen
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

Gestión integral del ciclo de vida de los miembros de un equipo de IA. Cree bots de canal, configure agentes de IA, emparéjelos y establezca la comunicación entre agentes — todo desde una sola skill.

**Autónomo:** Incluye [enconvo-gw](../enconvo-gw/) (no disponible públicamente), instala automáticamente [OpenClaw](https://github.com/nicepkg/openclaw) y guía al usuario en la configuración inicial de todas las dependencias.

## Funcionalidades

### Lado del canal (Telegram y Discord)
- **Crear bots** — Bots de Telegram vía BotFather, aplicaciones de Discord vía el portal de desarrolladores
- **Configurar bots** — Nombre, descripción, foto de perfil, privacidad, intents
- **Obtener tokens** — Extraer y gestionar tokens de bot programáticamente
- **Invitar a servidores/grupos** — Añadir bots a servidores de Discord y grupos de Telegram

### Plataforma de agentes IA (OpenClaw y EnConvo)
- **Crear agentes** — Registrar nuevos agentes con espacio de trabajo, identidad y configuración de modelo
- **Enrutamiento de canales** — Vincular cuentas de canal a agentes específicos mediante reglas de enrutamiento
- **Malla inter-agentes** — Configurar la comunicación entre agentes (malla completa o selectiva)
- **Listas de permitidos de grupos** — Controlar en qué grupos/gremios participan los agentes

### Operaciones de equipo
- **Añadir miembro** — Bot + agente + vinculación + actualización de malla + emparejamiento
- **Eliminar miembro** — Eliminación limpia en todos los canales y plataformas
- **Configuración completa** — Desde cero: instalar dependencias, crear todos los bots, configurar todos los agentes, establecer malla, emparejar
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

Gerenciamento completo do ciclo de vida dos membros de uma equipe de IA. Crie bots de canal, configure agentes de IA, emparelhe-os e configure a comunicação entre agentes — tudo a partir de uma única skill.

**Autossuficiente:** Inclui [enconvo-gw](../enconvo-gw/) (não disponível publicamente), instala automaticamente o [OpenClaw](https://github.com/nicepkg/openclaw) e orienta o usuário na configuração inicial de todas as dependências.

## Funcionalidades

### Lado do canal (Telegram e Discord)
- **Criar bots** — Bots do Telegram via BotFather, aplicativos do Discord via Portal do Desenvolvedor
- **Configurar bots** — Nome, descrição, foto de perfil, privacidade, intents
- **Obter tokens** — Extrair e gerenciar tokens de bot programaticamente
- **Convidar para servidores/grupos** — Adicionar bots a servidores do Discord e grupos do Telegram

### Plataforma de agentes IA (OpenClaw e EnConvo)
- **Criar agentes** — Registrar novos agentes com workspace, identidade e configuração de modelo
- **Roteamento de canais** — Vincular contas de canal a agentes específicos por regras de roteamento
- **Malha inter-agentes** — Configurar a comunicação entre agentes (malha completa ou seletiva)
- **Listas de permissão de grupos** — Controlar em quais grupos/guildas os agentes participam

### Operações de equipe
- **Adicionar membro** — Bot + agente + vinculação + atualização de malha + emparelhamento
- **Remover membro** — Remoção limpa em todos os canais e plataformas
- **Configuração completa** — Do zero: instalar dependências, criar todos os bots, configurar todos os agentes, estabelecer malha, emparelhar
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
