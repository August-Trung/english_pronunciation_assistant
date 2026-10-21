# MyHanh classroom registration and sign-in

Primary flow requested by the user:
class invite -> Create Account (username/password, optional full name) -> authenticated
student session -> automatically enroll into the invited class -> Homework.
Sign In is available alongside registration for returning learners. No Gmail or
email address is required. Existing email/Google account sign-in remains available.

Username is case-insensitive, 3–30 ASCII letters/digits/dot/underscore/hyphen.
Password is 8–128 characters and stored only as salted PBKDF2 hash. Internal
username@students.invalid identifiers are blocked from legacy email-only Google
login. Registration detects conflicts (409) and never merges users by name.
Authentication uses the actual student token when enrolling, not a supplied ID.
Six failed password checks per username/client within five minutes are rate-limited.
The rate counter is in-process and resets on backend restart.

The browser stores the signed JWT, never the plaintext password. The session is
valid for 90 days and refreshed on authenticated return. Deleted/suspended users
remain subject to the existing authentication checks. Explicit sign-out clears the
token and has a confirmation. If browser storage is cleared, the learner signs in
again with username/password. There is no recovery key step in the new flow.
Existing key-based learner profiles remain supported without deleting their data.

The registration response is saved before enrollment is attempted. If quota or a
network error prevents joining, the UI explicitly says the account is signed in but
the class could not be joined, and offers retry; it does not recreate the account.
If registration succeeded but its response was lost, the learner can use Sign In
with the same credentials. Registration and enrollment are separate transactions.
Existing /homework?join_code links redirect to /join preserving the invitation.
Email sign-in retains pending class intent. Educators are not silently switched.

Deploy app/main.py + app/learner_access.py and frontend together. Preserve live
DB/media before restart. No new database table is required. Old recordings, scores,
users and enrollments must not be deleted. Never publish raw account snapshots.

Validation: tests/test_learner_access.py covers legacy profile compatibility,
registration/sign-in, normalized usernames/conflicts, invalid classes, password
hashing, login throttling, session refresh, enrollment identity, and quotas. Check
browser registration -> automatic class entry -> reload on a disposable local DB.
