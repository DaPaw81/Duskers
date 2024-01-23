import random
from typing import Generator, List, Tuple

PLACE_NAMES = ("first", "second", "third")


class Search:
    def __init__(self):
        self.place_name = random.choice(PLACE_NAMES)
        self.titanium = random.randint(10, 100)
        self.encounter_rate = random.random()


class Move:
    def __init__(self):
        location_count = random.randint(1, 9)
        self.search_list = [Search() for _ in range(location_count)]
        self._choice = None
        self._robot_lost = None

    def _explore_chosen(self):
        self._robot_lost = random.random() < self._choice.encounter_rate

    def _choose_by_lowest_encounter(self):
        self._choice = sorted(
            self.search_list, key=lambda search: search.encounter_rate)[0]
        self._explore_chosen()

    def choose_optimal(self):
        if self._choice is None:
            self._choose_by_lowest_encounter()
        return self._choice

    @property
    def choice(self) -> Search:
        if self._choice is None:
            raise AssertionError("No move choice made yet.")

        return self._choice

    @property
    def selection(self) -> int:
        """Selections are 1 indexed"""
        if self._choice is None:
            raise AssertionError("No move choice made yet.")

        return self.search_list.index(self._choice) + 1

    @property
    def robot_lost(self) -> bool:
        if self._choice is None:
            raise AssertionError(
                "Cannot determine whether robot was lost before selecting"
                "search to explore.")

        return self._robot_lost


class Game:
    def __init__(self, robot_count: int, name: str = None):
        self.robot_count = robot_count
        self.moves: List[Move] = []
        self.name = name

    @property
    def game_over(self) -> bool:
        return self.robot_count == 0

    @property
    def move_count(self) -> int:
        return len(self.moves)

    def play_optimal_round(self):
        if self.game_over:
            raise AssertionError(
                "Cannot play any more rounds once game is over")

        move = Move()
        move.choose_optimal()

        if move.robot_lost:
            self.robot_count -= 1

        self.moves.append(move)

    def get_nth_move_selection(self, n: int) -> int:
        """Moves are indexed from 0"""
        if self.move_count <= n:
            raise ValueError(f"Tried to access move number {n},"
                             f"but only {self.move_count} moves were played.")
        return self.moves[n].selection

    def get_titanium_for_move_and_choice(self, move: int, choice: int) -> int:
        return self.moves[move].search_list[choice].titanium

    def get_encounter_percentage_for_move_and_choice(self, move: int, choice: int) -> int:
        return round(self.moves[move].search_list[choice].encounter_rate * 100)

    @property
    def titanium(self):
        end = -1 if self.game_over else len(self.moves)
        return sum([move.choice.titanium for move in self.moves[:end]])

    @property
    def moves_where_robot_lost(self) -> List[int]:
        return [index for index, move in enumerate(self.moves) if move.robot_lost]


def find_seed(target_yield: int, robot_count: int, initial_seed: int) -> Tuple[str, Game]:
    generated_yield = 0
    seed_generator = _seeds(initial_seed)

    while generated_yield < target_yield:
        seed = seed_generator.__next__()
        current_game = play_until_target(seed, target_yield, robot_count)
        generated_yield = current_game.titanium

        # Edge case: target yield met but game over
        if current_game.game_over:
            generated_yield = 0

    return seed, current_game


def play_until_target(seed: str, target_yield: int, robot_count: int) -> Game:
    """
    Returns:
        A Game object containing the actual titanium yield of playing a single
        game. The amount will either be less than the target if the target was
        not reached with the given seed, or it will be the  amount obtained just
        after reaching (or surpassing) the target.
    """
    random.seed(seed)
    game = Game(robot_count)

    while not game.game_over and game.titanium < target_yield:
        game.play_optimal_round()

    return game


def play_until_game_over(seed: str, robot_count: int, name: str = None) -> Game:
    random.seed(seed)
    game = Game(robot_count, name)

    while not game.game_over:
        game.play_optimal_round()

    return game


def _seeds(initial: int) -> Generator[str, None, None]:
    i = initial
    while True:
        yield str(i)
        i += 1
