import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)


class MinesweeperGame:
    def __init__(self, bomb_count):
        self.width = 5
        self.height = 5
        self.bomb_count = min(bomb_count, self.width * self.height - 1)
        self.suggested_areas = max(1, round((25 - self.bomb_count) / 2))
        self.board = [[' ' for _ in range(self.width)]
                      for _ in range(self.height)]
        self.revealed_cells = [
            [' ' for _ in range(self.width)] for _ in range(self.height)]
        self.game_over = False
        self.rewarded_times = 0
        self.w_commands_used = 0
        self.p_commands_used = 0

        # Place bombs randomly on the board
        bomb_positions = random.sample(
            range(self.width * self.height), self.bomb_count)
        for position in bomb_positions:
            row = position // self.width
            col = position % self.width
            self.board[row][col] = '💣'

    def display_board(self, reveal=False):
        emojis = {' ': '⬜', '💣': '💣', '💰': '💰', '⭕': '⭕', '✔': '✅'}
        displayed_board = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                if self.revealed_cells[i][j] == ' ' and reveal:
                    row.append(emojis[self.board[i][j]])
                else:
                    row.append(emojis[self.revealed_cells[i][j]])

            displayed_board.append(' '.join(row))

        return '\n'.join(displayed_board)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.command(name='ms')
async def minesweeper(ctx, bombs: int):
    print(f"Command used: !ms {bombs}")

    game = MinesweeperGame(bombs)
    board_message = await ctx.send(f"Here's your Minesweeper board:\n```{game.display_board()}```", reference=ctx.message, mention_author=False)

    await board_message.add_reaction('✅')
    await board_message.add_reaction('❌')

    while not game.game_over:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=lambda r, u: u == ctx.author and r.emoji in ['✅', '❌'])

            if reaction.emoji == '✅':
                # Randomly suggest safe cells to click
                suggested_count = min(
                    game.suggested_areas, game.width * game.height)
                suggested_positions = random.sample(
                    range(game.width * game.height), suggested_count)

                for position in suggested_positions:
                    row = position // game.width
                    col = position % game.width
                    if game.board[row][col] != '💣' and game.revealed_cells[row][col] == ' ':
                        # Randomly decide if it's a safe cell
                        chance = random.uniform(0, 1)
                        # Adjust the probability as needed (70% chance)
                        if chance < 0.7:
                            game.revealed_cells[row][col] = '💰'
                        else:
                            game.revealed_cells[row][col] = '⭕'

                await board_message.edit(content=f"Revealing safe cells and suggesting where to click:\n```{game.display_board(reveal=True)}```")
            elif reaction.emoji == '❌':
                await board_message.edit(content="Game lost! ❌\n" + game.display_board(reveal=True))
                await ctx.send("Punishing the bot! Use !p")
                game.p_commands_used += 1
                break
            else:
                # Handle other reactions if needed
                pass

        except asyncio.TimeoutError:
            await ctx.send("Time's up! The game ended.")
            break


@client.command(name='p')
async def punish(ctx):
    await ctx.send("Punishing the bot!")
    game.p_commands_used += 1


@client.command(name='w')
async def reward(ctx):
    await ctx.send("Rewarding the bot!")
    game.rewarded_times += 1


@client.command(name='m')
async def show_percentage(ctx):
    total_commands_used = game.w_commands_used + game.p_commands_used
    if total_commands_used > 0:
        percentage = (game.rewarded_times / total_commands_used) * 100
        await ctx.send(f"Bot Reward Percentage: {percentage:.2f}% ({game.rewarded_times} times rewarded / {total_commands_used} total commands used)")
    else:
        await ctx.send("Bot has not been rewarded or punished yet.")


@client.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred: {args[0]}")

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
client.run('')
