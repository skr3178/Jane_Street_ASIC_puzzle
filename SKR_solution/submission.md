# Submission — Jane Street ASIC Reverse-Engineering Puzzle

**Form:** <https://docs.google.com/forms/d/e/1FAIpQLScNCnfZ1wC4HbARwynUZ25EKZyqJIzXM_5H5aHom-QeAhE6FA/viewform>
**Blog post:** <https://blog.janestreet.com/can-you-reverse-engineer-an-asic/> (archived locally at [blog-post.md](blog-post.md))
**Deadline:** September 4th, 2026
**Questions:** asic-puzzle@janestreet.com (they answer logistics, not hints)

## The task, as stated by the authors

> Your job is to reverse engineer it. First, recover a netlist from the layout. Then figure out
> the circuit's true purpose. And then comes the puzzle within the puzzle: once you understand
> what the chip does, use it to tease out the output it's looking for, and find the string value
> that's your final answer.

Pointers given in the post:

- The circuit is **physically arranged to hint at its functionality** — look closely at the layout.
- One section generates the output but does not affect `success`. Ignore it for initial RE, but you
  must simulate it to get the final string.
- You need a way to **simulate** the recovered circuit to test candidate solutions.
- You have it right when `success` goes high. **Toggle `rst_n` before each input attempt.**
- Easter eggs are hidden in the circuit and the repository — the form asks about them.

## Rules that affect this submission

- **Do not feed the puzzle files directly into an AI tool, and do not use AI to generate the writeup.**
  Using AI to write scripts/code as part of solving is explicitly allowed, as is using AI on the
  warm-up puzzle.
- No spoilers or public writeups until submissions close (Sept 4, 2026). Collaboration with friends
  is fine. After close, you may publish and email them the link.

## Status

- [x] Recover netlist from `puzzle.gds` — `extract/puzzle/extracted_puzzle.v`, validated 6 ways
- [x] Determine circuit purpose — **a two-star Star Battle checker on an 11×11 grid** (region map
      recovered from the silicon; rules decoded flag-by-flag; `recon/opam/README.md`)
- [x] Find input sequence that drives `success` high — the 122-bit key = the puzzle's unique solution
      (found by BMC cover, then re-derived by an independent Star Battle solver)
- [x] Simulate output generator to read the final string — **`(* TWO STARS *)`** (answer: `TWO STARS`)
- [x] Note any Easter eggs — see `SOLUTION.md` (leap second, "Leave no stone unturned!", OCaml comment,
      five messages incl. `TWO NOT TOUCH` / `EMPTY SKY` / `BIG BANG`, the chip is itself a Star Battle)
- [ ] Write up approach and submit (writeup is written by hand, per the rules)

Answer to enter in the form: `TWO STARS` (literal chip output `(* TWO STARS *)`).

---

## Form fields (copy of the live form)

Can You Reverse Engineer an ASIC? — Submission Form
Cracked the chip? Submit your answer below, along with a writeup of how you did it. We'll feature the most interesting writeups and techniques in a follow-up post on the Jane Street Blog, and we'll send swag for our favorite solutions — we'll use the email you provide to reach out if yours is selected.
Deadline: September 4th, 2026
sangram.kr.rout@gmail.com Switch account

 
Not shared
 
* Indicates required question
Full Name
*

Email
*

What is your current academic or professional status?
*
High school student
University student
PhD Candidate
Professional
Other:

Affiliation 
*
Examples: school, employer, research lab, etc.

Country
*
Confirm the country of your mailing address. We'll use this to prepare swag shipments. 
*Swag may be substituted with items of equal value due to shipping or customs restrictions in certain locations.

Your answer
The string value you recovered from the chip.  
*

Writeup
Provide a brief explanation of what tools you used to reverse-engineer the chip and what you found in the puzzle.

If you're interested in being featured in the follow-up blog, feel free to link to a longer document explaining how you reverse engineered the chip — your approach, any tools you built or used, any problems you ran into, and how you recovered the final answer.
*

Easter Eggs
Did you find any of the easter eggs we hid in the puzzle? Drop them below!

Do you agree to us publishing your name and solution if selected?  
*
Yes
No
Comments
Is there anything else we should know about your submission?

Interested in exploring careers at Jane Street? 
Share your LinkedIn or personal page URL

Never submit passwords through Google Forms.
This form was created inside of Jane Street. - Contact form owner
Does this form look suspicious? Report
Google Forms