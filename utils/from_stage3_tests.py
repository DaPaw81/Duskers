from hstest import CheckResult, StageTest, TestedProgram, dynamic_test


class FromStage3DuskersTest(StageTest):

    @dynamic_test(data=["ex", "save", "up"])
    def test_placeholders_hub(self, option):
        pr = TestedProgram()
        pr.start()
        pr.execute("play")
        pr.execute("hyperskill")
        pr.execute("yes")

        short_message = pr.execute(option).strip()
        if not short_message or short_message == "":
            return CheckResult.wrong(
                "No placeholder text displayed to the user upon selecting a "
                f"menu option that has not yet been implemented: [{option}]."
            )

        if not pr.is_finished():
            return CheckResult.wrong(
                "Your program should terminate upon selecting a non-implemented "
                f"option: [{option}]."
            )

        return CheckResult.correct()
