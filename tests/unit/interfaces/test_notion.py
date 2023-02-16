from shared_items.interfaces.notion import Notion, Prop as NotionProp


def test_assemble_prop_handles_rich_text():
    notion = Notion()

    dummy_prop: NotionProp = {
        "name": "SomeName",
        "type": "rich_text",
        "content": "yadayada",
    }

    dummy_output = notion.assemble_prop(dummy_prop)
    expected_output = {"rich_text": [{"text": {"content": "yadayada"}}]}

    assert dummy_output == expected_output


def test_assemble_props_handles_rich_text():
    notion = Notion()

    dummy_prop: NotionProp = {
        "name": "SomeName",
        "type": "rich_text",
        "content": "yadayada",
    }

    dummy_output = notion.assemble_props([dummy_prop])
    expected_output = {"SomeName": {"rich_text": [{"text": {"content": "yadayada"}}]}}

    assert dummy_output == expected_output
