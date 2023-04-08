from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import hikari
import lightbulb
from discord import SyncWebhook # Import SyncWebhook
from csv import writer
from better_profanity import profanity
from tinydb import TinyDB, Query
import random
import openai

App = Query()
db = TinyDB('data.json')

chatbot = ChatBot(
    "kitten", 
    read_only=False
    )



bot = lightbulb.BotApp(
    token="MTA3Mjg3OTcyNzc1MDE2MDQ5Nw.GO7ZPk.QsGYWJxeWyIH-xbHwBLGBGmuOpAV1AiqNaCRnE",
    help_slash_command=True,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT 
)

@bot.listen(hikari.StartedEvent)
async def bot_started(event):
    print('Bot has started.')
    guilds = await bot.rest.fetch_my_guilds()
    server_count = len(guilds)
    await bot.update_presence(
        status=hikari.Status.ONLINE,
        activity=hikari.Activity(
            name=f"Kitten is used in {server_count} servers!",
            type=hikari.ActivityType.PLAYING
        )
    )
    print(f"My bot is in {server_count} servers.")


"""
    webhook = SyncWebhook.from_url('https://discord.com/api/webhooks/1054075338533109780/8ZeIdyQydFwUyDOD6rNWxFopZ31Gbg1EmTo6tOlyGIF37pH-f5oPvcGLbmNsWe5yOjd_') # Initializing webhook
    webhook.send(content="Bot online :white_check_mark:") # Executing webhook.
"""

@bot.command()
@lightbulb.option(name="query", description="What do you want to say", type=str, required=True)
@lightbulb.command("query", "Ask the bot something")
@lightbulb.implements(lightbulb.SlashCommand)
async def ask(ctx: lightbulb.SlashContext) -> None:

    #trainer = ListTrainer(chatbot)
    guild_id = ctx.guild_id
    user_id = ctx.author.id
    user = db.search(App.user == user_id)
    if user == []:
        db.insert({'read': "False", 'user': user_id, 'gpt': 0, 'dm': "yes"})
        await ctx.respond("WARNING: All of the responses you get here are AI generated and are not controlled. If you are in a language sensitive server have a user with `ADMINSTRATOR` set the profanity filter on. Use the command again to get past this warning.\nIf you get a response that seems incorrect use `/correct` to request a training for that word/sentence. This bot is in BETA.. Many errors will occur\n``This bot learns and self corrects based off common responses...keep this in mind. The more queries the better trained it will become.``")
        db.update({'read': "True"}, App.user == user_id)
        return
        
    results =db.search(App.guild == guild_id)
    # If guild is not in the data file add it
    if results == []:
        db.insert({'guild': guild_id, 'prof': "False"})
        results =db.search(App.guild == guild_id)
    # Check if profanity filter setting is enabled
    if results[0]['prof'] == "True":
        xit_conditions = (":q", "quit", "exit")
        query = ctx.options.query
        response = chatbot.get_response(query)
        profanity.load_censor_words()

        censored_text = profanity.censor(response)
        respond = hikari.Embed(
            title=f"Query: {query}",
            description=f"Kitten: {censored_text}",
            color="#00FF00",

            )
        id = random.randint(10000, 99999)
        results = db.search(App.id == id)
        if results == []:
            respond.set_footer(f"User: {ctx.author}; Made by brncray 🔺#6770; ID: {id}")
            await ctx.respond(respond)
            db.insert({'user_id': ctx.author.id, 'query': query, 'response': censored_text, 'id': id})
        else:
            db.remove(App.id == id)
            respond.set_footer(f"User: {ctx.author}; Made by brncray 🔺#6770; ID: {id}")
            await ctx.respond(respond)
            db.insert({'user_id': ctx.author.id, 'query': query, 'response': censored_text, 'id': id})
        # Log to data.csv
        """
        List = [f' user: {ctx.author.id}', f' query: {query}', f' response: {censored_text}']
        with open('data.csv', 'a') as f_object:
    
            # Pass this file object to csv.writer()
            # and get a writer object
            writer_object = writer(f_object)
        
            # Pass the list as an argument into
            # the writerow()
            writer_object.writerow(List)
        
            # Close the file object
            f_object.close()
        """
    else:
        exit_conditions = (":q", "quit", "exit")
        query = ctx.options.query
        response = chatbot.get_response(query)
        profanity.load_censor_words(whitelist_words=['gay'])

        censored_text = profanity.censor(response)
        respond = hikari.Embed(
            title=f"Query: {query}",
            description=f"Kitten: {response}",
            color="#00FF00",

            )
        id = random.randint(10000, 99999)
        results = db.search(App.id == id)
        if results == []:
            respond.set_footer(f"User: {ctx.author}; Made by brncray 🔺#6770; ID: {id}")
            await ctx.respond(respond)
            db.insert({'user_id': ctx.author.id, 'query': query, 'response': censored_text, 'id': id})
        else:
            db.remove(App.id == id)
            respond.set_footer(f"User: {ctx.author}; Made by brncray 🔺#6770; ID: {id}")
            await ctx.respond(respond)
            db.insert({'user_id': ctx.author.id, 'query': query, 'response': censored_text, 'id': id})
            

        """
        List = [f' user: {ctx.author.id}', f' query: {query}', f' response: {censored_text}']
        with open('data.csv', 'a') as f_object:
    
            # Pass this file object to csv.writer()
            # and get a writer object
            writer_object = writer(f_object)
        
            # Pass the list as an argument into
            # the writerow()
            writer_object.writerow(List)
        
            # Close the file object
            f_object.close()
        """







@bot.command()
@lightbulb.option(name="bot", description="What you want bot to say", type=str, required=True)
@lightbulb.option(name="you", description="What you say", type=str, required=True)
@lightbulb.command("train", "Train the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def train(ctx: lightbulb.SlashContext) -> None:
    if ctx.author.id != 539213950688952320:
        if ctx.author.id != 488070555967160370:
            await ctx.respond("You are not authorized to use this command")
            return
    trainer = ListTrainer(chatbot)


    trainer.train([
        ctx.options.you,
        ctx.options.bot
    ])
    await ctx.respond("Training succesful!")

@bot.command()
@lightbulb.option(name="proper", description="What it should say", type=str, required=True)
@lightbulb.option(name="query_id", description="ID of the query. Displayed at the bottom of the response", type=int, required=True)
@lightbulb.command("correct", "Sends a correction request to fix a response that the bot said")
@lightbulb.implements(lightbulb.SlashCommand)
async def correct(ctx: lightbulb.SlashContext) -> None:
    
    res = db.search(App.id == ctx.options.query_id)
    if res == []:
        await ctx.respond("Query not found")
        return
    
    id = random.randint(1,9999)
    response_embed = hikari.Embed(
        title="Correction <@1076545072226631804>",
        description=f"User > {res[0]['query']}\nBot > {res[0]['response']}\nProper: {ctx.options.proper}\nSent by {ctx.author}"
    )
    response_embed.set_footer(f"ID: {id}")
    await bot.rest.create_message(1075575934641508353, response_embed)
    db.insert({'id': id, 'query': res[0]['query'], 'proper': ctx.options.proper, 'user': ctx.author.id, 'dm':"yes"})
    #webhook = SyncWebhook.from_url('https://discord.com/api/webhooks/1075575964542718043/B4K3I9XHbJUmMDwhBIznDSA_RjGx8tQ5GXXL9B9Ge_EjSDRpHNO5NyG_5s0kFmISE7dK') # Initializing webhook
    #webhook.send(content=f"User > {ctx.options.what_you_said}\nBot > {ctx.options.what_the_bot_said}\nProper: {ctx.options.what_the_bot_shouldve_said}") 
    await ctx.respond("Correction sent! You will get a DM if the correction has been accepted.")

    
@bot.command()
@lightbulb.option(name="toggle", description="on/off", choices=["True", "False"], required=True)

@lightbulb.option(name="settings", description="What setting to change", choices=['Profanity Filter', 'Allow DMS'], required=True)

@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR),
    lightbulb.bot_has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command("settings", "change server settings")


@lightbulb.implements(lightbulb.SlashCommand)
async def settings(ctx: lightbulb.SlashContext) -> None:
    if ctx.options.settings == "Profanity Filter" and ctx.options.toggle == "True":
        db.update({'prof':ctx.options.toggle}, App.guild == ctx.guild_id)
        await ctx.respond(f"Set `{ctx.options.settings}` to `{ctx.options.toggle}`.")
    elif ctx.options.settings == "Profanity Filter" and ctx.options.toggle == "False":
        db.update({'prof':ctx.options.toggle}, App.guild == ctx.guild_id)
        await ctx.respond(f"Set `{ctx.options.settings}` set to `{ctx.options.toggle}`.")
    if ctx.options.settings == "Allow DMS" and ctx.options.toggle == "True":
        db.update({'dm':"yes"}, App.user == ctx.author.id)
        await ctx.respond(f"Set `{ctx.options.settings}` to `{ctx.options.toggle}`.")
    elif ctx.options.settings == "Allow DMS" and ctx.options.toggle == "False":
        db.update({'dm':"no"}, App.user == ctx.author.id)
        await ctx.respond(f"Set `{ctx.options.settings}` to `{ctx.options.toggle}`.")



@bot.command()
@lightbulb.option(name="deny_reason", description="If you denied, why?", type=str, required=False)
@lightbulb.option(name="id", description="ID of correction", type=int, required=True)
@lightbulb.option(name="decision", description="Reject or Accept", choices=['Reject', 'Accept'], required=True)
@lightbulb.add_checks(lightbulb.has_roles(1076545072226631804))
@lightbulb.command("add", "For corrections team only")
@lightbulb.implements(lightbulb.SlashCommand)
async def correct(ctx: lightbulb.SlashContext) -> None:
    results = db.search(App.id == ctx.options.id)
    if results == []:
        await ctx.respond("Correction not found.")
        return
    
    trainer = ListTrainer(chatbot)



    user = await ctx.app.rest.fetch_user(results[0]['user'])
    #user = bot.get_user(results[0]['user'])
    if results[0]['dm'] == "yes":
        if ctx.options.decision == "Reject":
            if ctx.options.deny_reason == None:
                reason = "No reason supplied"
            else:
                reason = ctx.options.deny_reason
            await ctx.respond("Correction denied.")
            await ctx.respond(hikari.Embed(
                title="Correction Rejected",
                description=f"Query: {results[0]['query']}\nProper: {results[0]['proper']}\nID: {ctx.options.id}",
                color="#FF0000"
            ))
            await user.send(f"Thank you for submitting a correction request. It has been denied for reason: `{reason}`")
            return
        else:
            trainer.train([
            results[0]['query'],
            results[0]['proper']
            ])
            await ctx.respond(hikari.Embed(
                title="Correction Accepted",
                description=f"Query: {results[0]['query']}\nProper: {results[0]['proper']}\nID: {ctx.options.id}",
                color="#00FF00"
            ))            
            await user.send("Thank you for submitting a corrections request. It has been accepted.")
            return
    else:
        trainer.train([
            results[0]['query'],
            results[0]['proper']
            ])
        
        db.remove(App.id == ctx.options.id)



@bot.command()
@lightbulb.option(name="input", description="What to ask", type=str, required=True)

@lightbulb.command("gpt", "Use chatgpt")


@lightbulb.implements(lightbulb.SlashCommand)
async def settings(ctx: lightbulb.SlashContext) -> None:
    openai.api_key = "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" 

    results = db.search(App.user == ctx.author.id)
    if results == []:
        db.insert({'read': "False", 'user': ctx.author.id, 'gpt': 10, 'dm': "yes"})
        results = db.search(App.user == ctx.author.id)
    if results[0]['gpt'] == 0:
        await ctx.respond("You have used all of your gpt responses. To get more you can join the discord server: https://discord.gg/KBfThutEVT. Or you can buy them through nitro or an equivelent.")
        return

    model_engine = "text-davinci-003" 

        
    prompt = ctx.options.input
    completion = openai.Completion.create( 
    engine=model_engine,
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
    )
    new = results[0]['gpt'] - 1
    db.update({'gpt': new}, App.user == ctx.author.id)
    results = db.search(App.user == ctx.author.id)
    embed = hikari.Embed(
        title="GPT",
        description=f"{completion.choices[0].text}"
    )
    embed.set_footer(f"GPT Uses: {results[0]['gpt']}")
    await ctx.respond(embed)
    response_embed = hikari.Embed(
        title="GPT ",
        description=f"User > {ctx.options.input}\nBot > {completion.choices[0].text}"

    )
    await bot.rest.create_message(1076656666063413351, response_embed)
    trainer = ListTrainer(chatbot)
    trainer.train([
            ctx.options.input,
            completion.choices[0].text
    ])
    #webhook = SyncWebhook.from_url('https://discord.com/api/webhooks/1075575964542718043/B4K3I9XHbJUmMDwhBIznDSA_RjGx8tQ5GXXL9B9Ge_EjSDRpHNO5NyG_5s0kFmISE7dK') # Initializing webhook
    #webhook.send(content=f"User > {ctx.options.what_you_said}\nBot > {ctx.options.what_the_bot_said}\nProper: {ctx.options.what_the_bot_shouldve_said}") 
    
@bot.command()
@lightbulb.option('member', 'member to give',type = hikari.Member, required = True)
@lightbulb.option(name="uses", description="How many uses to give", type=int, required=True)
@lightbulb.command("give", "Give a user more gpt uses. Owner only")
@lightbulb.implements(lightbulb.SlashCommand)
async def correct(ctx: lightbulb.SlashContext) -> None:
    if ctx.author.id == 539213950688952320:
        res = db.search(App.user == ctx.options.member.id)
        if res == []:
            await ctx.respond("User not found")
            return
        new = res[0]['gpt'] + ctx.options.uses
        db.update({'gpt': new}, App.user == ctx.options.member.id)
        await ctx.respond(f"Gave {ctx.options.member} {ctx.options.uses} uses. ")
    

@bot.command()
@lightbulb.command("invite", "Invite to use the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def invite(ctx: lightbulb.SlashContext) -> None:

    await ctx.author.send("Invite Kitten to your server: https://discord.com/oauth2/authorize?client_id=1072879727750160497&scope=bot&permissions=8")
    await ctx.respond("A dm was sent to you containing the invite link.")




@bot.command()
@lightbulb.option('section', 'What section to get info on',choices=['how it works', 'invite'], required = True)

@lightbulb.command("info", "Info about the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def correct(ctx: lightbulb.SlashContext) -> None:
    if ctx.options.section == "how it works":
        embed = hikari.Embed(
            title="How does it work?",
            description="Kitten learns from responses that it was given, it uses what you said to pick and search for appropriate responses. "
        )
        await ctx.respond(embed)
    elif ctx.options.section == "invite":
        await invite(ctx)

    








bot.run()





