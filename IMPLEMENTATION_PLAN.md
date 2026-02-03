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

---

# APPENDIX: Research & Implementation Suggestions

The following sections contain 300+ curated suggestions from research across multiple AI systems and academic sources. These are organized by category for easy reference during implementation.

---

## A. Behavioral Fingerprint Features (70+ Extractable Signals)

**Key Insight**: These features capture HOW you communicate without storing WHAT you say. Think "feature vectors," not transcripts.

### A.1 Stylometry & Surface Fingerprints (Message-Level)

| # | Feature | Description |
|---|---------|-------------|
| 1 | Character n-grams | Robust stylometry baseline; content-light |
| 2 | Word-shape features | Xxxx vs xxxx vs XXXX, digit patterns |
| 3 | Punctuation profile | Periods vs dashes vs semicolons vs ellipses |
| 4 | Emoji usage histogram | Types, density, position (start/middle/end) |
| 5 | Exclamation/question rates | And combos like "?!", "!!", "??" |
| 6 | Capitalization habits | ALL CAPS bursts, sentence-case consistency |
| 7 | Contraction rate | "I'm" vs "I am" as informality marker |
| 8 | Average message length + variance | Per-platform distribution |
| 9 | Sentence count per message | Single-shot vs multi-sentence style |
| 10 | Link/media attachment frequency | URLs, images, voice notes as behavior |

### A.2 Syntax & Structure (How You Build Sentences)

| # | Feature | Description |
|---|---------|-------------|
| 11 | POS-tag n-grams | Part-of-speech patterns; less content-dependent |
| 12 | Dependency depth stats | Simple vs nested syntax |
| 13 | Clause/subordination rate | "because/although/while" usage |
| 14 | Passive voice probability | Correlates with formality/hedging |
| 15 | Question vs statement ratio | Curiosity/leadership signal |
| 16 | List/formatting habits | Bullets, numbering, line breaks |
| 17 | Discourse marker frequency | "so," "anyway," "btw," "tbh" |

### A.3 Formality, Assertiveness, Politeness (Pragmatics)

| # | Feature | Description |
|---|---------|-------------|
| 18 | Formality score | Via feature mix (contractions↓, slang↓, structure↑) |
| 19 | Readability indices | Flesch–Kincaid, Gunning Fog as style proxies |
| 20 | Hedge density | "maybe," "kinda," "I think," "might" |
| 21 | Certainty markers | "definitely," "no doubt," "I'm sure" |
| 22 | Imperative/directive rate | "Do X" vs "Could we…" |
| 23 | Modal verbs balance | "should" vs "could" vs "must" |
| 24 | Politeness classifier score | please/thanks/apologies + phrasing cues |
| 25 | Boundary-setting markers | "can't," "not possible," "won't," "later" |

### A.4 Sentiment & Affect (Tone, Not Topics)

| # | Feature | Tool/Method |
|---|---------|-------------|
| 26 | VADER sentiment | Fast + good for short informal messages |
| 27 | TextBlob sentiment/subjectivity | Simple baseline |
| 28 | Flair sentiment | Stronger ML baseline |
| 29 | Transformer sentiment | Hugging Face models for nuance |
| 30 | Emotion lexicons | Joy/anger/sadness/fear distributions |
| 31 | Arousal/valence scoring | Calm vs excited tone over time |
| 32 | Sentiment volatility | How swingy your tone is across a thread |
| 33 | Tone mirroring | Do you match the other person's sentiment? |

### A.5 Temporal Patterns & Responsiveness

| # | Feature | Description |
|---|---------|-------------|
| 34 | Response latency distribution | Per contact (median, p90, long-tail) |
| 35 | Time-to-first-reply survival models | Hazard of replying vs time |
| 36 | Circadian + weekday heatmaps | When you initiate vs respond |
| 37 | Burstiness (inter-message CV) | Steady chatter vs clustered bursts |
| 38 | Sessionization by idle gaps | Define "conversations" from timestamps |
| 39 | Double-text rate | You send again before they reply |
| 40 | Escalation behavior | Switch to call/voice note when delayed |
| 41 | Priority inference model | Predict reply speed from non-content cues |

### A.6 Cross-Platform Persona Comparison

| # | Feature | Description |
|---|---------|-------------|
| 42 | Platform-specific normalization | Compare z-scored features, not raw |
| 43 | Platform embeddings | One "style vector" per platform, same schema |
| 44 | KL-divergence | Between platform feature distributions (persona gap) |
| 45 | Domain adaptation | Separate "you" signal from platform artifacts |
| 46 | Multitask model | Shared backbone + platform "heads" |
| 47 | Invariance tests | Which features stay stable across platforms? |
| 48 | Style drift tracking | How your platform persona changes monthly |

### A.7 Conversation-Level Dynamics (Thread Behavior)

| # | Feature | Description |
|---|---------|-------------|
| 49 | Turn-taking ratio | Who dominates; your share of turns |
| 50 | Initiation rate | How often you start threads vs respond |
| 51 | Thread length distribution | Quick closes vs long dialogues |
| 52 | Question-asking cadence | Questions per 10 turns |
| 53 | Repair/clarification moves | "wait," "to clarify," "meaning…" frequency |
| 54 | Closure signatures | How you end: "cool/thanks/✅/talk soon" |
| 55 | Latency elasticity | Do you speed up once the thread is "hot"? |

### A.8 Relationship Strength Inference (Non-Content)

| # | Feature | Description |
|---|---------|-------------|
| 56 | Interaction frequency | Rolling 7/30/90-day message counts |
| 57 | Reciprocity index | Sent/received balance |
| 58 | Mutual responsiveness | Both parties' median reply time |
| 59 | Regularity/entropy | Of contact times (routine vs sporadic) |
| 60 | Relationship longevity | Active months; reactivation patterns |
| 61 | Language-style matching (LSM) | Function-word alignment |
| 62 | Coordination markers rate | "let's," "we should," scheduling patterns |
| 63 | Context switching | Work-hours only vs all-hours availability |
| 64 | Network features | Shared groups, triadic closure, centrality |

### A.9 Privacy-Preserving Feature Engineering

| # | Technique | Description |
|---|-----------|-------------|
| 65 | Named-entity stripping | Keep only counts/types, not the entities |
| 66 | Hashing trick for n-grams | Store hashes, not tokens |
| 67 | Store aggregates only | Per-contact/per-platform histograms, not text |
| 68 | Random projections | Obfuscate feature vectors against inversion |
| 69 | Differential privacy noise | On sensitive aggregates (contact-level stats) |
| 70 | On-device extraction | Raw text never leaves local machine |

### A.10 Implementation Pattern

```
raw text → ephemeral parsing → feature vector → discard raw → train/predict on vectors
```

You get "you-ness" without the gossip. This creates a **behavioral genome**: stable traits (punctuation, hedging, timing) + situational traits (platform, relationship, urgency).

---

## B. LLM Optimization for M2 MacBook (16GB RAM)

### B.1 Batching Strategies

| Strategy | Description |
|----------|-------------|
| Process in chunks | 100–200 messages at a time to prevent OOM |
| Group by length/source | Uniform-length batches make efficient use of context window |
| Multi-item prompts | List several items in one prompt, ask model to respond to each |
| Hierarchical summarization | First summarize chunks, then summarize summaries |
| Asynchronous processing | Overlap I/O and computation to keep pipeline busy |
| Continuous batching | Use vLLM or ray for automatic batching if applicable |

### B.2 Embeddings vs LLM Calls Decision Matrix

| Use Embeddings For | Use LLM Calls For |
|--------------------|-------------------|
| Search & recall (index data, find similar) | Complex reasoning requiring interpretation |
| Retrieval-augmented queries (RAG) | Summarizing conversation meaning |
| Clustering and trend analysis | Extracting nuanced sentiments |
| Finding duplicates | Generating new text |
| Recommending similar notes | Understanding context |

### B.3 Model Selection Guide

| Model | Params | Use Case | Notes |
|-------|--------|----------|-------|
| **Phi-3 mini** | 3.8B | Quick classification, filtering | Matches 7B+ on reasoning, 128K context |
| **Mistral 7B** | 7B | General tasks | Outperforms Llama-2 13B, efficient architecture |
| **Llama 3 8B** | 8B | Dialogue, complex analysis | Good all-rounder |
| **spaCy/DistilBERT** | ~100M | NER, sentiment, language detection | CPU-friendly, deterministic |

### B.4 Prompt Engineering for Structured Output

- **Define clear format**: "Provide output as JSON with keys: date, sender, summary"
- **Use delimiters**: Triple backticks for code/data segments
- **Provide examples**: Few-shot with input → output pairs
- **Ask for lists/tables**: Easier to parse than prose
- **Iterative refinement**: Secondary prompt to reformat if needed
- **Avoid open-ended**: Specific instructions reduce variability

### B.5 Caching Strategies

| Strategy | Description |
|----------|-------------|
| Memoize repeated queries | Cache results keyed by hash of prompt text |
| Embed once, use many | Generate embeddings once, save to disk |
| Intermediate results caching | Cache outputs of each pipeline stage |
| Exact-match prompt cache | Key-value store for identical prompts |
| Semantic caching | Reuse past result if new prompt is very similar |

### B.6 Regex vs LLM Decision

| Use Regex For | Use LLM For |
|---------------|-------------|
| Deterministic patterns (emails, phones, dates, URLs) | Context-dependent fuzzy extraction |
| Well-defined formats | Variable formats requiring interpretation |
| Speed-critical paths | "Find all mentions of project delays" |
| 100% consistency needed | Complex semantic understanding |

**Pro tip**: LLM-generated regex – ask the LLM to produce a regex pattern, then use that regex directly.

### B.7 Quantization

| Level | Memory Reduction | Quality Impact | Notes |
|-------|------------------|----------------|-------|
| 4-bit | ~75% | Minor (<1%) | Ollama default, recommended |
| 5-bit | ~68% | Minimal | Good balance |
| 8-bit | ~50% | Near-identical | Higher quality if RAM allows |

### B.8 Parallel Processing on Apple Silicon

- **Multi-core**: Run independent tasks in parallel threads (8 cores available)
- **Avoid bandwidth saturation**: CPU + GPU share memory bandwidth
- **Mix workloads**: Use GPU for LLM, CPU for preprocessing simultaneously
- **Threading in libraries**: Configure llama.cpp threads (-t 4-6)
- **Memory caution**: Two 7B models in parallel = ~16GB (will swap)

### B.9 Memory Management

- **7B model in 4-bit**: ~8GB RAM (safe for 16GB Mac)
- **13B model in 4-bit**: ~16GB RAM (leaves nothing for OS)
- **One model at a time**: Load embedding model → process → unload → load LLM
- **Stream data from disk**: Don't load entire dataset into RAM
- **Clear context frequently**: Reset LLM context after it grows large

---

## C. Entity Resolution Research & Techniques

### C.1 Algorithms & Matching

| Technique | Description | Tool/Library |
|-----------|-------------|--------------|
| Probabilistic Record Linkage | Fellegi-Sunter model with weighted attributes | Splink |
| Deterministic Rules | Exact match on unique IDs (email, phone) | Custom |
| Jaro-Winkler | Fuzzy string matching for similar names | jellyfish |
| Phonetic Encoding | Soundex, Metaphone for pronunciation matching | jellyfish |
| Blocking | Group by coarse key before detailed comparison | dedupe |
| Two-pass Matching | Quick pass for obvious matches, then fuzzy | Custom |
| Graph Connectivity | Union-find on match edges | NetworkX |
| Active Learning | Label a few pairs, model improves | dedupe |
| Siamese Networks | Neural network comparing record pairs | DeepMatcher |

### C.2 Knowledge Graph Design

```
Person (node)
  ├── HAS_ACCOUNT → Instagram Account (@looganoo)
  ├── HAS_ACCOUNT → iMessage Handle (+1234567890)
  ├── HAS_ACCOUNT → Email (logan@example.com)
  ├── ALIAS → "Logan", "LR", "Ruddick"
  └── FRIEND_OF → Other Person nodes
```

### C.3 Name Matching & Embeddings

- **Embed names**: Use sentence-transformers to catch "Jon" vs "Johnathan"
- **Profile text embeddings**: Similar bios = likely same person
- **FastText for names**: Handles unusual names via subword patterns
- **Composite embeddings**: "Alex Lee California" vs "Alex Lee New York"
- **Vector search**: FAISS/Annoy for nearest neighbors

### C.4 Tools & Libraries

| Tool | Description |
|------|-------------|
| **dedupe** | ML-based matching with active learning |
| **Splink** | Probabilistic linkage, scales to millions |
| **PyJedAI** | State-of-the-art ER algorithms in Python |
| **DeepMatcher** | Neural network for entity matching |
| **recordlinkage** | Simple Python interface for prototyping |
| **jellyfish** | Fast phonetic keys and string distance |
| **NetworkX** | In-memory graph for entity networks |
| **Neo4j** | Graph database for complex queries |

### C.5 Heuristics for Nicknames/Typos

| Heuristic | Example |
|-----------|---------|
| Nickname dictionary | Bob → Robert, Liz → Elizabeth |
| Case/accent normalization | José = Jose, Özil = Ozil |
| Edit distance threshold | Allow distance 1-2 for typos |
| Initials handling | "John P. Doe" ≈ "John Doe" |
| Transliteration | "Алексей" → "Alexey" |

### C.6 Academic Papers

| Paper | Key Insight |
|-------|-------------|
| Shu et al. (2017) | Survey of cross-platform identity linkage |
| Hydra (SIGMOD 2014) | Multi-behavioral features improve accuracy |
| Bartunov et al. (2012) | Network links + profile attributes together |
| Zhang et al. (2020) | Graph embeddings for user alignment |

---

## D. Embeddings & Vector Search Optimization

### D.1 Model Selection

| Model | Dims | Speed | Use Case |
|-------|------|-------|----------|
| MiniLM | 384 | Fast | Good for resource-constrained |
| MPNet | 768 | Medium | Higher accuracy |
| BGE-en | 1024 | Slow | State-of-the-art |
| nomic-embed-text | 768 | Fast | Ollama-compatible |

### D.2 Quantization

| Level | Reduction | Method |
|-------|-----------|--------|
| Float32 → Uint8 | 75% | Qdrant scalar quantization |
| Float32 → Binary | 96% (32×) | Hamming distance search |
| Product Quantization | Variable | Faiss IVF-PQ |

### D.3 Vector Database Comparison

| DB | Deployment | Best For |
|----|------------|----------|
| **ChromaDB** | Embedded (Python) | Prototypes, small data |
| **Qdrant** | Standalone/Docker | Performance, production |
| **LanceDB** | Embedded (Arrow) | Multi-modal, serverless |
| **Faiss** | Library | Maximum control, scale |

### D.4 Chunking Strategies

| Content Type | Strategy |
|--------------|----------|
| Long documents | 300-500 tokens with 10-20% overlap |
| Chat logs | Group consecutive messages by time window |
| Emails | One email = one chunk (unless very long) |
| Tweets/SMS | No chunking needed; use as-is |
| PDFs | Split by paragraph or section headers |

### D.5 Hybrid Search

- **Blend semantic + lexical**: Catch exact keyword matches
- **Use metadata filters**: source=SMS, year=2020
- **Re-rank top-N**: Cross-encoder on top 50 candidates
- **Exact-match fallbacks**: For error codes, IDs, rare terms

### D.6 Caching

- Cache embeddings keyed by text hash (MD5/SHA256)
- Precompute static data (old emails, archives) overnight
- LRU eviction for memory management
- Cache query embeddings for repeated/similar questions

### D.7 Dimension Reduction

| Method | Reduction | Quality Loss |
|--------|-----------|--------------|
| PCA 768→128 | 83% | ~5% |
| Autoencoder | Variable | Can be lower than PCA |
| Matryoshka | First N dims | ~7% at 1/12 dims |

---

## E. Platform-Specific Ingestion Tips

### E.1 iMessage (chat.db)

```sql
-- Key query pattern
SELECT m.rowid, m.text, m.date, m.is_from_me, h.id as handle_id
FROM message m
LEFT JOIN handle h ON m.handle_id = h.rowid
LEFT JOIN chat_message_join cmj ON m.rowid = cmj.message_id
WHERE m.text IS NOT NULL
```

| Tip | Details |
|-----|---------|
| Timestamp conversion | `(date/1e9) + 978307200` → Unix time |
| Newer macOS | Text in `attributedBody` (hex-serialized NSAttributedString) |
| Attachments | Use `attachment` table, `filename` column has paths |
| Conversation windows | Group messages within 60 minutes = one conversation |

### E.2 Instagram (JSON Export)

| Tip | Details |
|-----|---------|
| Multiple files | Iterate `messages/inbox/*/message_*.json` |
| Encoding fix | If garbled, decode Latin-1 → UTF-8 |
| Timestamps | Unix milliseconds, divide by 1000 |
| Media | Reference files in export archive |

### E.3 Facebook (JSON/HTML)

| Tip | Details |
|-----|---------|
| Multi-part messages | Combine `message_1.json`, `message_2.json` in order |
| Unicode fix | Multi-byte chars broken into `\u00XX` sequences |
| Reactions | Array of reaction objects with emoji + actor |
| Timestamps | `timestamp_ms` in milliseconds, UTC |

### E.4 X/Twitter (JSON)

| Tip | Details |
|-----|---------|
| Large files | Use streaming JSON parser (ijson) |
| Large IDs | Treat as strings to avoid overflow |
| Timestamps | Parse "Wed Oct 10 20:19:24 +0000 2025" format |
| Threading | Use `in_reply_to_status_id` or `conversation_id` |

### E.5 Gmail (MBOX)

| Tip | Details |
|-----|---------|
| Use libraries | Python `mailbox` or `email` package |
| Deduplication | Use `Message-ID` header |
| Threading | Use `In-Reply-To` and `References` headers |
| Large MBOX | Split by year/month, stream line by line |

### E.6 Safari (History.db)

```sql
SELECT h.url, h.title, v.visit_time + 978307200 as unix_time
FROM history_items h
JOIN history_visits v ON h.id = v.history_item
```

### E.7 Apple Notes (NoteStore.sqlite)

- Use `apple-notes-parser` library
- Content is gzipped binary, needs decoding
- Timestamps use Apple epoch (+978307200)
- Attachments in separate table or files

### E.8 Contacts (vCard)

- Use vCard parsing library
- Deduplicate by UID field
- Photos are base64 encoded
- Map to unified schema (first, last, phones[], emails[])

### E.9 ChatGPT Export

- Messages in tree structure, walk via `parent` pointers
- Preserve `author.role` (user/assistant/system)
- Content may have `parts` array, concatenate
- Format changed in 2024, build flexible parser

### E.10 PDFs

- Use PyMuPDF or PDFBox for text extraction
- OCR scanned PDFs with Tesseract
- Extract metadata (title, author, dates)
- Process in chunks for large files

---

## F. Cross-Platform Best Practices (25 Key Strategies)

| # | Strategy | Description |
|---|----------|-------------|
| 1 | **UTF-8 everywhere** | Standardize all text encoding |
| 2 | **Normalize Unicode** | NFC/NFD for consistent comparisons |
| 3 | **Preserve raw data** | Archive originals for re-processing |
| 4 | **Content hash dedup** | MD5/SHA256 to catch duplicates |
| 5 | **UTC timestamps** | Single time standard, convert on ingestion |
| 6 | **Timezone-aware storage** | Store UTC, convert for display |
| 7 | **Unified attachments** | Single table with references, not BLOBs |
| 8 | **Files on disk** | Don't store large binaries in DB |
| 9 | **Thread/Conversation model** | Unified entity linking messages |
| 10 | **Master contact table** | Map participants across platforms |
| 11 | **Extensible metadata** | JSON field for platform-specific extras |
| 12 | **Status indicators** | read/unread, starred, pinned fields |
| 13 | **Batch processing** | Chunks of 1000 records, periodic commits |
| 14 | **Parallel ingestion** | Multiple cores for huge datasets |
| 15 | **Checkpoint/resume** | Progress log for interrupted jobs |
| 16 | **Stream, don't load** | Generators for memory efficiency |
| 17 | **Index key fields** | Timestamps, sender, thread_id |
| 18 | **Archive originals** | Keep raw export files |
| 19 | **Audit logs** | Log parsing errors with identifiers |
| 20 | **Incremental updates** | Upsert by unique ID, don't duplicate |
| 21 | **Encryption at rest** | Secure the unified storage |
| 22 | **Compress text** | Text compresses well |
| 23 | **Test on samples** | Validate edge cases before full run |
| 24 | **Monitor resources** | CPU, memory during ingestion |
| 25 | **Document schema mapping** | How each platform maps to unified schema |

---

## G. High-Impact Priorities (Top 20)

Based on cross-referencing suggestions from multiple sources:

### Tier 1: Foundation (Do First)

1. **Contacts ingestor as ground truth** - Phone/email/social handles are canonical identifiers
2. **60-minute conversation windows for iMessage** - Analyze conversations, not individual texts
3. **UTF-8 normalization everywhere** - Prevents encoding bugs across all sources
4. **Embed once, cache forever** - Generate embeddings for static data once
5. **4-bit quantization for local LLMs** - 75% memory savings, minimal quality loss

### Tier 2: Entity Resolution (Critical Path)

6. **Deterministic ID matching first** - Same phone/email = same person (100% confidence)
7. **Phonetic encoding (Soundex/Metaphone)** - Catch "Jon" vs "John"
8. **Nickname dictionary** - Bob↔Robert, Liz↔Elizabeth mappings
9. **Active learning with dedupe** - System improves from your corrections
10. **Network proximity scoring** - Shared connections boost match confidence

### Tier 3: Behavioral Analysis (Core Value)

11. **Response latency distribution per contact** - Key relationship signal
12. **Formality score per platform** - Captures persona switching
13. **Turn-taking ratio** - Leadership/dominance in conversations
14. **Initiation rate** - Who starts conversations
15. **Sentiment volatility** - Emotional consistency/variability

### Tier 4: Performance & Scale

16. **Blocking before detailed matching** - Critical for scale
17. **Hybrid search (vector + keyword)** - Don't miss exact matches
18. **Hierarchical summarization** - Chunk → summarize → summarize summaries
19. **Stream large files** - Never load 10GB+ into memory
20. **Index timestamps + sender** - Fast queries on common patterns

---

## H. Quick Wins (Easy + High Value)

| Win | Effort | Impact |
|-----|--------|--------|
| Use VADER for sentiment | 1 hour | Immediate tone analysis |
| Add emoji histogram | 2 hours | Strong behavioral signal |
| Implement response time tracking | 2 hours | Relationship strength proxy |
| Create nickname dictionary | 1 hour | Better entity matching |
| Enable 4-bit quantization | 30 min | 75% memory savings |
| Cache embeddings to disk | 2 hours | Faster restarts |
| Add conversation sessionization | 3 hours | Better context for analysis |
| Normalize all timestamps to UTC | 2 hours | Cross-source timeline |

---

## I. Research Rabbit Holes Worth Exploring

1. **Matryoshka embeddings** - OpenAI technique for using first N dims of larger embedding
2. **Language Style Matching (LSM)** - Pennebaker's research on function-word alignment
3. **Survival analysis for response times** - Hazard models for reply prediction
4. **Federated learning for personal AI** - Privacy-preserving training approaches
5. **Differential privacy on aggregates** - Mathematical privacy guarantees
6. **Knowledge distillation** - Train smaller model on larger model's outputs
7. **Siamese networks for entity matching** - Neural approach to record linkage
8. **Graph neural networks for identity** - Node2Vec, GraphSAGE for entity embeddings
9. **Cross-encoder re-ranking** - BERT-based final ranking of search results
10. **Conversation analysis (CA)** - Academic field studying turn-taking, repair sequences

---

## J. Contrarian Ideas (Might Be Genius or Bad)

| Idea | Potential | Risk |
|------|-----------|------|
| **Skip embeddings entirely** - Just use TF-IDF + cosine | Fast, simple, interpretable | May miss semantic similarity |
| **Binary embeddings only** - 32× compression | Blazing fast search | Quality loss on nuanced queries |
| **No LLM for inference** - Pure statistical features | Deterministic, fast, explainable | May miss complex patterns |
| **Graph DB from day 1** - Neo4j instead of SQLite | Rich relationship queries | Overkill for MVP, slower dev |
| **Fine-tune on your data** - LoRA on personal corpus | Perfect style matching | Expensive, risk of overfitting |
| **Store raw text temporarily** - Delete after feature extraction | Maximum privacy | Can't re-analyze later |
| **Behavior-only export** - Zero entity names to Ares | Maximum privacy | Less personalized responses |

---

## K. Safety & Ethics Guardrails

If building a "clone," add safeguards against impersonation:

1. **Visible disclosure**: "AI-assisted" label on all outputs
2. **Audit logs**: Track all usage with timestamps
3. **Strict scoping**: Only allowed to draft, never auto-send
4. **Kill switch**: Instant revocation of Digital Spirit
5. **No identity theft**: Don't impersonate in harmful contexts
6. **Consent tracking**: Log what data was used for what inference
7. **Right to delete**: User can purge any data/inference

---

## L. Architecture Pattern Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW PATTERN                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  RAW DATA                                                                │
│     │                                                                    │
│     ▼                                                                    │
│  ┌─────────────┐                                                         │
│  │  Ingestors  │ ── Platform-specific parsing                           │
│  │             │ ── Timestamp normalization (UTC)                        │
│  │             │ ── Encoding fix (UTF-8)                                 │
│  └─────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────┐                                                         │
│  │  Entity     │ ── Deterministic matching (phone/email)                │
│  │  Resolution │ ── Fuzzy matching (name similarity)                    │
│  │             │ ── Human confirmation for ambiguous                    │
│  └─────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────┐                                                         │
│  │  Feature    │ ── 70+ behavioral features                             │
│  │  Extraction │ ── Stylometry, timing, sentiment                       │
│  │             │ ── Per-contact, per-platform                           │
│  └─────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────┐                                                         │
│  │  Inference  │ ── Cross-source pattern detection                      │
│  │  Generation │ ── LLM for complex reasoning                           │
│  │             │ ── Confidence scoring                                  │
│  └─────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────┐                                                         │
│  │   Triage    │ ── Human approval/rejection                            │
│  │   Interface │ ── Entity confirmation                                 │
│  │             │ ── Feedback improves system                            │
│  └─────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────┐                                                         │
│  │  Digital    │ ── Behavioral patterns only                            │
│  │  Spirit     │ ── No raw data                                         │
│  │  Export     │ ── Encrypted JSON                                      │
│  └─────┬───────┘                                                         │
│        │                                                                 │
│        ▼                                                                 │
│     ARES (Remote) ── Uses patterns to "be you"                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*End of Research Appendix*
