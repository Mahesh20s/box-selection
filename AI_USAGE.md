# AI Usage

> This file was drafted with Claude's help from the actual chat session (see `CHAT_TRANSCRIPT.md`).
> Everything below describes what really happened. Lines marked **TODO(me)** are things only I can
> state truthfully - fill them in before submitting and delete this note.

## 1. Tools used
- **Claude (claude.ai chat)** - the only AI tool used. It generated the project code, tests and docs, and helped me debug errors I hit while running it.
- No Copilot, ChatGPT or Cursor.

## 2. Prompts I gave
The full conversation is in `CHAT_TRANSCRIPT.md`. The key prompts, in order:

1. Uploaded the assignment `.docx` with no message.
2. "help me to create the project as they also sayed that you can take help"
3. "is that the complete project?"
4. "dont we need front end" 
5. "the project is not working" (then pasted the 404 page, warnings, tracebacks and terminal output as I ran each step)
6. "give me the proper ai_usage.md"
7. "explain the project"




## 3. What output I accepted
- **Data model** (`shipping/models.py`): `Product`, `Box`, `Order`, `OrderItem` with dimensions in cm and weights in kg.
- **Recommendation logic** (`shipping/services/packing.py`), kept as pure Python with no Django imports:
  - fast rejections: total weight over the limit, an item that fits in no rotation, total volume larger than the box;
  - a guillotine 3D packing heuristic with 90-degree rotations, trying three item orderings;
  - an independent `verify_placements` check (in bounds, no overlaps);
  - cheapest passing box wins; ties go to the smaller volume, then the name.
- **API** (`shipping/views.py`): `POST /api/recommend-box/`, `GET /api/orders/<ref>/recommend-box/`, a root overview page, JSON errors (400/404).
- **Admin, `seed_data` command, README, GitHub Actions workflow, 33 tests** (`shipping/tests/`).
- **Known limitation, accepted knowingly:** the packer is a heuristic (exact 3D bin packing is NP-hard). It never recommends a box that cannot hold the order, but it can reject a box that an optimal packer would accept. This is documented in the README.

## 4. What output I rejected or modified
- Rejected: building a front end. I asked whether one was needed; the assignment does not require one, so I kept the admin as the data-entry interface.
- Modified after the AI's first version, because of problems I hit (details in section 5): added a root route, made missing orders return a JSON 404, set `DEFAULT_AUTO_FIELD`, raised the minimum Django version to 5.2, added Windows commands to the README.
- **TODO(me): describe my own design change(s)**, for example counting the empty box's weight, adding padding, or changing the tie-break rule - what I changed, why, and which test I added. If I changed nothing, say so honestly here.

## 5. Mistakes the AI made
1. **No page at `/`.** The first version had no root route, so opening `http://127.0.0.1:8000/` showed a Django 404 and looked like the project was broken. Fixed by adding an overview page.
2. **Inconsistent error handling.** The unknown-SKU case returned a JSON 404, but a missing order used `get_object_or_404`, which returns Django's HTML 404 page. Rendering that page under the test client crashed on Python 3.14 with an older Django (`'super' object has no attribute 'dicts'`), so `test_order_not_found` failed on my machine while it passed on the AI's. Fixed by returning a JSON 404 for missing orders.
3. **Requirements too permissive.** `requirements.txt` allowed Django 5.0+, but the first Django to support Python 3.14 is 5.2. My global Python had Django 4.2.29. Fixed by requiring `Django>=5.2,<7.0` and using a virtual environment.
4. **`DEFAULT_AUTO_FIELD` not set.** On my Django version this produced `models.W042` warnings on every command. Fixed by setting it to `BigAutoField`.
5. **Linux-only setup instructions.** The README first used `source .venv/bin/activate`, which does not work in Windows PowerShell. Fixed by adding the Windows activation commands.
6. **Tested only on one setup.** The AI's tests ran on Python 3.12 and Django 5.0-6.1 but not on Python 3.14, which is where the failure above appeared.

Not an AI mistake, but worth recording: I ran `seed_data` before `migrate` and got `no such table: shipping_product`. The README lists `migrate` first.

## 6. How I verified the final code
- **Automated:** `python manage.py test -v 2` - 33 tests pass on my machine (Python 3.14, Django 6.1.1, in a fresh `.venv`). Output is in `TEST_OUTPUT.md`. An earlier run on Django 4.2.29 had 1 error (mistake 2), and it passed after the fix.
- **Manual:** ran `migrate`, `seed_data` and `runserver`, then `curl.exe -i http://127.0.0.1:8000/api/orders/ORD-1001/recommend-box/` and got HTTP 200 with the "Small" box and three placements (mug and two books), which is correct by hand: they fit inside 25x20x10 cm and weigh 1.3 kg against a 2 kg limit.
- **URL routing:** checked with `resolve('/api/orders/ORD-1001/recommend-box/')`, which returned `recommend_for_order`.
- **Environment:** reproduced and fixed the failure by moving from the global Python to a clean virtual environment.
- TODO(me): list any extra checks I do (oversized items, 20 mugs, changed box limits in `/admin/`, code I read line by line).

## 7. What I did not use AI for
`CHAT_TRANSCRIPT.md` is my own export and `LEARNINGS.md` is written entirely by me.