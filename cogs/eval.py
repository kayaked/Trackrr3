import ast
import sys
import json
import discord
from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import aiohttp
import faker
import textwrap
import getpass
import time
from contextlib import redirect_stdout
import io
import shlex
import calendar
import datetime

try:
    import pyduktape
except Exception:
    pass
from os import listdir
from os.path import isfile, join
# to expose to the eval command
from collections import Counter
from cogs.mods.keys import Keys


def is_authorized():
    def predicate(ctx):
        # Thanks rewrite docs!
        return ctx.author.id in [
            232133184404455424,
            356139270446120960
        ]
    return commands.check(predicate)


class Eval(object):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content[3:][:-3].split('\n')[1:])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f"```python\n{e.__class__.__name__}: {e}\n```"
        else:
            pass
        return f'```python\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(pass_context=True, hidden=True, name="js_eval")
    @is_authorized()
    async def _js_eval(self, ctx, *, body: str):
        try:
            jsctx = pyduktape.DuktapeContext()
            jsctx.set_globals(**globals(), ctx=ctx, bot=self.bot, channel=ctx.message.channel)
            a = jsctx.eval_js(self.cleanup_code(body))
            await ctx.send(f'```js\n{a}\n```')
        except NameError:
            await ctx.send('This instance of Trackrr is not eligible for JS evaluation.')

    @commands.command(pass_context=True, hidden=True, name='eval')
    @is_authorized()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'guild': ctx.message.guild,
            'message': ctx.message,
            '_': self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```python\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```python\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```python\n{value}{ret}\n```')

    @commands.command(pass_context=True, hidden=True, name="load")
    @is_authorized()
    async def load(self, ctx, *, module=None):
        """Loads a module."""
        try:
            if module:
                self.bot.load_extension("cogs." + module)
            else:
                for module in [f.replace('.py', "") for f in listdir("cogs") if isfile(join("cogs", f)) and f.endswith('.py')]:
                    self.bot.load_extension("cogs." + module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.message.add_reaction('✅')

    @commands.command(name='api')
    @is_authorized()
    async def api(self, ctx, endpoint, *, args=None):
        args_d = {}
        if args:
            args = shlex.split(args)
            args = [arg for arg in args if '=' in arg]
            for v in args:
                vspl = v.split('=', 1)
                args_d[vspl[0]] = vspl[-1]
        args_d['key'] = Keys.OWNERKEY
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://localhost:8080/{endpoint}', params=args_d, timeout=5) as resp:
                jso = await resp.json()
        await ctx.send(f'```json\n{json.dumps(jso, indent=2)}```')

    @commands.command(pass_context=True, hidden=True, name="unload")
    @is_authorized()
    async def unload(self, ctx, *, module=None):
        """Unloads a module."""
        try:
            if module:
                self.bot.unload_extension("cogs." + module)
            else:
                for module in [f.replace('.py', "") for f in listdir("cogs") if isfile(join("cogs", f)) and f.endswith('.py')]:
                    self.bot.unload_extension("cogs." + module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.message.add_reaction('✅')

    @commands.command(pass_context=True, name='reload', hidden=True, aliases=['rl'])
    @is_authorized()
    async def _reload(self, ctx, *, module=None):
        """Reloads a module."""
        try:
            if module:
                self.bot.unload_extension("cogs." + module)
                self.bot.load_extension("cogs." + module)
            else:
                for module in [f.replace('.py', "") for f in listdir("cogs") if isfile(join("cogs", f)) and f.endswith('.py')]:
                    self.bot.unload_extension("cogs." + module)
                    self.bot.load_extension("cogs." + module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.message.add_reaction('✅')

    @commands.command(name="embed")
    @is_authorized()
    async def embed(self, ctx, *, body):
        body = self.cleanup_code(body)

        try:
            body = json.loads(body)
        except:
            try:
                body = ast.literal_eval(body)
                assert isinstance(body, dict)
            except:
                return await ctx.send("Not a valid embed index! (JSON or python dict)")
        try:
            return await ctx.send(embed=discord.Embed.from_data(body))
        except:
            return await ctx.send("Not a valid embed index! (Missing fields, see leovoel embed visualizer)")


def setup(bot):
    bot.add_cog(Eval(bot))
