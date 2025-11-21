import pytest
from examples.ai_chatbot.ai_chatbot import handle_command, conversation_history, history_lock


def test_handle_command_help():
    resp = handle_command('addr1', '/help')
    assert 'AI Assistant Commands' in resp


def test_handle_command_reset():
    # seed history
    with history_lock:
        conversation_history['addr2'] = [{'role':'system','content':'sys'},{'role':'user','content':'hi'}]
    resp = handle_command('addr2','/reset')
    assert 'Conversation reset' in resp
    with history_lock:
        assert len(conversation_history['addr2'])==1


def test_handle_command_stats():
    with history_lock:
        conversation_history['addr3'] = [{'role':'system','content':'sys'},{'role':'user','content':'a'},{'role':'assistant','content':'b'}]
    resp = handle_command('addr3','/stats')
    assert 'Bot Statistics' in resp
*** End Patch