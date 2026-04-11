#!/usr/bin/env python3
"""Family Memory Center — CLI Tool"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.memory import MemoryCenter, init_db
from src.rag.query import RAGQueryEngine


def cmd_init(args):
    """Initialize database"""
    init_db()
    mc = MemoryCenter()
    mc.initialize()
    print("✓ Database initialized")


def cmd_add(args):
    """Add knowledge"""
    mc = MemoryCenter(requester_id=args.agent)
    kid = mc.add_knowledge(
        content=args.content,
        knowledge_type=args.type,
        category=args.category,
        visibility=args.visibility,
        owner_member_id=args.owner,
        confidence=args.confidence
    )
    print(f"✓ Knowledge added: {kid}")


def cmd_search(args):
    """Search knowledge using RAG"""
    engine = RAGQueryEngine(requester_id=args.agent)
    result = engine.ask(args.query)
    print(result)


def cmd_list(args):
    """List knowledge"""
    mc = MemoryCenter(requester_id=args.agent)
    results = mc.query(
        visibility=args.visibility,
        owner_member_id=args.owner,
        knowledge_type=args.type,
        limit=args.limit
    )
    print(f"Found {len(results)} items:")
    for r in results:
        print(f"  [{r['id']}] {r['content']}")
        print(f"    type={r['type']}, visibility={r['visibility']}")


def cmd_members(args):
    """List members"""
    mc = MemoryCenter()
    members = mc.get_members()
    print(f"Found {len(members)} members:")
    for m in members:
        print(f"  [{m['id']}] {m['name']} ({m['relationship']}) - {m['role']}")


def cmd_export(args):
    """Export data"""
    mc = MemoryCenter()
    data = mc.export()
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Family Memory Center CLI")
    subparsers = parser.add_subparsers()
    
    p = subparsers.add_parser("init", help="Initialize database")
    p.set_defaults(cmd=cmd_init)
    
    p = subparsers.add_parser("add", help="Add knowledge")
    p.add_argument("--content", "-c", required=True, help="Knowledge content")
    p.add_argument("--type", "-t", required=True, choices=["fact", "preference", "habit", "taboo"])
    p.add_argument("--category", "-C", required=True, help="Category")
    p.add_argument("--visibility", "-v", required=True,
                    choices=["family_shared", "member_shared", "member_private"])
    p.add_argument("--owner", "-o", help="Owner member ID")
    p.add_argument("--confidence", default=0.5, type=float)
    p.add_argument("--agent", default="cli")
    p.set_defaults(cmd=cmd_add)
    
    p = subparsers.add_parser("search", help="Search knowledge (RAG)")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--agent", "-a", default="cli")
    p.set_defaults(cmd=cmd_search)
    
    p = subparsers.add_parser("list", help="List knowledge")
    p.add_argument("--visibility", "-v")
    p.add_argument("--owner", "-o")
    p.add_argument("--type", "-t")
    p.add_argument("--limit", "-l", type=int, default=100)
    p.add_argument("--agent", "-a", default="cli")
    p.set_defaults(cmd=cmd_list)
    
    p = subparsers.add_parser("members", help="List members")
    p.set_defaults(cmd=cmd_members)
    
    p = subparsers.add_parser("export", help="Export data")
    p.set_defaults(cmd=cmd_export)
    
    args = parser.parse_args()
    
    if hasattr(args, "cmd"):
        args.cmd(args)
    else:
        parser.print_help()
