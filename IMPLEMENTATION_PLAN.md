# Digital Alchemy - Complete Implementation Plan

## Vision Recap

**Goal**: Create a secure "Digital Clone" that learns *how* you think, communicate, and present yourself across all digital platforms - without exposing raw data to the external agent (Ares).

**Key Principles**:
1. **Entity-Centric**: Everything revolves around understanding WHO you interact with and HOW
2. **Behavioral, Not Content**: Extract patterns of communication, not just topics
3. **Incremental Learning**: Every new data point or confirmation triggers re-evaluation
4. **Human-in-the-Loop**: Critical entity links require user confirmation
5. **Secure Distillation**: Ares receives patterns/archetypes, never raw data

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              JARVIS (Local)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Ingestors  │───▶│   Entity     │───▶│  Inference   │                   │
│  │              │    │   Resolver   │    │   Engine     │                   │
│  │ - Instagram  │    │              │    │              │                   │
│  │ - Facebook   │    │ - Extract    │    │ - Behavioral │                   │
│  │ - iMessage   │    │ - Match      │    │ - Relational │                   │
│  │ - Email      │    │ - Confirm    │    │ - Temporal   │                   │
│  │ - Safari     │    │ - Merge      │    │ - Cross-src  │                   │
│  │ - X/Twitter  │    │              │    │              │                   │
│  │ - ChatGPT    │    └──────┬───────┘    └──────┬───────┘                   │
│  │ - Notes      │           │                   │                           │
│  │ - Contacts   │           ▼                   ▼                           │
│  │ - PDF/Upload │    ┌──────────────────────────────────┐                   │
│  └──────────────┘    │         Knowledge Graph          │                   │
│                      │                                  │                   │
│                      │  Entities ←→ Relationships ←→    │                   │
│                      │  Inferences ←→ Behaviors         │                   │
│                      └──────────────┬───────────────────┘                   │
│                                     │                                       │
│                                     ▼                                       │
│                      ┌──────────────────────────────────┐                   │
│                      │       Triage Interface           │                   │
│                      │                                  │                   │
│                      │  - Entity Confirmation           │                   │
│                      │  - Inference Approval            │                   │
│                      │  - Relationship Validation       │                   │
│                      └──────────────┬───────────────────┘                   │
│                                     │                                       │
│                                     ▼                                       │
│                      ┌──────────────────────────────────┐                   │
│                      │    Digital Spirit Exporter       │──────────────────▶│
│                      │                                  │                   │
│                      │  Behavioral Patterns Only        │     To Ares       │
│                      │  No Raw Data                     │                   │
│                      └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Entity Resolution System (CRITICAL)

This is the foundation. Without proper entity resolution, cross-source inference is impossible.

### 1.1 Entity Data Model

```python
# app/models.py - New models to add

class Entity(BaseModel):
    """A resolved person/organization/concept across all sources"""
    id: str                          # Canonical ID (UUID)
    type: str                        # person, organization, place, concept
    canonical_name: str              # "Logan Ruddick"
    aliases: List[str]               # ["Logan", "looganoo", "LR"]
    source_identifiers: Dict[str, str]  # {"instagram": "@looganoo", "imessage": "+1234567890"}
    attributes: Dict[str, Any]       # {"business": "Fraternitees", "relationship": "friend"}
    first_seen: datetime
    sources: List[str]               # ["instagram", "imessage", "facebook"]
    confidence: float                # How confident we are this is one entity
    confirmed_by_user: bool          # User has explicitly confirmed this entity

class EntityMention(BaseModel):
    """A single mention of an entity in raw data"""
    id: str
    raw_data_id: str                 # Link to RawDataItem
    entity_id: Optional[str]         # Link to resolved Entity (None if unresolved)
    mention_text: str                # "Logan", "@looganoo", etc.
    context: str                     # Surrounding text for disambiguation
    source: str                      # "instagram", "imessage", etc.
    timestamp: Optional[datetime]
    confidence: float                # Confidence this mention = entity_id

class EntityCandidate(BaseModel):
    """Proposed entity merge for user confirmation"""
    id: str
    entity_a_id: str
    entity_b_id: str
    confidence: float
    evidence: List[str]              # Why we think they're the same
    status: str                      # "pending", "confirmed", "rejected"
```

### 1.2 Entity Extraction Pipeline

Each ingestor must extract entity mentions during ingestion:

```python
# app/ingestors/base.py - Enhanced interface

class BaseIngestor(ABC):
    @abstractmethod
    def ingest(self) -> List[RawDataItem]:
        """Ingest raw data from source"""
        pass

    @abstractmethod
    def extract_entities(self, raw_item: RawDataItem) -> List[EntityMention]:
        """Extract entity mentions from a raw data item"""
        pass

    @abstractmethod
    def get_source_identifier(self, mention: EntityMention) -> Optional[str]:
        """Get platform-specific identifier (e.g., @username, phone number)"""
        pass
```

### 1.3 Entity Resolution Algorithm

```python
# app/entities/resolver.py - Full implementation

class EntityResolver:
    def __init__(self, embedding_engine, db):
        self.embedding_engine = embedding_engine  # For semantic similarity
        self.db = db                               # Persistence layer
        self.threshold = 0.75                      # Match confidence threshold

    def resolve_mention(self, mention: EntityMention) -> Tuple[Optional[Entity], float]:
        """
        Resolve a mention to an existing entity or create candidate for new one.

        Resolution priority:
        1. Exact source identifier match (same phone number, same @username)
        2. High-confidence name + context match
        3. Network proximity (entities that share connections)
        4. Create new entity if no match
        """

        # Step 1: Check exact identifier match
        if mention.source_identifier:
            entity = self.db.find_entity_by_identifier(mention.source, mention.source_identifier)
            if entity:
                return entity, 1.0

        # Step 2: Find candidates by name similarity
        candidates = self.find_candidates(mention)

        # Step 3: Score candidates
        scored = [(c, self.score_match(mention, c)) for c in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        if scored and scored[0][1] >= self.threshold:
            return scored[0]

        # Step 4: Check if we should propose a merge
        if scored and scored[0][1] >= 0.5:
            self.propose_merge(mention, scored[0][0], scored[0][1])

        return None, 0.0

    def score_match(self, mention: EntityMention, entity: Entity) -> float:
        """Score how likely a mention refers to an entity"""
        score = 0.0

        # Name similarity (embedding-based)
        name_sim = self.embedding_engine.similarity(mention.mention_text, entity.canonical_name)
        score += name_sim * 0.3

        # Alias match
        for alias in entity.aliases:
            if mention.mention_text.lower() == alias.lower():
                score += 0.4
                break

        # Context similarity
        context_sim = self.embedding_engine.similarity(mention.context, entity.get_context())
        score += context_sim * 0.2

        # Network proximity (shared connections)
        network_score = self.calculate_network_proximity(mention, entity)
        score += network_score * 0.1

        return min(score, 1.0)

    def propose_merge(self, mention: EntityMention, entity: Entity, confidence: float):
        """Create a merge candidate for user confirmation"""
        # This creates the "Is Logan Ruddick the same as @looganoo?" prompt
        candidate = EntityCandidate(
            id=str(uuid4()),
            entity_a_id=mention.entity_id or self.create_temp_entity(mention).id,
            entity_b_id=entity.id,
            confidence=confidence,
            evidence=self.gather_evidence(mention, entity),
            status="pending"
        )
        self.db.save_candidate(candidate)

    def confirm_merge(self, candidate_id: str):
        """User confirmed the merge - trigger re-inference"""
        candidate = self.db.get_candidate(candidate_id)

        # Merge entities
        merged = self.merge_entities(candidate.entity_a_id, candidate.entity_b_id)

        # CRITICAL: Trigger re-inference for all affected data
        self.trigger_reinference(merged)

    def trigger_reinference(self, entity: Entity):
        """Mark all inferences involving this entity as needing re-evaluation"""
        affected_inferences = self.db.get_inferences_by_entity(entity.id)
        for inf in affected_inferences:
            inf.status = "needs_reeval"
            self.db.save_inference(inf)

        # Also mark inferences for related entities
        related = self.db.get_related_entities(entity.id)
        for rel in related:
            related_inferences = self.db.get_inferences_by_entity(rel.id)
            for inf in related_inferences:
                if inf.status == "approved":
                    inf.status = "needs_reeval"
                    self.db.save_inference(inf)
```

### 1.4 User Confirmation UI

Add to the triage interface:

```javascript
// Entity confirmation card
{
  type: "entity_confirmation",
  question: "Is Logan Ruddick (iMessage) the same as @looganoo (Instagram)?",
  entity_a: {
    name: "Logan Ruddick",
    source: "iMessage",
    context: "Texts about Notion AI, AI tools",
    sample_messages: ["Hey did you try Notion AI?", "..."]
  },
  entity_b: {
    name: "@looganoo",
    source: "Instagram",
    bio: "@fraternitees",
    context: "DMs about ChatGPT",
    sample_messages: ["ChatGPT is insane", "..."]
  },
  evidence: [
    "Both discuss AI tools",
    "Name similarity: Logan",
    "Both connected to you since ~2018"
  ],
  confidence: 0.72
}
```

---

## Phase 2: Incremental Re-Inference System

### 2.1 Inference Dependency Tracking

```python
# app/models.py - Enhanced Inference model

class Inference(BaseModel):
    id: str
    type: str                        # behavioral, relational, temporal, etc.
    statement: str
    confidence: float

    # Provenance tracking
    source_ids: List[str]            # Raw data that contributed
    entity_ids: List[str]            # Entities involved
    parent_inference_ids: List[str]  # Inferences this builds upon

    # Versioning
    version: int                     # Increments on re-inference
    previous_version_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Status
    status: str                      # pending, approved, rejected, needs_reeval, superseded

    # Re-inference tracking
    last_evaluated: datetime
    trigger_sources: List[str]       # What triggered last re-evaluation
```

### 2.2 Re-Inference Engine

```python
# app/inference_engine/reinference.py

class ReinferenceEngine:
    def __init__(self, db, llm, entity_resolver):
        self.db = db
        self.llm = llm
        self.entity_resolver = entity_resolver

    def on_new_data(self, raw_items: List[RawDataItem]):
        """Called when new data is ingested"""

        # 1. Extract and resolve entities
        for item in raw_items:
            mentions = self.extract_entities(item)
            for mention in mentions:
                entity, confidence = self.entity_resolver.resolve_mention(mention)
                if entity:
                    self.link_data_to_entity(item, entity)

        # 2. Find affected entities
        affected_entities = self.get_affected_entities(raw_items)

        # 3. Mark related inferences for re-evaluation
        for entity in affected_entities:
            self.mark_for_reeval(entity)

        # 4. Generate new inferences from new data
        self.generate_inferences(raw_items)

    def on_entity_merge(self, merged_entity: Entity):
        """Called when user confirms entity merge"""

        # 1. Get all data points for merged entity
        all_data = self.db.get_data_for_entity(merged_entity.id)

        # 2. Get all existing inferences
        existing = self.db.get_inferences_by_entity(merged_entity.id)

        # 3. Generate new cross-source inferences
        new_inferences = self.generate_cross_source_inferences(merged_entity, all_data)

        # 4. Check for inference upgrades
        for new_inf in new_inferences:
            existing_similar = self.find_similar_inference(new_inf, existing)
            if existing_similar:
                # Upgrade existing inference
                self.upgrade_inference(existing_similar, new_inf)
            else:
                # Create new inference
                self.db.save_inference(new_inf)

    def generate_cross_source_inferences(self, entity: Entity, data: List[RawDataItem]) -> List[Inference]:
        """Generate inferences that span multiple data sources"""

        # Group by source
        by_source = defaultdict(list)
        for item in data:
            by_source[item.source].append(item)

        # Only generate cross-source if we have 2+ sources
        if len(by_source) < 2:
            return []

        # Build context for LLM
        context = self.build_cross_source_context(entity, by_source)

        # Generate inferences via LLM
        prompt = f"""
        Analyze the following data about {entity.canonical_name} from multiple sources.
        Focus on BEHAVIORAL PATTERNS - how does the user communicate with this person?

        {context}

        Generate inferences about:
        1. Relationship type and strength
        2. Communication style patterns
        3. Topics and interests they share
        4. Temporal patterns (when they communicate)
        5. How the user presents themselves to this person

        Format as JSON array of inferences.
        """

        return self.llm.generate_inferences(prompt)
```

### 2.3 Inference Evolution Tracking

```python
# Track how inferences evolve over time

class InferenceHistory:
    """
    Example evolution:

    v1: "Logan is someone Bryce texts about AI"
        (source: iMessage only)

    v2: "Logan Ruddick (@looganoo) is a close friend who shares AI interests"
        (source: iMessage + Instagram merged)

    v3: "Logan Ruddick, owner of Fraternitees, is one of Bryce's best friends
         since high school. They frequently discuss AI, ChatGPT, Notion, and
         entrepreneurship. Communication style: casual, frequent, idea-sharing."
        (source: iMessage + Instagram + Facebook merged, confirmed by user)
    """

    def upgrade_inference(self, old: Inference, new_data: List[RawDataItem]) -> Inference:
        """Create upgraded version of inference with new data"""

        upgraded = Inference(
            id=str(uuid4()),
            type=old.type,
            statement=None,  # Will be generated
            confidence=old.confidence,  # May increase
            source_ids=old.source_ids + [d.id for d in new_data],
            entity_ids=old.entity_ids,
            parent_inference_ids=[old.id],
            version=old.version + 1,
            previous_version_id=old.id,
            status="pending",
            trigger_sources=[d.source for d in new_data]
        )

        # Mark old as superseded
        old.status = "superseded"

        return upgraded
```

---

## Phase 3: Data Source Ingestors

### 3.1 Priority Order

| Priority | Source | Complexity | Value |
|----------|--------|------------|-------|
| 1 | iMessage | Medium | Very High |
| 2 | Instagram (Personal) | Low | High |
| 3 | Instagram (Business) | Low | High |
| 4 | Contacts | Low | Critical |
| 5 | Facebook | Low | High |
| 6 | ChatGPT | Done | High |
| 7 | Safari | Done | Medium |
| 8 | X/Twitter | Low | Medium |
| 9 | Email (Gmail) | Medium | High |
| 10 | Notes | Medium | Medium |
| 11 | Google Drive | High | Medium |
| 12 | PDF Upload | Low | Variable |

### 3.2 Ingestor Implementations

#### iMessage Ingestor (macOS)

```python
# app/ingestors/imessage.py

class IMessageIngestor(BaseIngestor):
    """
    Reads from ~/Library/Messages/chat.db
    Requires Full Disk Access permission on macOS
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.expanduser("~/Library/Messages/chat.db")

    def ingest(self) -> List[RawDataItem]:
        items = []

        # Connect read-only
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)

        query = """
        SELECT
            m.rowid,
            m.text,
            m.date,
            m.is_from_me,
            h.id as handle_id,
            c.display_name as chat_name
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.rowid
        LEFT JOIN chat_message_join cmj ON m.rowid = cmj.message_id
        LEFT JOIN chat c ON cmj.chat_id = c.rowid
        WHERE m.text IS NOT NULL
        ORDER BY m.date DESC
        """

        for row in conn.execute(query):
            items.append(RawDataItem(
                id=f"imessage_{row[0]}",
                source="imessage",
                content=row[1],
                timestamp=self.convert_apple_timestamp(row[2]),
                metadata={
                    "is_from_me": bool(row[3]),
                    "handle_id": row[4],  # Phone number or email
                    "chat_name": row[5],
                    "direction": "outgoing" if row[3] else "incoming"
                }
            ))

        return items

    def extract_entities(self, item: RawDataItem) -> List[EntityMention]:
        """Extract the person being messaged"""
        return [EntityMention(
            id=str(uuid4()),
            raw_data_id=item.id,
            mention_text=item.metadata.get("handle_id", "Unknown"),
            context=item.content[:200],
            source="imessage",
            timestamp=item.timestamp,
            source_identifier=item.metadata.get("handle_id")
        )]
```

#### Instagram Ingestor

```python
# app/ingestors/instagram.py

class InstagramIngestor(BaseIngestor):
    """
    Parses Instagram data export (JSON format)
    Handles: DMs, posts, comments, following, followers
    """

    def __init__(self, export_path: str, account_type: str = "personal"):
        self.export_path = export_path
        self.account_type = account_type  # "personal" or "business"

    def ingest(self) -> List[RawDataItem]:
        items = []

        # Parse DMs
        dm_path = os.path.join(self.export_path, "messages", "inbox")
        if os.path.exists(dm_path):
            items.extend(self.parse_dms(dm_path))

        # Parse posts
        posts_path = os.path.join(self.export_path, "content", "posts_1.json")
        if os.path.exists(posts_path):
            items.extend(self.parse_posts(posts_path))

        # Parse profile info for entity extraction
        profile_path = os.path.join(self.export_path, "personal_information")
        if os.path.exists(profile_path):
            items.extend(self.parse_profile(profile_path))

        return items

    def parse_dms(self, dm_path: str) -> List[RawDataItem]:
        items = []
        for convo_dir in os.listdir(dm_path):
            convo_path = os.path.join(dm_path, convo_dir, "message_1.json")
            if os.path.exists(convo_path):
                with open(convo_path) as f:
                    data = json.load(f)

                participants = [p["name"] for p in data.get("participants", [])]

                for msg in data.get("messages", []):
                    items.append(RawDataItem(
                        id=f"instagram_dm_{hash(msg.get('timestamp_ms', ''))}",
                        source=f"instagram_{self.account_type}",
                        content=msg.get("content", ""),
                        timestamp=datetime.fromtimestamp(msg["timestamp_ms"] / 1000),
                        metadata={
                            "sender": msg.get("sender_name"),
                            "participants": participants,
                            "conversation_id": convo_dir,
                            "type": "dm",
                            "is_from_me": msg.get("sender_name") == "Your Name"  # Replace with actual
                        }
                    ))
        return items

    def extract_entities(self, item: RawDataItem) -> List[EntityMention]:
        entities = []

        # Extract from participants
        for participant in item.metadata.get("participants", []):
            entities.append(EntityMention(
                id=str(uuid4()),
                raw_data_id=item.id,
                mention_text=participant,
                context=item.content[:200],
                source=f"instagram_{self.account_type}",
                timestamp=item.timestamp,
                source_identifier=f"@{participant.lower().replace(' ', '')}"  # Approximate
            ))

        return entities
```

#### Facebook Ingestor

```python
# app/ingestors/facebook.py

class FacebookIngestor(BaseIngestor):
    """
    Parses Facebook data export
    Handles: Messages, posts, friends list, tagged photos
    """

    def ingest(self) -> List[RawDataItem]:
        items = []

        # Messages
        messages_path = os.path.join(self.export_path, "messages", "inbox")
        items.extend(self.parse_messages(messages_path))

        # Friends list (for entity resolution)
        friends_path = os.path.join(self.export_path, "friends_and_followers", "friends.json")
        items.extend(self.parse_friends(friends_path))

        # Tagged photos (relationship evidence)
        photos_path = os.path.join(self.export_path, "posts", "your_photos.json")
        items.extend(self.parse_tagged_photos(photos_path))

        return items

    def parse_friends(self, path: str) -> List[RawDataItem]:
        """Parse friends list - critical for entity resolution"""
        items = []
        with open(path) as f:
            data = json.load(f)

        for friend in data.get("friends_v2", []):
            items.append(RawDataItem(
                id=f"facebook_friend_{friend['name']}",
                source="facebook",
                content=f"Facebook friend: {friend['name']}",
                timestamp=datetime.fromtimestamp(friend.get("timestamp", 0)),
                metadata={
                    "type": "friend",
                    "name": friend["name"],
                    "friend_since": datetime.fromtimestamp(friend.get("timestamp", 0))
                }
            ))

        return items
```

#### Contacts Ingestor (Critical for Entity Resolution)

```python
# app/ingestors/contacts.py

class ContactsIngestor(BaseIngestor):
    """
    Reads Apple Contacts or vCard export
    CRITICAL: This provides the canonical names and identifiers for entity resolution
    """

    def ingest(self) -> List[RawDataItem]:
        items = []

        # Parse vCard file
        with open(self.source_path) as f:
            vcards = self.parse_vcards(f.read())

        for vcard in vcards:
            items.append(RawDataItem(
                id=f"contact_{vcard['uid']}",
                source="contacts",
                content=f"Contact: {vcard['full_name']}",
                timestamp=datetime.now(),
                metadata={
                    "type": "contact",
                    "full_name": vcard["full_name"],
                    "first_name": vcard.get("first_name"),
                    "last_name": vcard.get("last_name"),
                    "nickname": vcard.get("nickname"),
                    "phones": vcard.get("phones", []),
                    "emails": vcard.get("emails", []),
                    "organization": vcard.get("organization"),
                    "social_profiles": vcard.get("social_profiles", {}),
                    "notes": vcard.get("notes")
                }
            ))

        return items

    def create_entity_from_contact(self, item: RawDataItem) -> Entity:
        """Contacts create canonical entities that other sources link to"""
        meta = item.metadata

        # Build source identifiers from contact info
        identifiers = {}
        for phone in meta.get("phones", []):
            identifiers["phone"] = phone
        for email in meta.get("emails", []):
            identifiers["email"] = email
        for platform, handle in meta.get("social_profiles", {}).items():
            identifiers[platform] = handle

        return Entity(
            id=str(uuid4()),
            type="person",
            canonical_name=meta["full_name"],
            aliases=[meta.get("nickname"), meta.get("first_name")],
            source_identifiers=identifiers,
            attributes={"organization": meta.get("organization")},
            first_seen=item.timestamp,
            sources=["contacts"],
            confidence=1.0,  # Contacts are ground truth
            confirmed_by_user=True  # User added this contact
        )
```

#### Generic Upload/PDF Ingestor

```python
# app/ingestors/upload.py

class GenericUploadIngestor(BaseIngestor):
    """
    Handles arbitrary file uploads: PDF, TXT, JSON, etc.
    User can specify what type of data this is.
    """

    def __init__(self, file_path: str, data_type: str, metadata: Dict = None):
        self.file_path = file_path
        self.data_type = data_type  # "journal", "notes", "export", etc.
        self.user_metadata = metadata or {}

    def ingest(self) -> List[RawDataItem]:
        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == ".pdf":
            return self.parse_pdf()
        elif ext == ".json":
            return self.parse_json()
        elif ext in [".txt", ".md"]:
            return self.parse_text()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def parse_pdf(self) -> List[RawDataItem]:
        """Extract text from PDF, chunk into items"""
        import PyPDF2  # Add to requirements

        items = []
        with open(self.file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    items.append(RawDataItem(
                        id=f"upload_{hash(self.file_path)}_{i}",
                        source="upload",
                        content=text,
                        timestamp=datetime.now(),
                        metadata={
                            "type": self.data_type,
                            "file": os.path.basename(self.file_path),
                            "page": i + 1,
                            **self.user_metadata
                        }
                    ))

        return items
```

---

## Phase 4: Behavioral Pattern Extraction

### 4.1 Focus on HOW, Not WHAT

The key insight: Ares doesn't need to know "Bryce texted Logan about Notion AI". Ares needs to know:

- **How** Bryce communicates with close friends (casual, frequent, idea-sharing)
- **When** Bryce is most engaged in conversations (evenings, weekends)
- **What triggers** Bryce to reach out (excitement about new tools, wanting feedback)
- **How** Bryce presents himself differently across platforms

### 4.2 Behavioral Inference Types

```python
# app/inference_engine/behavioral.py

class BehavioralInferenceEngine:
    """Extract behavioral patterns, not content summaries"""

    BEHAVIORAL_DIMENSIONS = {
        "communication_style": {
            "formality_spectrum": "casual <-> formal",
            "message_length": "terse <-> verbose",
            "emoji_usage": "none <-> heavy",
            "response_speed": "immediate <-> delayed",
            "initiation_ratio": "initiator <-> responder"
        },
        "relationship_dynamics": {
            "emotional_availability": "guarded <-> open",
            "support_style": "advice-giving <-> listening",
            "conflict_approach": "avoidant <-> direct",
            "vulnerability_level": "surface <-> deep"
        },
        "intellectual_patterns": {
            "learning_style": "structured <-> exploratory",
            "information_sharing": "hoarder <-> sharer",
            "debate_style": "agreeable <-> contrarian",
            "depth_preference": "breadth <-> depth"
        },
        "temporal_patterns": {
            "peak_energy_times": "morning <-> evening",
            "response_urgency": "async <-> realtime",
            "planning_horizon": "spontaneous <-> planner"
        }
    }

    def analyze_communication_patterns(self, entity: Entity, messages: List[RawDataItem]) -> Dict:
        """Analyze how user communicates with a specific person"""

        outgoing = [m for m in messages if m.metadata.get("is_from_me")]
        incoming = [m for m in messages if not m.metadata.get("is_from_me")]

        return {
            "relationship_with": entity.canonical_name,
            "patterns": {
                "initiation_ratio": len([m for m in outgoing if self.is_conversation_starter(m)]) / max(len(outgoing), 1),
                "avg_response_time": self.calculate_avg_response_time(messages),
                "message_length_ratio": self.avg_length(outgoing) / max(self.avg_length(incoming), 1),
                "emoji_frequency": self.count_emojis(outgoing) / max(len(outgoing), 1),
                "question_ratio": self.count_questions(outgoing) / max(len(outgoing), 1),
                "topics_initiated": self.extract_initiated_topics(outgoing),
                "communication_hours": self.extract_active_hours(outgoing),
                "platform_preference": self.get_platform_breakdown(messages)
            }
        }

    def generate_behavioral_inference(self, patterns: Dict) -> Inference:
        """Convert patterns into natural language behavioral inference"""

        prompt = f"""
        Based on these communication patterns with {patterns['relationship_with']}:
        {json.dumps(patterns['patterns'], indent=2)}

        Generate a behavioral inference about HOW the user communicates with this person.
        Focus on:
        - Communication style (not topics)
        - Relationship dynamic
        - The user's role in the relationship

        Do NOT mention specific topics or content.

        Format: A single sentence describing the behavioral pattern.
        """

        statement = self.llm.generate(prompt)

        return Inference(
            type="behavioral",
            statement=statement,
            confidence=0.8,
            entity_ids=[patterns["relationship_with"]]
        )
```

### 4.3 Cross-Platform Self-Presentation Analysis

```python
class SelfPresentationAnalyzer:
    """How does user present themselves differently across platforms?"""

    def analyze_platform_personas(self, entity_data: Dict[str, List[RawDataItem]]) -> Dict:
        """
        Compare user's communication style across platforms

        Example output:
        {
            "instagram_personal": {
                "tone": "casual, playful",
                "topics": "lifestyle, friends, humor",
                "formality": 0.2
            },
            "instagram_business": {
                "tone": "professional, enthusiastic",
                "topics": "products, customer engagement",
                "formality": 0.6
            },
            "imessage": {
                "tone": "direct, informal",
                "topics": "logistics, deep conversations",
                "formality": 0.3
            }
        }
        """

        personas = {}
        for platform, data in entity_data.items():
            outgoing = [d for d in data if d.metadata.get("is_from_me")]

            personas[platform] = {
                "avg_message_length": self.avg_length(outgoing),
                "vocabulary_complexity": self.analyze_vocabulary(outgoing),
                "emoji_usage": self.emoji_frequency(outgoing),
                "formality_score": self.calculate_formality(outgoing),
                "sentiment_distribution": self.analyze_sentiment(outgoing),
                "response_patterns": self.analyze_responses(data)
            }

        return personas

    def generate_persona_inference(self, personas: Dict) -> Inference:
        """Generate inference about multi-platform self-presentation"""

        return Inference(
            type="self_presentation",
            statement=f"User presents more formally on business platforms (formality: {personas.get('instagram_business', {}).get('formality', 'N/A')}) compared to personal communication (formality: {personas.get('imessage', {}).get('formality', 'N/A')})",
            confidence=0.75
        )
```

---

## Phase 5: Digital Spirit Export Format

### 5.1 What Ares Receives (NO Raw Data)

```python
# app/export/digital_spirit.py

class DigitalSpiritExporter:
    """Export validated knowledge for Ares - behavioral patterns only"""

    def export(self) -> Dict:
        return {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "owner": {
                "behavioral_profile": self.export_behavioral_profile(),
                "communication_styles": self.export_communication_styles(),
                "temporal_patterns": self.export_temporal_patterns(),
                "platform_personas": self.export_platform_personas()
            },
            "relationships": self.export_relationships(),
            "interests_and_values": self.export_interests(),
            "interaction_guidelines": self.export_guidelines()
        }

    def export_behavioral_profile(self) -> Dict:
        """Core behavioral traits - HOW the person operates"""
        return {
            "communication": {
                "default_tone": "casual but thoughtful",
                "formality_triggers": ["professional context", "new acquaintances"],
                "humor_style": "dry, reference-based",
                "conflict_approach": "direct but diplomatic"
            },
            "thinking_style": {
                "learning_preference": "hands-on exploration",
                "decision_making": "research-then-intuition",
                "information_processing": "visual and systematic"
            },
            "social_patterns": {
                "energy_source": "small groups over large",
                "relationship_investment": "deep over wide",
                "support_style": "problem-solving oriented"
            }
        }

    def export_relationships(self) -> List[Dict]:
        """Relationship summaries - NO message content"""
        return [
            {
                "entity": "Logan Ruddick",
                "relationship_type": "close_friend",
                "relationship_strength": 0.9,
                "since": "high school",
                "interaction_style": {
                    "tone": "casual, idea-sharing",
                    "topics_category": ["technology", "entrepreneurship"],  # Categories, not specifics
                    "communication_frequency": "high",
                    "preferred_platforms": ["imessage", "instagram"]
                },
                "notable_patterns": [
                    "Often shares new tool discoveries",
                    "Collaborative brainstorming relationship",
                    "Business owner - Fraternitees"
                ]
            }
        ]

    def export_guidelines(self) -> Dict:
        """How Ares should behave based on learned patterns"""
        return {
            "voice_guidelines": {
                "do": [
                    "Be direct and concise",
                    "Use casual language with close contacts",
                    "Ask clarifying questions before assuming"
                ],
                "avoid": [
                    "Excessive formality with friends",
                    "Long-winded explanations",
                    "Unsolicited advice"
                ]
            },
            "response_patterns": {
                "to_close_friends": "casual, quick, emoji-light",
                "to_professional_contacts": "friendly but structured",
                "to_new_people": "warm but measured"
            }
        }
```

---

## Phase 6: Implementation Roadmap

### Sprint 1: Foundation (1-2 weeks)
- [ ] Enhanced data models (Entity, EntityMention, EntityCandidate)
- [ ] SQLite persistence layer (replace JSON files)
- [ ] Contacts ingestor (canonical entity source)
- [ ] Basic entity extraction interface

### Sprint 2: Entity Resolution (2-3 weeks)
- [ ] Entity resolver with similarity scoring
- [ ] Embedding integration (local sentence-transformers)
- [ ] Entity merge candidate generation
- [ ] Entity confirmation UI
- [ ] Merge confirmation → re-inference trigger

### Sprint 3: Core Ingestors (2 weeks)
- [ ] iMessage ingestor
- [ ] Instagram ingestor (personal + business)
- [ ] Facebook ingestor
- [ ] X/Twitter ingestor

### Sprint 4: Behavioral Analysis (2 weeks)
- [ ] Communication pattern extraction
- [ ] Self-presentation analyzer
- [ ] Cross-platform behavioral comparison
- [ ] Behavioral inference generation

### Sprint 5: Re-Inference System (2 weeks)
- [ ] Inference dependency tracking
- [ ] Incremental re-inference engine
- [ ] Inference versioning and history
- [ ] Inference upgrade pipeline

### Sprint 6: Advanced Features (2 weeks)
- [ ] Email ingestor (Gmail export)
- [ ] Google Drive ingestor
- [ ] PDF/generic upload handler
- [ ] Notes ingestor

### Sprint 7: Export & Polish (1 week)
- [ ] Digital Spirit export format
- [ ] Relationship graph visualization
- [ ] Inference chain visualization
- [ ] Export validation

---

## Technical Recommendations

### Local LLM
- **For M2 MacBook**: Use Ollama with `llama3:8b` or `mistral:7b`
- **For entity extraction**: Consider smaller model like `phi3:mini` for speed
- **For embeddings**: `nomic-embed-text` via Ollama or `sentence-transformers` locally

### Database
- **SQLite** for simplicity and portability (current approach is fine)
- **Consider**: Adding a vector store (ChromaDB) for embedding-based search
- **Future**: Neo4j for complex relationship queries (optional)

### Privacy
- All processing happens locally
- Raw data never leaves Jarvis
- Ares receives only behavioral patterns and relationship summaries
- Consider encryption at rest for sensitive data

---

## Key Success Metrics

1. **Entity Resolution Accuracy**: % of cross-platform entities correctly linked
2. **Inference Quality**: User approval rate of generated inferences
3. **Behavioral Accuracy**: Does Ares "sound like" the user?
4. **Re-inference Coverage**: % of affected inferences updated after entity merge
5. **Export Completeness**: Does Digital Spirit capture the full behavioral profile?

---

## Next Steps

1. Review this plan and prioritize based on your goals
2. Start with Sprint 1 (Foundation) - especially the Contacts ingestor
3. The Contacts → Entity Resolution pipeline is the critical path
4. Test with real data early - entity resolution quality depends on real-world patterns
