import re
from hstest import CheckResult, StageTest, TestedProgram, dynamic_test
from .helper.useful import CASE_INSENSITIVITY_REMINDER


class FromStage1DuskersTest(StageTest):

    @dynamic_test
    def test_menu_print(self):
        pr = TestedProgram()
        menu = pr.start()
        menu_lines = re.split("\n+", menu)

        if len(menu_lines) < 10:
            return CheckResult.wrong(
                "Output too short.\n"
                "Your title should take up exactly 8 non-empty lines,\n"
                "then the main menu options should be displayed on separate lines."
            )

        play_button = menu_lines[8].lower()
        if "[play]" not in play_button:
            return CheckResult.wrong(
                "Play option should be right underneath the title, "
                "which should take up exactly 8 non-empty lines."
            )

        exit_button = menu_lines[9].lower()
        if "[exit]" not in exit_button:
            return CheckResult.wrong("Exit option should be under [Play].\n")

        return CheckResult.correct()

    @dynamic_test(data=[
        ["hyperskill", "yes"],
        ["hyper", "YES"],
        ["automated test", "yES"]])
    def test_play_option(self, player_name, yes):
        pr = TestedProgram()
        pr.start()
        pr.execute("play")
        ready_prompt = pr.execute(player_name).lower()

        if player_name not in ready_prompt:
            return CheckResult.wrong("Player not greeted personally.")

        if "[yes]" not in ready_prompt or "[no]" not in ready_prompt:
            return CheckResult.wrong(
                "Player not asked if he/she is ready to begin.\n"
                "Remember to display possible commands for player to choose from."
            )

        short_message = pr.execute(yes)

        if not short_message:
            return CheckResult.wrong(
                "No short message found after selecting [Yes] from the ready menu.\n"
                "Tell the player to get back to some more coding!"
            )

        if not pr.is_finished:
            return CheckResult.wrong(
                "Program should finish after player says that they're ready.\n"
                + CASE_INSENSITIVITY_REMINDER)

        return CheckResult.correct()

    @dynamic_test
    def test_keep_asking_for_readiness(self):
        pr = TestedProgram()
        pr.start()
        pr.execute("play")
        ready_prompt = re.split("\n+", pr.execute("hyperskill"))[-1]

        for _ in range(3):
            re_ready_prompt = pr.execute("no")

            if ready_prompt not in re_ready_prompt:
                return CheckResult.wrong(
                    "You must keep asking the player if they are ready until "
                    "they choose [Yes] if they chose [No] when asked if ready.\n"
                    + CASE_INSENSITIVITY_REMINDER
                )

        pr.execute("yes")
        if not pr.is_finished():
            return CheckResult.wrong(
                "Your program should finish when the player finally decides"
                "that they're ready."
            )

        return CheckResult.correct()
