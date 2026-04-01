🎵 Record Hunter (v1.0)
Welcome to Record Hunter! This is a DIY tool designed to audit a personal vinyl collection against "Official" discographies. It helps you find the gaps in your crates so you know exactly what to look for at the record store (or on Trade Me).

🏗️ How it Works (The "Big Picture")
Think of Record Hunter as a three-stage factory:

The Grabber (collector.py): Goes to the internet to see what you already own.

The Library (cataloguer.py): Goes to a different part of the internet to see what an artist actually released.

The Auditor (main.py): Compares the two lists and tells you what's missing.

📂 The File Breakdown
1. collector.py (The Personal Scout)
What it does: Uses your private Discogs API Token to "call" your digital shelf.

The Output: It saves everything it finds into a local file called collection.json.

When to run it: Only when you buy new records and want to update your local list.

2. cataloguer.py (The Music Expert)
What it does: Connects to MusicBrainz (the "Wikipedia of Music").

The Logic: It knows the difference between a "Studio Album" and a "Live/Compilation" album so your "Missing List" doesn't get cluttered with bootlegs.

3. collection.json (The Digital Crate)
What it is: A simple text file that acts as a snapshot of your collection.

Why it's here: It allows main.py to work instantly without having to wait for the internet to load your 300+ records every single time.

4. main.py (The Brains)
What it does: This is the file you actually "Run."

The Magic: It uses "Fuzzy Matching." If your Discogs says U2 - War and MusicBrainz says War, main.py is smart enough to know they are the same thing.

5. .gitignore (The Privacy Shield)
What it does: Tells GitHub: "Don't upload my private passwords or my personal data."

Why it matters: It keeps your private API tokens safe while allowing you to share your cool code with the world.

🔄 The "Circle of Life" Process
Sync: Run collector.py to update your collection.json.

Audit: Run main.py and type an artist name (e.g., The Cure).

Discover: Review the ✅ Owned vs ❌ Missing report.

Hunt: Click the automatically generated Trade Me links to go find those missing gems.

🛠️ Tech Stack for Learners
Language: Python 3

APIs: Discogs (Personal Data) & MusicBrainz (Official Data)

Matching: Difflib (Fuzzy String Matching)

Version Control: Git & GitHub
