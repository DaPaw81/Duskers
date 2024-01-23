import random
from sys import argv
from .useful import MENU_OPTIONS

# see interactive_test() for idea how this algorithm should be implemented in
# order to pass tests
# run in command line with same arguments as duskers.py for demo


class TestData:
    def __init__(self, explorations: int, searches: int, seed, chosen: int, places: str):
        self.explorations = explorations
        self.searches = searches
        self.seed = seed
        self.chosen = chosen
        self.places = places


def generate(n):
    result = []
    for _ in range(n):
        place_name = random.choice(place_names)
        place_titanium = random.randint(10, 100)
        result.append((place_name, place_titanium))
    return result


def interactive_test():
    no_of_places = random.randint(1, 9)
    print("Number of places:", no_of_places)
    no_of_searches = int(input("How many searches: "))
    print(generate(no_of_searches))
    print()


def test(no_of_searches):
    no_of_places = random.randint(1, 9)
    if no_of_searches > no_of_places:
        no_of_searches = no_of_places
    return generate(no_of_searches)


def init_test(test_case: TestData):
    global place_names
    random.seed(test_case.seed)
    place_names = []
    argv_places = test_case.places.split(",")
    for item in argv_places:
        place = " ".join(item.split("_"))
        place_names.append(place)

    results = []
    for exploration in range(test_case.explorations):
        results.append(test(test_case.searches))
    return results


class TestAlg:
    def __init__(self, data: TestData):
        self.data = data
        self.gen_results()
        # makes sure that chosen place is not out of range in (all) explorations
        max_choice = min([len(self.results[i])
                          for i in range(len(self.results))])
        if data.chosen > max_choice:
            self.data.chosen = max_choice
        self.calc_expected()
        self.gen_input()
        self.seed = data.seed
        self.places = data.places

    def calc_expected(self):
        """Expected value is sum of titanium after all the explorations"""
        self.expected = str(sum([
            self.results[explr][self.data.chosen - 1][1]
            for explr in range(self.data.explorations)
        ]))

    def gen_input(self):
        self.input = ([MENU_OPTIONS[0]] + ['s'] * (self.data.searches - 1) +
                      [str(self.data.chosen)]) * self.data.explorations

    def gen_results(self):
        self.results = init_test(self.data)

    def regenerate(self, exploration_count: int):
        self.data.explorations = exploration_count
        self.gen_results()
        self.calc_expected()
        self.gen_input()


test_data = [
    TestData(1, 8, "1", 1, "place1,place2"),
    TestData(2, 8, "100", 8, "Middle_of_nowhere,Ice_desert,Underground_city"),
    TestData(20, 9, "hyperskill", 5,
             "Old_power_plant,Abandoned_warehouse,Zombie_canteen"),
    TestData(10, 2, "seed", 1, "Middle_of_nowhere,Ice_desert,Underground_city")
]

tests = [TestAlg(data) for data in test_data]


if __name__ == "__main__":

    if len(argv) == 5:
        random.seed(a=argv[1])
        wait_time_min = int(argv[2])
        wait_time_max = int(argv[3])
        place_names = []
        argv_places = argv[4].split(",")
        for item in argv_places:
            place = " ".join(item.split("_"))
            place_names.append(place)
    else:
        print("Incorrect parameters")
        exit()

    while True:
        comm = input("Type 'exit()' to exit or any other character(s) to continue testing: ")
        if comm == "exit()":
            break
        interactive_test()
