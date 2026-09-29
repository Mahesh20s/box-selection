
# What I Learned Building the Box Selection System

## Setup, Database Migrations, and Python Versions
I did not write the Product model code from scratch; Claude generated the model file. However, I read through the fields, ran python manage.py migrate, and watched Django create the underlying database tables.

Setting up the project locally brought up two practical environment issues:
1. Migration Order: Running python manage.py seed_data on an unmigrated database threw a "no such table" error because the command queried models before the database tables existed. Running python manage.py migrate first resolved this issue.
2. Python and Django Versioning: Running tests under Python 3.14 initially failed because my global Python installation had an older Django version (4.2.29) installed, which did not support Python 3.14. Creating a fresh virtual environment (.venv) with a newer Django version fixed the test client runner.

## Understanding Django Management Commands
I did not write seed_data.py, but I read and executed it. I learned that Django management commands are Python files saved inside an app's management/commands/ directory. When running python manage.py seed_data, Django matches the command name to seed_data.py and executes the Command class defined inside it.

## How the Packing Algorithm Works in Code
After re-reading shipping/services/packing.py, I mapped out how the box selection logic functions in practice. The algorithm first screens out boxes that cannot work by checking if the order's combined weight exceeds the box capacity, if any single item fails to fit under all six rotations, or if total item volume exceeds box volume. For valid candidate boxes, it checks item layouts using three ordering strategies: sorting items by volume, by longest side, or by shortest side. It tests spatial fitting sequentially with 6-way item rotations, stopping at the first valid layout. After testing all boxes, it selects the winner using Python's min() function—choosing the box with the lowest cost, using smallest internal volume as the first tie-breaker, and box name as the second. Because this uses a greedy search without spatial backtracking, it can sometimes reject a box that might physically fit items if packed in a different order.

## Catching AI Inconsistencies and Testing
I learned to verify AI output through hands-on testing rather than assuming generated code works. When running unit tests locally, a test failed because missing order lookups returned HTML error pages instead of JSON error responses. I also hit a 404 page when navigating to the root URL (/) because no root endpoint had been configured. To verify the project end-to-end, I ran the test suite via python manage.py test and manually tested endpoints using curl to confirm expected JSON payloads.


