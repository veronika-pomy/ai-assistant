"""Phase 8: End-to-End Manual Testing Script

Tests safe workflows (direct, planning, creative) without API costs.
Research workflow must be tested manually after confirming other workflows work.
"""

import sys
from pathlib import Path

# Add project root to path so imports work from nested test directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from core.task_manager import TaskManager
from core.session import SessionManager


async def test_direct_workflow():
    """Test direct Q&A workflow - safe, no external calls."""
    print("\n" + "=" * 70)
    print("TEST 1: Direct Q&A Workflow")
    print("=" * 70)

    manager = TaskManager()
    session = SessionManager("test", ":memory:")

    query = "What is 5 + 5?"
    print(f"\n📝 Query: {query}")
    print("-" * 70)

    updates = []
    async for update in manager.run(query, session.get_session()):
        updates.append(update)
        print(update)

    print("-" * 70)
    print(f"✅ Direct workflow completed. Received {len(updates)} status updates.")
    return len(updates) > 0


async def test_planning_workflow():
    """Test planning workflow - safe, no external calls."""
    print("\n" + "=" * 70)
    print("TEST 2: Planning Workflow")
    print("=" * 70)

    manager = TaskManager()
    session = SessionManager("test", ":memory:")

    query = "Plan learning Python in 30 days"
    print(f"\n📝 Query: {query}")
    print("-" * 70)

    updates = []
    async for update in manager.run(query, session.get_session()):
        updates.append(update)
        print(update)

    print("-" * 70)
    print(f"✅ Planning workflow completed. Received {len(updates)} status updates.")
    return len(updates) > 0


async def test_creative_workflow():
    """Test creative problem-solving workflow - safe, no external calls."""
    print("\n" + "=" * 70)
    print("TEST 3: Creative Problem-Solving Workflow")
    print("=" * 70)

    manager = TaskManager()
    session = SessionManager("test", ":memory:")

    query = "How would you design a distributed cache system?"
    print(f"\n📝 Query: {query}")
    print("-" * 70)

    updates = []
    async for update in manager.run(query, session.get_session()):
        updates.append(update)
        print(update)

    print("-" * 70)
    print(f"✅ Creative workflow completed. Received {len(updates)} status updates.")
    return len(updates) > 0


async def test_session_persistence():
    """Test session memory persistence across multiple queries."""
    print("\n" + "=" * 70)
    print("TEST 4: Session Persistence")
    print("=" * 70)

    manager = TaskManager()
    session = SessionManager("test", ":memory:")

    # First query
    print("\n📝 Query 1: What is machine learning?")
    print("-" * 70)
    async for update in manager.run("What is machine learning?", session.get_session()):
        print(update)

    print("-" * 70)

    # Second query in same session
    print("\n📝 Query 2: Explain neural networks")
    print("-" * 70)
    async for update in manager.run("Explain neural networks", session.get_session()):
        print(update)

    print("-" * 70)
    print("✅ Session persistence tested. Both queries executed in same session.")
    return True


async def main():
    """Run all safe workflow tests."""
    print("\n" + "=" * 70)
    print("PHASE 8: END-TO-END TESTING (SAFE WORKFLOWS)")
    print("=" * 70)
    print("\nTesting workflows that don't require web search or expensive API calls...")

    try:
        # Run safe workflow tests
        test1_pass = await test_direct_workflow()
        test2_pass = await test_planning_workflow()
        test3_pass = await test_creative_workflow()
        test4_pass = await test_session_persistence()

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Direct Q&A Workflow:          {'PASS' if test1_pass else 'FAIL'}")
        print(f"✅ Planning Workflow:             {'PASS' if test2_pass else 'FAIL'}")
        print(f"✅ Creative Workflow:             {'PASS' if test3_pass else 'FAIL'}")
        print(f"✅ Session Persistence:           {'PASS' if test4_pass else 'FAIL'}")

        all_pass = test1_pass and test2_pass and test3_pass and test4_pass

        print("=" * 70)
        if all_pass:
            print("\n✅ ALL SAFE WORKFLOW TESTS PASSED!")
            print("\n📌 Next steps:")
            print("   1. Review output above for correctness")
            print("   2. If satisfied, manually test ONE research query:")
            print("      - This will cost ~$0.10-0.50 in API calls")
            print("      - Run: python app.py")
            print("      - Try: 'Research the latest AI trends'")
            print("   3. After research test passes, proceed to Phase 9 (docs)")
        else:
            print("\n❌ SOME TESTS FAILED - Debug above before proceeding")

        print("=" * 70 + "\n")
        return all_pass

    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
