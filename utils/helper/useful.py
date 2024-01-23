import glob
import os
import re
from typing import List
from hstest import WrongAnswer, TestPassed, TestedProgram


class StageData:
    STAGE_NO = 0


CASE_INSENSITIVITY_REMINDER = ("Remember, the user's input should be handled "
                               "in a non case-sensitive way.")
TERMINATE_ON_BAD_INPUT_MSG = ("Your program should not terminate if invalid"
                              " input is entered.")

INVALID_INPUT_RESPONSE_MSG = (
    "Your program did not respond properly to invalid input.\n"
    "Make sure to include the message 'Invalid input' before "
    "Re-prompting the user for input."
)

REDISPLAY_AFTER_INVALID_INPUT_MSG = (
    "The {} was not redisplayed after entering invalid input."
)

INVALID_RETURN_MSG = (
    "Your program should not return to the "
    "{place} if invalid input is entered in the high scores.\n"
    "Only entering [Back] should return the user to the {place}."
)

DEFAULT_CLI_ARGS = "hyperskill", "0", "0", "place1,place2"

SAVE_FILE_NAME = "*save_file*"
HIGH_SCORE_FILE_NAME = "*high_score*"
MENU_OPTIONS = "ex", "save", "up", "m"


def new_game_command():
    return "play" if StageData.STAGE_NO <= 4 else "new"


def run_for_stages(*stageNumbers: int):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            if StageData.STAGE_NO in stageNumbers:
                return function(self, *args, **kwargs)
            else:
                print(f"Not applicable for this stage ({StageData.STAGE_NO}), skipped.")
                raise TestPassed

        return wrapper

    return decorator


def clean_game_files():
    """clean up files created by game after test"""
    for file in [SAVE_FILE_NAME, HIGH_SCORE_FILE_NAME]:
        for file_name in glob.glob(file):
            try:
                os.remove(file_name)
            except PermissionError:
                raise WrongAnswer("PermissionError occurred. Save file can't be deleted for testing purposes"
                                  " because it might still be in use by your program.")


def file_cleanup(function):
    def wrapper(*args, **kwargs):
        clean_game_files()
        result = function(*args, **kwargs)
        clean_game_files()
        return result

    return wrapper


def check_graphical_robots(robots_display: List[str], number_of_robots: int) \
        -> bool:
    """helper method to check for arbitrary number of robots"""

    result = True
    if number_of_robots == 0:
        return True
    if len(robots_display) == 0:
        return False

    positions = []
    prev_position = -1
    while robots_display[0].find("|", prev_position + 1) != -1:
        prev_position = robots_display[0].find("|", prev_position + 1)
        positions.append(prev_position)
    if len(positions) != number_of_robots - 1:
        return False

    for line in robots_display:
        stripped_lines = [robot_line.strip() for robot_line in re.split("\|", line)]
        if len(stripped_lines) != number_of_robots:
            return False
        prev_position = -1
        for pos in positions:
            if line.find("|", prev_position + 1) != pos:
                return False
            prev_position = pos
        result = result and all(
            (robot == stripped_lines[0] and (robot != "" or number_of_robots == 0)) for robot in stripped_lines[1:])
    return result


def get_robot_lines(hub: str) -> List[str]:
    hub_lines = re.split("\n+", hub)

    robots = []
    state = 0
    for line in hub_lines:
        if len(line.strip()) > 0 and line.strip()[0] == '+':
            if state == 1:
                state = 2
                break
            else:
                state = 1
            continue
        if state == 1:
            robots.append(line)

    if state != 2:
        raise WrongAnswer(
            "Please make sure your HUB contains two lines, starting with '+' character\n"
            "Robot images should be placed between first two of them."
        )

    return robots


def restart(pr: TestedProgram, args: List[str] = [], input: List[str] = []) \
        -> TestedProgram:
    pr.stop()
    pr = TestedProgram()
    print("\n**PROGRAM RELOADED**")

    pr.start(*args)
    for command in input:
        pr.execute(command)

    return pr
