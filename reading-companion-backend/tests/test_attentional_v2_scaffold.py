"""Tests for the attentional_v2 Phase 1 scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.attentional_v2.prompts import (
    ATTENTIONAL_V2_PROMPTS,
    ATTENTIONAL_V2_PROMPTSET_VERSION,
    ATTENTIONAL_V2_PROMPT_REGISTRY,
    READ_BOOK_INFO_TEMPLATE,
    READ_CURRENT_FOCUS_TEMPLATE,
    READ_OUTPUT_CONTRACT_FRAGMENT_REGISTRY,
    READ_OUTPUT_CONTRACT_TEMPLATE,
    READ_READING_STATE_TEMPLATE,
    READ_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY,
    READ_ROLE_AND_INSTRUCTION_TEMPLATE,
    READ_UNIT_PROMPT_VERSION,
    READ_UNIT_ROLE_AND_INSTRUCTION_FRAGMENTS,
    READ_UNIT_SYSTEM_PROMPT,
    READ_XML_PROMPTSET_VERSION,
    READ_XML_PROMPT_VERSION,
    PromptAssembler,
    PromptAssemblySpec,
    PromptFragment,
    PromptFragmentRegistry,
    PromptRegistry,
    PromptTemplateNode,
    render_prompt_template_xml,
    render_read_book_info_xml,
    render_read_current_focus_xml,
    render_read_output_contract_xml,
    render_read_prompt_xml,
    render_read_reading_state_xml,
    render_read_role_and_instruction_xml,
    render_read_xml_prompt_example,
)
from src.attentional_v2 import runner as runner_module
from src.attentional_v2.slow_cycle import project_chapter_result_compatibility
from src.attentional_v2.schemas import (
    ATTENTIONAL_V2_MECHANISM_VERSION,
    ATTENTIONAL_V2_POLICY_VERSION,
    ATTENTIONAL_V2_SCHEMA_VERSION,
    build_empty_active_attention,
    build_empty_concept_registry,
    build_empty_local_buffer,
    build_empty_local_continuity,
    build_empty_reaction_records,
    build_empty_reflective_frames,
    build_empty_thread_trace,
)
from src.attentional_v2.storage import (
    ATTENTIONAL_V2_MECHANISM_KEY,
    chapter_result_compatibility_file,
    concept_registry_file,
    event_stream_file,
    knowledge_activations_file,
    local_buffer_file,
    local_continuity_file,
    reaction_records_file,
    reader_policy_file,
    read_audit_file,
    reflective_frames_file,
    reconsolidation_records_file,
    revisit_index_file,
    resume_metadata_file,
    settlement_audit_file,
    slow_cycle_audit_file,
    survey_map_file,
    thread_trace_file,
    unit_span_ledger_file,
    unitization_audit_file,
    active_attention_file,
)
from src.reading_core.runtime_contracts import ParseRequest, ReadRequest
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_runtime.provisioning import ProvisionedBook
from src.reading_runtime.artifacts import checkpoint_summary_file, mechanism_manifest_file, runtime_shell_file
from src.reading_runtime.shell_state import load_runtime_shell


def test_prompt_template_xml_resolves_fragments_slots_and_literals() -> None:
    registry = PromptFragmentRegistry(
        [
            PromptFragment(
                fragment_id="test.read.role.v1",
                text="Fixed <role> & instruction text.",
            )
        ]
    )

    rendered = render_prompt_template_xml(
        [
            PromptTemplateNode(
                element_name="RoleAndInstruction",
                children=[
                    PromptTemplateNode(element_name="Role", prompt_fragment_ref="test.read.role.v1"),
                    PromptTemplateNode(
                        element_name="ReadBehavior",
                        attributes={"kind": "A&B"},
                        value_slot="read_behavior",
                    ),
                    PromptTemplateNode(element_name="LiteralHint", literal_value="Use fixed literal text."),
                ],
            ),
            PromptTemplateNode(element_name="CurrentFocus", value_slot="current_focus"),
        ],
        registry=registry,
        slot_values={
            "read_behavior": "Read A & B < carefully.",
            "current_focus": "Current unit text.",
        },
    )

    assert "<RoleAndInstruction>" in rendered
    assert "<Role>" in rendered
    assert "Fixed &lt;role&gt; &amp; instruction text." in rendered
    assert '<ReadBehavior kind="A&amp;B">' in rendered
    assert "Read A &amp; B &lt; carefully." in rendered
    assert "Use fixed literal text." in rendered
    assert rendered.index("<RoleAndInstruction>") < rendered.index("<CurrentFocus>")
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "ref=" not in rendered
    assert "test.read.role.v1" not in rendered
    assert "read_behavior" not in rendered
    assert "current_focus" not in rendered
    assert [fragment.fragment_id for fragment in registry.list()] == ["test.read.role.v1"]


def test_prompt_template_xml_missing_fragment_fails_fast() -> None:
    with pytest.raises(KeyError, match="missing.fragment"):
        render_prompt_template_xml(
            [PromptTemplateNode(element_name="Role", prompt_fragment_ref="missing.fragment")],
            registry=PromptFragmentRegistry([]),
            slot_values={},
        )


def test_prompt_template_xml_missing_value_slot_fails_fast() -> None:
    with pytest.raises(KeyError, match="missing_slot"):
        render_prompt_template_xml(
            [PromptTemplateNode(element_name="Role", value_slot="missing_slot")],
            registry=PromptFragmentRegistry([]),
            slot_values={},
        )


def test_prompt_template_xml_rejects_multiple_content_sources() -> None:
    with pytest.raises(ValueError, match="must use only one content source"):
        render_prompt_template_xml(
            [
                PromptTemplateNode(
                    element_name="Role",
                    prompt_fragment_ref="test.read.role.v1",
                    value_slot="role_slot",
                )
            ],
            registry=PromptFragmentRegistry(
                [PromptFragment(fragment_id="test.read.role.v1", text="Role text.")]
            ),
            slot_values={"role_slot": "Role slot text."},
        )


def test_prompt_template_xml_empty_value_policy_is_explicit() -> None:
    rendered = render_prompt_template_xml(
        [
            PromptTemplateNode(element_name="EmptyValue", literal_value=""),
            PromptTemplateNode(element_name="SkippedValue", value_slot="skipped_value", skip_if_empty=True),
        ],
        registry=PromptFragmentRegistry([]),
        slot_values={"skipped_value": ""},
    )

    assert "<EmptyValue>" in rendered
    assert "</EmptyValue>" in rendered
    assert "SkippedValue" not in rendered


def test_prompt_assembler_renders_spec_and_metadata_without_live_migration() -> None:
    spec = PromptAssemblySpec(
        spec_id="attentional_v2.test_node.xml.v1",
        owner_node="test_node",
        prompt_version="attentional_v2.test.v1",
        promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
        template_nodes=(
            PromptTemplateNode(
                element_name="RoleAndInstruction",
                children=(
                    PromptTemplateNode(element_name="Role", prompt_fragment_ref="test.role.v1"),
                    PromptTemplateNode(element_name="Behavior", prompt_fragment_ref="test.behavior.v1"),
                ),
            ),
            PromptTemplateNode(element_name="CurrentFocus", value_slot="current_focus"),
            PromptTemplateNode(element_name="OutputContract", literal_value="Return JSON only."),
        ),
        fragment_registry=PromptFragmentRegistry(
            [
                PromptFragment(fragment_id="test.role.v1", text="Read carefully."),
                PromptFragment(fragment_id="test.behavior.v1", text="Use A & B < safely."),
            ]
        ),
        required_slots=("current_focus",),
        output_contract="test_output_v1",
    )

    result = PromptAssembler().assemble(
        spec,
        slot_values={"current_focus": "Current unit <text> & intent."},
    )

    assert result.rendered_text.startswith("<RoleAndInstruction>")
    assert "<CurrentFocus>" in result.rendered_text
    assert "Use A &amp; B &lt; safely." in result.rendered_text
    assert "Current unit &lt;text&gt; &amp; intent." in result.rendered_text
    assert "Return JSON only." in result.rendered_text
    assert result.spec_id == "attentional_v2.test_node.xml.v1"
    assert result.owner_node == "test_node"
    assert result.prompt_version == "attentional_v2.test.v1"
    assert result.promptset_version == ATTENTIONAL_V2_PROMPTSET_VERSION
    assert result.output_contract == "test_output_v1"
    assert result.rendered_blocks == ("RoleAndInstruction", "CurrentFocus", "OutputContract")
    assert result.used_fragment_ids == ("test.role.v1", "test.behavior.v1")
    assert result.used_slot_names == ("current_focus",)
    assert "prompt_fragment_ref" not in result.rendered_text
    assert "value_slot" not in result.rendered_text
    assert "test.role.v1" not in result.rendered_text
    assert "current_focus" not in result.rendered_text
    assert "ref=" not in result.rendered_text
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system == READ_UNIT_SYSTEM_PROMPT
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt


def test_prompt_assembler_missing_required_slot_fails_fast_before_rendering() -> None:
    spec = PromptAssemblySpec(
        spec_id="attentional_v2.test_node.xml.v1",
        owner_node="test_node",
        prompt_version="attentional_v2.test.v1",
        promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
        template_nodes=(PromptTemplateNode(element_name="CurrentFocus", value_slot="current_focus"),),
        fragment_registry=PromptFragmentRegistry([]),
        required_slots=("current_focus",),
        output_contract="test_output_v1",
    )

    with pytest.raises(KeyError, match="current_focus"):
        PromptAssembler().assemble(spec, slot_values={})


def test_prompt_assembler_missing_fragment_ref_fails_fast_during_rendering() -> None:
    spec = PromptAssemblySpec(
        spec_id="attentional_v2.test_node.xml.v1",
        owner_node="test_node",
        prompt_version="attentional_v2.test.v1",
        promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
        template_nodes=(PromptTemplateNode(element_name="Role", prompt_fragment_ref="missing.fragment"),),
        fragment_registry=PromptFragmentRegistry([]),
        required_slots=(),
        output_contract="test_output_v1",
    )

    with pytest.raises(KeyError, match="missing.fragment"):
        PromptAssembler().assemble(spec, slot_values={})


def test_prompt_assembly_spec_validation_rejects_empty_or_duplicate_contract_parts() -> None:
    with pytest.raises(ValueError, match="spec_id"):
        PromptAssemblySpec(
            spec_id="",
            owner_node="test_node",
            prompt_version="attentional_v2.test.v1",
            promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
            template_nodes=(PromptTemplateNode(element_name="Role", literal_value="x"),),
            fragment_registry=PromptFragmentRegistry([]),
            required_slots=(),
            output_contract="test_output_v1",
        )

    with pytest.raises(ValueError, match="required_slots must be unique"):
        PromptAssemblySpec(
            spec_id="attentional_v2.test_node.xml.v1",
            owner_node="test_node",
            prompt_version="attentional_v2.test.v1",
            promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
            template_nodes=(PromptTemplateNode(element_name="Role", literal_value="x"),),
            fragment_registry=PromptFragmentRegistry([]),
            required_slots=("same", "same"),
            output_contract="test_output_v1",
        )

    with pytest.raises(ValueError, match="template_nodes"):
        PromptAssemblySpec(
            spec_id="attentional_v2.test_node.xml.v1",
            owner_node="test_node",
            prompt_version="attentional_v2.test.v1",
            promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
            template_nodes=(),
            fragment_registry=PromptFragmentRegistry([]),
            required_slots=(),
            output_contract="test_output_v1",
        )


def test_read_xml_prompt_example_does_not_replace_live_read_prompt() -> None:
    rendered = render_read_xml_prompt_example(
        book_info='{"title": "Demo & Book"}',
        reading_state='{"recent_reading_memory": []}',
        current_focus='{"reading_object": "Alpha < Beta"}',
        output_contract='{"return": "json"}',
    )

    assert "<RoleAndInstruction>" in rendered
    assert "<BookInfo>" in rendered
    assert "<ReadingState>" in rendered
    assert "<CurrentFocus>" in rendered
    assert "<OutputContract>" in rendered
    assert "&amp;" in rendered
    assert "&lt;" in rendered
    assert "fragment_id" not in rendered
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "ref=" not in rendered
    assert "attentional_v2.read.role_and_instruction.example.v1" not in rendered
    assert "book_info" not in rendered
    assert "reading_state" not in rendered
    assert "current_focus" not in rendered
    assert "output_contract" not in rendered
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert ATTENTIONAL_V2_PROMPTS.read_unit_version == READ_UNIT_PROMPT_VERSION
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system.startswith("You are a careful reader")
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt


def test_full_read_prompt_xml_assembly_renders_all_target_blocks_without_live_migration() -> None:
    result = render_read_prompt_xml(
        book_title="Demo Book",
        author="Tester",
        chapter_title="Chapter 1",
        output_language_name="English",
        recent_reading_memory={
            "active_entries": [
                {"memory_text": "The author frames the opening as testimony."},
            ]
        },
        current_unit_source={
            "paragraph_slices": [
                {"paragraph_index": 1, "text": "Alpha <source> & line."},
            ]
        },
    )

    assert result.spec_id == "attentional_v2.read_unit.xml.v2"
    assert result.owner_node == "read_unit"
    assert result.prompt_version == READ_XML_PROMPT_VERSION
    assert result.promptset_version == READ_XML_PROMPTSET_VERSION
    assert result.output_contract == "read_unit_xml_json_v3"
    assert result.rendered_blocks == (
        "RoleAndInstruction",
        "BookInfo",
        "ReadingState",
        "CurrentFocus",
        "OutputContract",
    )
    assert result.used_slot_names == (
        "book_identity",
        "recent_memory",
        "reading_path",
        "reading_position",
        "reading_intent",
        "language_contract",
    )
    assert "<RoleAndInstruction>" in result.rendered_text
    assert "<BookInfo>" in result.rendered_text
    assert "<ReadingState>" in result.rendered_text
    assert "<CurrentFocus>" in result.rendered_text
    assert "<OutputContract>" in result.rendered_text
    assert "Alpha &lt;source&gt; &amp; line." in result.rendered_text
    assert "The author frames the opening as testimony." in result.rendered_text
    assert '"recent_reading_memory": []' in result.rendered_text
    assert '"memory_uptake_ops"' not in result.rendered_text
    assert "memory_uptake_ops" not in result.rendered_text
    assert "prompt_fragment_ref" not in result.rendered_text
    assert "value_slot" not in result.rendered_text
    assert "book_identity" not in result.rendered_text
    assert "read.role_and_stance" not in result.rendered_text
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system == READ_UNIT_SYSTEM_PROMPT


def test_read_role_and_instruction_xml_renders_target_structure_without_live_migration() -> None:
    rendered = render_read_role_and_instruction_xml()

    assert "<RoleAndInstruction>" in rendered
    assert "<ReaderRole>" in rendered
    assert "<ContextUseGuide>" in rendered
    assert "<ReadingBehavior>" in rendered
    assert "<ReadingImpression>" in rendered
    assert "<SurfacedReaction>" in rendered
    assert "<ReactionSelection>" in rendered
    assert "<ReactionGroundingAndCallback>" in rendered
    assert "<MemoryInstruction>" in rendered
    assert "<MemoryBoundary>" in rendered
    assert "<RecentReadingMemory>" in rendered
    assert "\n  <SourceGrounding>\n" in rendered
    assert "<RouteBoundary>" not in rendered
    assert "<ResponseDiscipline>" in rendered
    assert "<DurableMemory>" not in rendered
    assert "<ActiveTension>" not in rendered
    assert "ActiveTension" not in rendered
    assert "active_attention" not in rendered
    assert "concept_registry" not in rendered
    assert "thread_trace" not in rendered
    assert "read.durable_memory_policy" not in rendered
    assert "read.active_tension_policy" not in rendered
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "ref=" not in rendered
    assert "READ_ROLE_AND_INSTRUCTION" not in rendered
    assert "reading-companion-backend" not in rendered
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system == READ_UNIT_SYSTEM_PROMPT
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt
    assert rendered.index("<ReaderRole>") < rendered.index("<ContextUseGuide>")
    assert rendered.index("<ContextUseGuide>") < rendered.index("<ReadingBehavior>")
    assert "BookInfo as orientation" in rendered
    assert "ReadingState as carried understanding" in rendered
    assert "CurrentFocus/ReadingObject as the source text to read now" in rendered
    assert "OutputContract as the required response shape" in rendered


def test_read_role_and_instruction_xml_template_uses_only_target_fragment_refs() -> None:
    rendered = render_prompt_template_xml(
        READ_ROLE_AND_INSTRUCTION_TEMPLATE,
        registry=READ_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY,
        slot_values={},
    )

    assert rendered == render_read_role_and_instruction_xml()
    assert "read.durable_memory_policy" not in rendered
    assert "read.active_tension_policy" not in rendered


def test_read_book_info_xml_renders_light_orientation_block() -> None:
    rendered = render_read_book_info_xml(
        book_title="活出生命的意义 & More",
        author="Viktor <Frankl>",
    )

    assert "<BookInfo>" in rendered
    assert "<BookIdentity>" in rendered
    assert '"book_title": "活出生命的意义 &amp; More"' in rendered
    assert '"author": "Viktor &lt;Frankl&gt;"' in rendered
    assert "ChapterIdentity" not in rendered
    assert "chapter_title" not in rendered
    assert "output_language" not in rendered
    assert "book_language" not in rendered
    assert "chapter_ref" not in rendered
    assert "chapter_path" not in rendered
    assert "source_span" not in rendered
    assert "sentence_id" not in rendered
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "book_identity" not in rendered
    assert "chapter_identity" not in rendered
    assert "ref=" not in rendered
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt


def test_read_book_info_template_uses_only_dynamic_slots() -> None:
    root = READ_BOOK_INFO_TEMPLATE[0]

    assert root.element_name == "BookInfo"
    assert [child.element_name for child in root.children] == ["BookIdentity"]
    assert [child.value_slot for child in root.children] == ["book_identity"]
    assert all(child.prompt_fragment_ref is None for child in root.children)


def test_read_current_focus_xml_renders_mainline_source_unit_with_paragraphs() -> None:
    rendered = render_read_current_focus_xml(
        chapter_title="第一章",
        current_unit_source={
            "source_span_id": "src:c1:p45@0-p46@24",
            "source_span": {
                "start_cursor": {"paragraph_index": 45, "char_offset": 0},
                "end_cursor": {"paragraph_index": 46, "char_offset": 24},
            },
            "source_text": "第一段。\n\n第二段。",
            "paragraph_slices": [
                {
                    "paragraph_index": 45,
                    "text_role": "body",
                    "start_char": 0,
                    "end_char": 3,
                    "text": "第一段 & A。",
                },
                {
                    "paragraph_index": 46,
                    "text_role": "body",
                    "start_char": 0,
                    "end_char": 3,
                    "text": "第二段 <B>。",
                },
            ],
        },
    )

    assert "<CurrentFocus>" in rendered
    assert "<ReadingPath>" in rendered
    assert '"mode": "mainline"' in rendered
    assert "<ReadingPosition>" in rendered
    assert '"chapter_title": "第一章"' in rendered
    assert '"human_position": "第一章, p45-p46"' in rendered
    assert "<ReadingObject>" in rendered
    assert "<SourceUnit>" in rendered
    assert '<Paragraph n="45">' in rendered
    assert '<Paragraph n="46">' in rendered
    assert "第一段 &amp; A。" in rendered
    assert "第二段 &lt;B&gt;。" in rendered
    assert "<ReadingIntent>" in rendered
    assert '"intent": "read_current_source_unit_in_sequence"' in rendered
    assert "source_span_id" not in rendered
    assert "source_span" not in rendered
    assert "start_char" not in rendered
    assert "end_char" not in rendered
    assert "sentence_id" not in rendered
    assert "paragraph_slices" not in rendered
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "reading_path" not in rendered
    assert "reading_position" not in rendered
    assert "reading_intent" not in rendered
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt


def test_read_current_focus_xml_renders_current_sentences_fallback() -> None:
    rendered = render_read_current_focus_xml(
        chapter_title="第一章",
        current_unit_sentences=[
            {"sentence_id": "c1-s1", "text": "Fallback sentence & text.", "text_role": "body"}
        ],
    )

    assert '"mode": "mainline"' in rendered
    assert '"intent": "read_current_source_unit_in_sequence"' in rendered
    assert "Fallback sentence &amp; text." in rendered
    assert "sentence_id" not in rendered


def test_read_current_focus_template_declares_target_children() -> None:
    root = READ_CURRENT_FOCUS_TEMPLATE[0]

    assert root.element_name == "CurrentFocus"
    assert [child.element_name for child in root.children] == [
        "ReadingPath",
        "ReadingPosition",
        "ReadingObject",
        "ReadingIntent",
    ]


def test_read_reading_state_xml_projects_recent_memory_as_text_array_only() -> None:
    rendered = render_read_reading_state_xml(
        recent_reading_memory={
            "active_entries": [
                {
                    "entry_id": "recent:c1:u0001:m1",
                    "kind": "event_or_situation",
                    "memory_text": "作者说明 A & B < C。",
                    "source_unit_span_id": "src:c1:p1@0-p1@20",
                    "created_at_unit_index": 1,
                    "status": "active",
                },
                {
                    "entry_id": "recent:c1:u0002:m1",
                    "kind": "claim_or_argument",
                    "memory_text": "第二个阅读单元把作者的证据边界说清楚。",
                    "source_unit_span_id": "src:c1:p2@0-p2@20",
                    "created_at_unit_index": 2,
                    "status": "active",
                },
                {
                    "entry_id": "recent:c1:u0003:m1",
                    "kind": "other",
                    "memory_text": "",
                },
            ],
            "active_entry_count": 3,
        }
    )

    assert "<ReadingState>" in rendered
    assert "<ReadingMemory>" in rendered
    assert "<RecentMemory>" in rendered
    assert "作者说明 A &amp; B &lt; C。" in rendered
    assert "第二个阅读单元把作者的证据边界说清楚。" in rendered
    assert "recent:c1:u0001:m1" not in rendered
    assert "event_or_situation" not in rendered
    assert "source_unit_span_id" not in rendered
    assert "created_at_unit_index" not in rendered
    assert "active_entry_count" not in rendered
    assert "active_entries" not in rendered
    assert "status" not in rendered
    assert "<DurableMemory>" not in rendered
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "recent_memory" not in rendered
    assert "ref=" not in rendered
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt


def test_read_reading_state_template_declares_recent_memory_subset() -> None:
    root = READ_READING_STATE_TEMPLATE[0]

    assert root.element_name == "ReadingState"
    assert [child.element_name for child in root.children] == ["ReadingMemory"]
    reading_memory = root.children[0]
    assert [child.element_name for child in reading_memory.children] == ["RecentMemory"]
    assert reading_memory.children[0].value_slot == "recent_memory"


def test_read_output_contract_xml_renders_target_contract_without_live_migration() -> None:
    rendered = render_read_output_contract_xml(output_language_name="Chinese")

    assert "<OutputContract>" in rendered
    assert "<OutputUseGuide>" in rendered
    assert "<LanguageContract>" in rendered
    assert "必须使用 Chinese" in rendered
    assert "<ReturnFormat>" in rendered
    assert '"reading_impression": "..."' in rendered
    assert '"surfaced_reactions": []' in rendered
    assert '"recent_reading_memory": []' in rendered
    assert '"memory_uptake_ops"' not in rendered
    assert "<FieldContracts>" in rendered
    assert "<ReadingImpressionContract>" in rendered
    assert "immediate expression after finishing the current unit" in rendered
    assert "not durable memory and is not Recent Reading Memory" in rendered
    assert "not be carried into later Read context" in rendered
    assert "<SurfacedReactionContract>" in rendered
    assert '"source_quote": "..."' in rendered
    assert "<RecentReadingMemoryContract>" in rendered
    assert "Write only Recent Reading Memory entries here." in rendered
    assert "Do not include operation-level reasons." in rendered
    assert "prompt_fragment_ref" not in rendered
    assert "value_slot" not in rendered
    assert "language_contract" not in rendered
    assert "read.output_use_guide" not in rendered
    assert "ref=" not in rendered
    assert READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system == READ_UNIT_SYSTEM_PROMPT
    assert "Structural frame:" in ATTENTIONAL_V2_PROMPTS.read_unit_prompt


def test_read_output_contract_template_declares_target_children() -> None:
    root = READ_OUTPUT_CONTRACT_TEMPLATE[0]

    assert root.element_name == "OutputContract"
    assert [child.element_name for child in root.children] == [
        "OutputUseGuide",
        "LanguageContract",
        "ReturnFormat",
        "FieldContracts",
    ]
    field_contracts = root.children[3]
    assert [child.element_name for child in field_contracts.children] == [
        "ReadingImpressionContract",
        "SurfacedReactionContract",
        "RecentReadingMemoryContract",
    ]
    assert render_prompt_template_xml(
        READ_OUTPUT_CONTRACT_TEMPLATE,
        registry=READ_OUTPUT_CONTRACT_FRAGMENT_REGISTRY,
        slot_values={"language_contract": "Use Chinese."},
    ).startswith("<OutputContract>")


def test_read_unit_role_and_instruction_fragments_are_lossless() -> None:
    fragment_ids = [fragment.fragment_id for fragment in READ_UNIT_ROLE_AND_INSTRUCTION_FRAGMENTS]

    assert fragment_ids == [
        "read.role_and_stance",
        "read.reading_impression_policy",
        "read.surfaced_reaction_policy",
        "read.reaction_anchor_and_callback_policy",
        "read.memory_general_policy",
        "read.recent_reading_memory_policy",
        "read.durable_memory_policy",
        "read.active_tension_policy",
        "read.source_grounding_policy",
        "read.output_behavior_policy",
    ]
    assert len(set(fragment_ids)) == len(fragment_ids)
    assert READ_UNIT_SYSTEM_PROMPT == "\n".join(
        fragment.text for fragment in READ_UNIT_ROLE_AND_INSTRUCTION_FRAGMENTS
    )
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system == READ_UNIT_SYSTEM_PROMPT
    assert READ_UNIT_SYSTEM_PROMPT.startswith("You are a careful reader")


def test_attentional_v2_prompt_registry_contains_node_definitions() -> None:
    definitions = ATTENTIONAL_V2_PROMPT_REGISTRY.list()
    prompt_ids = [definition.prompt_id for definition in definitions]

    assert len(definitions) == 7
    assert len(set(prompt_ids)) == len(prompt_ids)
    assert prompt_ids == [
        "attentional_v2.survey_chapter_zone",
        "attentional_v2.navigate_choose_next_unit",
        "attentional_v2.read_unit",
        "attentional_v2.bridge_resolution",
        "attentional_v2.reflective_promotion",
        "attentional_v2.reconsolidation",
        "attentional_v2.chapter_consolidation",
    ]
    assert all(definition.status == "active" for definition in definitions)
    assert all(definition.required_inputs for definition in definitions)
    assert all(definition.output_contract.endswith(("_v1", "_v2", "_v3")) for definition in definitions)


def test_attentional_v2_prompt_registry_projects_current_bundle() -> None:
    read = ATTENTIONAL_V2_PROMPT_REGISTRY.get("attentional_v2.read_unit")
    navigate = ATTENTIONAL_V2_PROMPT_REGISTRY.get("attentional_v2.navigate_choose_next_unit")
    chapter = ATTENTIONAL_V2_PROMPT_REGISTRY.get("attentional_v2.chapter_consolidation")

    assert ATTENTIONAL_V2_PROMPTSET_VERSION == "attentional_v2-phase6-v40"
    assert ATTENTIONAL_V2_PROMPTS.promptset_version == ATTENTIONAL_V2_PROMPTSET_VERSION
    assert read.version == READ_UNIT_PROMPT_VERSION == "attentional_v2.read.v32"
    assert ATTENTIONAL_V2_PROMPTS.read_unit_version == read.version
    assert ATTENTIONAL_V2_PROMPTS.read_unit_system == read.system_prompt
    assert ATTENTIONAL_V2_PROMPTS.read_unit_prompt == read.user_prompt_template
    assert ATTENTIONAL_V2_PROMPTS.navigate_choose_next_unit_system == navigate.system_prompt
    assert ATTENTIONAL_V2_PROMPTS.chapter_consolidation_prompt == chapter.user_prompt_template


def test_prompt_registry_rejects_duplicate_prompt_ids() -> None:
    read = ATTENTIONAL_V2_PROMPT_REGISTRY.get("attentional_v2.read_unit")

    with pytest.raises(ValueError, match="Duplicate prompt id"):
        PromptRegistry([read, read])


def _fixture_epub() -> Path:
    """Return the tracked EPUB fixture used for live runner tests."""

    return Path(__file__).resolve().parent / "fixtures" / "e2e_runtime" / "sample-upload.epub"


def _provisioned_book() -> ProvisionedBook:
    """Return a lightweight shared parsed-book fixture for attentional runner tests."""

    book_document = {
        "metadata": {
            "book": "Demo Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Alpha sentence. Beta sentence.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:24",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Alpha sentence.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 15,
                            "start_cfi": "/6/2[chap01]!/4/2/1:0",
                            "end_cfi": "/6/2[chap01]!/4/2/1:15",
                        },
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "Beta sentence.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 16,
                            "char_end": 30,
                            "start_cfi": "/6/2[chap01]!/4/2/1:16",
                            "end_cfi": "/6/2[chap01]!/4/2/1:30",
                        },
                    },
                ],
            }
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Demo Book",
        author="Tester",
        book_language="en",
        output_language="en",
        output_dir=Path("output/demo-book"),
        raw_chapters=None,
        book_document=book_document,
    )


def _provisioned_two_chapter_book() -> ProvisionedBook:
    """Return a compact two-chapter fixture."""

    book_document = {
        "metadata": {
            "book": "Two Chapter Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Opening setup. First consequence.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:32",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Opening setup.",
                        "text_role": "body",
                        "locator": {"href": "chapter-1.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 14},
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "First consequence.",
                        "text_role": "body",
                        "locator": {"href": "chapter-1.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 15, "char_end": 33},
                    },
                ],
            },
            {
                "id": 2,
                "title": "Chapter 2",
                "chapter_number": 2,
                "reference": "Chapter 2",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Later question. Closing line.",
                        "href": "chapter-2.xhtml",
                        "start_cfi": "/6/2[chap02]!/4/2/1:0",
                        "end_cfi": "/6/2[chap02]!/4/2/1:28",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c2-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Later question.",
                        "text_role": "body",
                        "locator": {"href": "chapter-2.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 15},
                    },
                    {
                        "sentence_id": "c2-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "Closing line.",
                        "text_role": "body",
                        "locator": {"href": "chapter-2.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 16, "char_end": 29},
                    },
                ],
            },
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Two Chapter Book",
        author="Tester",
        book_language="en",
        output_language="en",
        output_dir=Path("output/two-chapter-book"),
        raw_chapters=None,
        book_document=book_document,
    )


def _provisioned_book_with_supporting_chapters() -> ProvisionedBook:
    """Return a three-chapter fixture with support material around one body chapter."""

    book_document = {
        "metadata": {
            "book": "Support Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Preface",
                "chapter_number": None,
                "reference": "Preface",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "How to use this book.",
                        "href": "preface.xhtml",
                        "start_cfi": "/6/2[preface]!/4/2/1:0",
                        "end_cfi": "/6/2[preface]!/4/2/1:22",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "How to use this book.",
                        "text_role": "body",
                        "locator": {
                            "href": "preface.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 22,
                        },
                    }
                ],
            },
            {
                "id": 2,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Main idea.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:10",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c2-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Main idea.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 10,
                        },
                    }
                ],
            },
            {
                "id": 3,
                "title": "Afterword",
                "chapter_number": None,
                "reference": "Afterword",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Closing reflection.",
                        "href": "afterword.xhtml",
                        "start_cfi": "/6/2[afterword]!/4/2/1:0",
                        "end_cfi": "/6/2[afterword]!/4/2/1:18",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c3-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Closing reflection.",
                        "text_role": "body",
                        "locator": {
                            "href": "afterword.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 18,
                        },
                    }
                ],
            },
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Support Book",
        author="Tester",
        book_language="en",
        output_language="en",
        output_dir=Path("output/support-book"),
        raw_chapters=None,
        book_document=book_document,
    )


@pytest.fixture(autouse=True)
def _stub_survey_artifacts(monkeypatch):
    """Keep scaffold tests deterministic by stubbing the survey artifact writer."""

    def fake_write_book_survey_artifacts(output_dir, book_document, *, policy_snapshot=None):
        chapters = [dict(chapter) for chapter in book_document.get("chapters", []) if isinstance(chapter, dict)]
        chapter_map = []
        mainline_chapter_ids: list[int] = []
        deferred_chapter_ids: list[int] = []
        for chapter in chapters:
            chapter_id = int(chapter.get("id", 0) or 0)
            title = str(chapter.get("title", "") or "")
            lowered = title.lower()
            if any(marker in lowered for marker in ("preface", "foreword", "introduction", "prologue")):
                zone = "front_support"
                deferred_chapter_ids.append(chapter_id)
            elif any(marker in lowered for marker in ("appendix", "afterword", "epilogue", "postscript")):
                zone = "back_support"
                deferred_chapter_ids.append(chapter_id)
            elif any(marker in lowered for marker in ("notes", "references", "bibliography", "index")):
                zone = "auxiliary"
            else:
                zone = "main_body"
                mainline_chapter_ids.append(chapter_id)
            chapter_map.append(
                {
                    "chapter_id": chapter_id,
                    "title": title,
                    "chapter_number": chapter.get("chapter_number"),
                    "level": int(chapter.get("level", 1) or 1),
                    "structural_role_guess": "body",
                    "role_confidence": "weak",
                    "chapter_zone": zone,
                    "zone_confidence": "stub",
                    "zone_reason": "test_stub",
                    "heading_text": "",
                    "opening_sentences": [],
                    "closing_sentences": [],
                    "pivot_headings": [],
                }
            )
        if not mainline_chapter_ids:
            mainline_chapter_ids = [
                int(chapter.get("id", 0) or 0)
                for chapter in chapters
                if int(chapter.get("id", 0) or 0) > 0 and int(chapter.get("id", 0) or 0) not in deferred_chapter_ids
            ]
        survey = {
            "schema_version": 1,
            "mechanism_version": "attentional_v2-phase6",
            "generated_at": "2026-04-22T00:00:00Z",
            "status": "orientation_only",
            "book_frame": {
                "book": str(book_document.get("metadata", {}).get("book", "") or ""),
                "author": str(book_document.get("metadata", {}).get("author", "") or ""),
                "total_chapters": len(chapters),
            },
            "chapter_map": chapter_map,
            "reading_plan": {
                "mode": "body_first",
                "mainline_chapter_ids": mainline_chapter_ids,
                "deferred_chapter_ids": deferred_chapter_ids,
            },
            "initial_motif_seeds": [],
            "survey_caveats": [],
            "policy_snapshot": dict(policy_snapshot or {}),
        }
        revisit = {
            "schema_version": 1,
            "mechanism_version": "attentional_v2-phase6",
            "generated_at": "2026-04-22T00:00:00Z",
            "status": "survey_seeded",
            "anchors": {},
            "chapter_boundaries": {},
            "opening_sentence_ids": [],
        }
        survey_map_file(output_dir).write_text(json.dumps(survey, ensure_ascii=False, indent=2), encoding="utf-8")
        revisit_index_file(output_dir).write_text(json.dumps(revisit, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"survey_map": survey, "revisit_index": revisit}

    monkeypatch.setattr(runner_module, "write_book_survey_artifacts", fake_write_book_survey_artifacts)


def test_attentional_v2_initialization_writes_mechanism_artifacts(tmp_path):
    """The mechanism should write the shared shell and private state files."""

    output_dir = tmp_path / "output" / "demo-book"

    result = AttentionalV2Mechanism().initialize_artifacts(output_dir)

    assert result["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert result["mechanism_version"] == ATTENTIONAL_V2_MECHANISM_VERSION
    assert result["policy_version"] == ATTENTIONAL_V2_POLICY_VERSION

    shell = load_runtime_shell(runtime_shell_file(output_dir))
    assert shell["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert shell["mechanism_version"] == ATTENTIONAL_V2_MECHANISM_VERSION
    assert shell["observability_mode"] == "standard"
    assert shell["cursor"]["position_kind"] == "chapter"

    checkpoint = json.loads(checkpoint_summary_file(output_dir, "bootstrap").read_text(encoding="utf-8"))
    assert checkpoint["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert checkpoint["observability_mode"] == "standard"
    assert checkpoint["resume_kind"] == "warm_resume"

    manifest = json.loads(mechanism_manifest_file(output_dir, ATTENTIONAL_V2_MECHANISM_KEY).read_text(encoding="utf-8"))
    assert manifest["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY

    active_attention = json.loads(active_attention_file(output_dir).read_text(encoding="utf-8"))
    assert active_attention["schema_version"] == ATTENTIONAL_V2_SCHEMA_VERSION
    assert active_attention["active_items"] == []
    assert ("gate_" + "state") not in active_attention

    local_buffer = json.loads(local_buffer_file(output_dir).read_text(encoding="utf-8"))
    assert local_buffer["recent_sentences"] == []
    assert local_buffer["recent_meaning_units"] == []

    local_continuity = json.loads(local_continuity_file(output_dir).read_text(encoding="utf-8"))
    assert local_continuity["recent_sentence_ids"] == []
    assert set(local_continuity).issuperset(
        {"recent_sentence_ids", "open_meaning_unit_sentence_ids", "recent_meaning_units", "mainline_cursor"}
    )

    concept_registry = json.loads(concept_registry_file(output_dir).read_text(encoding="utf-8"))
    assert concept_registry["entries"] == []

    thread_trace = json.loads(thread_trace_file(output_dir).read_text(encoding="utf-8"))
    assert thread_trace["entries"] == []

    assert not (active_attention_file(output_dir).parent / "anchor_bank.json").exists()

    reflective = json.loads(reflective_frames_file(output_dir).read_text(encoding="utf-8"))
    assert reflective["chapter_understandings"] == []

    activations = json.loads(knowledge_activations_file(output_dir).read_text(encoding="utf-8"))
    assert activations["knowledge_use_mode"] == "book_grounded_only"
    assert activations["search_policy_mode"] == "no_search"

    reaction_records = json.loads(reaction_records_file(output_dir).read_text(encoding="utf-8"))
    assert reaction_records["records"] == []

    reconsolidation = json.loads(reconsolidation_records_file(output_dir).read_text(encoding="utf-8"))
    assert reconsolidation["records"] == []

    policy = json.loads(reader_policy_file(output_dir).read_text(encoding="utf-8"))
    assert policy["policy_version"] == ATTENTIONAL_V2_POLICY_VERSION
    assert policy["unitize"]["max_coverage_unit_sentences"] == 12
    assert policy["bridge"]["enabled"] is False
    assert policy["bridge"]["source_ref_required"] is True
    assert policy["search"]["default_mode"] == "no_search"
    assert policy["resume"]["cold_resume_target_sentences"] == 8
    assert policy["resume"]["reconstitution_resume_max_sentences"] == 30
    assert policy["logging"]["observability_mode"] == "standard"
    assert policy["logging"]["debug_event_stream"] is False

    resume_metadata = json.loads(resume_metadata_file(output_dir).read_text(encoding="utf-8"))
    assert resume_metadata["resume_available"] is False
    assert resume_metadata["default_resume_kind"] == "warm_resume"

    survey = json.loads(survey_map_file(output_dir).read_text(encoding="utf-8"))
    assert survey["status"] == "not_started"
    assert survey["chapter_map"] == []
    assert survey["reading_plan"]["mode"] == "body_first"
    assert survey["reading_plan"]["mainline_chapter_ids"] == []
    assert survey["reading_plan"]["deferred_chapter_ids"] == []

    revisit = json.loads(revisit_index_file(output_dir).read_text(encoding="utf-8"))
    assert revisit["anchors"] == {}

    assert event_stream_file(output_dir).read_text(encoding="utf-8") == ""
    assert result["artifact_map"]["active_attention"].endswith("active_attention.json")
    assert result["artifact_map"]["settlement_audit"].endswith("settlement_audit.jsonl")
    assert result["artifact_map"]["slow_cycle_audit"].endswith("slow_cycle_audit.jsonl")
    assert result["artifact_map"]["unit_span_ledger"].endswith("unit_span_ledger.jsonl")
    assert not slow_cycle_audit_file(output_dir).exists()
    assert unit_span_ledger_file(output_dir).read_text(encoding="utf-8") == ""


def test_attentional_v2_parse_book_creates_ready_artifacts_without_iterator_structure(tmp_path, monkeypatch):
    """The live parse path should build canonical attentional artifacts without iterator structure."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())
    mechanism = AttentionalV2Mechanism()
    result = mechanism.parse_book(
        ParseRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
        )
    )

    assert result.book_document["chapters"]
    assert result.mechanism_artifact is not None
    assert result.mechanism_artifact["artifact_map"]["survey_map"].endswith("survey_map.json")
    assert survey_map_file(result.output_dir).exists()
    assert not (result.output_dir / "_mechanisms" / "iterator_v1" / "derived" / "structure.json").exists()
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert json.loads((result.output_dir / "public" / "book_manifest.json").read_text(encoding="utf-8"))["chapters"]
    survey = json.loads(survey_map_file(result.output_dir).read_text(encoding="utf-8"))
    assert survey["reading_plan"]["mode"] == "body_first"


def test_attentional_v2_runner_prefers_main_body_before_supporting_chapters(tmp_path, monkeypatch):
    """Full-book runs should consume main-body chapters before deferred support chapters."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book_with_supporting_chapters())
    chapter_read_order: list[str] = []

    def fake_read_unit(**kwargs):
        focal_sentence = kwargs["current_unit_sentences"][-1]
        chapter_read_order.append(str(kwargs["chapter_title"]))
        return {
            "reading_impression": f"Read {focal_sentence['sentence_id']}.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        return {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    manifest = json.loads((result.output_dir / "public" / "book_manifest.json").read_text(encoding="utf-8"))
    assert chapter_read_order == ["Chapter 1", "Preface", "Afterword"]
    assert shell["status"] == "completed"
    assert manifest["chapters"][0]["status"] == "done"
    assert manifest["chapters"][1]["status"] == "done"
    assert manifest["chapters"][2]["status"] == "done"


def test_attentional_v2_chapter_selection_honors_explicit_request_over_reading_plan(tmp_path):
    """Explicit chapter requests should bypass body-first chapter reordering."""

    document = _provisioned_book_with_supporting_chapters().book_document
    output_dir = tmp_path / "output" / "support-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)
    survey_map = {
        "reading_plan": {
            "mode": "body_first",
            "mainline_chapter_ids": [2],
            "deferred_chapter_ids": [1, 3],
        }
    }

    chapters = runner_module._chapter_selection(  # noqa: SLF001
        document,
        output_dir,
        survey_map=survey_map,
        chapter_number=3,
        continue_mode=False,
        resume_chapter_id=None,
    )

    assert [chapter["title"] for chapter in chapters] == ["Afterword"]


def _empty_choose_next_unit_state() -> dict[str, dict[str, object]]:
    """Return the minimal live state required by Navigate.choose_next_unit."""

    return {
        "local_buffer": build_empty_local_buffer(),
        "local_continuity": build_empty_local_continuity(),
        "continuation_capsule": {},
        "active_attention": build_empty_active_attention(),
        "concept_registry": build_empty_concept_registry(),
        "thread_trace": build_empty_thread_trace(),
        "reflective_frames": build_empty_reflective_frames(),
        "reaction_records": build_empty_reaction_records(),
    }


def _fake_single_sentence_navigate_act(**kwargs):
    """Return one small source-anchor unit for runner smoke tests."""

    preview = kwargs.get("mainline_preview", {})
    source_text = str(preview.get("source_text", "") if isinstance(preview, dict) else "")
    stripped = source_text.lstrip()
    if "." in stripped:
        end_anchor_text = stripped[: stripped.index(".") + 1]
    else:
        end_anchor_text = stripped
    return {
        "decision": "choose_unit",
        "selection_mode": "mainline",
        "end_anchor_text": end_anchor_text,
        "boundary_type": "paragraph_end",
        "reason": "test_choose_source_anchor_unit",
        "continuation_pressure": False,
    }


def test_navigate_choose_next_unit_selects_mainline_unit(tmp_path, monkeypatch):
    """The current Navigator contract should wrap mainline unitization as one next-unit decision."""

    provisioned = _provisioned_two_chapter_book()
    document = provisioned.book_document
    state = _empty_choose_next_unit_state()

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)

    result = runner_module.navigate_choose_next_unit(
        current_chapter=document["chapters"][1],
        current_cursor={"paragraph_index": 1, "char_offset": 0},
        local_buffer=state["local_buffer"],  # type: ignore[arg-type]
        continuation_capsule=state["continuation_capsule"],
        active_attention=state["active_attention"],  # type: ignore[arg-type]
        concept_registry=state["concept_registry"],  # type: ignore[arg-type]
        thread_trace=state["thread_trace"],  # type: ignore[arg-type]
        reflective_frames=state["reflective_frames"],  # type: ignore[arg-type]
        reaction_records=state["reaction_records"],  # type: ignore[arg-type]
        local_continuity=state["local_continuity"],  # type: ignore[arg-type]
        reader_policy=runner_module.build_default_reader_policy(),
        output_language=provisioned.output_language,
        output_dir=tmp_path,
        book_title=provisioned.title,
        author=provisioned.author,
    )

    assert result["selection_mode"] == "mainline"
    assert result["chapter_id"] == 2
    assert [sentence["sentence_id"] for sentence in result["selected_unit_sentences"]] == ["c2-s1"]


def test_attentional_v2_read_book_runs_live_loop_and_persists_compatibility_results(tmp_path, monkeypatch):
    """The live runner should persist unitization/read audits, reactions, and compatibility payloads."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())
    captured_unit_reads: list[list[str]] = []
    captured_carry_forward_contexts: list[dict[str, object]] = []

    def fake_read_unit(**kwargs):
        current_unit_sentences = kwargs["current_unit_sentences"]
        focal_sentence = current_unit_sentences[-1]
        anchor_quote = str(focal_sentence.get("text", "") or "").strip()[:80]
        captured_unit_reads.append([str(sentence.get("sentence_id")) for sentence in current_unit_sentences])
        captured_carry_forward_contexts.append(dict(kwargs["carry_forward_context"]))
        return {
            "reading_impression": f"Meaning unit around {anchor_quote[:24]}",
            "surfaced_reactions": [
                {
                    "source_quote": anchor_quote,
                    "content": f"Read noticed: {anchor_quote[:40]}",
                    "prior_link": {
                        "ref_ids": ["source:src:c1:p1@0-p1@10"],
                        "relation": "callback",
                        "note": "The earlier thread quietly set this up.",
                    },
                }
            ],
            "memory_uptake_ops": [
                {
                    "operation_type": "append",
                    "target_store": "active_attention",
                    "target_key": f"hot-{focal_sentence.get('sentence_id')}",
                    "payload": {
                        "tension_from": f"The unit leaves a charge around: {anchor_quote[:24]}",
                        "tension_focus": "This point remains alive in attention.",
                        "working_interpretation": "",
                        "attention_tags": ["motif"],
                        "last_touched_sentence_id": focal_sentence.get("sentence_id"),
                    },
                }
            ],
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    assert result.normalized_eval_bundle is not None
    assert result.normalized_eval_bundle["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    unitize_lines = unitization_audit_file(result.output_dir).read_text(encoding="utf-8").strip().splitlines()
    read_audit_lines = read_audit_file(result.output_dir).read_text(encoding="utf-8").strip().splitlines()
    settlement_audit_lines = settlement_audit_file(result.output_dir).read_text(encoding="utf-8").strip().splitlines()
    unit_span_lines = unit_span_ledger_file(result.output_dir).read_text(encoding="utf-8").strip().splitlines()
    read_audits = [json.loads(line) for line in read_audit_lines]
    settlement_audits = [json.loads(line) for line in settlement_audit_lines]
    unit_spans = [json.loads(line) for line in unit_span_lines]
    assert chapter_payload["visible_reaction_count"] >= 1
    assert captured_unit_reads == [["c1-s1"], ["c1-s2"]]
    assert captured_carry_forward_contexts[0]["packet_version"] == "attentional_v2.state_packet.v1"
    assert "active_attention_digest" in captured_carry_forward_contexts[0]
    assert captured_carry_forward_contexts[0]["continuity_digest"]["recent_reactions"] == []
    assert captured_carry_forward_contexts[1]["continuity_digest"]["recent_reactions"]
    assert len(unitize_lines) == 2
    assert len(read_audit_lines) == 2
    assert len(settlement_audit_lines) == 2
    assert len(unit_span_lines) == 2
    assert [record["start_cursor"]["char_offset"] for record in unit_spans] == [0, 15]
    assert [record["end_cursor"]["char_offset"] for record in unit_spans] == [15, 30]
    paragraph_text = result.book_document["chapters"][0]["paragraphs"][0]["text"]
    reconstructed = "".join(
        paragraph_text[record["start_cursor"]["char_offset"] : record["end_cursor"]["char_offset"]]
        for record in unit_spans
    )
    assert reconstructed == paragraph_text
    assert all(audit["surfaced_reaction_count"] == 1 for audit in read_audits)
    assert all(audit["source_span_id"] for audit in read_audits)
    assert read_audits[1]["carry_forward_ref_ids"]
    assert settlement_audits[0]["memory_uptake_ops_by_target_store"] == {"active_attention": 1}
    assert settlement_audits[0]["source_span_id"] == unit_spans[0]["source_span_id"]
    assert settlement_audits[0]["state_deltas"]["active_attention"]["added_ids"] == ["hot-c1-s1"]
    assert settlement_audits[0]["state_deltas"]["reaction_records"]["added_ids"]
    assert "anchor_bank" not in settlement_audits[0]["state_deltas"]
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert shell["status"] == "completed"
    assert shell["last_checkpoint_id"] == "chapter-001"
    manifest = json.loads((result.output_dir / "public" / "book_manifest.json").read_text(encoding="utf-8"))
    chapter_manifest = manifest["chapters"][0]
    assert chapter_manifest["result_file"] == "_mechanisms/attentional_v2/derived/chapter_result_compatibility/chapter-001.json"
    assert chapter_manifest["visible_reaction_count"] >= 1
    assert chapter_manifest["reaction_type_diversity"] >= 1
    persisted_reactions = json.loads(reaction_records_file(result.output_dir).read_text(encoding="utf-8"))["records"]
    assert persisted_reactions[0]["record_source"] == "read_surface"
    assert persisted_reactions[0]["thought"].startswith("Read noticed:")
    assert persisted_reactions[0]["prior_link"]["ref_ids"] == ["source:src:c1:p1@0-p1@10"]


def test_attentional_v2_runner_persists_multiple_read_surface_reactions(tmp_path, monkeypatch):
    """Read-owned surfaced reactions should persist directly without a separate express pass."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())

    def fake_read_unit(**kwargs):
        focal_sentence = kwargs["current_unit_sentences"][-1]
        anchor_quote = str(focal_sentence.get("text", "") or "").strip()[:80]
        return {
            "reading_impression": f"Meaning unit around {anchor_quote[:24]}",
            "surfaced_reactions": [
                {
                    "source_quote": anchor_quote,
                    "content": f"First surfaced: {anchor_quote[:20]}",
                },
                {
                    "source_quote": anchor_quote,
                    "content": f"Second surfaced: {anchor_quote[:20]}",
                    "search_intent": {
                        "query": "why this line lands so hard",
                        "rationale": "The second reaction opens a follow-up question.",
                    },
                },
            ],
            "memory_uptake_ops": [],
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    persisted_reactions = json.loads(reaction_records_file(result.output_dir).read_text(encoding="utf-8"))["records"]
    assert len(persisted_reactions) == 4
    assert all(record["record_source"] == "read_surface" for record in persisted_reactions)
    assert persisted_reactions[0]["thought"].startswith("First surfaced:")
    assert persisted_reactions[1]["search_intent"]["query"] == "why this line lands so hard"


def test_attentional_v2_read_book_tolerates_missing_reaction_payload(tmp_path, monkeypatch):
    """The live runner should tolerate a read result with no raw reaction payload."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())

    def fake_read_unit(**kwargs):
        focal_sentence = kwargs["current_unit_sentences"][-1]
        anchor_quote = str(focal_sentence.get("text", "") or "").strip()[:80]
        return {
            "reading_impression": f"Meaning unit around {anchor_quote[:24]}",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    assert result.normalized_eval_bundle is not None
    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    assert chapter_payload["visible_reaction_count"] == 0
    reaction_records = json.loads(reaction_records_file(result.output_dir).read_text(encoding="utf-8"))
    assert reaction_records["records"] == []
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["status"] == "completed"


def test_attentional_v2_read_book_runs_source_anchor_units_without_sentence_cursor(tmp_path, monkeypatch):
    """Source-anchor units should enter formal reads without sentence-intake cursor state."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    read_calls: list[list[str]] = []

    def fake_read_unit(**kwargs):
        read_calls.append(
            [
                str(sentence.get("sentence_id"))
                for sentence in kwargs["current_unit_sentences"]
            ]
        )
        return {
            "reading_impression": "single-sentence path still got read",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
        }

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    local_buffer = json.loads(local_buffer_file(result.output_dir).read_text(encoding="utf-8"))
    local_continuity = json.loads(local_continuity_file(result.output_dir).read_text(encoding="utf-8"))
    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    unit_span_records = [
        json.loads(line)
        for line in unit_span_ledger_file(result.output_dir).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))

    assert local_buffer["current_sentence_id"] == ""
    assert local_continuity["mainline_cursor"]["position_kind"] == "span"
    assert local_continuity["mainline_cursor"]["paragraph_index"] == 1
    assert local_continuity["mainline_cursor"]["char_offset"] == 30
    assert [record["end_cursor"]["char_offset"] for record in unit_span_records] == [15, 30]
    assert chapter_payload["visible_reaction_count"] == 0
    assert shell["status"] == "completed"
    assert read_calls == [["c1-s1"], ["c1-s2"]]


def test_attentional_v2_runner_stops_at_audit_window_cap_and_persists_partial_outputs(tmp_path, monkeypatch):
    """Audit-only unit caps should stop the live loop cleanly and still persist partial exports."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_two_chapter_book())
    read_calls: list[list[str]] = []

    def fake_read_unit(**kwargs):
        sentence_ids = [str(sentence.get("sentence_id")) for sentence in kwargs["current_unit_sentences"]]
        read_calls.append(sentence_ids)
        focal_sentence = kwargs["current_unit_sentences"][-1]
        return {
            "reading_impression": f"Read {sentence_ids[-1]}.",
            "surfaced_reactions": [
                {
                    "source_quote": str(focal_sentence.get("text")),
                    "content": f"Immediate reaction to {sentence_ids[-1]}.",
                }
            ],
            "memory_uptake_ops": [],
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    monkeypatch.setattr(runner_module, "navigate_choose_next_unit_act", _fake_single_sentence_navigate_act)
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(
        runner_module,
        "run_phase6_chapter_cycle",
        lambda **_kwargs: pytest.fail("phase6 should not run when audit_window_max_units stops the loop early"),
    )

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={"audit_window_max_units": 2},
        )
    )

    assert read_calls == [["c1-s1"], ["c1-s2"]]
    assert result.normalized_eval_bundle is not None
    assert len(result.normalized_eval_bundle["reactions"]) == 2
    assert chapter_result_compatibility_file(result.output_dir, 1).exists()
    assert not chapter_result_compatibility_file(result.output_dir, 2).exists()

    read_audit_entries = [
        json.loads(line)
        for line in read_audit_file(result.output_dir).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(read_audit_entries) == 2

    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    assert chapter_payload["visible_reaction_count"] == 2

    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["status"] == "completed"


def test_attentional_v2_rejects_book_analysis_mode(tmp_path, monkeypatch):
    """The live runner should fail fast on book_analysis mode in this slice."""

    monkeypatch.chdir(tmp_path)
    mechanism = AttentionalV2Mechanism()

    with pytest.raises(ValueError, match=r"does not support .*book_analysis mode"):
        mechanism.read_book(
            ReadRequest(
                book_path=_fixture_epub(),
                mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
                task_mode="book_analysis",
            )
        )
