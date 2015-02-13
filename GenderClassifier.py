#!/usr/bin/env python
# CS124 Homework 5 Jeopardy
# Original written in Java by Sam Bowman (sbowman@stanford.edu)
# Ported to Python by Milind Ganjoo (mganjoo@stanford.edu)

# This is a gender classifier you can use.
# There's nothing for you to implement here, hooray!

class GenderClassifier:
    def __init__(self):
        # To stay current, we use only the most freshly
        # downloaded copies of 1990 census data.
        self.male_names = self.load_dict("../data/dist.male.first.tsv")
        self.female_names = self.load_dict("../data/dist.female.first.tsv")

    def guessGender(self, name):
        """This returns a guess of the gender of a name. A name is classified
        with a gender ('m', 'f') if it shows up with that gender at least three
        times as often as the opposite gender, or if it is only reported for
        that gender. Otherwise, 'u' is returned."""
        name = name.upper()
        if name in self.male_names:
            if name in self.female_names:
                if self.male_names[name] > 3 * self.female_names[name]:
                    return "m"
                elif 3 * self.male_names[name] < self.female_names[name]:
                    return "f"
                else:
                    return "u"
            else:
                return "m"
        elif name in self.female_names:
            return "f"
        return "u"

    def load_dict(self, file_name):
        count_dict = {}
        with open(file_name) as f:
            for line in f:
                name, freq = line.split()[:2]
                count_dict[name] = float(freq)
        return count_dict
