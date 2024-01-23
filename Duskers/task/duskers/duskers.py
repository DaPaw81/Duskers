import sys
import random
import time
import os
import json
from datetime import datetime


class Game:
    """
    A class to represent and manage player and rules
    """
    def __init__(self, name, seed, min_t, max_t, loc, metal=0, robot=3, up=0):
        self.name = name
        self.seed = seed
        self.min_animation_time = min_t
        self.max_animation_time = max_t
        self.location = loc
        random.seed(self.seed)
        self.gold = metal
        self.game_graphics = GameGraphics()
        self.robots = robot
        self.upgrades = up

    def messages(self, msg=0):
        messages = {
            0: '\nYour command:\n',
            1: f"Greetings, commander {self.name}!",
            2: "How about now.",
            3: "Are you ready to begin?\n    [Yes] [No] Return to Main[Menu]",
            4: "Invalid input",
            5: f"Welcome back, commander {self.name}!",
            6: "Purchase successful. You can now see how much titanium you can get from each found location.",
            7: "Purchase successful. You will now see how likely you will encounter an enemy at each found location.",
            8: "Purchase successful. You now have an additional robot"
        }
        return messages.get(msg, 'Invalid message code.')

    @classmethod
    def help(cls):
        print("""+==============================================================================+
                             GAME RULES
+==============================================================================+
| Main Rule is to scan for new locations and search them with yours robots.    |
| By searching locations your robots will aquire some titanium,                |
| but they may also encounter enemies.                                         |
| When that happen you always lose one robot but if any robots remain they     |
| will get the titanium.                                                       |
| Using titanium player can buy upgrades like scanner or even more robots.     |
| Game ends when player lose all robots. GOOD LUCK                             |
+==============================================================================+

[back] to return to Main Menu""")
        while True:
            command = input().lower()
            if command == 'back':
                main_menu()
            else:
                print(f"You should work on your spelling. Try again. This time type 'back' not '{command}'")

    @classmethod
    def high_scores(cls):
        if not os.path.exists('high_scores.txt'):
            print("No scores to display.\n  [Back]")
            while True:
                command = input('Your command:\n').lower()
                if command == 'back':
                    main_menu()
                else:
                    print("Invalid input")
                    continue
            return

        with open('high_scores.txt', 'r') as file:
            print(file.readline(), end='')
            print(file.readline(), end='')
            rank = 1
            for line in file:
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    name, score = parts[1], parts[2]
                    print(f"({rank}) {name} {score}")
                    rank += 1

    def save_highscore(self):

        today = datetime.now()
        time_stamp = today.strftime("%Y-%m-%d %H:%M")
        current_score_entry = f"100|{self.name}|{self.gold}|{time_stamp}\n"

        high_scores = []
        if os.path.exists('high_scores.txt'):
            with open('high_scores.txt', 'r') as file:
                high_scores = file.readlines()

        high_scores.append(current_score_entry)
        high_scores = [score for score in high_scores if len(score.split('|')) >= 4]
        high_scores.sort(key=lambda x: (-int(x.split('|')[2]), x.split('|')[3]))
        high_scores = high_scores[:11]
        with open('high_scores.txt', 'w') as file:
            file.write("HIGH SCORES\n\n")
            for i, entry in enumerate(high_scores[:10]):
                ignore_me, name, score, time_ = entry.strip().split('|')
                file.write(f"({i + 1})|{name}|{score}|{time_}\n")

    def play_from_load(self, msg):
        print(self.messages(msg))
        self.game_graphics.display_game_hub(self.robots, self.gold)
        self.play()

    def upgrade_menu(self):
        print(self.game_graphics.upgrade_store())
        while True:
            command = input(self.messages()).lower()
            if command == 'back':
                self.game_graphics.display_game_hub(self.robots, self.gold)
                self.play()
            elif command.isdigit() and int(command) == 1 and self.gold >= 250:
                self.gold -= 250
                self.upgrades = 6 if self.upgrades == 4 else 2
                print(self.messages(6))
                self.game_graphics.display_game_hub(self.robots, self.gold)
                self.play()
            elif command.isdigit() and int(command) == 2 and self.gold >= 500:
                self.gold -= 500
                self.upgrades = 6 if self.upgrades == 2 else 4
                print(self.messages(7))
                self.game_graphics.display_game_hub(self.robots, self.gold)
                self.play()
            elif command.isdigit() and int(command) == 3 and self.gold >= 1000:
                self.gold -= 1000
                self.robots += 1
                print(self.messages(8))
                self.game_graphics.display_game_hub(self.robots, self.gold)
                self.play()
            else:
                print(self.messages(4))

    def play(self):
        while True:
            command = input(self.messages()).lower()
            if command == 'ex':
                self.explore()
            elif command == 'up':
                self.upgrade_menu()
            elif command == 'save':
                self.save_game_menu()
            elif command == 'm':
                self.sub_menu()
            else:
                print(self.messages(4))

    def location_generator(self):
        while True:
            yield random.choice(self.location)

    def explore(self):

        no_loc = random.randint(1, 9)
        generator = self.location_generator()
        new_list = []
        value_list = []
        encounter_chance = []
        counter = 0

        # searching
        wrd = "Searching"
        while True:
            new_list.append(next(generator))
            self.time_delay(wrd)
            counter += 1
            value_list.append(random.randint(10, 100))
            encounter_chance.append(random.random())
            for x in range(counter):
                if self.upgrades == 6:
                    formula = (f"[{x + 1}] {new_list[x]} Titanium: {value_list[x]} "
                               f"Encounter rate: {round(encounter_chance[x] * 100)}")
                elif self.upgrades == 2:
                    formula = f"[{x + 1}] {new_list[x]} Titanium: {value_list[x]}"
                elif self.upgrades == 4:
                    formula = f"[{x + 1}] {new_list[x]} Encounter rate: {round(encounter_chance[x] * 100)}"
                else:
                    formula = f"[{x + 1}] {new_list[x]}"
                print(formula)
            print("\n[S] to continue searching")
            while True:
                command = input(self.messages()).lower()
                if command == 's':
                    if counter < no_loc:
                        break
                    else:
                        print("Nothing more in sight.")
                        print("        [Back]")

                elif command == 'back':
                    self.game_graphics.display_game_hub(self.robots, self.gold)
                    self.play()
                elif command.isdigit() and 1 <= int(command) <= counter:
                    wrd = 'Deploying robots'
                    self.time_delay(wrd)
                    encounter_roll = random.random()
                    if encounter_roll < encounter_chance[int(command) - 1]:
                        self.robots -= 1
                        if self.robots == 0:
                            self.game_over()
                        print("Enemy encounter")
                        print(f"{new_list[int(command) - 1]} explored successfully, 1 robot lost..")
                        print(f"Acquired {value_list[int(command) - 1]} lumps of titanium")
                        self.gold += value_list[int(command) - 1]
                        self.game_graphics.display_game_hub(self.robots, self.gold)
                        self.play()
                    else:
                        print(f"{new_list[int(command) - 1]} explored successfully, with no damage taken.")
                        self.gold += value_list[int(command) - 1]
                        print(f"Acquired {value_list[int(command) - 1]} lumps of titanium")

                        self.game_graphics.display_game_hub(self.robots, self.gold)
                        self.play()
                else:
                    print(self.messages(4))

    def sub_menu(self):
        GameGraphics.display_menu()
        while True:
            command = input(self.messages()).lower()
            if command == 'back':
                self.game_graphics.display_game_hub(self.robots, self.gold)
                self.play()
            elif command == 'main':
                main_menu()
            elif command == 'save':
                self.save_game_menu(1)
            elif command == 'exit':
                print('Thanks for playing, bye!')
                exit()

    def save_game_menu(self, ex=0):
        slot_1, slot_2, slot_3 = 'empty', 'empty', 'empty'
        print("Select save slot:")
        if is_file_exist('save_file.txt'):
            slot_1 = load_data(0)
            slot_2 = load_data(3)
            slot_3 = load_data(6)
        print(f'[1] {slot_1}\n[2] {slot_2}\n[3] {slot_3}\n')
        while True:
            command = input("Your command:\n")
            if command == 'back':
                return
            try:
                command_int = int(command)
                if command_int == 1:
                    self.save_game(0, ex)
                elif command_int == 2:
                    self.save_game(3, ex)
                elif command_int == 3:
                    self.save_game(6, ex)
                else:
                    print("Choose slot or 'back'")
            except ValueError:
                print("Invalid input. Please enter a number or 'back'")

    def save_game(self, slot, ex=0):
        file_path = r'C:\Users\dawid\PycharmProjects\Duskers\Duskers\task\save_file.txt'
        data = ['empty\n'] * 9
        today = datetime.now()
        time_stamp = today.strftime("%Y-%m-%d %H:%M")
        data_format = f"{self.name} Titanium: {self.gold} Robots: {self.robots} Last save: {time_stamp}\n"
        # name, seed, min_t, max_t, loc[], metal=0, robot=3, upgrades=0
        data_int = f"{self.name},{self.seed},{self.min_animation_time},\
{self.max_animation_time},{self.gold},{self.robots},{self.upgrades}\n"
        data_loc = json.dumps(self.location) + '\n'

        if is_file_exist(file_path):
            with open(file_path, 'r') as save_file:
                data = save_file.readlines()
            data[slot] = data_format
            data[slot + 1] = data_int
            data[slot + 2] = data_loc
        else:
            data[slot] = data_format
            data[slot + 1] = data_int
            data[slot + 2] = data_loc
        with open(file_path, 'w') as save_file:
            save_file.writelines(data)

        print(self.game_graphics.save_successfull())
        self.game_graphics.display_game_hub(self.robots, self.gold)
        if ex == 1:
            exit()
        self.play()

    def game_main_menu(self):
        while True:
            print(self.messages(3))
            command = input(self.messages()).lower()
            if command == 'no':
                continue
            elif command == 'yes':

                self.game_graphics.display_game_hub(self.robots)
                self.play()
            elif command == 'menu':
                main_menu()
            else:
                print('Invalid input')

    def time_delay(self, word):
        duration = self.custom_random()
        interval = 1
        end_time = time.time() + duration
        while time.time() < end_time:
            print(f"{word}", end='', flush=True)
            for _ in range(int(duration / interval)):
                time.sleep(interval)
                print(".", end='', flush=True)
        print()

    def custom_random(self):
        random_generator = random.Random(1234)
        return random_generator.randint(self.min_animation_time, self.max_animation_time)

    def game_over(self):
        self.save_highscore()
        print("""Enemy encounter!!!
        Mission aborted, the last robot lost...
                                |==============================|
                                |          GAME OVER!          |
                                |==============================|\n""")
        main_menu()


class GameGraphics:
    """
    A class to represent and manage game graphics.
    """
    @staticmethod
    def upgrade_store():
        upgrade_disp_menu = """                       |================================|
                       |          UPGRADE STORE         |
                       |                         Price  |
                       | [1] Titanium Scan         250  |
                       | [2] Enemy Encounter Scan  500  |
                       | [3] New Robot            1000  |
                       |                                |
                       | [Back]                         |
                       |================================|"""
        return upgrade_disp_menu

    @staticmethod
    def load_successfull():
        load_success = ("""                        |==============================|
                        |    GAME LOADED SUCCESSFULLY  |
                        |==============================|""")

        return load_success

    @staticmethod
    def save_successfull():
        save_success = ("""                        |==============================|
                        |    GAME SAVED SUCCESSFULLY   |
                        |==============================|""")

        return save_success

    @staticmethod
    def generate_robot():
        robot = [
            "  $   $$$$$$$   $  ",
            "  $$$$$     $$$$$  ",
            "      $$$$$$$      ",
            "     $$$   $$$     ",
            "     $       $     "
        ]

        robot = [line.ljust(20) for line in robot]
        return robot

    @staticmethod
    def generate_robots_row(num_robots):
        robots = [GameGraphics.generate_robot() for _ in range(num_robots)]
        robot_row = ['|'.join(robot_line) for robot_line in zip(*robots)]
        return '\n'.join(robot_row)

    def display_game_hub(self, num_robots, gold=0):
        """
        Prints the game hub interface with a dynamic number of robots.
        """

        str_titanium = f"| Titanium: {gold:<20}                                               |"
        separator = "+" + "=" * 78 + "+"
        robots_display = self.generate_robots_row(num_robots)
        print(f"""
{separator}
{robots_display}
{separator}
{str_titanium}
{separator}
|                  [Ex]plore                          [Up]grade                |
|                  [Save]                             [M]enu                   |
{separator}
        """)

    @staticmethod
    def display_menu():
        print("""                          |==========================|
                          |            MENU          |
                          |                          |
                          | [Back] to game           |
                          | Return to [Main] Menu    |
                          | [Save] and exit          |
                          | [Exit] game              |
                          |==========================|""")


def main_menu():
    r_s, min_a, max_a, loc = start_arguments()
    title = """+=======================================================================+
######*   ##*   ##*  #######*  ##*  ##*  #######*  ######*   #######*
##*  ##*  ##*   ##*  ##*       ##* ##*   ##*       ##*  ##*  ##*
##*  ##*  ##*   ##*  #######*  #####*    #####*    ######*   #######*
##*  ##*  ##*   ##*       ##*  ##* ##*   ##*       ##*  ##*       ##*
######*    ######*   #######*  ##*  ##*  #######*  ##*  ##*  #######*
                    (Survival ASCII Strategy Game)
+=======================================================================+"""
    print(title)
    print('')
    print('[New] Game\n[Load] Game\n[High] scores\n[Help]\n[Exit]\n')

    while True:
        initial_command = input('Your command:\n').lower()

        if initial_command == 'new':
            name = input("Enter your name:\n")
            start = Game(name, r_s, min_a, max_a, loc)
            print(start.messages(1))
            start.game_main_menu()
        elif initial_command == 'high':
            Game.high_scores()
        elif initial_command == 'help':
            Game.help()
        elif initial_command == 'load':
            load_game_menu()
        elif initial_command == 'exit':
            print('Thanks for playing, bye!')
            exit()
        else:
            print('Invalid input')


def load_data(line_number, file=r'\Users\dawid\PycharmProjects\Duskers\Duskers\task\save_file.txt'):
    if is_file_exist(file):
        with open(file) as new_file:
            lines = new_file.readlines()
            if line_number < len(lines):
                return lines[line_number].strip()
    return 'empty'



def load_game_menu():
    slot_1, slot_2, slot_3 = 'empty', 'empty', 'empty'

    print("Select save slot:")
    if is_file_exist(r'C:\Users\dawid\PycharmProjects\Duskers\Duskers\task\save_file.txt'):
        slot_1 = load_data(0)
        slot_2 = load_data(3)
        slot_3 = load_data(6)
    print(f'[1] {slot_1}\n[2] {slot_2}\n[3] {slot_3}\n')

    while True:
        command = input("Your command:\n")
        if command == 'back':
            return
        elif int(command) == 1 and slot_1 != 'empty':
            loader(1)
        elif int(command) == 2 and slot_2 != 'empty':
            loader(4)
        elif int(command) == 3 and slot_3 != 'empty':
            loader(7)
        else:
            print("Empty slot!")


def loader(game_slot):
    data = load_data(game_slot).split(',')
    list_str = load_data(game_slot + 1)
    try:
        locations = json.loads(list_str)
    except json.JSONDecodeError:
        print("Error: The list in the save file is not in a valid JSON format.")
        return
    # [0]name, [1]seed, [2]min_t, [3]max_t, loc[], [4]metal=0, [5]robot=3, [6]upgrades=0
    load_game = Game(data[0], data[1], int(data[2]), int(data[3]), locations, int(data[4]), int(data[5]), int(data[6]))

    print(GameGraphics.load_successfull())
    load_game.play_from_load(5)


def is_file_exist(file_name):
    return os.path.isfile(file_name)


def coming_soon():
    print("Coming SOON! Thanks for playing!")
    exit()


def start_arguments():

    r_s = sys.argv[1] if len(sys.argv) > 1 else "testISmySEED"
    min_a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    max_a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    loc = sys.argv[4].split(',') if len(sys.argv) > 4 else ["KWK_Jas_Mos", "KWK_Zofiowka", "KWK_Pniowek", "KWK_Borynia"]
    return r_s, min_a, max_a, loc


if __name__ == "__main__":
    main_menu()
    # game = Game('Dawid3x', 'test', 0, 1, ['k_one', 'cheat_mode_on', 'Loc_two', 'test'], 9990, 1, 6)
    # game.game_main_menu()
    # game.play_from_load(6)
    # game_graphics = GameGraphics()
    # game_graphics.display_game_hub(3)
    # game_graphics.display_menu()
    # print(game_graphics.save_successfull())
