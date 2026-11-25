# DOOM — Inferno na Terra

Um jogo de tiro em primeira pessoa inspirado em *Doom*, feito em Python com Pygame. O projeto usa ray casting para desenhar um labirinto em perspectiva, com demônios, combate, ondas progressivas e uma interface em português.

> Projeto independente e experimental, sem vínculo oficial com a franquia *Doom*.

## Recursos

- Visão em primeira pessoa com paredes sombreadas e perspectiva.
- Movimento com colisão contra as paredes do mapa.
- Demônios que perseguem o jogador quando conseguem vê-lo e atacam a curta distância.
- Combate com escopeta, mira, clarão de disparo e munição limitada por rodada.
- Ondas contínuas: cada nova onda traz mais inimigos, com até três ativos ao mesmo tempo.
- Recuperação de 25 pontos de vida e 10 cartuchos ao concluir uma onda. A vida tem limite de 100 pontos.
- Painel com vida, munição, abates e onda atual.
- Tela de derrota com opção para recomeçar.

## Requisitos

- Python 3.10 ou mais recente.
- Pygame 2.6.1, instalado pelo arquivo `requirements.txt`.

## Instalação e execução

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/weskerxvi/doom-python.git
cd doom-python
```

Crie um ambiente virtual e instale as dependências.

### Windows — PowerShell

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Linux e macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

O jogo abre em uma janela de 960 × 600 pixels e captura o mouse para mirar. Execute-o pelo terminal para visualizar mensagens de erro caso a janela feche inesperadamente.

## Controles

| Ação | Controle |
| --- | --- |
| Avançar e recuar | `W` / `S` ou `↑` / `↓` |
| Mover para os lados | `A` / `D` |
| Mirar | Mouse ou `←` / `→` |
| Atirar | Clique esquerdo ou `Espaço` |
| Recomeçar após a derrota | `R` |
| Sair | `Esc` ou fechar a janela |

## Como funciona

O cenário é um mapa em grade definido no início de `main.py`. A classe `Mundo` consulta esse mapa para detectar paredes, verificar a linha de visão e lançar os raios usados na renderização. A classe `Jogo` controla entrada, movimento, inimigos, combate, ondas e desenho da tela. Cada demônio é representado pela classe `Demonio`.

O jogador começa com 100 pontos de vida e 30 cartuchos. Os demônios precisam de dois disparos para serem derrotados. Ao concluir uma onda, o jogador recebe vida e munição, e a próxima onda começa automaticamente. Se a vida chegar a zero, pressione `R` para iniciar uma nova partida.

## Estrutura do projeto

```text
doom-python/
├── main.py           # Lógica e execução do jogo
├── requirements.txt  # Dependências Python
└── README.md         # Documentação do projeto
```

## Dependências

As dependências estão fixadas em `requirements.txt`:

```text
pygame==2.6.1
```

## Contribuidores

- [weskerxvi](https://github.com/weskerxvi) — responsável pelo repositório.
- **OpenAI Codex** — assistência na implementação e na documentação deste projeto.

O crédito ao OpenAI Codex identifica a assistência de IA neste README. O gráfico automático de contribuidores do GitHub associa commits a contas por e-mail; não há uma conta GitHub própria do Codex para vincular a esse gráfico.
