import pytest
from myagent.agent import Agent
from myagent.config import Config
from myagent.model.mock_client import MockModelClient
from myagent.model.base import ModelResponse, ToolCall
from myagent.permissions import PermissionManager

def test_autonomous_agent_loop_with_mock(tmp_path):
    # Setup mock responses: Step 1 calls list_dir, Step 2 returns final answer
    step1 = ModelResponse(
        content="Let me check files.",
        tool_calls=[ToolCall(name="list_dir", arguments={"path": "."})]
    )
    step2 = ModelResponse(
        content="I have listed the directory and completed the task.",
        tool_calls=[]
    )

    mock_client = MockModelClient(responses=[step1, step2])
    config = Config(workdir=tmp_path)
    pm = PermissionManager(auto_approve_all=True)

    agent = Agent(
        config=config,
        model_client=mock_client,
        permission_manager=pm,
    )

    final_messages = agent.run("List files in the directory.")

    # Verify conversation history
    assert len(final_messages) >= 4
    assert final_messages[-1]["role"] == "assistant"
    assert "completed the task" in final_messages[-1]["content"]

def test_stuck_detection(tmp_path):
    # Setup 3 identical repeated tool calls
    step = ModelResponse(
        content="Calling same tool again",
        tool_calls=[ToolCall(name="list_dir", arguments={"path": "."})]
    )

    mock_client = MockModelClient(responses=[step, step, step, step])
    config = Config(workdir=tmp_path)
    pm = PermissionManager(auto_approve_all=True)

    agent = Agent(
        config=config,
        model_client=mock_client,
        permission_manager=pm,
    )

    final_messages = agent.run("Test stuck detection.")

    # Should detect stuck loop and stop
    tool_msgs = [m for m in final_messages if m.get("role") == "tool"]
    assert any("stuck in a loop" in m.get("content", "") for m in tool_msgs)
