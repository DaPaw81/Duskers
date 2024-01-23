from hstest import CheckResult, dynamic_test, TestedProgram, StageTest
from .helper.test_unit import tests, TestAlg
from .helper.useful import run_for_stages, DEFAULT_CLI_ARGS, new_game_command, \
    INVALID_INPUT_RESPONSE_MSG, INVALID_RETURN_MSG, REDISPLAY_AFTER_INVALID_INPUT_MSG


class FromStage4DuskersTest(StageTest):

    @dynamic_test(order=0)
    @run_for_stages(4, 5, 6)
    def test_initial_titanium_balance(self):
        pr = TestedProgram()
        pr.start(*DEFAULT_CLI_ARGS)
        pr.execute(new_game_command())

        pr.execute("hyperskill")
        hub = pr.execute("yes").lower()

        for line in hub.splitlines():
            if "titanium" in line:
                if "0" not in line:
                    return CheckResult.wrong(
                        "Wrong titanium balance displayed.\n"
                        "Make sure it is set to 0 when starting a new game."
                    )
                break
        else:
            return CheckResult.wrong(
                "Titanium balance not displayed inside the hub."
            )

        return CheckResult.correct()

    @dynamic_test(data=tests, order=1)
    @run_for_stages(4, 5)
    def test_exploration_based_on_seed(self, test: TestAlg):
        pr = TestedProgram()
        pr.start(test.seed, "0", "0", test.places)
        pr.execute(new_game_command())
        pr.execute("hyperskill")
        pr.execute("yes")

        for command in test.input:
            output = pr.execute(command)

        if test.expected not in output:
            return CheckResult.wrong(
                "Something went wrong with the exploration.\n\n"
                "Make sure the titanium amount from exploration is based on the seed,\n"
                "and that the exploration data is generated in the exact order mentioned.\n"
                "Make sure that the titanium balance is update accordingly in the hub.\n"
                "It might be helpful to reproduce the input from examples and compare output."
            )

        return CheckResult.correct()

    @dynamic_test(data=["blah", "jibberjabbter", "invalid"], order=2)
    @run_for_stages(4, 5, 6)
    def test_invalid_input_in_exploration(self, bad_input):
        pr = TestedProgram()
        pr.start(*DEFAULT_CLI_ARGS)
        pr.execute(new_game_command())
        pr.execute("hyperskill")
        hub = pr.execute("yes")
        prompt = pr.execute("ex").split("\n")[-1]

        response_to_invalid_input = pr.execute(bad_input)

        if "invalid input" not in response_to_invalid_input.lower():
            return CheckResult.wrong(INVALID_INPUT_RESPONSE_MSG)

        if hub in response_to_invalid_input:
            return CheckResult.wrong(
                INVALID_RETURN_MSG.format(place="hub")
            )

        if prompt not in response_to_invalid_input:
            return CheckResult.wrong(
                REDISPLAY_AFTER_INVALID_INPUT_MSG.format("command prompt")
            )

        return CheckResult.correct()

    @dynamic_test(order=3)
    @run_for_stages(4, 5, 6)
    def test_back_button_from_exploration(self):
        pr = TestedProgram()
        pr.start(*DEFAULT_CLI_ARGS)
        pr.execute(new_game_command())
        pr.execute("hyperskill")
        hub = pr.execute("yes")
        pr.execute("ex")
        redisplayed_hub = pr.execute("back")

        if hub not in redisplayed_hub:
            return CheckResult.wrong(
                "Game HUB not displayed after selecting back on the exploration"
                " menu."
            )

        return CheckResult.correct()
