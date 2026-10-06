from utils.ui import (
    print_banner,
    print_diff,
    print_node_result,
    print_node_start,
    print_summary_card,
)


def test_ui_renderers_run_without_errors():
    # Verify banner
    print_banner(repo_path="/test/repo", provider="ollama", model="qwen", mode="Local")

    # Verify node headers
    for node in ["Planner", "Coder", "Test Runner", "Evaluator", "PR Writer", "Custom"]:
        print_node_start(node, step_num=1, total_steps=5)

    # Verify diff renderer
    print_diff("--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new", title="Test Diff")
    print_diff("")  # empty diff handling

    # Verify node results
    print_node_result("Planner", {"relevant_files": ["foo.py"], "fix_plan": "step 1: fix"})
    print_node_result("Coder", {"patch_code": "modified foo.py"}, diff_snippet="diff...")
    print_node_result("Test Runner", {"test_output": "== 5 passed in 0.1s =="})
    print_node_result("Evaluator", {"status": "SUCCESS", "retry_count": 0})
    print_node_result("Evaluator", {"status": "FAILED", "retry_count": 1})
    print_node_result("PR Writer", {"status": "PR #1 created"})

    # Verify summary table
    print_summary_card(
        repo_path="/test/repo",
        task_desc="Fix bug in calculation",
        final_status="SUCCESS",
        nodes_executed=["Planner", "Coder", "Test Runner", "Evaluator", "PR Writer"],
        retries=0,
        branch_name="bugsolver/fix-test",
        pr_url="https://github.com/foo/bar/pull/1",
    )
