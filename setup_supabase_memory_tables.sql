-- Supabase Memory & Agent Interactions Tables Setup

-- 1. Agent Memories Table (Memory 4 Architecture Core)
CREATE TABLE IF NOT EXISTS public.agent_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_text TEXT NOT NULL,
    summary TEXT,
    entities JSONB DEFAULT '[]'::jsonb,
    topics JSONB DEFAULT '[]'::jsonb,
    importance FLOAT DEFAULT 0.5,
    source TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Agent Interactions Table (Luca AGIBrain Local Chat Sync)
CREATE TABLE IF NOT EXISTS public.agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id TEXT,
    user_msg TEXT,
    ai_reply TEXT,
    model TEXT,
    has_error BOOLEAN DEFAULT FALSE,
    error_msg TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Agent Lessons Table (Luca AGIBrain Self-healing & Reflection Sync)
CREATE TABLE IF NOT EXISTS public.agent_lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
