## FAQ

### Why?

The short answer: we couldn't think of a more useless project.

The longer answer: Amiga UNIX is a mostly forgotten corner of Amiga history. It was only around
for a couple of years between 1990 and 1992. Unlike AmigaOS it pretty much vanished the moment
Commodore stopped working on it. In the 30+ years since, a handful of people have tried installing
it and poking at it, but for understandable reasons nobody really built anything new on top of it.
Originally the system was expensive and rare and owned by very few. Therefore it was natural that
it never picked up the nostalgia that AmigaOS did.

We still think Amiga UNIX is an interesting piece of the story. This project is basically about
getting familiar with an old, forgotten system and getting it running on better hardware. The
point is to make Amiga UNIX run on newer Amiga machines and keep a bit of its heritage alive while
we're at it.

### But wouldn't it be better to spend time on Linux or \*BSD?

This project is specifically about Amiga UNIX and preserving it as a piece of Amiga and
computing history. It isn't meant to be serious, or even particularly sensible, but then neither
is using an Amiga in 2026. If you need a computer for actual work, please use a more modern one.

### Can I get Amiga UNIX running on hardware X?

Probably. For the CPU, the main question is whether it has working MMU support. Emulating an
MMU is tricky and slow, so at the moment a real CPU is likely always the fastest option.

What runs today: [Supported hardware](../hardware/index.md). Anything not listed there, another
68060 card for example, is untested: see
[how to ask for it](%SUPPORT_HARDWARE%).

### Do I need a Kickstart ROM?

Yes, your own. We ship none.

### Is this just AI slop?

Many components of this project lean on AI a lot, and there's no point pretending otherwise. It
isn't a requirement, though, and some of the drivers were written the old-fashioned way. Without
it, most of what's here simply wouldn't be realistic, or motivating, in the time we have available
— which is probably why development on Amiga UNIX died in the first place. And even with the help of
AI, most of the projects here have taken months of work and a lot of testing on real hardware. AI does
change the way one can work on totally crazy projects such as these.

### Where do I report a problem?

In [%SUPPORT_REPO%](%SUPPORT_ISSUES%): an issue for a bug or an install problem,
a discussion for a question or an idea. More under [Support](../about/index.md#support).

### How can I help?

Come say hi on the #AMIX channel of the Amiga.dev Discord, or in the Amiga Unix section of the
EAB forums.
