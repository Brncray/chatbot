




from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
chatbot = ChatBot("kitten")



trainer = ListTrainer(chatbot)






corpus = ChatterBotCorpusTrainer(chatbot)



corpus.train(
    "chatterbot.corpus.english"
)