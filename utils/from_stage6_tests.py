from hstest import CheckResult, StageTest, TestedProgram, dynamic_test
from typing import List, Tuple
from .helper.useful import DEFAULT_CLI_ARGS, check_graphical_robots, get_robot_lines, file_cleanup
from .helper.stage6_test_unit import PLACE_NAMES, Game, find_seed, play_until_game_over
from enum import Enum


DEFAULT_ROBOT_COUNT = 3
MAX_NUMBER_OF_HIGH_SCORES = 10

ILLEGAL_SALE_MSG = "The sale of upgrades should not be possible if player has" \
                   " insufficient titanium. Detected illegal sale of " \
                   "'{}'."


class Upgrade:
    def __init__(self, command: str, price: int):
        self.command = command
        self.price = price


class GameUpgrades(Enum):
    TITANIUM = Upgrade("1", 250)
    ENCOUNTER = Upgrade("2", 500)
    ROBOT = Upgrade("3", 1000)


def gen_input(choices: List[int], n: int = None):
    if n is None:
        n = len(choices)

    generated_input = []

    for choice in choices[:n]:
        generated_input.append("ex")
        generated_input += ["s" for _ in range(9)]
        generated_input += str(choice)

    return generated_input


class FromStage6DuskersTest(StageTest):
    @staticmethod
    def get_cli_args(seed: str):
        place_args = ",".join(PLACE_NAMES)
        return [seed, "0", "0", place_args]

    @staticmethod
    def simulate_optimal_game(seed: str, game: Game, end: int, start: int = 0,
                              pr: TestedProgram = None, name: str = "hyperskill") -> Tuple[TestedProgram, str]:
        if pr is None:
            pr = TestedProgram()
            pr.start(*FromStage6DuskersTest.get_cli_args(seed))

            for command in ["new", name, "yes"]:
                pr.execute(command)

        for command in gen_input([move.selection for move in game.moves[start:end]]):
            output = pr.execute(command)
        return pr, output

    @staticmethod
    def buy_upgrade(pr: TestedProgram, upgrade: Upgrade, explore_after: bool = True) -> str:
        for command in ["up", upgrade.command]:
            output = pr.execute(command)

        if explore_after:
            output = pr.execute("ex")
        return output

    @staticmethod
    def save_game(pr: TestedProgram, save_slot: str) -> None:
        for command in ["back", "save", save_slot, "m", "exit"]:
            pr.execute(command)

    @staticmethod
    def restart_game(seed: int, save_slot: str) -> Tuple[TestedProgram, str]:
        pr = TestedProgram()
        pr.start(*FromStage6DuskersTest.get_cli_args(seed))
        pr.execute("load")
        output = pr.execute(save_slot)
        return pr, output

    @dynamic_test(order=10)
    def test_illegal_upgrade_sale(self):
        pr = TestedProgram()
        pr.start(*DEFAULT_CLI_ARGS)

        for command in ["new", "hyperskill", "yes", "up", "2", "back", "ex"]:
            output = pr.execute(command)

        if "%" in output:
            return CheckResult.wrong(
                ILLEGAL_SALE_MSG.format("Enemy Encounter Scan")
            )

        for command in ["back", "up", "3"]:
            pr.execute(command)

        game_menu = pr.execute("back")

        hub_lines = get_robot_lines(game_menu)

        if not check_graphical_robots(hub_lines, 3):
            return CheckResult.wrong(
                ILLEGAL_SALE_MSG.format("New Robot")
            )

        return CheckResult.correct()

    @dynamic_test(data=["0", "10", "101"],order=11)
    def test_losing_robot_hub_update(self, seed):
        game = play_until_game_over(seed, DEFAULT_ROBOT_COUNT)
        current_robot_count = DEFAULT_ROBOT_COUNT

        pr = None
        move_indices = [-1] + game.moves_where_robot_lost
        i = 0
        while True:  # do ...
            pr, output = self.simulate_optimal_game(
                seed, game, move_indices[i + 1] + 1, move_indices[i] + 1, pr)

            current_robot_count -= 1

            hub_lines = get_robot_lines(output)

            if not check_graphical_robots(hub_lines, current_robot_count):
                return CheckResult.wrong(
                    "Expected one robot to disappear from the hub after an "
                    "enemy encounter, but it did not.\n"
                    "Please check your enemy encounter algorithm and make sure "
                    "your hub is updated accordingly."
                )

            i += 1
            # ... while
            if i >= len(move_indices) - 2:
                break

        return CheckResult.correct()

    @dynamic_test(data=[0, 10, 1090],order=12)
    @file_cleanup
    def test_sale_and_persistence_of_titanium_upgrade(self, initial_seed):
        seed, game = find_seed(
            GameUpgrades.TITANIUM.value.price, DEFAULT_ROBOT_COUNT, initial_seed)
        # Play additional round to later compare titanium count displayed
        game.play_optimal_round()

        pr, _ = self.simulate_optimal_game(seed, game, -1)
        output = self.buy_upgrade(pr, GameUpgrades.TITANIUM.value)

        if str(game.get_titanium_for_move_and_choice(-1, 0)) not in output:
            return CheckResult.wrong(
                "No titanium upgrade detected. This could also be due to your"
                "random generation algorithm not implemented as expected.\n"
                "Please double check the exact"
                "steps in the stage description and look at the examples."
            )

        self.save_game(pr, "1")
        pr, _ = self.restart_game(seed, "1")
        output = pr.execute("ex")

        if str(game.get_titanium_for_move_and_choice(0, 0)) not in output:
            return CheckResult.wrong(
                "No titanium upgrade detected after saving and reloading the game."
            )
        return CheckResult.correct()

    @dynamic_test(data=[0, 10, 1090],order=13)
    @file_cleanup
    def test_sale_and_persistence_of_encounter_upgrade(self, initial_seed):
        seed, game = find_seed(
            GameUpgrades.ENCOUNTER.value.price, DEFAULT_ROBOT_COUNT, initial_seed)
        # Play additional round to later compare encounter rate displayed
        game.play_optimal_round()

        pr, _ = self.simulate_optimal_game(seed, game, -1)
        output = self.buy_upgrade(pr, GameUpgrades.ENCOUNTER.value)

        if str(game.get_encounter_percentage_for_move_and_choice(-1, 0)) not in output:
            return CheckResult.wrong(
                "No enemy encounter scan upgrade detected after purchasing it."
                "This could also be due to your enemy encounter rate not being "
                "implemented as expected.\n"
                "Please double check the exact steps in the stage description "
                "and look at the examples."
            )

        self.save_game(pr, "1")
        pr, _ = self.restart_game(seed, "1")
        output = pr.execute("ex")

        if str(game.get_encounter_percentage_for_move_and_choice(0, 0)) not in output:
            return CheckResult.wrong(
                "No enemy encounter scan upgrade detected after saving and reloading the game."
            )

        return CheckResult.correct()

    @dynamic_test(data=[1, 21, 2000],order=14)
    @file_cleanup
    def test_sale_and_persistence_of_robot_upgrade(self, initial_seed):
        seed, game = find_seed(
            GameUpgrades.ROBOT.value.price, DEFAULT_ROBOT_COUNT, initial_seed)

        pr, _ = self.simulate_optimal_game(seed, game, len(game.moves))
        output = self.buy_upgrade(
            pr, GameUpgrades.ROBOT.value, explore_after=False)

        hub_lines = get_robot_lines(output)

        if not check_graphical_robots(hub_lines, game.robot_count + 1):
            return CheckResult.wrong(
                "No new robot detected after purchasing the 'New Robot' upgrade.\n"
                "The new robot should appear right next to the existing ones in the hub."
            )

        self.save_game(pr, "1")
        pr, output = self.restart_game(seed, "1")

        if not check_graphical_robots(get_robot_lines(output), game.robot_count + 1):
            return CheckResult.wrong(
                "Purchased robot did not persist after saving and reloading the game.")

        return CheckResult.correct()

    @dynamic_test(data=["3", "31", "3000"],order=15)
    @file_cleanup
    def test_game_over(self, seed):
        game = play_until_game_over(seed, DEFAULT_ROBOT_COUNT)
        pr = TestedProgram()
        main_menu = pr.start(*self.get_cli_args(seed))

        for command in ["new", "hyperskill", "yes"]:
            pr.execute(command)

        _, output = self.simulate_optimal_game(
            seed, game, len(game.moves), pr=pr)

        if "game over" not in output.lower():
            return CheckResult.wrong(
                "The string 'game over' not found when the player looses all robots."
            )

        if main_menu not in output:
            return CheckResult.wrong(
                "Main menu not displayed after a game over.\n"
                "Make sure to take the player to the main menu right after the game is over."
            )

        return CheckResult.correct()

    @dynamic_test(data=[[1, 7], [70, 10], [10000, 20]],order=16)
    @file_cleanup
    def test_high_scores(self, initial_seed, game_count):
        games: List[Game] = []

        for _ in range(game_count):
            seed = str(initial_seed)
            # arbitrary number appended to name
            name = "hyperskill" + str(initial_seed % 7)
            game = play_until_game_over(seed, DEFAULT_ROBOT_COUNT, name)
            games.append(game)

            self.simulate_optimal_game(seed, game, game.move_count, name=name)

            initial_seed += 1

        pr = TestedProgram()
        pr.start(*self.get_cli_args(seed))

        output_lines = pr.execute('high').splitlines()
        games.sort(key=lambda g: g.titanium, reverse=True)

        game_index = 0
        line_index = 0
        target = min(len(games), MAX_NUMBER_OF_HIGH_SCORES)

        while line_index < len(output_lines) and game_index < target:
            game = games[game_index]
            line = output_lines[line_index]

            if game.name in line and str(game.titanium) in line:
                game_index += 1
            line_index += 1

        if game_index < target:
            return CheckResult.wrong(
                "High scores not displayed properly. Please make sure that the "
                "player's name and their score (titanium balance at time of game over) "
                "is displayed on a single line.\n"
                "Ensure that the scores are sorted from highest to lowest, and "
                "that the 10 highest ones are displayed.\n"
                "If less than 10 games were played, display all games that were "
                "played till the game over screen.\n"
                "Make sure the high scores persists when exiting and reopening the program."
            )
        return CheckResult.correct()
