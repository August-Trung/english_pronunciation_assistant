# Email-free MyHanh classroom entry

Teachers share /join?join_code=... on MyHanh. Existing /homework?join_code=...
links redirect to the new entry while preserving the code. Unauthenticated learners
see class metadata, enter their full name and join without Gmail/email/password.
The server creates a normal student identity and reuses existing enrollment/license
quota checks. Name alone never restores or merges identities.

The browser generates a 256-bit random Student Key and saves it before requesting
join (idempotent retries). The backend derives an internal learners.invalid identifier
and stores only the salted password hash of the key. On return, /learners/resume
verifies the key and issues a fresh JWT; no email-only auto-login is allowed for
these identities. Existing email account users can still sign in and join their own
profile. Join enrollment now requires authenticated ownership for ordinary users.

Keys are sensitive account credentials: never send them in chat/logs/URLs. The
learner can privately save their key with a parent or open Student Key in the account
menu. The same key restores the same user/enrollments on another device. If browser
data is cleared, private browsing is used, or the user explicitly signs out, automatic
return cannot be guaranteed; the saved key is needed. Explicit sign-out has a
confirmation and clears the device key. Existing student sessions are reused; an
educator is not silently switched to a new student account.

The database stores profiles, enrollments, history and submissions, so retaining
live DB snapshots across ephemeral backend redeployments remains required.
No migration/new table is introduced. If quota prevents joining, an un-enrolled
identity may remain for a safe retry; it does not count as an enrolled seat.
The frontend must be deployed with app/main.py and app/learner_access.py together.
Preserve live data/media before restart and never publish raw account backups.

Validation: 11 focused tests cover first join, repeat requests, resume, same-name
separation, invalid/archived/non-elementary links, recovery key validation, deleted
profiles, quotas, email-only login rejection and enrollment ownership.
Local browser fixture verified legacy link redirect, no-email enrollment, entering
Homework, reload restoring the same learner and class, and confirmed sign-out
preventing silent re-entry. It used an isolated SQLite fixture, not real children.
