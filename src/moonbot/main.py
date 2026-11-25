import discord,logging,os,httpx,asyncio,tomllib
from discord.ext import commands, tasks
from dotenv import load_dotenv
from pathlib import Path


#==========================#
#  FILE PATHING & LOGGING  #
#==========================#

BASE_DIR = Path(__file__).resolve().parents[2]    #  goes back 3 file levels as it start at 0/parent
moonbot_log =  BASE_DIR / "moonbot.log"
config_file = BASE_DIR / "config.toml"

logging.basicConfig(
    level=logging.INFO,    #max log level
    filename=moonbot_log,    #log file path
    encoding='utf-8',    #log file system type
    filemode='a',    #log data entry type
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",    #log formating
            #systemtime -   loglevel    -logsource - logmessage
)


#===========================================================================#
#  INTENTS, ENV LOADING, CONFIG LOADING, BOT DEFINITION & GLOBAL variables  #
#===========================================================================#


#run load_dotenv and provide discord token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

with open(config_file, "rb") as f:
    config = tomllib.load(f)

#edits the 'intents' variable from 'discord' and enables intents
intents = discord.Intents.default()
intents.members = True
intents.message_content= True

bot = commands.Bot(command_prefix='*', intents=intents)

admin_channel = bot.get_channel(config["DiscordAdminAlerts"]["alert_channel"])


#======================#
#  DISCORD CONNECTIONS #
#======================#


online = False

#When the bot is fully running, prints a custom msg in the
@bot.event
async def on_online():
    print(f"{bot.user.name} online")
    online = True
    return online

@bot.event
async def on_disconnect():
    print(f"{bot.user.name} disconnected, trying to reconnect to discord API ")
    online = False
    return online

@bot.event
async def on_resumed():
    print(f"{bot.user.name} has reconnected to discord API")
    online = True
    return online

@bot.event
async def on_ready(online):
    if online:   #if followed by nothing, 'if' only triggers with true
        print(f"{bot.user.name} ready for work")
    else:
        print(f"Something wrong has happened with {bot.user.name}, view log for info ")


#==========#
#  EVENTS  #
#==========#

#  ASSIGN A ROLE ON JOIN
#On users joining the server, mentions the users in a designated channel
class OnJoinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_channel = config["OnJoin"]["message_channel"]
        self.join_role = config["OnJoin"]["join_role"]


    @commands.Cog.listener()    #listeners are the cog version of 'on_event'
    async def on_member_join(self, member: discord.Member):    #'guild' is a part of 'member'
        channel = self.bot.get_channel(self.message_channel)

        if channel is None:
            await admin_channel.send("[WARNING] No channel assigned for on join messages ")

        else:
            role = member.guild.get_role(self.join_role)

            if role is None:
                await admin_channel.send("[WARNING] No role assigned for: on join role ")

            else:
                await  member.add_roles(role)
                #  Have to save as a venerable as '.format' only works before its sent
                message = (config["OnJoin"]["join_message"]).format(member=member) #Without '.format' the bot would send 'member' without data.
                await channel.send(message)


#=========================#
#  GAME SERVER FUNCTIONS  #
#=========================#


#  PUBLIC IP CHANGED ALERT
# When the public IP changes, message new IP in a designated channel
class GameServerFunctionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alert_channel = config["GameServerFunctions"]["alert_channel"]
        self.current_ip = None

        self.ipchange.start()    # asyncly starts the background task, ipchange

    #  loops every 5 secs to ping the URL to fetch Public IP
    @tasks.loop(seconds=60)
    async def ipchange(self):
        async with httpx.AsyncClient() as client:
            new_ip = (await client.get('https://api.ipify.org')).text  #outputs everything in a () into a string (.text)

        if self.current_ip is None:
            self.current_ip = new_ip
            return

        if new_ip != self.current_ip:
            channel = self.bot.get_channel(self.alert_channel)

            if channel:
                alert_message = (config["GameServerFunctions"]["alert_message"]).format(new_ip=new_ip)
                await channel.send(alert_message)
                self.current_ip = new_ip

    #  waits until the bot is connected to discord/ready before allowing the loop/task to run
    @ipchange.before_loop
    async def on_ready(self):
        if online:
            await self.bot.wait_until_ready()


#  SELF ASSIGN ALERT ROLE COMMANDS
#  allows users to assign a role to themselves
class SelfAssignedAlertRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def assign(self, ctx, role: discord.Role):
        if role in ctx.author.roles:
            await ctx.send(f"You are already in: {role}.")


        if role.id in config["SelfAssignedAlertRoles"]["roles"]:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention}, You are now in {role}. Welcome!")

        elif role.id not in config["SelfAssignedAlertRoles"]["roles"]:
            await ctx.send(f"You do not have permission to assign yourself {role}.")

    @assign.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("That is not a role on this server")

    #  allows users to remove a role from themselves
    @commands.command()
    async def remove(self, ctx, role: discord.Role):
        if role not in ctx.author.roles:
            await ctx.send(f"You arent in: {role}.",)
            return

        if role.id in config["SelfAssignedAlertRoles"]["roles"]:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention}, You are no longer in {role}. Toodles!")

        elif role.id not in config["SelfAssignedAlertRoles"]["roles"]:
            await ctx.send(f"You do not have permission to remove {role}.")

    @remove.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("That is not a role on this server")



#==================#
#  COG MANAGEMENT  #
#==================#



#=============================#
#  MAIN FUNCTION & BOT START  #
#=============================#


#  Main function, This is to organize the startup sequence
async def main():
    async with bot:     # cleanly shutdowns bot through errors by using "with"
        await bot.add_cog(GameServerFunctionsCog(bot))    # declares cog to bot
        await bot.add_cog(OnJoinCog(bot))
        await bot.add_cog(SelfAssignedAlertRolesCog(bot))
        await bot.start(token)    # Connects discord to the bot, 'start' enables async running

#  runs the bot
asyncio.run(main())    #'asyncio' enables the ability to run async definitions, 'run' enables synced running
