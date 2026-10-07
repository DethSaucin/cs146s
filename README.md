# CS146S self-study

This is my own self-study of **CS146S: The Modern Software Developer** (Stanford, Fall 2026).
I'm not enrolled in the course. Nothing here was submitted or graded. I'm working through the
public materials to learn how modern coding agents work and how to use them well.

## Credit

- Course: **CS146S: The Modern Software Developer**, Stanford University. Instructor: Mihail Eric.
  TAs: Isaac Kan, Vijay Daita. Course site: <https://themodernsoftware.dev>
- Official assignments: <https://github.com/mihail911/modern-software-dev-assignments>.
  Assignment text copied into this repo (for example `week1/assignment_upstream.md`) is the course
  staff's work and is labeled as an upstream copy. The upstream repo has no LICENSE file, so all
  rights stay with the original authors. My own notes, write-ups, and code are everything else here.

## Layout

| Folder | Week topic | Contents |
|---|---|---|
| [`week1/`](week1/) | The Internals of Coding Agents | Trace dissection of a real Claude Code session: [teaching summary](week1/week1_summary.md), [completed write-up](week1/writeup.md), capture and analysis [tools](week1/tools/), and the [scratch repo](week1/scratch-textstats/) the agent worked on |

More weeks will be added as `week2/`, `week3/`, and so on.

## What's intentionally not in this repo

- Raw proxy captures (`*.flows`) and full request dumps. The assignment says to keep traces local, and
  they can contain paths, source code, and credentials. Only short, sanitized excerpts are quoted in
  the write-ups.
- Model weights, virtualenvs, local Claude Code config, and logs (see `.gitignore`).
