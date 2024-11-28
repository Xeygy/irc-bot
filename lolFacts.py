import pandas as pd
import random
import requests
import nltk
from thefuzz import process, fuzz
from bs4 import BeautifulSoup


class LolFacts():
    def __init__(self):
        self.active = False

        self.df = pd.read_csv("Loldle Data.csv")

        list_columns = ["Position", "Species", "Range Type", "Region"] 

        for col in list_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(lambda x: str(x).split(',') if pd.notna(x) else [])

    def __str__(self):
        return self.df.to_string()
    
    def restart(self):
        self.df = pd.read_csv("Loldle Data.csv")

        list_columns = ["Position", "Species", "Range Type", "Region"] 

        for col in list_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(lambda x: str(x).split(',') if pd.notna(x) else [])

    # Loldle stuff
    def convertList(self, attribute: str):
        if "," in attribute:
            return attribute.split(",")
        return [attribute]
    
    # wrong - 0, correct - 1, partial - 2
    def updateAttributeSingle(self, attributeName: str, attribute: str, correct: int):
        if correct:
            self.df = self.df[self.df[attributeName] == attribute]
        else:
            self.df = self.df[self.df[attributeName] != attribute]

    def updateAttributeList(self, attributeName: str, attribute: str, correct: int):
        if correct:
            if correct == 1:
                attributeList = self.convertList(attribute)
                self.df = self.df[self.df[attributeName].apply(lambda tags: attributeList == tags)]
            else:
                self.df = self.df[self.df[attributeName].apply(lambda tags: attribute in tags)]
        else:
            self.df = self.df[~self.df[attributeName].apply(lambda tags: attribute in tags)]

    def updateAttribute(self, attributeName: str, attribute: str, correct: int):
        single = ["Name", "Gender", "Resource", "Release Year"]

        if attributeName in single:
            self.updateAttributeSingle(attributeName, attribute, correct)
        else:
            self.updateAttributeList(attributeName, attribute, correct)

    def possibleChampion(self, dataframe = None):
        if dataframe is not None:
            possibleChamps = list(dataframe.iterrows())
            randomChamp = random.choice(possibleChamps)
            return randomChamp[1]
        else:
            if self.optionsLeft():
                possibleChamps = list(self.df.iterrows())
                randomChamp = random.choice(possibleChamps)
                return randomChamp[1]
            else:
                return "No Possible Champion"

    def genderIdentity(self, gender: str):
        if gender == "Female":
            return "She"
        elif gender == "Male":
            return "He"
        return "They"
    
    def rangeType(self, range: list):
        if len(range) > 1:
            return "both melee and ranged"
        return range[0].lower()
    
    def resourceType(self, resource: str):
        if resource == "Manaless":
            return "has no resource"
        else:
            if resource == "Health Costs":
                type = "health"
            elif resource == "Shield":
                type = "shields"
            else:
                type = resource.lower()
            return "uses " + type + " as a resource"

    def speciesModifier(self, species: str):
        vowels = ["a", "e", "i", "o", "u"]
        if "alter" in species.lower() or "undead" in species.lower():
            return ""
        elif species[0].lower() in vowels:
            return "an "
        else:
            return "a "
        
    def multipleOptions(self, attribute: list, species: bool = None):
        numAttributes = len(attribute)

        options = ""
        for i in range(numAttributes):
            if species:
                options += self.speciesModifier(attribute[i])

            options += attribute[i]

            if numAttributes - i == 2:
                options += " and "
            else:
                options += ", "
        return options[:-2]
    
    def interpretChampion(self, champion: pd.core.series.Series = None):
        if champion is None:
            champion = self.possibleChampion()
        elif type(champion) == str:
            champion = self.possibleChampion(self.df[self.df["Name"] == champion])

        gender = self.genderIdentity(champion["Gender"])
        role = self.multipleOptions(champion["Position"]).lower()
        species = self.multipleOptions(champion["Species"], species=True).lower()
        resource = self.resourceType(champion["Resource"])
        range = self.rangeType(champion["Range Type"])
        region = self.multipleOptions(champion["Region"])

        if "," in role or "and" in role:
            roleMod = "roles"
        else:
            roleMod = "role"

        message = f"{champion['Name']} was released in {champion['Release Year']}. {gender} is a {range} champion that {resource}. {gender} is generally played in the {role} {roleMod}. {gender} is considered to be {species}. {gender} can found in {region}."
        return message

    def optionsLeft(self):
        return self.df.shape[0]
    
    def getChampionTrivia(self, champion: str):
        if " " in champion:
            champion = champion.replace(" ", "_")

        if "Nunu" in champion:
            champion == "Nunu"
        
        url = f"https://wiki.leagueoflegends.com/en-us/{champion}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        trivia_h2 = soup.find('span', {'id': 'Trivia'}).find_parent('h2')

        triviaElements = []
        for sibling in trivia_h2.find_next_siblings():
            if sibling.name == 'h2':
                break
            triviaElements.append(sibling)

        trivia = []
        for element in triviaElements:
            if hasattr(element, 'get_text'):
                trivia.append(element.get_text()) 
            elif isinstance(element, str):
                trivia.append(element.strip())

        triviaJoined = " ".join(trivia)

        triviaSentences = nltk.sent_tokenize(triviaJoined)

        return random.choice(triviaSentences)

    def interpretMessage(self, message: str):
        words = nltk.word_tokenize(message)

        funFact = "fun fact" in message.lower()
        loldle = "loldle" in message.lower()

        champions = []
        bestMatch = ""
        highestScore = 0
        for word in words:
            name, score, idx = process.extractOne(word, self.df['Name'], scorer=fuzz.ratio)
            # print(f"{word} - {name} {score}")
            if score > 85:
                champions.append(name)

            if score > highestScore:
                bestMatch = name
                highestScore = score

        returnMessages = []
        if not len(champions):
            # no similar enough name
            returnMessages.append(f"You didn't name any champion, but {bestMatch} was the closet to any word you said.")
            champions.append(bestMatch)
        
        for champion in champions:
            if loldle:
                returnMessages.append(self.interpretChampion(champion))

            if funFact:
                returnMessages.append(self.getChampionTrivia(champion))

            if not loldle and not funFact:
                # returnMessages.append(f"You didn't specify what you wanted so here is a fun fact about {champion}.")
                returnMessages.append(self.getChampionTrivia(champion))

        return returnMessages

if __name__ == "__main__":
    lolFacts = LolFacts()
    
    # Test getting possible champion
    # print(loldleSolver.interpretChampion(loldleSolver.possibleChampion()))

    # Test updating attributes
    # loldleSolver.updateAttribute("Gender", "Female", 1)
    # loldleSolver.updateAttribute("Species", "Human", 1)
    # loldleSolver.updateAttribute("Resource", "Mana", 1)
        # loldleSolver.updateAttribute("Range Type", "Ranged", 1)
    # loldleSolver.updateAttribute("Region", "Piltover", 0)

    # print(loldleSolver)
    # print(loldleSolver.optionsLeft())

    # Test Interpretting Messages
    message = "I what a loldle and fun fact for Azxir and Maokais and Aatrox and caitlyn"
    # message = "I want to watch arcane"
    for i in lolFacts.interpretMessage(message):
        print(i)

    # print(lolFacts)
    # print(lolFacts.interpretChampion(lolFacts.possibleChampion()))



