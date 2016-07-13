import pytest
import bot.commprocessor

def test_iscommand():
    assert bot.comm_processor.isCommand("moe test")
    assert bot.comm_processor.isCommand("moe ")
    assert bot.comm_processor.isCommand("moe another one")
    assert not bot.comm_processor.isCommand("")
    assert not bot.comm_processor.isCommand("moe")
    assert not bot.comm_processor.isCommand("tes moe")

def test_getCommandName():
    assert bot.comm_processor.getCommandName("moe test") == "test"
    assert bot.comm_processor.getCommandName("moe test arg 2") == "test"
    assert bot.comm_processor.getCommandName("moe n a") == "n"
    assert bot.comm_processor.getCommandName("moe ") == "ERROR"
    assert bot.comm_processor.getCommandName("") == "ERROR"
    assert bot.comm_processor.getCommandName(" moe ") == "ERROR"

def test_getArguments():
    assert bot.comm_processor.getArguments("moe test") == []
    assert bot.comm_processor.getArguments("moe test 1") == ["1"]
    assert bot.comm_processor.getArguments("moe test 1 2 ") == ["1", "2"]
