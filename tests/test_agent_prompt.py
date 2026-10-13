"""The system prompt carries today's date, computed per call so cached agents never go stale."""

from datetime import date

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import dated_prompt


def test_prompt_states_todays_date_before_the_conversation():
    msgs = dated_prompt("You are a tax assistant.")({"messages": [HumanMessage("Which GPM law applies?")]})
    assert isinstance(msgs[0], SystemMessage)
    assert msgs[0].content.startswith("You are a tax assistant.")
    assert f"Today's date is {date.today().isoformat()}." in msgs[0].content
    assert msgs[1].content == "Which GPM law applies?"


def test_date_is_computed_at_call_time():
    days = iter([date(2031, 1, 1), date(2031, 1, 2)])
    prompt = dated_prompt("System.", today=lambda: next(days))
    assert "Today's date is 2031-01-01." in prompt({"messages": []})[0].content
    assert "Today's date is 2031-01-02." in prompt({"messages": []})[0].content
