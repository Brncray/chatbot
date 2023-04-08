from chatterbot import *
from chatterbot.trainers import ChatterBotCorpusTrainer


chatbot = ChatBot("kitten")

trainer = ChatterBotCorpusTrainer(chatbot)


trainer.train(
    "chatterbot.corpus.english"
)