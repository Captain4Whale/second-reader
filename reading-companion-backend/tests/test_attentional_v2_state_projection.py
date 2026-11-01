"""Current carry-forward projection includes recent memory and reaction refs."""
from src.attentional_v2.schemas import build_empty_local_buffer, build_empty_recent_reading_memory, build_empty_reaction_records
from src.attentional_v2.state_projection import build_carry_forward_context, build_digest_prompt_packet


def test_current_projection_keeps_recent_understanding_without_retired_stores():
    memory = build_empty_recent_reading_memory()
    memory["entries"] = [{"entry_id": "u1", "memory_text": "A question becomes clear.", "status": "active"}]
    context = build_carry_forward_context(chapter_ref="Chapter 1", current_unit_sentence_ids=[],
        local_buffer=build_empty_local_buffer(), recent_reading_memory=memory,
        reaction_records=build_empty_reaction_records())
    packet = build_digest_prompt_packet(carry_forward_context=context)
    assert packet["recent_reading_memory"]["active_entry_count"] == 1
    assert not {"active_attention", "reflective_digest"}.intersection(packet)
    assert not {"active_attention_digest", "chapter_reflective_frame"}.intersection(context["continuation_capsule"])
