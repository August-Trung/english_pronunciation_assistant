# Assistant correction and validation

The assistant authenticates /api/agent/chat via the existing Bearer JWT dependency.
Body user_id/role are retained for request compatibility but never authorize tools.
Queries use authenticated identity. Teacher scope is limited to classes they teach;
unknown class names and ambiguous class selection return clarification instead of
silently choosing the newest class. Student pending homework excludes submitted,
closed, deleted and other classroom assignments. Weak words are scoped to student
or selected teacher class. Grade averages explicitly describe their calculation.

Creating classroom assignments through chat no longer performs a hidden INSERT
with a fixed sentence, IPA and past due date. It offers Open Teacher Hub and explains
that the teacher must choose the class, author and preview content, then assign.
This is navigation assistance, not automatic generation of an assignment draft.
The widget renders explicit navigation buttons and sends an authenticated request.

Other learning questions use Groq conversation without data-changing tools.
Conversation history allows user/assistant text only and is bounded. A provider
failure is disclosed instead of silently matching unrelated broad keywords. English
is used when requested or during roleplay. No claim of hearing pronunciation from
text alone is allowed. HTML is escaped before simple markdown rendering.

Validation: tests/test_assistant_service.py has SQLite fixtures for two teachers,
three learners, active/closed/submitted/pending assignments and separate weak words.
It covers scope, thresholds, unknown/ambiguous classes, no hidden assignment writes,
IPA distinction, roleplay clarification, authentication/body spoofing, provider outage
and empty input. It does not establish real model response quality across every
possible phrase. Live acceptance should test logged-in teacher and student sessions,
role-appropriate tokens, navigation buttons, follow-up learning conversation, and
provider failure. No production test should create/delete user assignments.

Deploy app/main.py and app/assistant_service.py together, then the frontend build.
Preserve live database/media before any backend restart; no public raw snapshots.
