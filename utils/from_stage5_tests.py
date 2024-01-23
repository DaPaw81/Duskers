import glob
from .helper.useful import DEFAULT_CLI_ARGS, run_for_stages, get_robot_lines, check_graphical_robots, \
    SAVE_FILE_NAME, file_cleanup, restart
from .helper.test_unit import tests, TestAlg
from hstest import CheckResult, TestedProgram, dynamic_test, StageTest
from datetime import datetime, timedelta

NOT_FOUND_MSG = "{} not found in save slot.\n" \
                "Please check your game saving logic and display the " \
                "specified data in the right format in the load menu."


def timestamp_with_seconds(time: datetime = datetime.today()):
    return str(time)[:16]


class FromStage5DuskersTest(StageTest):
    @staticmethod
    def test_save(pr: TestedProgram, username: str) -> CheckResult:
        save_time = datetime.today()
        pr = restart(pr, DEFAULT_CLI_ARGS)

        load_menu = pr.execute("load")

        expected_data_in_load_menu = {
            "player name": username,
            "titanium balance": 0,
            "robot count": 3,
        }

        for element, value in expected_data_in_load_menu.items():
            if str(value) not in load_menu:
                return CheckResult.wrong(
                    NOT_FOUND_MSG.format(element.capitalize())
                )

        # tolerate 1 sec difference in recorded save time
        valid_save_timestamps = [timestamp_with_seconds(date) for date in
                                 [save_time, save_time - timedelta(seconds=1)]
                                 ]

        if not any(timestamp in load_menu for timestamp in valid_save_timestamps):
            return CheckResult.wrong(
                NOT_FOUND_MSG.format("Last saved time")
            )

        if len([line for line in load_menu.lower().splitlines()
                if "empty" in line]) != 2:
            return CheckResult.wrong(
                "There should be exactly two slots displaying 'empty' "
                "when 1 slot is occupied by save data."
            )

        if len(glob.glob(SAVE_FILE_NAME)) < 1:
            return CheckResult.wrong(
                f"No file with '{SAVE_FILE_NAME}' within the filename found.\n"
                f"Please make sure all save files have this '{SAVE_FILE_NAME}' "
                "in their name and are created in the directory of program "
                "execution."
            )

        return CheckResult.correct()

    @dynamic_test(order=4)
    def test_updated_menu(self):
        pr = TestedProgram()
        main_menu = pr.start(*DEFAULT_CLI_ARGS).lower()

        if "load" not in main_menu or "new" not in main_menu:
            return CheckResult.wrong("The player should now have the option"
                                     "of choosing to start a [New] game or to [Load] a game.")

        return CheckResult.correct()

    @dynamic_test(order=5)
    @file_cleanup
    def test_load_with_no_saves(self):
        pr = TestedProgram()
        pr.start(*DEFAULT_CLI_ARGS)
        load_menu = pr.execute("load").lower()

        if len([line for line in load_menu.splitlines() if "empty" in line]) != 3:
            return CheckResult.wrong(
                "There should be exactly three slots displaying 'empty' upon "
                "initially starting the game and choosing the 'load' option."
            )

        return CheckResult.correct()

    @dynamic_test(data=["Hyperskill", "explorer", "random"], order=6)
    @file_cleanup
    def test_save_file_created_after_saving_new_game(self, username):
        pr = TestedProgram()
        pr.start(*DEFAULT_CLI_ARGS)
        for command in ["new", username, "yes", "save", "1"]:
            pr.execute(command)

        return self.test_save(pr, username)

    @dynamic_test(data=tests, order=7)
    @run_for_stages(5)
    @file_cleanup
    def save_file_created_after_saving_game(self, test: TestAlg):
        username = "hyperskill"
        cli_args = (test.seed, "0", "0", test.places)

        pr = TestedProgram()
        pr.start(*cli_args)
        for command in ["new", username, "yes", *test.input, "save", "1"]:
            pr.execute(command)

        return self.test_save(pr, username)

    @dynamic_test(data=tests, order=8)
    @run_for_stages(5)
    @file_cleanup
    def test_data_loaded_into_game(self, test: TestAlg):
        username = "hyperskill"
        cli_args = (test.seed, "0", "0", test.places)

        pr = TestedProgram()
        pr.start(*cli_args)
        for command in ["new", username, "yes", *test.input, "save", "1"]:
            pr.execute(command)

        # regeneration of test data runs before starting new program instance to
        # not mess with the seed
        starting_titanium = test.expected
        test.regenerate(1)
        new_titanium = str(int(test.expected) + int(starting_titanium))

        pr = restart(pr, cli_args, ["load"])
        loaded_game = pr.execute("1")

        if username not in loaded_game:
            return CheckResult.wrong("Player not greeted after loading the game")

        if starting_titanium not in loaded_game:
            return CheckResult.wrong(
                "Wrong titanium balance displayed after loading game."
            )

        hub_lines = get_robot_lines(loaded_game)

        if not check_graphical_robots(hub_lines, 3):
            return CheckResult.wrong(
                "Robots loaded into the game hub incorrectly."
            )

        for command in test.input:
            game_output = pr.execute(command)

        if new_titanium not in game_output:
            return CheckResult.wrong(
                "Titanium balance not updated correctly after loading game "
                "and exploring."
            )

        return CheckResult.correct()

    @dynamic_test(data=tests[0:2], order=9)
    @run_for_stages(5)
    @file_cleanup
    def test_multiple_save_slots(self, test: TestAlg):
        titanium_balances = []

        for slot in range(1, 4):
            username = "hyperskill"
            cli_args = (test.seed, "0", "0", test.places)

            pr = TestedProgram()
            pr.start(*cli_args)
            for command in ["new", username, "yes", *test.input, "save", str(slot)]:
                pr.execute(command)

            titanium_balances.append(test.expected)
            pr.stop()
            test.regenerate(test.data.explorations + 1)

        pr = TestedProgram()
        pr.start(*cli_args)
        load_menu = pr.execute("load")

        if len([line for line in load_menu.splitlines() if "empty" in line]) > 0:
            return CheckResult.wrong(
                "After to 3 different slots, there should not be any save "
                "slots that read 'empty' in the load menu."
            )

        for slot in range(1, 4):
            loaded_game = pr.execute(str(slot))
            if titanium_balances[slot - 1] not in loaded_game:
                return CheckResult.wrong(
                    "Wrong titanium balance displayed after loading game "
                    "where multiple save slots are occupied."
                )

            pr = restart(pr, cli_args)
            load_menu = pr.execute("load")

        return CheckResult.correct()
