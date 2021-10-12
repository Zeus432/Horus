from datetime import datetime
from discord.ext import commands
import discord


class TodoCog(commands.Cog):
    """ A list of commands to manage your task and keep a neat list of your things to do """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.todo_cache = {}
    
    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
    
    class TodoClear(discord.ui.View):
        def __init__(self):
            super().__init__(timeout = 10)
            self.value = None
    
        @discord.ui.button(label= "Confirm", style=discord.ButtonStyle.blurple)
        async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.id != self.user.id:
                return
            await self.message.edit('I have cleared your todo list!')
            self.value = True
            self.stop()
            await self.disableall(button.label)
        
        @discord.ui.button(label= "Cancel", style=discord.ButtonStyle.red)
        async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.id != self.user.id:
                return
            await self.message.edit("Alright I won't clear your todo list then")
            self.stop()
            await self.disableall(button.label)
        
        async def disableall(self, label):
            for item in self.children:
                item.style = discord.ButtonStyle.gray
                item.disabled = True
                if label == item.label:
                    item.style = discord.ButtonStyle.green if label == "Confirm" else discord.ButtonStyle.red
            await self.message.edit(view = self)
        
        async def on_timeout(self):
            await self.message.edit("Alright I won't clear your todo list then")
            await self.disableall("Cancel")
    
    @commands.group(name = "todo", brief = "Todo list related commands", invoke_without_command = True)
    async def todo(self, ctx):
        """ View your todo list """
        try:
            result = self.todo_cache[ctx.author.id]
        except KeyError:
            result = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
            self.todo_cache[ctx.author.id] = result
        if not result:
            return await ctx.send(f"Your todo list is empty. You can add tasks to your todo by running `{ctx.clean_prefix}{ctx.invoked_with} add <task_here>`")
        elif not result['data']:
            return await ctx.send(f"Your todo list is empty. You can add tasks to your todo by running `{ctx.clean_prefix}{ctx.invoked_with} add <task_here>`")
        todostuff = []
        data = result['data']
        for index, dct in enumerate(data):
            todostuff.append(f"**[{index+1})]({data[dct]['messagelink']})** {data[dct]['stuff']}") 
        
        embed = discord.Embed(title = f"**{ctx.author.display_name}**'s todo list:",description = "\n".join(todostuff), color = self.bot.colour)
        await ctx.send(embed = embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @todo.command(name = "add", brief = "Add todo task")
    async def todo_add(self, ctx, *, task: str):
        if len(task) > 50:
            return await ctx.reply('Please reduce the number of letters in your task')

        try:
            result = self.todo_cache[ctx.author.id]
        except KeyError:
            result = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        if not result:
            result = await self.bot.db.fetchrow(f'INSERT INTO todo(userid, lastupdated, data) VALUES($1, $2, $3) ON CONFLICT (userid) DO UPDATE SET lastupdated = $2 RETURNING *', ctx.author.id, int(datetime.timestamp(datetime.now())), {})
        
        self.todo_cache[ctx.author.id] = result

        result['data'][ctx.message.id] = {'messagelink':f'{ctx.message.jump_url}','stuff':f'{task}'}
        self.todo_cache[ctx.author.id] = result

        await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.timestamp(datetime.now())), result['data'])
        await ctx.reply('Your todo list has been updated!')

    @todo.command(name = "remove", brief = "Remove todo task")
    async def remove(self, ctx, id:int):
        """ Remove a task from your todo list"""
        try:
            result = self.todo_cache[ctx.author.id]
        except KeyError:
            result = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        if id > len(result['data']) or id <= 0:
            return await ctx.reply(f"You don't have a task with id: `{id}`")
        for index, dct in enumerate(result['data']):
            if index+1 == id:
                del result['data'][dct]
                await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.timestamp(datetime.now())), result['data'])
                await ctx.reply(f'I have removed task with id: `{id}` from your todo list')
                break
    
    @todo.command(name = "clear", brief = "Clear todo")
    async def clear(self, ctx):
        """ Clear your todo list completely """
        try:
            result = self.todo_cache[ctx.author.id]
        except KeyError:
            result = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        if not result:
            return await ctx.send(f"There is nothing to clear in your todo list. You can add tasks to your todo by running `{ctx.clean_prefix}todo add <task_here>`")
        elif not result['data']:
            return await ctx.send(f"There is nothing to clear in your todo list. You can add tasks to your todo by running `{ctx.clean_prefix}todo add <task_here>`")
        view = self.TodoClear()
        view.message, view.user = await ctx.reply(f'This will clear all your todo tasks (`{len(result["data"])}`). Are you absolutely sure you want to clear your entire list {self.bot.emojislist("vconcerneyes")}?', view = view), ctx.author
        await view.wait()
        print(view.value)
        if view.value:
            result['data'].clear()
            await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.timestamp(datetime.now())), result['data'])

def setup(bot: commands.Bot):
    bot.add_cog(TodoCog(bot))