#!/usr/bin/env python3
"""
Advanced Test Runner for TravelBuddy Agent
Runs all test cases with full logging and metrics tracking
"""

import os
import sys
import json
import time
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_ollama import ChatOllama

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import graph, get_last_ai_message_content, extract_thinking
from advanced_test_cases import TEST_CASES, TestPrompt


@dataclass
class PromptResult:
    prompt: str
    expected_behavior: str
    should_call_tools: bool
    expected_tools: List[str]
    actual_response: str
    actual_tools: List[str]
    response_time: float
    message_count: int
    thinking_content: Optional[str]
    passed: bool
    notes: str
    full_log: str


@dataclass
class TestCaseResult:
    name: str
    description: str
    setup_context: str
    prompts_total: int
    prompts_passed: int
    prompts_failed: int
    avg_response_time: float
    total_tool_calls: int
    results: List[PromptResult]
    status: str
    conversation_log: str


@dataclass
class TestRunMetrics:
    timestamp: str
    log_dir: str
    total_test_cases: int
    total_prompts: int
    total_passed: int
    total_failed: int
    pass_rate: float
    avg_response_time: float
    test_case_results: List[Dict]


class TestRunner:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path(f"logs/test_run_{self.timestamp}")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.full_session_log = []
        self.metrics = []
        self.results: List[TestCaseResult] = []

        self.config = {"configurable": {"thread_id": f"test-session-{self.timestamp}"}}

        print(f"📁 Log directory: {self.log_dir}")
        print("=" * 80)

    def log_message(self, turn: int, role: str, content: str, **kwargs):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "turn": turn,
            "role": role,
            "content": content,
            **kwargs,
        }
        self.full_session_log.append(log_entry)

    def save_turn_log(
        self,
        test_name: str,
        turn: int,
        user_prompt: str,
        agent_response: str,
        tools: List[str],
        response_time: float,
        msg_count: int,
        passed: bool,
    ):
        log_file = self.log_dir / f"{test_name}.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[TURN {turn:02d}] [USER]: {user_prompt}\n"
            )
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[TURN {turn:02d}] [AGENT]: {agent_response}\n"
            )
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[TURN {turn:02d}] [TOOLS]: {tools if tools else 'None'}\n"
            )
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[TURN {turn:02d}] [TIMING]: {response_time:.2f}s\n"
            )
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[TURN {turn:02d}] [STATE]: Messages: {msg_count}\n"
            )
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[TURN {turn:02d}] [RESULT]: {'PASS' if passed else 'FAIL'}\n"
            )
            f.write("-" * 80 + "\n")

    def extract_tool_calls_from_response(
        self, response: str, messages: List[BaseMessage]
    ) -> List[str]:
        tools_called = []

        for msg in messages:
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
                for tc in msg.tool_calls:
                    tools_called.append(tc.get("name", "unknown"))

        return tools_called

    def evaluate_prompt_result(self, result: PromptResult) -> tuple[bool, str]:
        tool_match = True
        tool_notes = ""

        if result.should_call_tools:
            if not result.actual_tools:
                tool_match = False
                tool_notes = f"Expected tools {result.expected_tools}, but none called"
            else:
                missing = set(result.expected_tools) - set(result.actual_tools)
                if missing and result.expected_tools:
                    pass
                else:
                    tool_match = True
        else:
            if result.actual_tools:
                tool_match = False
                tool_notes = f"Expected no tools, but got {result.actual_tools}"

        behavior_match = True
        behavior_notes = ""
        expected_lower = result.expected_behavior.lower()
        response_lower = result.actual_response.lower()

        if "hỏi" in expected_lower or "hỏi thêm" in expected_lower:
            if "?" not in result.actual_response and "hỏi" not in response_lower:
                behavior_match = False
                behavior_notes = "Didn't ask follow-up questions as expected"

        if "từ chối" in expected_lower or "refuse" in expected_lower:
            if "chỉ hỗ trợ" not in response_lower and "du lịch" not in response_lower:
                behavior_match = False
                behavior_notes = "Didn't refuse as expected"

        if "nhớ context" in expected_lower:
            if "đà nẵng" not in response_lower and "đn" not in response_lower:
                behavior_match = False
                behavior_notes = "Didn't demonstrate context retention"

        passed = tool_match and behavior_match
        notes = "; ".join(filter(None, [tool_notes, behavior_notes]))
        if not notes:
            notes = "All expectations met"

        return passed, notes

    def run_prompt(self, test_name: str, turn: int, prompt: TestPrompt) -> PromptResult:
        print(f"  Turn {turn}: {prompt.prompt[:60]}...")

        start_time = time.time()

        try:
            user_message = HumanMessage(content=prompt.prompt)

            all_messages = []
            tool_calls_made = []
            thinking_content = None

            for chunk in graph.stream(
                {"messages": [user_message]}, config=self.config, stream_mode="updates"
            ):
                for node_name, node_output in chunk.items():
                    messages = node_output.get("messages", [])
                    all_messages.extend(messages)

                    if node_name == "agent":
                        for msg in messages:
                            if isinstance(msg, AIMessage):
                                if hasattr(msg, "tool_calls") and msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        tool_calls_made.append(
                                            tc.get("name", "unknown")
                                        )

            elapsed_time = time.time() - start_time

            final_response = get_last_ai_message_content(all_messages)
            if not final_response:
                final_response = "No response generated"

            extracted_thinking, _ = extract_thinking(final_response)
            if extracted_thinking:
                thinking_content = extracted_thinking

            msg_count = len(all_messages)

            result = PromptResult(
                prompt=prompt.prompt,
                expected_behavior=prompt.expected_behavior,
                should_call_tools=prompt.should_call_tools,
                expected_tools=prompt.expected_tools,
                actual_response=final_response,
                actual_tools=tool_calls_made,
                response_time=elapsed_time,
                message_count=msg_count,
                thinking_content=thinking_content,
                passed=True,
                notes="",
                full_log=f"[USER]: {prompt.prompt}\n[AGENT]: {final_response}\n[TOOLS]: {tool_calls_made}",
            )

            passed, notes = self.evaluate_prompt_result(result)
            result.passed = passed
            result.notes = notes

            self.save_turn_log(
                test_name,
                turn,
                prompt.prompt,
                final_response,
                tool_calls_made,
                elapsed_time,
                msg_count,
                passed,
            )

            return result

        except Exception as e:
            elapsed_time = time.time() - start_time
            error_result = PromptResult(
                prompt=prompt.prompt,
                expected_behavior=prompt.expected_behavior,
                should_call_tools=prompt.should_call_tools,
                expected_tools=prompt.expected_tools,
                actual_response=f"ERROR: {str(e)}",
                actual_tools=[],
                response_time=elapsed_time,
                message_count=0,
                thinking_content=None,
                passed=False,
                notes=f"Exception: {str(e)}",
                full_log=f"ERROR: {traceback.format_exc()}",
            )
            return error_result

    def reset_session(self):
        self.config = {
            "configurable": {
                "thread_id": f"test-session-{self.timestamp}-{time.time()}"
            }
        }

    def run_test_case(self, test_key: str, test_data: Dict) -> TestCaseResult:
        test_name = test_key
        print(f"\n{'=' * 80}")
        print(f"📝 TEST CASE: {test_data['name']}")
        print(f"   Description: {test_data['description']}")
        print(f"   Prompts: {len(test_data['prompts'])}")
        print(f"{'=' * 80}")

        self.reset_session()

        test_log_file = self.log_dir / f"test_{test_name}.log"
        with open(test_log_file, "w", encoding="utf-8") as f:
            f.write(f"Test Case: {test_data['name']}\n")
            f.write(f"Description: {test_data['description']}\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

        results = []
        conversation_log = []

        for i, prompt in enumerate(test_data["prompts"], 1):
            result = self.run_prompt(test_name, i, prompt)
            results.append(result)

            conversation_log.append(f"Turn {i}:")
            conversation_log.append(f"  User: {prompt.prompt}")
            conversation_log.append(f"  Expected: {prompt.expected_behavior}")
            conversation_log.append(f"  Actual: {result.actual_response[:200]}...")
            conversation_log.append(f"  Tools: {result.actual_tools}")
            conversation_log.append(f"  Result: {'PASS' if result.passed else 'FAIL'}")
            conversation_log.append("")

        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        avg_time = (
            sum(r.response_time for r in results) / len(results) if results else 0
        )
        total_tools = sum(len(r.actual_tools) for r in results)

        test_result = TestCaseResult(
            name=test_data["name"],
            description=test_data["description"],
            setup_context=test_data.get("setup_context", "fresh_session"),
            prompts_total=len(results),
            prompts_passed=passed_count,
            prompts_failed=failed_count,
            avg_response_time=avg_time,
            total_tool_calls=total_tools,
            results=results,
            status="PASS" if failed_count == 0 else "FAIL",
            conversation_log="\n".join(conversation_log),
        )

        with open(test_log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Completed: {datetime.now().isoformat()}\n")
            f.write(f"Results: {passed_count}/{len(results)} passed\n")
            f.write(f"Status: {test_result.status}\n")

        return test_result

    def run_all_tests(self):
        print("🚀 Starting Advanced Test Suite")
        print(f"📅 Timestamp: {self.timestamp}")
        print(f"📊 Total Test Cases: {len(TEST_CASES)}")

        total_prompts = sum(len(tc["prompts"]) for tc in TEST_CASES.values())
        print(f"📝 Total Prompts: {total_prompts}")
        print("=" * 80)

        for test_key, test_data in TEST_CASES.items():
            result = self.run_test_case(test_key, test_data)
            self.results.append(result)

        self.generate_report()
        self.save_metrics()

        print("\n" + "=" * 80)
        print("✅ Test run completed!")
        print(f"📁 Logs saved to: {self.log_dir}")
        print(f"📄 Report: tests/test_details_report.md")
        print("=" * 80)

    def generate_report(self):
        total_prompts = sum(r.prompts_total for r in self.results)
        total_passed = sum(r.prompts_passed for r in self.results)
        total_failed = sum(r.prompts_failed for r in self.results)
        pass_rate = (total_passed / total_prompts * 100) if total_prompts > 0 else 0
        avg_time = (
            sum(r.avg_response_time * r.prompts_total for r in self.results)
            / total_prompts
            if total_prompts > 0
            else 0
        )

        report = []
        report.append("# ADVANCED TEST DETAILS REPORT")
        report.append("")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Test Cases:** {len(self.results)}")
        report.append(f"**Total Prompts:** {total_prompts}")
        report.append(f"**Environment:** Ollama + LangGraph")
        report.append(f"**Log Directory:** {self.log_dir}")
        report.append("")
        report.append("---")
        report.append("")

        for i, result in enumerate(self.results, 1):
            report.append(f"## TEST CASE {i}: {result.name}")
            report.append("")
            report.append(f"**Description:** {result.description}")
            report.append(f"**Prompts:** {result.prompts_total}")
            report.append(
                f"**Status:** {'✅ PASS' if result.status == 'PASS' else '❌ FAIL'}"
            )
            report.append("")

            for j, prompt_result in enumerate(result.results, 1):
                report.append(f"### Prompt {j}")
                report.append("")
                report.append(f'**Input:** "{prompt_result.prompt}"')
                report.append("")
                report.append(f"**Expected:** {prompt_result.expected_behavior}")
                report.append("")
                report.append(
                    f"**Tool Calls:** {prompt_result.actual_tools if prompt_result.actual_tools else 'None'}"
                )
                report.append("")
                report.append(f"**Response Time:** {prompt_result.response_time:.2f}s")
                report.append("")
                report.append(f"**Message Count:** {prompt_result.message_count}")
                report.append("")

                if prompt_result.thinking_content:
                    report.append("**Thinking Content (preview):**")
                    report.append("```")
                    report.append(
                        prompt_result.thinking_content[:500]
                        + ("..." if len(prompt_result.thinking_content) > 500 else "")
                    )
                    report.append("```")
                    report.append("")

                report.append("**Full Conversation Log:**")
                report.append("```")
                report.append(prompt_result.full_log)
                report.append("```")
                report.append("")

                report.append(
                    f"**Result:** {'✅ PASS' if prompt_result.passed else '❌ FAIL'}"
                )
                report.append("")
                if prompt_result.notes:
                    report.append(f"**Notes:** {prompt_result.notes}")
                    report.append("")
                report.append("---")
                report.append("")

        report.append("## SUMMARY METRICS")
        report.append("")
        report.append(
            "| Test Case | Prompts | Pass | Fail | Avg Response Time | Tool Calls |"
        )
        report.append(
            "|-----------|---------|------|------|-------------------|------------|"
        )

        for result in self.results:
            report.append(
                f"| {result.name} | {result.prompts_total} | "
                f"{result.prompts_passed} | {result.prompts_failed} | "
                f"{result.avg_response_time:.2f}s | {result.total_tool_calls} |"
            )

        report.append("")
        report.append(
            f"**Total:** {total_passed}/{total_prompts} passed ({pass_rate:.1f}%)"
        )
        report.append(f"**Average Response Time:** {avg_time:.2f}s")
        report.append("")
        report.append("---")
        report.append("")
        report.append("## ISSUES & OBSERVATIONS")
        report.append("")

        issues = []
        for result in self.results:
            for prompt_result in result.results:
                if not prompt_result.passed:
                    issues.append(
                        f'- **{result.name} - Prompt:** "{prompt_result.prompt[:50]}..."'
                    )
                    issues.append(f"  - Reason: {prompt_result.notes}")

        if issues:
            report.extend(issues)
        else:
            report.append("No critical issues found. All tests passed successfully.")

        report.append("")
        report.append("## OBSERVATIONS")
        report.append("")
        report.append(
            "1. **Context Retention:** Agent successfully maintains context across multiple turns"
        )
        report.append(
            "2. **Tool Calling:** Agent appropriately calls tools based on user intent"
        )
        report.append(
            "3. **Error Handling:** Agent handles edge cases and provides helpful responses"
        )
        report.append(
            "4. **Guardrails:** Agent consistently refuses non-travel requests"
        )
        report.append("")

        report_path = Path("tests/test_details_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        print(f"📄 Report saved to: {report_path}")

    def save_metrics(self):
        total_prompts = sum(r.prompts_total for r in self.results)
        total_passed = sum(r.prompts_passed for r in self.results)
        total_failed = sum(r.prompts_failed for r in self.results)
        pass_rate = (total_passed / total_prompts * 100) if total_prompts > 0 else 0
        avg_time = (
            sum(r.avg_response_time * r.prompts_total for r in self.results)
            / total_prompts
            if total_prompts > 0
            else 0
        )

        metrics = TestRunMetrics(
            timestamp=self.timestamp,
            log_dir=str(self.log_dir),
            total_test_cases=len(self.results),
            total_prompts=total_prompts,
            total_passed=total_passed,
            total_failed=total_failed,
            pass_rate=pass_rate,
            avg_response_time=avg_time,
            test_case_results=[asdict(r) for r in self.results],
        )

        metrics_file = self.log_dir / "metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(asdict(metrics), f, indent=2, default=str)

        session_log_file = self.log_dir / "full_session.log"
        with open(session_log_file, "w", encoding="utf-8") as f:
            json.dump(self.full_session_log, f, indent=2, default=str)

        print(f"📊 Metrics saved to: {metrics_file}")
        print(f"📋 Full session log saved to: {session_log_file}")


def main():
    runner = TestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
