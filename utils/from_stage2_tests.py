from hstest import CheckResult, StageTest, TestedProgram, dynamic_test
from .helper.useful import CASE_INSENSITIVITY_REMINDER
import re


class FromStage2DuskersTest(StageTest):

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

        hub = pr.execute("yes").strip()

        if not hub or len(hub) == 0:
            return CheckResult.wrong(
                "No hub found after finally selecting yes from the "
                "ready menu. For now this hub can be anything.\n"
                "Take a look where you continuously ask the player if they're "
                "ready.\n" + CASE_INSENSITIVITY_REMINDER
            )

        if not pr.is_finished():
            return CheckResult.wrong(
                "Your program should finish when the player finally decides "
                "that they're ready."
            )

        return CheckResult.correct()
