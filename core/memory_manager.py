import os
import time
from datetime import datetime
from modules.vector_store import search_vector_store, add_to_vector_store
import json

SHORT_TERM_MEMORY_PATH = "memory/short_term.json"
SNAPSHOT_DIR = "memory/long_term/snapshots"

class MemoryManager:
    def __init__(self):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(SHORT_TERM_MEMORY_PATH), exist_ok=True)
        self.flush_threshold = 5
        self.last_topic = None
        # Initialize short-term memory file if it doesn't exist
        if not os.path.exists(SHORT_TERM_MEMORY_PATH) or os.path.getsize(SHORT_TERM_MEMORY_PATH) == 0:
            with open(SHORT_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("[MemoryManager] Initialized empty short_term.json")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write("[MemoryManager] Initialized empty short_term.json\n")
        else:
            snapshots = sorted(
                [f for f in os.listdir(SNAPSHOT_DIR) if f.startswith("short_term_snapshot")],
                reverse=True
            )
            if snapshots:
                latest_snapshot = os.path.join(SNAPSHOT_DIR, snapshots[0])
                with open(latest_snapshot, "r", encoding="utf-8") as f:
                    memory = json.load(f)
                with open(SHORT_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
                    json.dump(memory, f, indent=2)
                print(f"[MemoryManager] Loaded from snapshot: {latest_snapshot}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[MemoryManager] Loaded from snapshot: {latest_snapshot}\n")

    def recall(self, query: str = None, topic: str = None) -> str:
        if query:
            return self.search_long_term_memory(query)
        if topic:
            try:
                with open(SHORT_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                    memory = json.load(f)
                relevant = [m for m in memory if m.get("topic") == topic]
                return "\n".join([f"{m['role']}: {m['message']}" for m in relevant])
            except Exception as e:
                print(f"[MemoryManager] Error recalling by topic: {e}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[MemoryManager] Error recalling by topic: {e}\n")
                return ""
        return self.get_short_term_context()

    def get_short_term_context(self, max_messages=5, context_window=None) -> str:
        try:
            with open(SHORT_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                memory = json.loads(content) if content else []
            if context_window:
                recent = [m for m in memory if m.get("topic") == context_window][-max_messages:]
            else:
                recent = memory[-max_messages:]
            context = "\n".join([f"{m['role']}: {m['message']}" for m in recent])
            print(f"[MemoryManager] Retrieved short-term context: {context}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Retrieved short-term context: {context}\n")
            return context
        except Exception as e:
            print(f"[MemoryManager] Error retrieving short-term context: {e}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Error retrieving short-term context: {e}\n")
            return ""

    def search_long_term_memory(self, query: str, top_k=3) -> str:
        try:
            results = search_vector_store(query, top_k=top_k)
            long_term_context = "\n".join([f"- {res['text']}" for res in results])
            print(f"[MemoryManager] Long-term memory search results: {long_term_context}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Long-term memory search results: {long_term_context}\n")
            return long_term_context
        except Exception as e:
            print(f"[MemoryManager] Error searching long-term memory: {e}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Error searching long-term memory: {e}\n")
            return ""

    def append_to_short_term(self, role: str, message: str):
        from core.llm import classify_message
        try:
            if os.path.exists(SHORT_TERM_MEMORY_PATH):
                try:
                    with open(SHORT_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        memory = json.loads(content) if content else []
                except json.JSONDecodeError:
                    print("[MemoryManager] Corrupt short_term.json. Reinitializing.")
                    with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                        log_file.write("[MemoryManager] Corrupt short_term.json. Reinitializing.\n")
                    memory = []
            else:
                memory = []

            classification = classify_message(message)
            self.last_topic = classification["topic"]
            memory.append({"role": role, "message": message, "topic": classification["topic"], "important": classification["important"]})
            print(f"[MemoryManager] Added to short-term memory: {role}: {message} (Topic: {classification['topic']})")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Added to short-term memory: {role}: {message} (Topic: {classification['topic']})\n")

            if len(memory) > self.flush_threshold * 2:
                dropped = memory[:-self.flush_threshold * 2]
                memory = memory[-self.flush_threshold * 2:]

                for msg in dropped:
                    if msg["role"] == "user":
                        add_to_vector_store(msg["message"], classify_message(msg["message"]))

            with open(SHORT_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2)

        except Exception as e:
            print(f"[MemoryManager] Failed to append short-term memory: {e}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Failed to append short-term memory: {e}\n")

    def snapshot_and_clear_short_term(self):
        try:
            if not os.path.exists(SHORT_TERM_MEMORY_PATH):
                return

            with open(SHORT_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                memory = json.loads(content) if content else []

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_path = os.path.join(SNAPSHOT_DIR, f"short_term_snapshot_{timestamp}.json")
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2)

            for msg in memory:
                if msg["role"] == "user":
                    add_to_vector_store(msg["message"], {"source": "short_term", "timestamp": timestamp})

            with open(SHORT_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
            print(f"[MemoryManager] Snapshot saved to {snapshot_path}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Snapshot saved to {snapshot_path}\n")

        except Exception as e:
            print(f"[MemoryManager] Failed to snapshot/clear short-term memory: {e}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MemoryManager] Failed to snapshot/clear short-term memory: {e}\n")