import pandas as pd
import random

class LoldleSolver():
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

    def possibleChampion(self):
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

        message = f"With {self.optionsLeft()} possible champions. I think it could be {champion["Name"]}, who released in {champion["Release Year"]}. {gender} is a {range} champion that {resource}. {gender} is generally played in the {role} {roleMod}. {gender} is considered to be {species}. {gender} can found in {region}."
        return message

    def optionsLeft(self):
        return self.df.shape[0]
    
    def interpretMessage(self, message: str):
        sentences = message.split(".")
        # Loldle - I tried Azir. He is too old. The region was correct. The position was partially right.
        
            

if __name__ == "__main__":
    loldleSolver = LoldleSolver()
    
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
    message = "For today's Loldle, the champion's gender is female and they were released in 2011."
    loldleSolver.interpretMessage(message)

    print(loldleSolver)
    print(loldleSolver.interpretChampion(loldleSolver.possibleChampion()))



