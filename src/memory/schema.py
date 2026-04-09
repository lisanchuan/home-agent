"""Family Memory Center — SQLite Schema"""

SCHEMA_SQL = """
-- Knowledge nodes table
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('fact', 'preference', 'habit', 'taboo')),
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    value TEXT,
    confidence REAL DEFAULT 0.5,
    visibility TEXT NOT NULL CHECK(visibility IN ('family_shared', 'member_shared', 'member_private')),
    owner_member_id TEXT,
    source TEXT DEFAULT 'learning',
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'pending_confirm', 'deprecated')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_triggered_at TEXT,
    trigger_count INTEGER DEFAULT 0,
    confirmed_at TEXT,
    confirmed_by TEXT
);

-- Knowledge version history
CREATE TABLE IF NOT EXISTS knowledge_history (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT NOT NULL,
    confidence REAL,
    changed_at TEXT NOT NULL,
    change_reason TEXT,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge_nodes(id)
);

-- Family members table
CREATE TABLE IF NOT EXISTS members (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    role TEXT DEFAULT 'member' CHECK(role IN ('head', 'member', 'child')),
    is_minor INTEGER DEFAULT 0,
    disclosure_level TEXT DEFAULT 'normal',
    allow_agent_proxy INTEGER DEFAULT 1,
    allow_spouse_view INTEGER DEFAULT 1,
    proxy_level TEXT DEFAULT 'none',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Access logs
CREATE TABLE IF NOT EXISTS access_logs (
    id TEXT PRIMARY KEY,
    requester_id TEXT NOT NULL,
    requester_type TEXT NOT NULL,
    action TEXT NOT NULL,
    knowledge_id TEXT,
    result TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Pending confirmations queue
CREATE TABLE IF NOT EXISTS pending_confirmations (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT,
    knowledge_type TEXT NOT NULL,
    knowledge_content TEXT NOT NULL,
    suggested_value TEXT,
    trigger_context TEXT,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

-- Decay records
CREATE TABLE IF NOT EXISTS decay_records (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    old_confidence REAL NOT NULL,
    new_confidence REAL NOT NULL,
    decay_reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge_nodes(id)
);

-- Deleted knowledge (soft delete)
CREATE TABLE IF NOT EXISTS deleted_knowledge (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    content TEXT NOT NULL,
    deleted_at TEXT NOT NULL,
    delete_reason TEXT
);

-- Search text column for fast LIKE searches
-- Note: Column may already exist, so this is a no-op if present
-- Run separately: ALTER TABLE knowledge_nodes ADD COLUMN search_text TEXT;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_nodes(type);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_nodes(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_visibility ON knowledge_nodes(visibility);
CREATE INDEX IF NOT EXISTS idx_knowledge_owner ON knowledge_nodes(owner_member_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_nodes(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_confidence ON knowledge_nodes(confidence);
CREATE INDEX IF NOT EXISTS idx_access_logs_requester ON access_logs(requester_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_pending_expires ON pending_confirmations(expires_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_search ON knowledge_nodes(search_text);
"""

MEMBER_DEFAULT = {
    "father": {
        "id": "member_father",
        "name": "爸爸",
        "relationship": "父亲",
        "role": "head",
        "is_minor": False,
        "disclosure_level": "normal",
        "allow_agent_proxy": True,
        "allow_spouse_view": True,
        "proxy_level": "none"
    },
    "mother": {
        "id": "member_mother",
        "name": "妈妈",
        "relationship": "母亲",
        "role": "head",
        "is_minor": False,
        "disclosure_level": "normal",
        "allow_agent_proxy": True,
        "allow_spouse_view": True,
        "proxy_level": "none"
    }
}
